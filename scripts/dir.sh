#!/bin/bash

mkdir -p data/{raw,processed,example}
mkdir -p scripts
mkdir -p notebooks
mkdir -p outputs/{tables,figures,models,reports}
mkdir -p config
mkdir -p environment
mkdir -p workflow/nextflow
mkdir -p docs


cd scripts 
touch 01_download_or_prepare_data.py \
02_clean_clinical_data.py \
03_process_mutation_data.py \
04_match_patient_ids.py \
05_generate_summary_tables.py \
06_generate_figures.py \
07_build_ml_feature_table.py \
08_train_baseline_model.py \
09_test_second_dataset.py 
 
touch README.md
touch docs/module_documentation.md
touch config/config.yaml
touch environment/environment.yml
touch environment/Dockerfile
touch outputs/reports/dataset_selection_report.md
touch outputs/reports/data_overview.md
cd ..
