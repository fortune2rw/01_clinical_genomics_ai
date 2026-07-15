import gzip
import io
import json
import tarfile
import time
from pathlib import Path
import pandas as pd
import requests

BASE_URL = "https://api.gdc.cancer.gov/"
CASE_ENDPT = "cases"
DATA_ENDPT = "data"
FILES_ENDPT = "files"

PROJECTS = ["TCGA-BRCA", "TCGA-LAML"]

BATCH_SIZE = 50      # files per download request 
MAX_RETRIES = 3
REQUEST_TIMEOUT = 120  # seconds

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Helper: validate field names against GDC's live schema
# before using them in a real query. 
# ---------------------------------------------------------
def validate_fields(fields, endpoint):
    resp = requests.get(f"{BASE_URL}{endpoint}/_mapping")
    resp.raise_for_status()
    valid_fields = set(resp.json()["fields"])

    invalid = [f for f in fields if f not in valid_fields]
    if invalid:
        raise ValueError(f"Invalid GDC field(s) for '{endpoint}': {invalid}")
    print(f"[validate] All {len(fields)} fields OK for '{endpoint}' endpoint.")


# ---------------------------------------------------------
# cli metadata
# ---------------------------------------------------------
cli_fields = [
    "submitter_id",
    "case_id",
    "diagnoses.age_at_diagnosis",
    "demographic.sex_at_birth",                     
    "demographic.vital_status",
    "demographic.days_to_death",
    "diagnoses.days_to_last_follow_up",
    "demographic.age_at_index",
    "diagnoses.primary_diagnosis",
    "diagnoses.eln_risk_classification",             
    "diagnoses.treatments.treatment_type",
    "diagnoses.treatments.treatment_outcome",
    "diagnoses.treatments.treatment_effect",
    "diagnoses.treatments.treatment_or_therapy",
    "family_histories.relative_with_cancer_history",
    "exposures.tobacco_smoking_status",
    "exposures.alcohol_history"
]

validate_fields(cli_fields, CASE_ENDPT)

cli_filters = {
    "op": "in",
    "content": {
        "field": "project.project_id",
        "value": PROJECTS
    }
}

cli_params = {
    "filters": json.dumps(cli_filters),
    "fields": ",".join(cli_fields),
    "format": "TSV",
    "size": "1500"
}

response = requests.get(BASE_URL + CASE_ENDPT, params=cli_params)
print(response.status_code)
response.raise_for_status()

cli_out = raw_dir / "cli_metadata.tsv"
with open(cli_out, "wb") as f:
    f.write(response.content)
print(f"Saved cli metadata to {cli_out} Successfully")

# ---------------------------------------------------------
# Mutation file metadata (find file UUIDs)
# ---------------------------------------------------------
mut_filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "cases.project.project_id",
                "value": PROJECTS
            }
        },
        {
            "op": "in",
            "content": {
                "field": "data_type",
                "value": ["Masked Somatic Mutation"]
            }
        }
    ]
}

mut_meta_fields = [
    "file_id", "file_name", "cases.submitter_id", "cases.case_id",
    "cases.project.project_id", "data_category", "data_type",
    "experimental_strategy", "analysis.workflow_type"
]

validate_fields(mut_meta_fields, FILES_ENDPT)

mut_params = {
    "filters": json.dumps(mut_filters),
    "fields": ",".join(mut_meta_fields),
    "format": "JSON",
    "size": "1500"
}

mut_meta_response = requests.get(BASE_URL + FILES_ENDPT, params=mut_params)
print(mut_meta_response.status_code)
mut_meta_response.raise_for_status()

mut_meta_out = raw_dir / "mut_metadata.json"
with open(mut_meta_out, "wb") as f:
    f.write(mut_meta_response.content)
print(f"Saved mutation file metadata to {mut_meta_out}")

file_ids = [hit["file_id"] for hit in mut_meta_response.json()["data"]["hits"]]
print(f"Found {len(file_ids)} mutation files")

if len(file_ids) == 0:
    print("No mutation files found for the specified projects. Exiting.")
    raise SystemExit(0)

# ---------------------------------------------------------
# Download the actual mutation (MAF) files, in batches.
# GDC resets the connection if you request hundreds/thousands
# of files in a single POST, so we split into small batches,
# retry on failure, and save each batch as its own archive.
# ---------------------------------------------------------
def download_batch(batch_ids, out_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                BASE_URL + DATA_ENDPT,
                data=json.dumps({"ids": batch_ids}),
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()

            # GDC sometimes returns a JSON error body instead of the
            # archive (e.g. bad request) — catch that before saving.
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                print(f"  GDC returned an error instead of a file: {resp.text[:200]}")
                return False

            with open(out_path, "wb") as f:
                f.write(resp.content)
            return True

        except requests.exceptions.RequestException as e:
            print(f"  attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(5)

    return False


archive_paths = []
num_batches = (len(file_ids) + BATCH_SIZE - 1) // BATCH_SIZE

for i in range(0, len(file_ids), BATCH_SIZE):
    batch = file_ids[i:i + BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    print(f"Downloading batch {batch_num}/{num_batches} ({len(batch)} files)...")

    batch_out = raw_dir / f"mut_files_batch{batch_num}.tar.gz"
    success = download_batch(batch, batch_out)

    if success:
        archive_paths.append(batch_out)
        print(f"  Saved {batch_out}")
    else:
        print(f"  Batch {batch_num} failed after {MAX_RETRIES} attempts — skipping.")

print(f"Downloaded {len(archive_paths)}/{num_batches} batches successfully.")

# ---------------------------------------------------------
# Extract + merge MAF files from all batch archives into one
# table, mapped to the columns required by the task brief
# ---------------------------------------------------------
column_map = {
    "Tumor_Sample_Barcode": "sample_id",
    "Hugo_Symbol": "gene",
    "Chromosome": "chromosome",
    "Start_Position": "start_position",
    "Variant_Classification": "variant_classification",
    "Variant_Type": "variant_type",
    "Reference_Allele": "reference_allele",
    "Tumor_Seq_Allele2": "tumour_allele",
    "HGVSp_Short": "protein_change",
}

merged_frames = []

for archive_path in archive_paths:
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                if not member.name.endswith(".maf.gz"):
                    continue
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                with gzip.open(io.BytesIO(extracted.read()), "rt") as maf_file:
                    lines = [line for line in maf_file if not line.startswith("#")]
                if not lines:
                    continue
                df = pd.read_csv(io.StringIO("".join(lines)), sep="\t", low_memory=False)
                available_cols = [c for c in column_map if c in df.columns]
                merged_frames.append(df[available_cols])
    except tarfile.ReadError:
        print(f"  Could not open {archive_path} as a tar.gz — skipping.")
        continue

if not merged_frames:
    print("No mutation data extracted — nothing to save.")
    raise SystemExit(1)

mut_df = pd.concat(merged_frames, ignore_index=True)
mut_df = mut_df.rename(columns=column_map)

# patient_id = first 12 characters of the TCGA sample barcode
# e.g. "TCGA-BH-A0BZ-01A-11D-A10Y-09" -> "TCGA-BH-A0BZ"
mut_df["patient_id"] = mut_df["sample_id"].str[:12]

mut_out = raw_dir / "mutation_metadata.tsv"
mut_df.to_csv(mut_out, sep="\t", index=False)
print(f"Saved merged mutation table to {mut_out} ({len(mut_df)} rows)")
