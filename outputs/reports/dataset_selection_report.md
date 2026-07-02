## Dataset Comparison Table

| Cohort | Cancer type | Clinical data | Mutation data | Survival data | Sample size | Suitable as primary? | Notes |
|---|---|---|---|---|---|---|---|
| TCGA-BRCA | Breast invasive carcinoma | Yes | Yes | Yes | ~1,080 | Yes | Large, well-characterised cohort; easy for genomic pipeline architecture. |
| TCGA-LUAD | Lung adenocarcinoma | Yes | Yes | Yes | ~566 | Yes | Smaller sample cohort than BRCA but still robust; alternative primary candidate. |
| TCGA-LAML | Acute myeloid leukaemia | Yes | Yes | Partial | ~200 | No (secondary) | Smaller cohort; different staging conventions (no solid-tumour TNM staging); good test of pipeline generalisability. |

# Dataset Selection Report

## Datasets Reviewed
TCGA-BRCA, TCGA-LUAD, TCGA-LAML (via cBioPortal, accessed [date])


## Primary Dataset Recommendation
TCGA-BRCA

## Secondary Dataset Recommendation
TCGA-LAML

## Available Clinical Variables
Mutation Count, Patient ID, Sex, Overall Survival Status, Tumour type, Cancer Type, Years Smoked, Prior treatment, Race category

## Available Genomic Variables
Mutation count, Mutated genes, CNA genes, Fraction Genome Altered

## Limitations Noticed
...

