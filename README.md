# Clinical-Genomics Harmonisation and AI Baseline Module

## Description

This module builds a reproducible pipeline that harmonises TCGA clinical
and genomic mutation data, matches patient/sample records by ID, generates
clinical-genomic summary tables and figures, and trains a baseline machine
learning model to predict overall survival status. It is a aprt of a larger
multi-omics integration analysis.

Clinical genomics is the application of genomic information (DNA sequence,
genetic variations) to real-world patient care and clinical decision-making
— for example, testing whether a mutation in *TP53* correlates with overall
patient survival or treatment resistance. This module uses TCGA data,
accessed via the GDC REST API, to build and test that kind of analysis
end-to-end.

## Dataset Source

Data is sourced from the **Genomic Data Commons (GDC)**, via the GDC REST
API (`https://api.gdc.cancer.gov`), covering TCGA (The Cancer Genome Atlas)
projects. TCGA spans approximately 33 cancer types with paired clinical
and molecular data, maintained to support translational research linking
tumour-specific genomics to clinical outcomes.

Reference: [The Cancer Genome Atlas (TCGA): An immeasurable source of
knowledge](https://pmc.ncbi.nlm.nih.gov/articles/PMC6066282/)

## Datasets Selection

**Primary dataset: TCGA-BRCA** (Breast Invasive Carcinoma) was selected for
pipeline construction due to its large sample size (~1,080 cases) and
robust, well-characterised clinical and mutation data, making it easier to
build the initial pipeline.

**Secondary dataset: TCGA-LAML** (Acute Myeloid Leukaemia) was selected to
test the pipeline's generalisability to a structurally different cohort
(smaller sample size, different staging conventions, different relevant
clinical endpoints).

## Folder Structure

```
01_clinical_genomics_ai/
├── data/
│   ├── raw/              # raw GDC downloads (clinical + mutation)
│   ├── processed/        # cleaned/merged/ML-ready tables
│   └── example/          
├── scripts/
│   ├── 01_download_or_prepare_data.py
│   ├── 02_clean_clinical_data.py
│   ├── 03_process_mutation_data.py
│   ├── 04_match_patient_ids.py
│   ├── 05_generate_summary_tables.py
│   ├── 06_generate_figures.py
│   ├── 07_build_ml_feature_table.py
│   ├── 08_train_baseline_model.py
│   └── 09_test_second_dataset.py
├── notebooks/
│   └── 01_exploratory_data_review.ipynb
├── outputs/
│   ├── tables/            
│   ├── figures/           
│   ├── models/            # trained AI model (.pkl)
│   └── reports/           
├── config/
│   └── config.yaml        # all paths, column names, settings
├── environment/
│   ├── environment.yml    # Conda environment 
│   └── Dockerfile         
├── workflow/
│   └── nextflow/
│       ├── main.nf
│       └── nextflow.config
├── docs/
│   └── module_documentation.md
└── README.md
```

## Input Data Requirements

**Clinical metadata** (minimum): patient/sample ID, age, sex, vital status,
days to death, days to last follow-up, primary diagnosis, treatment type
and outcome.

**Genomic mutation data** (minimum): patient/sample ID, gene, chromosome,
start position, variant classification, variant type, reference/tumour
allele, protein change.

Not every field is available for every project — see **Limitations** below
for fields found to be project-specific or unavailable.

## Installation

```bash
git clone https://github.com/LSMA2026/MI-Fortunate-MultiOmicsFlow.git
cd 01_clinical_genomics_ai
```

## Conda Setup

```bash
conda env create -f environment/environment.yml
conda activate clinical-genomics-ai
```

To add a new package later, edit `environment/environment.yml`, then run:
```bash
conda env update -f environment/environment.yml --prune
```

## Docker Setup

```bash
docker build -t clinical-genomics-ai -f environment/Dockerfile .
docker run --rm -v "$(pwd)":/app clinical-genomics-ai python3 scripts/02_clean_clinical_data.py
```
*(Docker setup is a first attempt — not yet fully
tested.)*

## How to Run Each Script

All scripts read paths and settings from `config/config.yaml` — no
command-line arguments are required.

```bash
python3 scripts/01_download_or_prepare_data.py     # downloads raw clinical + mutation data from GDC
python3 scripts/02_clean_clinical_data.py           # cleans clinical data, derives survival variables
python3 scripts/03_process_mutation_data.py         # cleans mutation data, classifies variant types
python3 scripts/04_match_patient_ids.py             # matches clinical + genomic records, merges tables
python3 scripts/05_generate_summary_tables.py       # mutation burden + clinical-genomic summary tables
python3 scripts/06_generate_figures.py              # generates all required figures
python3 scripts/07_build_ml_feature_table.py        # builds the ML-ready feature table
python3 scripts/08_train_baseline_model.py          # trains and evaluates the baseline model
python3 scripts/09_test_second_dataset.py           # tests pipeline generalisability on TCGA-LAML
```

Or run the full pipeline end-to-end using Nextflow:
```bash
nextflow run workflow/nextflow/main.nf -profile local
```

## Outputs

**Data:** `clinical_cleaned.csv`, `genomics_cleaned.csv`,
`clinical_genomics_merged.csv`, `ml_feature_table.csv`

**Tables:** `clinical_missingness_summary.csv`, `id_matching_summary.csv`,
`top_mutated_genes.csv`, `variant_classification_summary.csv`,
`mutation_counts_per_patient.csv`, `mutation_burden_summary.csv`,
`clinical_genomic_summary.csv`, `model_performance_summary.csv`,
`feature_importance.csv`

**Figures:** `top_mutated_genes_barplot.png`,
`variant_classification_distribution.png`, `mutations_per_patient.png`,
`mutation_burden_by_clinical_group.png`, `confusion_matrix.png`,
`roc_curve.png`

**Model:** `baseline_model.pkl`

**Reports:** `dataset_selection_report.md`, `data_overview.md`,
`second_dataset_test_report.md`, `nextflow_run_report.md`

## Limitations

- **Mixed cohort in current outputs:** the clinical download step does not
  currently request `project.project_id` as a returned field, so BRCA and
  LAML patients are combined in one file with no cohort identifier. The
  ML feature table and baseline model therefore currently train on a
  mixed BRCA+LAML population rather than BRCA only as intended. 
- **AML-specific fields are empty for BRCA cases** (e.g.
  `diagnoses.eln_risk_classification`), as expected given
  differing clinical protocols per cancer type, not a data quality issue.
- **Treatment records are highly sparse and variable-length** (up to 27
  treatment entries per diagnosis, up to 7 diagnoses per patient);
  collapsed into `num_treatments`/`had_treatment` rather than kept
  individually.
- **Small-subgroup statistics:** several `primary_diagnosis` categories in
  `clinical_genomic_summary.csv` have very few patients (some n=1) and
  should not be read as reliable group averages.
- **Sex-based comparison is confounded by cohort composition:** the
  male/female mutation burden difference observed likely reflects cancer
  type distribution (BRCA is predominantly female) rather than a true
  sex based biological difference.
- **`overall_survival_time` was deliberately excluded** from the ML
  feature set to avoid leaking the outcome variable.
- **`OS`/`OS.time` survival variables are not provided directly by
  GDC** — they are derived here from `vital_status`, `days_to_death`, and
  `days_to_last_follow_up`, following standard survival-analysis
  convention.
- **Docker setup is an unrefined first attempt** and has not been fully
  validated end-to-end.

## Future Work 

- Add `project.project_id` to the clinical download and re-run the
  pipeline with proper BRCA-only filtering.
- Extend driver-gene and pathway-level mutation flags using an external
  gene-to-pathway reference.
- Address class imbalance (~80/20 alive/dead split) in baseline model
  evaluation with additional metrics or resampling approaches.
- Refine and fully test the Docker environment.
- Month 2 task: extend the pipeline to incorporate the epigenomics layer,
  connecting gene regulation data with the clinical-genomic foundation
  built here.

## Reference

TCGA: [https://pmc.ncbi.nlm.nih.gov/articles/PMC6066282/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6066282/)
Nextflow: [Di Tommaso, P., Chatzou, M., Floden, E. et al. Nextflow enables reproducible computational workflows. Nat Biotechnol 35, 316–319 (2017)] [https://doi.org/10.1038/nbt.3820/]
