# environment/Dockerfile
#
# Build from the project root:
#   docker build -t clinical-genomics-ai -f environment/Dockerfile .
#
# Run a script inside the container, mounting the project directory so
# outputs are written back to the host filesystem:
#   docker run --rm -v "$(pwd)":/app clinical-genomics-ai \
#       python3 scripts/02_clean_clinical_data.py

FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy only the environment spec first, so Docker can cache this layer
# and skip reinstalling packages unless environment.yml actually changes
COPY environment/environment.yml environment/environment.yml

RUN conda env create -f environment/environment.yml && \
    conda clean -afy

# Activate the environment for all subsequent RUN/CMD/ENTRYPOINT
# instructions in this image
SHELL ["conda", "run", "-n", "clinical-genomics-ai", "/bin/bash", "-c"]

# Copy the rest of the project (scripts, config, etc.) into the image.
# Data folders are intentionally excluded via .dockerignore — raw/
# processed data should be mounted at runtime, not baked into the image.
COPY . .

# Default entrypoint runs commands inside the Conda environment;
# override the final command to run a specific script, e.g.:
#   docker run clinical-genomics-ai python3 scripts/02_clean_clinical_data.py
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "clinical-genomics-ai"]
CMD ["python3", "--version"]
