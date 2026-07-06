## Dataset Comparison Table

| Cohort | Cancer type | Clinical data | Mutation data | Survival data | Sample size | Suitable as primary? | Notes |
|---|---|---|---|---|---|---|---|
| TCGA-BRCA | Breast invasive carcinoma | Yes | Yes | Yes | 1,084 | Yes | Large, well-characterised cohort; easy for genomic pipeline architecture. |
| TCGA-LUAD | Lung adenocarcinoma | Yes | Yes | Yes | 566 | Yes | Smaller sample cohort than BRCA but still robust; alternative primary candidate. |
| TCGA-LAML | Acute myeloid leukaemia | Yes | Yes | Partial | 200 | No (secondary) | Smaller cohort; different staging conventions (no solid-tumour TNM staging); good test of pipeline generalisability. |

# Dataset Selection Report

## Datasets Reviewed
TCGA-BRCA, TCGA-LUAD, TCGA-LAML (via cBioPortal, accessed [06-7-2026])


## Primary Dataset Recommendation
TCGA-BRCA

## Secondary Dataset Recommendation
TCGA-LAML

## Available Clinical Variables
Mutation Count, Patient ID, Sex, Overall Survival Status, Tumour Type, Cancer Type, Years Smoked, Prior Treatment, Race Category

## Available Genomic Variables
Mutation count, Mutated genes, Copy Number Alteration data, Fraction Genome Altered, Structural Variants data, Protein data

## Limitations Noticed
Average follow up time for TCGA-BRCA was 27.7 months, needs a longer follow up time.
# Notes
Advise caution when intepreting overall survival analysis for TCGA-BRCA, as tumour type may influence outcome. For instance, patient with *breast cancer estrogen (-)* have a worse survival outcome than patient with *breast cancer estrogen (+)*
