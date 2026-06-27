# tests/edge — validation-strategy matrix (cases 1–13)

Edge-case coverage for [validation_strategy.md](../docs/validation_strategy.md) §13-case matrix.
T0 tests run under default `GGPLOTPY_SKIP_INTEGRATION=1`; T1 render tests require R and
`GGPLOTPY_SKIP_INTEGRATION=0` (or `scripts/run_tests.ps1 -Tier tier2`).

## Shared fixtures

- `tests/edge/conftest.py` — `make_synthetic_df(n, seed)` with numeric columns, categoricals,
  and awkward names (`weird-col`, `a b`).

## Case mapping

| # | Case | Tier | Edge module | Notes |
|---|------|------|-------------|-------|
| 1 | mtcars scatter | T1+T2 | — | `tests/integration/test_render_basic.py`, `tests/parity/test_to_r_parity.py` |
| 2 | Aes expressions (NSE matrix) | T0+T2 | `test_nse_expressions.py` | Goldens in `tests/golden/aes/nse_*.txt`; T1 render when R available |
| 3 | Facet wrap + grid | T1 | `test_facets_formulas.py` | Formula strings on synthetic data |
| 4 | Scale + theme composition | T1 | `test_coordinators_scales.py` | `scale_color_manual`, `theme_void`, `coord_flip` |
| 5 | `R()` escape annotate | T1 | — | `tests/integration/test_r_escape.py` |
| 6 | Error translation | T0+T1 | `test_invalid_inputs.py` (partial) | Pre-rpy2 `ValueError`/`TypeError`; full `last_r_code()` in integration |
| 7 | Empty / invalid DataFrame | T0 | `test_invalid_inputs.py` | `validate_pandas_df`, `validate_aes_columns` |
| 8 | Large frame (100k) pandas | T-X | `test_data_ingress_edge.py` | 5k-row smoke here; full timing in `exploration/perf/` (v0.5+) |
| 9 | Large frame Arrow | T-X | `test_data_ingress_edge.py` | Arrow ingress at 200 rows; `@pytest.mark.needs_arrow` |
| 10 | ggplot2 3.5 vs 4.0 same spec | T1 | — | CI matrix (`.github/workflows/ci.yml` `ggplot2-versions` job) |
| 11 | Extension smoke | T1 | — | `tests/extensions/test_*.py` |
| 12 | Notebook gallery execute | T1 | — | `tests/notebooks/` (when present) |
| 13 | Visual regression (10 plots) | T3 | — | `tests/gallery/test_gallery_render.py` |

## Running

```powershell
# T0 edge only (R-free cases 2, 6, 7)
$env:GGPLOTPY_SKIP_INTEGRATION = "1"
python -m pytest tests/edge -q -m "not needs_ggplot2"

# Full edge suite including R render (one subprocess per file — recommended)
Remove-Item Env:GGPLOTPY_SKIP_INTEGRATION -ErrorAction SilentlyContinue
.\scripts\run_tests.ps1 -Tier tier2

# Or single process (local, may OOM on Windows)
$env:GGPLOTPY_SKIP_INTEGRATION = "0"
python -m pytest tests/edge -q
```

## MVP gate

Cases **1–7** must pass for MVP exit. Edge folder adds explicit coverage for **2, 3, 4, 6, 7**
and smoke for **8–9** without blocking CI on exploration-tier timing tests.
