# Installation guide

Install paths for ggplotpy, ordered by recommendation. Engineering context: [packaging_plan.md on GitHub](https://github.com/Aakarsh751/ggplotpy/blob/main/docs/packaging_plan.md).

## Quick matrix

| Path | Command | Manual R? | Best for |
|------|---------|-----------|----------|
| **conda dev env** | `conda env create -f environment.yml` | No | Contributors, reproducible dev |
| **conda-forge** (when published) | `conda install -c conda-forge ggplotpy` | No — pulls `r-base`, `r-ggplot2`, `rpy2` | Windows, macOS, Linux; new users |
| **pip + bootstrap** | `pip install -e ".[dev]"` then `ggplotpy-bootstrap --profile core` | Partial — R must exist or be provisioned | pip-first workflows |
| **pip + system R** | `pip install ggplotpy` + user-installed R/ggplot2 | Yes | Developers with existing R |
| **Docker** | `docker build -t ggplotpy .` | No | CI, servers, Databricks |
| **Vendored R wheel** | — | — | **Not planned for v1** (GPL, fragility) |

## conda dev environment (recommended for contributors)

```bash
conda env create -f environment.yml
conda activate ggplotpy
ggplotpy-bootstrap --profile core
```

The `environment.yml` pins `python>=3.10`, `r-base`, `r-ggplot2`, `r-svglite`, `r-rlang`, `rpy2`, and installs the package editable with `[dev,arrow]` extras.

## conda-forge (primary end-user path)

When the feedstock is published:

```bash
conda install -c conda-forge ggplotpy
ggplotpy-bootstrap --profile core
```

A **recipe skeleton** exists at `conda/recipe/meta.yaml` (v0.5 gate — not yet on conda-forge).

## pip + bootstrap

1. `pip install ggplotpy` (or `pip install -e ".[dev,arrow]"` from source) — Python package + rpy2 dependency.
2. Ensure R is available (system install, rig, or miniforge — see `runtime/bootstrap.py`).
3. Run `ggplotpy-bootstrap --profile core` to install CRAN deps and the `r-helper/ggplotpy` companion.

## Install R packages from Python — `install_r()`

The easiest way to provision the R side. It installs CRAN packages as **prebuilt
binaries** on Windows/macOS (no compiler needed) plus ggplotpy's small R helper, on any OS:

```python
import ggplotpy

ggplotpy.install_r()            # core: ggplot2, rlang, svglite, ggplotpy helper
ggplotpy.install_r("all")       # + ggrepel, patchwork, gganimate, sf, ggthemes, ggdist, ggpubr
ggplotpy.install_r(packages=["ggridges"])   # any extra packages you want
```

If R itself isn't found, `install_r()` raises with a clear, per-OS message — the
fastest cross-platform path is always `conda install -c conda-forge r-base rpy2`.
The same set is available from the shell:

```bash
ggplotpy-bootstrap --profile all
```

## pip + system R

Install R 4.3+ and required packages yourself, then:

```bash
pip install ggplotpy
ggplotpy-bootstrap --profile core
```

### Platform notes

| Platform | Recommendation |
|----------|----------------|
| Windows | conda `r-base` (cleanest) or rig + Rtools; set `R_HOME` + `bin\x64` on PATH |
| macOS ARM/Intel | conda arm64/intel builds or rig |
| Linux | conda, rig, or distro R + dev headers for rpy2 |

rpy2 **Windows ABI** is fragile — prefer conda binary rpy2. CI runs on `ubuntu-latest`, `windows-latest`, and `macos-latest`.

### Windows R_HOME

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
```

## Docker

Reproduces the conda dev stack without a local R install:

```bash
docker build -t ggplotpy .
docker run --rm ggplotpy
```

See [Dockerfile](../../Dockerfile) and `environment.yml`.

## Optional extras

| Extra | Install | Purpose |
|-------|---------|---------|
| `arrow` | `pip install ggplotpy[arrow]` | Spark/Databricks Arrow ingress |
| `polars` | `pip install ggplotpy[polars]` | Polars DataFrame bridge |
| `geo` | `pip install ggplotpy[geo]` | GeoPandas → `sf` spatial ingress (`geom_sf`); also `install.packages("sf")` in R |
| `dev` | `pip install ggplotpy[dev]` | pytest, ruff, nbclient |
| `docs` | `pip install ggplotpy[docs]` | Sphinx build |

## Memory / OOM during tests

Integration and render tests load rpy2 + ggplot2 in-process. Running the full tree in one pytest process can **OOM on Windows**. Use the tier runner instead of `pytest tests/`:

```powershell
.\scripts\run_tests.ps1 -Tier tier0   # unit only
.\scripts\run_tests.ps1 -Tier tier1   # one subprocess per integration file
```

See [testing_guide.md on GitHub](https://github.com/Aakarsh751/ggplotpy/blob/main/docs/testing_guide.md) for `GGPLOTPY_SKIP_INTEGRATION`, `GGPLOTPY_SKIP_NOTEBOOKS`, and `GGPLOTPY_RUN_HEAVY`.

## Troubleshooting install

```python
from ggplotpy import check_setup

report = check_setup(profile="core")
# report.ok, report.messages, report.missing
```

If bootstrap fails, the report lists missing packages and suggested fix commands. See [Troubleshooting](troubleshooting.md).

## Licensing note

ggplotpy is **Apache-2.0**. R and ggplot2 are separate **GPL-2** components — conda and Docker treat them as linked runtime dependencies, not bundled in the Python wheel.
