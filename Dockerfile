# ggplotpy reproducible environment (v0.5+).
# CI, servers, Databricks — no manual R install required.
FROM condaforge/mambaforge:latest

WORKDIR /workspace/Ggplot2PY

COPY environment.yml .
RUN mamba env create -f environment.yml && mamba clean -afy

SHELL ["conda", "run", "-n", "ggplotpy", "/bin/bash", "-c"]

COPY . .
RUN pip install -e ".[dev,arrow]" && \
    Rscript -e 'install.packages("r-helper/ggplotpy", repos=NULL, type="source")'

ENV R_HOME=/opt/conda/envs/ggplotpy/lib/R

CMD ["conda", "run", "-n", "ggplotpy", "pytest", "tests/unit", "-q"]
