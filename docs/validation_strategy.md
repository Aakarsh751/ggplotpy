# Validation Strategy

ggplotpy-adapted from `RESEARCH_AND_PLAN.md` §9.3 and robstatm-py tiers. Companion: `testing_guide.md`.

**Trust contract (D-P007):** `to_r()` golden parity with idiomatic R — not pixel-perfect for every geom.

---

## Four verification tiers (semantic)

| Tier | Name | Requires R? | CI default? | Purpose |
|------|------|-------------|-------------|---------|
| **T0** | R-free unit | No | **Always** | API build, aes/`to_r()` string goldens, codegen emit, mocked errors |
| **T1** | Integration render | Yes | **Matrix** | Real ggplot2 render; non-empty bytes; no R error |
| **T2** | Parity + edge matrix | Yes | **Matrix** | Strict `to_r()` goldens; NSE/facet/ingress edge cases |
| **T3** | Visual + notebook gallery | Yes | **Subset / nightly** | SVG hash baselines; notebook execute |

**Exploration (T-X):** perf sweeps — `exploration/`; failures → `discoveries.md`; not PR-blocking until promoted (D-P006).

### Runner tier mapping (`scripts/run_tests.ps1`)

| Runner | Test paths | Semantic coverage |
|--------|------------|-------------------|
| **tier0** | `tests/unit/` | T0 |
| **tier1** | `integration/`, `parity/`, `gallery/`, `extensions/` | T1 render + T2 parity + T3 visual baselines |
| **tier2** | `tests/edge/` | T2 edge matrix (cases 2–9) |
| **tier3** | `tests/notebooks/` | Case 12 notebook gallery |

---

## Golden-file protocol

1. **Authoritative source:** idiomatic R script; store under `tests/golden/aes/` and `tests/golden/to_r/`.
2. **Normalize before compare:** strip trailing whitespace; consistent line endings (`test_to_r_normalize.py`).
3. **Updates:** intentional API change only; PR shows golden diff + `progress_log.md` note.
4. **NSE minimum set:** bare column; `factor(cyl)`; `log(wt)`; `.data[["odd-name"]]`; multi-aes; facet formula strings.

---

## 13-case verification matrix

| # | Case | Tier | Test file(s) | Assert |
|---|------|------|--------------|--------|
| 1 | mtcars scatter | T1+T2 | `tests/integration/test_render_basic.py`, `tests/parity/test_to_r_parity.py` | SVG renders; full normalized `to_r()` == golden |
| 2 | Aes expressions (NSE matrix) | T0+T2 | `tests/unit/test_aes_golden.py`, `tests/edge/test_nse_expressions.py` | Golden files in `tests/golden/aes/` |
| 2b | Layer-level aes + sequence args + direct ingress | T0+T2 | `tests/unit/test_layer_values_to_r.py`, `tests/edge/test_layer_aes.py` | `geom_*(aes(...))`, tuple/list kwargs, `ggplot(pandas/arrow)` render; `to_r()` stays valid R |
| 3 | Facet wrap + grid | T1+T2 | `tests/integration/test_facets.py`, `tests/edge/test_facets_formulas.py` | Builds without error |
| 4 | Scale + theme composition | T1+T2 | `tests/edge/test_coordinators_scales.py` | Layer stack builds + renders |
| 5 | `R()` escape annotate | T1 | `tests/integration/test_r_escape.py` | Renders with annotation |
| 6 | Error translation | T0+T1 | `tests/unit/test_errors.py`, `tests/unit/test_ux_errors.py`, `tests/edge/test_invalid_inputs.py` | Message + `last_r_code()` |
| 7 | Empty / invalid DataFrame | T0 | `tests/edge/test_invalid_inputs.py`, `tests/unit/test_data_ingress.py` | `ValueError` before rpy2 |
| 8 | Large frame pandas | T-X | `tests/edge/test_data_ingress_edge.py` (5k smoke) | Full timing in `exploration/perf/` |
| 9 | Large frame Arrow | T-X | `tests/edge/test_data_ingress_edge.py` | `@pytest.mark.needs_arrow` |
| 10 | ggplot2 3.5 vs 4.0 | T1 | CI `ggplot2-versions` job (`.github/workflows/ci.yml`) | Both render same spec |
| 11 | Extension smoke | T1 | `tests/extensions/test_*.py` | ggrepel, patchwork, gganimate — skip if missing |
| 12 | Notebook gallery execute | tier3 | `tests/notebooks/test_notebooks.py` → `notebooks/01–03` | nbclient clean execute |
| 13 | Visual regression | T3 | `tests/gallery/test_visual_baseline.py` | **5** SVG SHA256 baselines (tol via normalize) |
| 13b | Category coverage (all families render) | T1 | `tests/gallery/test_category_coverage.py` | **30** representative renders across geoms/stats/scales/coords/facets/themes/positions/guides/annotations |
| 14 | Python→R ingress matrix | T2 | `tests/edge/test_data_conversions.py` | dict / list-of-records / Series / numpy 1-D+2-D / datetime / categorical / NaN / pyarrow / GeoPandas (needs_sf) all render |
| 15 | Embedded R non-interactive | T2 | `tests/edge/test_noninteractive_r.py` | `rlang_interactive=FALSE`; missing optional pkg warns+renders, never hangs |
| 16 | sf spatial bridge | T0+T2 | `tests/unit/test_sf_bridge.py`, `tests/edge/test_data_conversions.py` | graceful errors w/o geopandas; `geom_sf` renders when sf present |
| 17 | Isolated subprocess render | T2 | `tests/edge/test_subprocess_render.py` | `render_isolated`/`save(isolated=True)` → valid PNG/SVG via child Rscript |

**Geom smoke (honest scope):** `tests/integration/test_geoms_smoke.py` — **15** common geoms.
**Full coverage sweep:** `scripts/verify_ggplot_coverage.py` renders **108** layers across all
categories on demand (0 real failures; 5 skips need hexbin/sf/map data).

**MVP gate:** cases 1–7. **v0.5+:** 8–11. **v1.0:** expand case 13 beyond 5 baselines.

Full edge folder index: `tests/edge/README.md`.

---

## Pytest markers

Register in `pyproject.toml`:

- `needs_r`, `needs_ggplot2`
- `needs_ggrepel`, `needs_patchwork`, `needs_gganimate`, `needs_sf`
- `needs_arrow`
- `slow`, `parity`, `visual`

Optional extensions **skip gracefully** when absent (D-P009).

---

## CI matrix (current)

| Job | OS / pins | Tiers |
|-----|-----------|-------|
| T0 fast | ubuntu + windows + macos | tier0 (`GGPLOTPY_SKIP_INTEGRATION=1`) |
| Integration | ubuntu + windows | tier1 + tier2 subprocess runners |
| ggplot2-versions | ubuntu | 3.5.2 + 4.0.0 |
| codegen | ubuntu | stub staleness |
| docs | ubuntu | Sphinx `-W`, no R import |

Full 4-OS + nightly exploration: v1.0 target.

---

## Risk → test mapping (Phase 11)

| Risk | Mitigation |
|------|------------|
| NSE edge cases | T0 golden matrix + edge T2; `.data[[]]` |
| ggplot2 4.0 S7 | Dual-version CI; public API only |
| Packaging / no R | `check_setup()`, `ggplotpy-bootstrap` |
| pandas slow ingress | `exploration/perf/benchmark_ingress.py` |
| rpy2 Windows ABI | `windows-latest` from MVP |
| Extension breakage | Extension smoke + runtime reflection |
| R crash | subprocess backend tests (v1.0) |
| OOM on render suites | tier1/tier2 one-file-per-subprocess runner |

---

## Per-session protocol (agents)

**Before:** `GGPLOTPY_SKIP_NOTEBOOKS=1 pytest tests/unit -q`  
**After:** run `run_tests.ps1` tiers for touched paths; log commands in `progress_log.md`.
