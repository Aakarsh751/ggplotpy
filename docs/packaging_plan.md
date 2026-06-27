# Packaging Plan

Research Phase 6. **#1 engineering risk:** frictionless R + rpy2 across OS. D-P002.

---

## Recommended install paths (priority order)

| Path | Command | "No manual R"? | Status |
|------|---------|----------------|--------|
| **conda dev env** | `conda env create -f environment.yml` | Yes | **Done** — contributor default |
| **conda-forge** | `conda install -c conda-forge ggplotpy` | Yes | **Recipe skeleton** at `conda/recipe/meta.yaml`; publish v1.0 |
| **pip + bootstrap** | `pip install ggplotpy` then `ggplotpy-bootstrap --profile core` | Partial | **Done** — CLI shipped |
| **pip + system R** | User installs R + ggplot2 | No | **Done** — documented fallback |
| **Docker** | `docker build -t ggplotpy .` | Yes | **Done** — Dockerfile + `environment.yml` |
| **Vendored R wheel** | — | — | **Avoid v1** (GPL, fragility) |

---

## pip bootstrap (reticulate-style)

1. `pip install ggplotpy` — Python package + rpy2 dependency.
2. On import or first plot, `check_setup()` detects R.
3. **Today:** `ggplotpy-bootstrap --profile core` installs CRAN deps + `r-helper/ggplotpy`.
4. **v1.0:** `install_r()` opt-in auto-trigger via rig/miniforge (not implemented yet).

Module: `src/ggplotpy/runtime/bootstrap.py` — entry point `ggplotpy-bootstrap` in `pyproject.toml`.

---

## Platform notes

| Platform | Recommended |
|----------|-------------|
| Windows | conda `r-base` (cleanest) or rig + Rtools; set `R_HOME` + `bin\x64` on PATH |
| macOS ARM/Intel | conda arm64/intel or rig |
| Linux | conda, rig, or distro R + dev headers for rpy2 |

rpy2 **Windows ABI** is fragile — prefer conda binary rpy2; CI `windows-latest` + `macos-latest` from MVP.

---

## Artifacts

| Artifact | Status |
|----------|--------|
| `pyproject.toml` | **Done** — dynamic version (single-sourced from `__init__.__version__`), full metadata |
| `environment.yml` | **Done** (v0.5) |
| `conda/recipe/meta.yaml` | **Release-ready** — sources PyPI sdist; maintainer set; needs sha256 (`scripts/pypi_sha256.py`) |
| `Dockerfile` | **Done** (v0.5) |
| PyPI wheel (no bundled R) | **Release-ready** — `python -m build` → `ggplotpy-0.1.0`; wheel **bundles the R helper** (`ggplotpy/_r_helper/`) |
| `.github/workflows/publish.yml` | **Done** — Trusted-Publishing on tag `ggplotpy-v*` |
| `RELEASING.md` | **Done** — one-command tag → PyPI; conda-forge PR steps |
| `install_r()` | **Done** — cross-OS CRAN-binary provisioning from Python |

---

## Licensing (not legal advice)

- ggplotpy: **Apache-2.0** (D-P010)
- R: **GPL-2** — separate component; do not statically bundle without review
- rpy2: GPL boundary via linking/embedding

---

## Success criteria

| Gate | Status |
|------|--------|
| New user on Windows → first plot via conda dev env | **Met locally** |
| `check_setup()` prints actionable fix commands | **Done** |
| Docker reproduces CI stack | **Done** |
| conda-forge one-liner for end users | **Recipe ready** — submit to staged-recipes after first PyPI release |
| `install_r()` pip auto-provision | **Done** — `ggplotpy.install_r("all")` |

User-facing install docs: [guides/installation.md](guides/installation.md), [getting-started.md](getting-started.md).
