# Testing Guide

How to run ggplotpy tests locally and interpret CI. Spec: `validation_strategy.md`.

---

## Prerequisites

- Python 3.10+ with editable install: `pip install -e ".[dev]"`
- R 4.3+ with **ggplot2** installed
- **rpy2** built against that R

### Windows — set R before any rpy2 import

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
python -c "import rpy2; print('ok')"
```

Adjust paths for your R version. Without this, rpy2 often fails to load `libR`.

---

## Directory layout

```
tests/
├── unit/           # tier0 — no R
├── integration/    # tier1 — render smoke
├── parity/         # tier1 — to_r() goldens (strict normalized compare)
├── edge/           # tier2 — validation matrix cases 2–9
├── extensions/     # tier1 — optional packages (graceful skip)
├── gallery/        # tier1 — render + T3 SVG hash baselines (5 plots)
├── notebooks/      # tier3 — nbclient execute notebooks 01–03
└── golden/         # committed expected outputs
exploration/        # local/nightly only (not PR-blocking)
```

---

## Runner tiers (`scripts/run_tests.ps1`)

The **authoritative local gate** uses four runner tiers. The script sets `GGPLOTPY_SKIP_NOTEBOOKS=1` for tier0–tier2.

| Tier | Command | Scope | Subprocess policy |
|------|---------|-------|-------------------|
| **tier0** | `.\scripts\run_tests.ps1 -Tier tier0` | `tests/unit` | Single process; sets `GGPLOTPY_SKIP_INTEGRATION=1` |
| **tier1** | `.\scripts\run_tests.ps1 -Tier tier1` | `integration/`, `parity/`, `gallery/`, `extensions/` | **One file per subprocess** (OOM-safe) |
| **tier2** | `.\scripts\run_tests.ps1 -Tier tier2` | `tests/edge/` | **One file per subprocess** |
| **tier3** | `.\scripts\run_tests.ps1 -Tier tier3` | `tests/notebooks/` | Single process; nbclient |
| **all** | `.\scripts\run_tests.ps1 -Tier all` | tier0 → tier1 → tier2 → tier3 | Full local gate |

Linux/macOS equivalent: `bash scripts/run_tests.sh tier0|tier1|tier2|tier3|all` (when present).

**Last verified (Windows, R 4.5.2):** tier0 45 passed / 1 skipped; tier1 11/11 files; tier2 5/5 files (20 tests); tier3 3/3 notebooks.

---

## Environment variables

| Variable | Behavior |
|----------|----------|
| `GGPLOTPY_SKIP_INTEGRATION=1` | Skip collecting `integration/`, `parity/`, `gallery/`, `extensions/` (default in tier0) |
| `GGPLOTPY_SKIP_NOTEBOOKS=1` | Skip notebook execute tests (set by tier0–tier2 runner) |
| `GGPLOTPY_RUN_HEAVY=1` | Opt-in: run skipped suites in one pytest process (local RAM only) |

**Do not** run `python -m pytest tests/ -q` in one process on Windows unless `GGPLOTPY_RUN_HEAVY=1`.

---

## Common commands

**Fast loop (development):**

```powershell
$env:GGPLOTPY_SKIP_INTEGRATION = "1"
$env:GGPLOTPY_SKIP_NOTEBOOKS = "1"
pytest tests/unit -q
```

**T0 edge only (R-free subset of edge matrix):**

```powershell
$env:GGPLOTPY_SKIP_INTEGRATION = "1"
pytest tests/edge -q -m "not needs_ggplot2"
```

**Single integration file (debug):**

```powershell
Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
pytest tests/integration/test_render_basic.py -q
```

**Visual baselines (part of tier1 gallery):**

```powershell
pytest tests/gallery/test_visual_baseline.py -q   # 5 SVG hash baselines
```

**Coverage (T0):**

```bash
pytest tests/unit --cov=src/ggplotpy --cov-report=term-missing
```

---

## OOM avoidance (rpy2 + ggplot2 render)

Running `pytest tests/` in a **single Python process** loads rpy2 once and keeps R graphics state and heap growth across many render tests. On Windows and in CI agents this often triggers **OOM kills**.

**Mitigations:**

| Mechanism | Behavior |
|-----------|----------|
| `scripts/run_tests.ps1 -Tier tier1` | One subprocess per integration/parity/gallery/extensions file |
| `scripts/run_tests.ps1 -Tier tier2` | One subprocess per edge file |
| `GGPLOTPY_SKIP_INTEGRATION=1` | T0 CI job — unit only |
| `conftest.py` | Module-scoped fixtures; `gc.collect()` after integration tests |
| `_render_plot` | `dev.off()` in `finally` always |

**Recommended local loop (Windows):**

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
.\scripts\run_tests.ps1 -Tier all
```

---

## Markers

| Marker | Meaning |
|--------|---------|
| `needs_r` | R + rpy2 |
| `needs_ggplot2` | ggplot2 in R |
| `needs_ggrepel` / `needs_patchwork` / `needs_gganimate` / `needs_sf` | Optional extension |
| `needs_arrow` | pyarrow extra |
| `slow` | >5s; exclude in fast loop |
| `parity` | T2 golden compare |
| `visual` | T3 SVG hash baseline |

Optional extensions **skip with reason** when absent (D-P009).

---

## Updating goldens

1. Confirm change is intentional (API or spec fix).
2. Regenerate or edit files under `tests/golden/`.
3. PR must include golden diff + explanation in `progress_log.md`.
4. Never silent-update goldens to make tests green.

**NSE goldens:** `tests/golden/aes/nse_*.txt`  
**Plot goldens:** `tests/golden/to_r/` (strict normalized full-script compare)

---

## CI interpretation

| Job | Meaning |
|-----|---------|
| `ci.yml` fast | T0 with `GGPLOTPY_SKIP_INTEGRATION=1` |
| `ci.yml` integration | `run_tests.sh tier1` (OOM-safe) |
| ggplot2-versions | 3.5.x + 4.0.x pin on ubuntu |
| `codegen.yml` | `generated/` matches introspection |
| `docs.yml` | Sphinx builds without R import |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Unable to locate R shared library` | Set `R_HOME` + PATH (Windows) |
| ggplot2 not found | `ggplotpy-bootstrap --profile core` |
| Extension tests skip | Expected if package not installed (D-P009) |
| Stale generated stubs | `python scripts/generate_stubs.py`; commit `generated/` |
| OOM mid-pytest | Use `run_tests.ps1 -Tier tier1` not full-tree pytest |

---

## Reference

- `tests/edge/README.md` — case 1–13 file mapping
- `validation_strategy.md` — semantic tiers and MVP gate
- RobStatTM-Py: `robstatm-py/docs/testing_guide.md` — rpy2 fixture patterns
