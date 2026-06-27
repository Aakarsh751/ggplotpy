# Decisions Log (ggplotpy)

Format: `D-PNNN  <title>` then Context · Decision · Consequences · Status.

Prefix `D-P` avoids collision with RobStatTM-Py `D-00N` in the parent monorepo.

---

## D-P001  Hybrid G architecture

- **Date:** 2026-06-21
- **Context:** Seven candidate architectures evaluated in `RESEARCH_AND_PLAN.md` Phase 3; plotnine reimplementation rejected.
- **Decision:** **Hybrid G** — rpy2 in-process engine + dynamic namespace reflection + Arrow data plane + thin hand-written ergonomic core (`+` grammar, `aes`, Jupyter repr) + optional backends (Rserve/subprocess v1.0) + `R()` escape hatch + generated `.pyi` stubs.
- **Consequences:** Layered module layout in `docs/architecture.md`; no direct `importr` outside `backend/`.
- **Status:** Active.

## D-P002  conda-forge primary install; no vendored R in v1

- **Date:** 2026-06-21
- **Context:** Cross-platform R packaging is the #1 project risk (research Phase 6, 11).
- **Decision:** Recommend `conda install -c conda-forge ggplotpy` first. Pip installs Python + rpy2; `install_r()` auto-provisions via `rig`/miniforge on first use (reticulate-style). **No bundled libR in wheels for v1.0** without legal review (R is GPL-2).
- **Consequences:** `docs/packaging_plan.md` is canonical; Docker image for CI/servers.
- **Status:** Active.

## D-P003  NSE via R helper `aes_from_strings` + `rlang::parse_expr`

- **Date:** 2026-06-21
- **Context:** ggplot2 aesthetics use tidy evaluation; Python has no bare symbols (research §2.4).
- **Decision:** Ship tiny R package `r-helper/ggplotpy` with `ggplotpy:::aes_from_strings()` that parses each Python string as an R expression via `rlang::parse_expr` and splices into `ggplot2::aes()`. Support full expressions, `.data[["col"]]` pronoun, and `R()` escape for unmodeled cases.
- **Consequences:** `core/aes.py` delegates to R helper; golden files under `tests/golden/aes/`.
- **Status:** Active.

## D-P004  Lazy ggplot2 namespace import

- **Date:** 2026-06-21
- **Context:** `importr("ggplot2")` at import time slows doc builds and test collection (robstatm D-009 pattern).
- **Decision:** Defer `importr` until first plot/render call. Cache namespace in `backend/inprocess.py`.
- **Consequences:** `import ggplotpy` is cheap; first plot pays R startup cost.
- **Status:** Active.

## D-P005  Local `project_memory/` governance; append-only audit trail

- **Date:** 2026-06-21
- **Context:** Resumption must work without re-reading 560 lines of research.
- **Decision:** Self-contained memory under `Ggplot2PY/project_memory/`; append-only; session blocks mandatory; ADRs prefixed `D-P`.
- **Consequences:** Every session updates `progress_log.md` and `STATUS.md`.
- **Status:** Active.

## D-P006  Verification tiers: T0+T1 default on PR; T2 for core API; T3 for gallery

- **Date:** 2026-06-21
- **Context:** Research §9.3 testing strategy; robstatm strict-tier precedent adapted for plotting.
- **Decision:** **T0** R-free unit always on PR. **T1** integration render on CI matrix. **T2** `to_r()` golden parity required for core API / aes changes. **T3** visual regression for gallery changes. Exploration tier (perf, version sweeps) local/nightly, not PR-blocking by default.
- **Consequences:** `docs/validation_strategy.md`, markers in `pyproject.toml`, `ggplotpy-verification.mdc`.
- **Status:** Active.

## D-P007  `to_r()` golden parity is the trust contract

- **Date:** 2026-06-21
- **Context:** Users need transparency and reproducibility with R colleagues; pixel-perfect match for every geom is impractical.
- **Decision:** Assert `to_r()` output matches idiomatic R golden scripts (normalized whitespace). Not pixel-perfect image comparison for every geom — that is T3's curated subset only.
- **Consequences:** Golden update requires intentional API change + PR diff + progress_log note.
- **Status:** Active.

## D-P008  Visual regression tolerance = 1e-3 image norm

- **Date:** 2026-06-21
- **Context:** Anti-alias / DPI noise across platforms (research §9.2).
- **Decision:** Gallery T3 tests use image-norm tolerance `1e-3`; SVG optional hash compare for selected plots.
- **Consequences:** Baselines in `tests/gallery/baseline_images/`.
- **Status:** Active.

## D-P009  Optional extensions skip gracefully when R package absent

- **Date:** 2026-06-21
- **Context:** ggrepel, patchwork, gganimate, sf are optional; core CI must not fail on missing packages.
- **Decision:** `@pytest.mark.needs_*` markers; skip with reason when R package not installed. Never fail core CI for optional extension absence.
- **Consequences:** Extension tests in `tests/extensions/`; conftest auto-skip helpers.
- **Status:** Active.

## D-P010  Apache-2.0 license; R remains separate GPL component

- **Date:** 2026-06-21
- **Context:** Research §9.5; ggplotpy drives R via rpy2 (GPL boundary), does not embed R in v1.
- **Decision:** ggplotpy source licensed **Apache-2.0**. R runtime is user/conda-provisioned GPL-2 component. No vendored R without legal review.
- **Consequences:** `LICENSE`, `pyproject.toml` license field.
- **Status:** Active.

## D-P011  Python kwarg names map to R dotted parameters (`na_rm` → `na.rm`)

- **Date:** 2026-06-22
- **Context:** ggplot2's API uses dot-separated parameter names (`na.rm`, `show.legend`, `inherit.aes`, `outlier.shape`, theme elements like `legend.position`) which are not valid Python identifiers. Before this decision ggplotpy passed kwarg names through unchanged, so every dotted parameter was silently unreachable — `theme(legend_position=...)` warned "element not defined" and `geom_point(na_rm=True)` was ignored. Verified by probe 2026-06-22.
- **Decision:** Normalize every wrapper kwarg name: strip a single trailing `_` first (reserved-word escape, `class_` → `class`), then replace remaining `_` with `.` (`na_rm` → `na.rm`). Applied centrally in `normalize_r_kwargs` (`core/defer.py`), used by the reflected-callable wrapper and `rcall`. `aes()` is unaffected (aesthetic names contain no dots). The `R()` escape hatch remains the fallback for the rare R parameter that genuinely needs an underscore.
- **Consequences:** Dotted ggplot2/extension parameters are now reachable from idiomatic Python. Minor breaking risk for any R arg that must keep an underscore (none in base ggplot2). Tested in `tests/unit/test_layer_values_to_r.py` and `tests/edge/test_layer_aes.py`.
- **Status:** Active.

## D-P012  Embedded R runs non-interactive

- **Date:** 2026-06-22
- **Context:** ggplot2/rlang `check_installed()` prompts to install optional packages (hexbin, mapproj, …) on stdin; in an embedded rpy2 session this **deadlocks** with no way to answer. Verified by a coverage sweep that hung on `geom_hex` without hexbin.
- **Decision:** On backend init (`_force_noninteractive_r`) set `options(rlang_interactive = FALSE, menu.graphics = FALSE, install.packages.check.source = 'no')`. Optional-package checks then degrade to non-fatal warnings and the plot renders without that layer, instead of hanging. ggplotpy never auto-installs R packages silently; provisioning stays explicit (`ggplotpy-bootstrap`, `check_setup`).
- **Consequences:** No interactive deadlocks in notebooks/CI/headless. Layers needing an absent package render with a warning rather than crashing. Tested in `tests/edge/test_noninteractive_r.py`.
- **Status:** Active.

## D-P013  sf ingress via GeoPackage round-trip; isolated render via saveRDS + Rscript

- **Date:** 2026-06-22
- **Context:** Two v1.0 gaps: spatial data (`geom_sf`) had no ingress path, and the only renderer ran in-process (an R crash during render kills Python). A full GeoArrow C-interface and a full IPC subprocess *backend* are both large; we want working, testable implementations now.
- **Decision:** (a) **sf ingress** — `sf_to_r()` writes the GeoPandas `GeoDataFrame` to a temporary **GeoPackage** and reads it back with `sf::st_read` (CRS + geometry type preserved); `geoarrow_to_r()` routes a GeoArrow table through `GeoDataFrame.from_arrow` into the same path; `ggplot(gdf)` auto-detects geopandas. (b) **Isolated render** — `render_in_subprocess()` serialises the finished plot with `saveRDS` and renders it in a fresh `Rscript` child (`GG.save(isolated=True)`, `GG.render_isolated()`); only base R is needed and a render crash can't kill Python. The full call-level IPC `SubprocessBackend` and a zero-copy GeoArrow path remain future work.
- **Consequences:** Spatial plots work from Python when `geopandas` (`pip install ggplotpy[geo]`) and R `sf` are present, with clear errors otherwise. Crash-isolated rendering available without extra R packages. Tested in `tests/unit/test_sf_bridge.py`, `tests/edge/test_subprocess_render.py`, and a `needs_sf` render test.
- **Status:** Active.
