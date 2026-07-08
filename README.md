# Clinical-Genomics AI

## Introduction

Clinical genomics is the application of genomic information (**DNA sequence, genetic variations**) to real-world patient care and clinical decision-making. It bridges raw genomic data and the clinical insights of a patient (**diagnosis, sex, survival status, treatment response**, etc.).

A real-world example is trying to find out if a mutation in the *TP53* gene is correlated with overall patient survival or resistance to a specific drug treatment. TCGA clinical data was used for the purpose of this analysis. Various TCGA projects exist, covering approximately 33 cancer types. Obtaining comprehensive clinical data annotation for each cancer type is important to enable the research community to derive translational relevance from tumour-specific genomics and pathway conclusions drawn from the analysis.

The aim of this project is to carefully select a dataset that is easier for pipeline architecture and debugging. Clinical data harmonisation and mutation data matching will be done using the same patient ID from TCGA clinical data and molecular data. A machine learning model will be developed, trained on clinical-genomics data, to predict patient treatment response and/or overall survival time.

It is noteworthy that, in clinical studies, overall survival rates are calculated based on progression and mortality events, with or without disease. It is very important to have adequate follow-up time for each endpoint to capture the events of interest. The minimum follow-up time depends on the aggressiveness of the disease — for instance, for instance, an aggressive tumour requires a shorter follow up time, because the patient will dissease progression/death occur faster, while a non agressive tumour requires a longer follow up because it takes longer for an event to occur.

TCGA-BRCA was selected as the primary dataset for construction of the pipeline model due to its large sample size and robust clinical and mutation data. For reproducibility purposes, TCGA-LAML was selected as the secondary dataset to test the generalisability of the pipeline.


## Usage
### Installation
python version: 3.9.6
python3 -m pip install pandas






## Reference
TCGA[https://pmc.ncbi.nlm.nih.gov/articles/PMC6066282/]
