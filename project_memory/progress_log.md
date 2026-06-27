# Progress Log

Chronological session blocks for ggplotpy. Append only — do not edit earlier entries.

---

## Session 2026-06-21 — Implementation kickoff (Phase 0 governance)

**Driver:** agent  
**Milestone:** M0 · **Task ID:** gov-memory, gov-agents, gov-cursor  
**Goal:** Establish governance, engineering docs, Cursor rules, and resume infrastructure before application code.

### Started from

- Last completed: `RESEARCH_AND_PLAN.md` (12-phase research complete; Hybrid G locked)
- Blockers consulted: none open

### Files created/modified

- `project_memory/` — README, progress_log, decisions (D-P001–D-P010), discoveries, blockers, lessons_learned, resume_prompts
- `AGENTS.md`, `STATUS.md`, `CHANGELOG.md`, `LICENSE`, `README.md`
- `docs/` — architecture, implementation_plan, implementation_rules, quality_gates, validation_strategy, testing_guide, documentation_plan, packaging_plan, coverage_matrix, nse_bridge, user_interface
- `.cursor/rules/` — ggplotpy-core, ggplotpy-session, ggplotpy-verification, ggplotpy-r-bridge, ggplotpy-codegen, ggplotpy-tests
- `.cursor/skills/ggplotpy-dev/SKILL.md`

### Commands run + results

- (none — docs-only session)

### Findings / discoveries

- Governance adapted from robstatm-py `project_memory/` patterns; ADR prefix `D-P` avoids collision with RobStatTM `D-00N`.

### Decisions

- Seeded `decisions.md` D-P001 through D-P010 (architecture, packaging, NSE, lazy import, memory protocol, verification tiers).

### Next actions (ordered)

1. M0 scaffold: `pyproject.toml`, `src/ggplotpy/` stubs, `r-helper/ggplotpy/`, `tests/` layout, CI workflows (Prompt #2).
2. First T0 smoke tests after scaffold lands.
3. MVP core: backend, `aes`, `ggplot`/`+`, SVG repr (Prompt #3).

---

## Session 2026-06-21 — M0 package scaffold

**Driver:** agent  
**Milestone:** M0 · **Task ID:** m0-scaffold, m0-backend, m0-tests, m0-ci  
**Goal:** Full ggplotpy package skeleton with hatchling, R helper, backend, core API, tests, CI.

### Started from

- Last completed: Phase 0 governance (2026-06-21 kickoff)
- Blockers consulted: none open

### Files created/modified

- `pyproject.toml` — hatchling, deps, extras, pytest markers, `ggplotpy-bootstrap` script
- `src/ggplotpy/` — backend (inprocess + stubs), core (aes, gg, raw, patchwork, errors, options), data bridges, runtime (check_setup, bootstrap), codegen, generated, ext
- `r-helper/ggplotpy/` — DESCRIPTION, NAMESPACE, R/aes.R, R/install.R
- `tests/` — conftest, unit (T0), integration, parity, extensions, gallery, golden fixtures
- `docs/conf.py`, `docs/index.md`
- `.github/workflows/ci.yml`, `docs.yml`, `codegen.yml`
- `notebooks/01_mvp_mtcars.ipynb` (via `scripts/create_notebook.py`)
- `../README.md` — Ggplot2PY row in repo map
- `STATUS.md` — M0 complete

### Commands run + results

```text
pip install -e ".[dev]"                          → OK
python -m pytest tests/unit -q                   → 10 passed
```

### Findings / discoveries

- Circular import if `ggplotpy/__init__.py` eagerly imports backend while `inprocess` imports `core.errors`; fixed with lazy `__getattr__` exports.
- Golden aes fragment uses sorted keys (color, x, y) for deterministic T0 comparison.

### Decisions

- (none new — follows D-P001 Hybrid G, D-P003 NSE, D-P004 lazy init)

### Next actions (ordered)

1. Run T1 integration locally after `ggplotpy-bootstrap --profile core`.
2. Wire pandas DataFrame auto-conversion in `ggplot()` (MVP polish).
3. Expand T2 parity goldens; codegen `.pyi` emit pipeline (v0.1).

---

## Parallel worker: packaging/docs — 2026-06-21

**Driver:** agent (parallel to core worker)  
**Milestone:** v0.5 packaging + platform doc stubs  
**Goal:** Conda/Docker artifacts and user-facing install/platform guides without touching `src/ggplotpy/core/gg.py`.

### Files created/modified

- `environment.yml` — conda-forge stack; pip `-e ".[dev,arrow]"`
- `Dockerfile` — mambaforge + editable ggplotpy install
- `conda/recipe/meta.yaml` — conda-forge feedstock skeleton
- `docs/getting-started.md` — conda-first install, bootstrap, first plot
- `docs/guides/installation.md` — install matrix from packaging_plan
- `docs/guides/colab.md` — Colab system R setup stub
- `docs/guides/databricks.md` — cluster notes; `ggplotpy.display()` stub
- `exploration/README.md`, `exploration/perf/README.md` — Phase 8 benchmark placeholder
- `docs/coverage_matrix.md` — documentation section added

### Skipped / unchanged

- `.github/workflows/ci.yml` — already includes `macos-latest`; no diff
- `src/ggplotpy/core/gg.py` — owned by core worker
- Integration tests — not run (per task scope)

### Next actions

1. Publish conda-forge feedstock when ggplotpy reaches v0.5 tag.
2. Flesh Colab/Databricks guides after display hook lands.
3. Implement `exploration/perf/bench_render.py` in Phase 8.

---

## Parallel worker: codegen complete

**Driver:** agent (parallel to OOM worker)  
**Milestone:** v0.1 codegen  
**Goal:** Reflection pipeline — introspect ggplot2, emit `.pyi`, lazy symbol cache, R-free unit tests, CI staleness.

### Files created/modified

- `scripts/generate_stubs.py` — introspect ggplot2, write 50-export `.pyi`, `--skip-if-no-r`
- `src/ggplotpy/codegen/emit.py` — `emit_pyi_stub()`, `formals_to_signature()` (empty vs None)
- `src/ggplotpy/codegen/reflect.py` — (unchanged) namespace export + formals introspection
- `src/ggplotpy/generated/__init__.py` — `_EXPORTS_CACHE` for `load_ggplot2_symbol()`
- `src/ggplotpy/generated/ggplot2_reflected.pyi` — 50 committed exports
- `tests/unit/test_codegen_reflect.py` — mock `list_namespace_exports` (R-free)
- `docs/api/index.md` — v0.1 API stub index
- `.github/workflows/codegen.yml` — regenerate + staleness; skip when ggplot2 absent
- `STATUS.md` — v0.1 codegen checkboxes

### Commands run + results

```text
python -m pytest tests/unit/test_codegen_reflect.py tests/unit/test_to_r_normalize.py -q → 12 passed
```

### Skipped / unchanged

- `src/ggplotpy/core/gg.py` — owned by OOM worker
- Integration pytest — not run (per scope)

### Next actions

1. Rd → docstrings pipeline (`codegen/rd_to_md.py`).
2. Expand ggplot2 export limit beyond 50; T2 parity goldens.
3. macOS × ggplot2 3.5/4.0 CI matrix for v0.1 exit gate.

---

## Parallel worker: v0.5 ecosystem

**Driver:** agent (parallel worker)  
**Milestone:** v0.5 ecosystem features  
**Goal:** patchwork operators, lazy ext reflection, Arrow/polars ingress, extension tests/notebook, perf stub — without touching `gg.py`, `conftest.py`, or CI integration job.

### Files created/modified

- `src/ggplotpy/core/patchwork.py` — `PlotComposition`, `from_plot()`, `|``/`` via R patchwork; setup guard
- `src/ggplotpy/ext/__init__.py` — `KNOWN_EXTENSIONS`, `list_installed_extensions()`, install hints
- `src/ggplotpy/data/arrow.py` — zero-copy attempt via rpy2 converter + R `arrow` pkg fallback
- `src/ggplotpy/data/polars_bridge.py` — polars → arrow → R
- `src/ggplotpy/data/__init__.py` — lazy `arrow_to_r` / `polars_to_r` exports
- `tests/unit/test_data_ingress.py`, `tests/unit/test_ext_lazy.py` — T0 R-free checks
- `tests/extensions/test_patchwork_operators.py` — `|``/`` smoke when patchwork installed
- `notebooks/02_extensions_demo.ipynb` — ggrepel + patchwork demo with graceful skip
- `exploration/perf/benchmark_ingress.py` — 10k-row pandas vs Arrow row-count stub
- `STATUS.md` — v0.5 checkboxes

### Commands run + results

```text
GGPLOTPY_SKIP_INTEGRATION=1 python -m pytest tests/unit tests/extensions -q → 26 passed, 1 skipped
```

### Skipped / unchanged

- `src/ggplotpy/core/gg.py`, `tests/conftest.py`, `scripts/run_tests.ps1`, `.github/workflows/ci.yml` integration job

### Next actions

1. gganimate render shim (`core/gganimate.py` or ext helper).
2. Wire `GG.__or__` / `__truediv__` when core worker owns `gg.py`.
3. Run `benchmark_ingress.py` with `GGPLOTPY_BENCH_R=1` locally after R arrow pkg install.


---

## v0.1 docs/CI worker — 2026-06-21

**Driver:** agent (parallel worker)  
**Milestone:** v0.1 docs + CI  
**Goal:** Sphinx furo skeleton, Rd extract stub, ggplot2 version CI, parity skip guard — without touching `gg.py` / root `conftest.py`.

### Files created/modified

- `docs/conf.py` — furo theme, sphinx-design/copybutton, engineering-doc excludes
- `docs/index.md` — landing page with grid cards and install blurb
- `docs/_static/.gitkeep` — static assets placeholder for Sphinx
- `docs/scripts/extract_rd.py` — ggplot2 Rd → JSON stub (`--skip-if-no-r`, `--limit 50`)
- `docs/getting-started.md` — link to `api/index.md`
- `.github/workflows/ci.yml` — comments + `ggplot2-versions` job (3.5.2, 4.0.0 on ubuntu)
- `tests/parity/test_to_r_parity.py` — `GGPLOTPY_SKIP_INTEGRATION` pytestmark skip
- `pyproject.toml` — docs extra: furo, sphinx-design, sphinx-copybutton
- `STATUS.md` — v0.1 Rd/CI/Sphinx checkboxes

### Commands run + results

```text
python -m pytest tests/unit -q  → 26 passed, 1 skipped
```

### Skipped / unchanged

- `src/ggplotpy/core/gg.py`, `scripts/run_tests.ps1`, `src/ggplotpy/core/patchwork.py` — per task scope
- `tests/conftest.py` — owned by OOM worker; parity skip added in test file instead
- macOS in primary CI matrix — already present; documented 3 OS × 2 ggplot2 deferral

### Next actions

1. `render_rd.py` + Jinja MyST pages (M2); wire autodoc.
2. Expand T2 parity goldens; promote integration job from continue-on-error when stable.
3. Run `extract_rd.py --all` in CI/docs workflow when Rd pipeline lands.
---

## Session 2026-06-21 — OOM infrastructure + T1 validation

**Driver:** agent (OOM subagent)
**Milestone:** MVP
**Goal:** Stop subagent OOM from monolithic pytest; validate Tier0/Tier1 on Windows.

### OOM fixes

- `src/ggplotpy/core/gg.py` — UTF-8 docstring; `ro.r["+"]` composition; `_render_plot` svglite/png + `try(dev.off(), silent=TRUE)` in `finally` always
- `r-helper/ggplotpy/R/aes.R` — `names(exprs) <- names(mapping)` (already present)
- `tests/conftest.py` — `GGPLOTPY_SKIP_INTEGRATION` collection gate; `GGPLOTPY_RUN_HEAVY`; module `mtcars_df`; `gc.collect()` after integration tests
- `scripts/run_tests.ps1`, `scripts/run_tests.sh` — Tier0 unit; Tier1 one subprocess per integration file; `heavy` opt-in full tree
- `pyproject.toml` — document env vars in pytest section
- `.github/workflows/ci.yml` — matrix `GGPLOTPY_SKIP_INTEGRATION=1`; separate `integration` job runs `run_tests.sh tier1`
- `docs/testing_guide.md` — OOM avoidance section
- `project_memory/discoveries.md` — root cause entry
- `src/ggplotpy/runtime/check_setup.py` — `CORE_R_PACKAGES`: ggplot2, rlang, svglite, ggplotpy

### Commands run + results (Windows, R 4.5.2)

```text
scripts/run_tests.ps1 -Tier tier0  -> exit 0 (26 passed, 1 skipped via direct pytest)
scripts/run_tests.ps1 -Tier tier1  -> exit 0
  PASS tests/integration/test_facets.py
  PASS tests/integration/test_r_escape.py
  PASS tests/integration/test_render_basic.py
```

### Next actions

1. Enable T2 parity in separate subprocess job (parity file isolated like T1).
2. Remove `continue-on-error` patterns once integration job stable on ubuntu.

## OOM worker complete — T1 validation

**Driver:** agent (OOM critical path)  
**Milestone:** MVP  
**Goal:** OOM-safe test runners, render hardening, CI split, local T1 green on Windows R 4.5.2.

### Files created/modified

- `scripts/run_tests.ps1`, `scripts/run_tests.sh` — tier0 batch unit; tier1 one subprocess per integration file
- `tests/conftest.py` — GGPLOTPY_SKIP_INTEGRATION / GGPLOTPY_RUN_HEAVY, gc.collect, module `mtcars_df` (prior session)
- `src/ggplotpy/core/gg.py` — `ro.r["+"]`, svglite render, try/finally `dev.off()`, UTF-8 SVG read
- `r-helper/ggplotpy/R/aes.R` — `names(exprs)` fix; reinstalled via R `install.packages(..., type='source')`
- `.github/workflows/ci.yml` — `test-fast` with `GGPLOTPY_SKIP_INTEGRATION=1`; `test-integration` runs `run_tests.sh tier1`
- `docs/testing_guide.md` — OOM section
- `project_memory/discoveries.md` — Windows integration OOM entry
- `STATUS.md` — MVP T1 local green

### Verification (R_HOME=C:\Program Files\R\R-4.5.2)

```
.\scripts\run_tests.ps1 -Tier all
```

- Tier0: 26 passed, 1 skipped (polars)
- Tier1: PASS `test_facets.py`, PASS `test_r_escape.py`, PASS `test_render_basic.py` (3/3)

**Did not run:** `pytest tests/` single process (OOM policy).


---

## Tier1 parity + gallery + CI — 2026-06-21

**Driver:** agent (subagent)
**Milestone:** MVP / T2 parity gate
**Goal:** Extend OOM-safe tier1 to parity/gallery; CI integration via `run_tests.ps1`; mark T2 green.

### Files modified

- `scripts/run_tests.ps1` — tier1 collects `tests/integration`, `tests/parity`, `tests/gallery` (one subprocess each)
- `scripts/run_tests.sh` — same tier1 file set + `GGPLOTPY_RUN_HEAVY=1` for parity/gallery
- `.github/workflows/ci.yml` — integration job: `pwsh ./scripts/run_tests.ps1 -Tier tier1` (no continue-on-error)
- `STATUS.md` — T2 parity + tier1 5/5 metrics

### Commands run + results (Windows, R_HOME=R-4.5.2)

```text
scripts/run_tests.ps1 -Tier tier1 → exit 0, 5/5 pass
  PASS tests/gallery/test_gallery_render.py
  PASS tests/integration/test_facets.py
  PASS tests/integration/test_r_escape.py
  PASS tests/integration/test_render_basic.py
  PASS tests/parity/test_to_r_parity.py
```

### Next actions

1. Confirm integration job green on ubuntu + windows CI.
2. Expand T2 golden set beyond mtcars scatter as core API grows.

---

## v0.5 extensions + T3 baseline — 2026-06-21

**Driver:** agent (subagent)
**Milestone:** v0.5 ecosystem · v1.0 stubs
**Goal:** patchwork on GG, gganimate wrapper, sf/GeoArrow stubs, T3 SVG baseline, extension tests in tier1.

### Files created/modified

- `src/ggplotpy/core/gg.py` — `GG.__or__` / `GG.__truediv__` delegate to patchwork
- `src/ggplotpy/core/animate.py` — `transition_states`, `animate()` → GIF bytes (gifski)
- `src/ggplotpy/data/sf_bridge.py` — GeoArrow/WKB stub docs + `NotImplementedError`
- `src/ggplotpy/backend/rserve.py`, `subprocess.py` — v1.0 interface docstrings
- `docs/scripts/render_rd.py` — M2 JSON → markdown stub
- `tests/extensions/` — ggrepel render, GG patchwork ops, gganimate (skip w/o gifski)
- `tests/gallery/test_visual_baseline.py` + `baseline_images/mtcars_scatter.svg*`
- `tests/unit/test_v05_stubs.py` — T0 stubs for animate/sf/backends
- `notebooks/03_synthetic_gallery.ipynb`
- `scripts/run_tests.ps1`, `run_tests.sh` — tier1 includes `tests/extensions`

### Commands run + results (Windows, R_HOME=R-4.5.2)

```text
pytest tests/unit -q                    → 43 passed, 1 skipped
scripts/run_tests.ps1 -Tier tier1       → 11/11 pass (gganimate/ggrepel skipped — not installed)
pytest tests/gallery/test_visual_baseline.py → 1 passed (SVG hash baseline)
```

### Next actions

1. Install ggrepel + gganimate + gifski in CI optional job for extension render smoke.
2. Expand T3 baseline set beyond mtcars scatter.

---

## full ggplot2 coverage worker — 2026-06-21

**Driver:** agent (subagent)
**Milestone:** v0.1 codegen — full namespace
**Goal:** Emit all `getNamespaceExports("ggplot2")` into `.pyi`; runtime resolve any export; geoms smoke + export-count tests.

### Files modified

- `scripts/generate_stubs.py` — default `--limit` removed (all exports); 643 symbols written
- `src/ggplotpy/generated/ggplot2_reflected.pyi` — **643** export stubs (was 50)
- `src/ggplotpy/generated/__init__.py` — `load_ggplot2_symbol` refreshes export cache on miss
- `tests/unit/test_ggplot2_exports.py` — pyi count vs live namespace; mock ≥100
- `tests/integration/test_geoms_smoke.py` — 15 geoms × 20-row synthetic df; `@slow`
- `docs/coverage_matrix.md` — export count table (643)
- `STATUS.md` — full namespace metrics

### Commands run + results (Windows, R_HOME=R-4.5.2)

```text
python scripts/generate_stubs.py → Wrote 643 symbols
GGPLOTPY_SKIP_INTEGRATION=1 pytest tests/unit -q → 43 passed, 1 skipped
pytest tests/integration/test_geoms_smoke.py -q → 15 passed
scripts/run_tests.ps1 -Tier tier1 → 11/11 pass
```

**Export count:** 643 (`getNamespaceExports("ggplot2")` == `ggplot2_reflected.pyi` def count)

### Next actions

1. CI codegen staleness job should pass with full 643-export tree.
2. Optional: expand `ggplotpy.__init__` lazy exports beyond `_GGLOT2_CORE` hand list.

---

## UX polish (Phase 4) — 2026-06-21

**Driver:** agent (subagent)  
**Milestone:** v0.1 UX / RESEARCH Phase 4  
**Goal:** "Great thorough" UX per `docs/user_interface.md`.

### Files created/modified

- `src/ggplotpy/core/errors.py` — `last_r_code()` re-export, `format_r_error()`, `GgplotpyRError` with offending line
- `src/ggplotpy/backend/inprocess.py` — `rcall()` attaches R line to errors
- `src/ggplotpy/core/to_r_util.py` — `format_layer_for_to_r()` for readable aes/geom hints
- `src/ggplotpy/core/gg.py` — layered `to_r()` script; mapping hints preserved
- `src/ggplotpy/core/defer.py` — use readable layer formatting
- `src/ggplotpy/__init__.py` — public API: ggplot, aes, GG, R, check_setup, set_options, last_r_code, display; star-import docstring
- `src/ggplotpy/runtime/check_setup.py` — robstatm-style one-screen report + install hints
- `src/ggplotpy/runtime/bootstrap.py` — `verbose=False` to avoid double print
- `src/ggplotpy/display.py` — Databricks/Jupyter mime bundle via `publish_display_data`
- `README.md` — 60-second quickstart
- `docs/guides/quickstart.md`, `docs/guides/troubleshooting.md` — new guides
- `docs/guides/databricks.md` — `display()` no longer stub
- `tests/unit/test_ux_errors.py` — 7 T0 tests (last_r_code, error shape, to_r aes)
- `STATUS.md` — UX section + T0 count

### UX checklist (Phase 4)

- [x] Star-import documented as primary (`from ggplotpy import *`)
- [x] Clean public API surface in `__init__.py`
- [x] `last_r_code()` exported; R errors show offending line
- [x] `to_r()` readable layered script with aes/geom hints
- [x] `check_setup()` friendly one-screen report (robstatm style)
- [x] `display()` for notebook HTML mime bundle
- [x] README 60-second quickstart
- [x] quickstart + troubleshooting guides

### Commands run + results

```text
python -m pytest tests/unit/test_ux_errors.py tests/unit -q
→ 43 passed, 1 skipped (polars)
```

---

## Resume stalled work — 2026-06-21

**Driver:** agent (subagent)  
**Milestone:** v0.1 + v0.5 resume  
**Goal:** Complete stalled tasks: lazy `__getattr__` for full ggplot2 namespace, notebook CI, T2 golden sync.

### Files created/modified

- `src/ggplotpy/__init__.py` — any unknown name → `load_ggplot2_symbol`; docstring for star-import vs attribute access
- `tests/unit/test_ggplot2_exports.py` — `ggplotpy.geom_bar` via `__getattr__`; unknown name raises
- `tests/notebooks/test_notebooks.py` — nbclient execute for `01_mvp_mtcars`, `02_extensions_demo` (skip `GGPLOTPY_SKIP_NOTEBOOKS=1`)
- `tests/golden/to_r/mtcars_scatter.r` — synced to layered `to_r()` UX format (intentional golden update)
- `pyproject.toml` — `nbclient>=0.9` in dev extras
- `STATUS.md` — test counts + last verify

### Already present (verified, not reworked)

- `src/ggplotpy/core/gg.py` — `GG.__or__` / `__truediv__` for patchwork
- `src/ggplotpy/core/animate.py` — gganimate stub + `animate()` → GIF bytes
- `scripts/run_tests.ps1` — tier1 includes `tests/extensions`
- `tests/extensions/test_patchwork_operators.py` — `test_gg_or_operator_direct` / truediv
- `notebooks/03_synthetic_gallery.ipynb`, `docs/scripts/render_rd.py`

### Commands run + results (Windows, R_HOME=R-4.5.2)

```text
GGPLOTPY_SKIP_INTEGRATION=1 pytest tests/unit -q           → 45 passed, 1 skipped
scripts/run_tests.ps1 -Tier tier1                      → 11/11 pass
pytest tests/notebooks/test_notebooks.py -q            → 2 passed (01, 02)
pytest tests/parity/test_to_r_parity.py -q               → 1 passed (after golden sync)
```

### Next actions

1. Fix `03_synthetic_gallery.ipynb` R-dotted kwargs (`max.overlaps`) for Python syntax; add to notebook CI when clean.
2. v1.0: implement `sf_bridge` / GeoArrow; expand T3 baseline gallery beyond 5 SVG hashes.
3. Optional CI job: ggrepel + gganimate + gifski for extension render smoke (currently skipped).


---

## Session close-out — 2026-06-21

**Driver:** agent (subagent)  
**Milestone:** v0.1/v0.5 gate verification + v1.0 prep  
**Goal:** Remaining open items from STATUS (exports, notebooks, T3, strict T2, tiers, docs).

### Files modified

- `src/ggplotpy/__init__.py` — `__getattr__` falls through to `load_ggplot2_symbol` (all ggplot2 exports)
- `tests/notebooks/test_notebooks.py` — notebooks 01–03; `GGPLOTPY_SKIP_NOTEBOOKS`
- `scripts/run_tests.ps1` — **tier3** notebooks; `all` runs tier0→1→2→3
- `tests/gallery/test_visual_baseline.py` — **5** parametrized SVG hash baselines
- `tests/gallery/baseline_images/*` — bar, histogram, facet, smooth + scatter
- `tests/parity/test_to_r_parity.py` — full normalized script == golden file
- `docs/guides/colab.md`, `docs/guides/databricks.md` — polished
- `environment.yml` — conda test note; `conda/recipe/meta.yaml` structure validated
- `notebooks/03_synthetic_gallery.ipynb` — `max_overlaps` Python kwarg fix
- `STATUS.md` — v0.1 complete; v0.5 mostly complete; honest v1.0 remainder

### Commands run + results (Windows, R_HOME=R-4.5.2)

```text
scripts/run_tests.ps1 -Tier tier0  → 45 passed, 1 skipped
scripts/run_tests.ps1 -Tier tier1  → 11/11 files pass
scripts/run_tests.ps1 -Tier tier2  → 5/5 files, 20 passed
scripts/run_tests.ps1 -Tier tier3  → 3/3 notebooks (after 03 fix)
pytest tests/gallery/test_visual_baseline.py → 5 passed
```

### Next actions (v1.0)

1. `install_r()` + conda-forge feedstock submission (replace PLACEHOLDER sha/maintainer).
2. 4-OS CI + optional extension render job (ggrepel/gganimate/gifski).
3. ggplot2 4.0 sign-off; sf/GeoArrow + Rserve backends.

---

## Documentation thorough update — 2026-06-21

**Driver:** agent (subagent)  
**Milestone:** v0.1/v0.5 docs sync  
**Goal:** Rewrite all user-facing and engineering docs to match current codebase (643 exports, tier runners, implemented APIs).

### Files updated (22 + governance)

- `README.md` — v0.1 complete status, tier table, lazy exports, guide links
- `docs/getting-started.md`, `docs/guides/*.md` (quickstart, installation, troubleshooting, colab, databricks)
- `docs/user_interface.md` — implemented vs planned; `animate()` module API; direct `GG | GG`
- `docs/api/index.md` — 643 exports, `load_ggplot2_symbol`, honest geom smoke scope
- `docs/architecture.md`, `coverage_matrix.md`, `testing_guide.md`, `validation_strategy.md`
- `docs/quality_gates.md`, `packaging_plan.md`, `documentation_plan.md`
- `docs/index.md` — guide cards + hidden toctree; `docs/conf.py` exclude comment
- `AGENTS.md`, `CHANGELOG.md`, `exploration/README.md`, `exploration/perf/README.md`
- `notebooks/README.md` (new) — 01–03, tier3 run instructions
- `STATUS.md` — user docs row only

### Contradictions fixed

- README/AGENTS claimed MVP/v0.1 "in progress" → **v0.1 complete**, v0.5 mostly complete
- `coverage_matrix.md` ergonomic core marked `not_started` → **done**
- `api/index.md` said 50-export stub → **643**
- `user_interface.md` listed `set_options` / `display` as planned → **implemented**; `anim.animate()` → `animate(plot, ...)`
- `CHANGELOG.md` claimed package not scaffolded → substantive **0.0.1.dev0** feature list
- `documentation_plan.md` M3 claimed `docs_sphinx/` → actual **`docs/` + furo**
- `quality_gates.md` M0/MVP/v0.1 checkboxes unchecked → aligned with STATUS
- Docs implied all geoms tested → **15 smoke + 643 reflection**
- Getting-started required `pandas_to_r()` → **`ggplot(df)` accepts pandas directly**
- patchwork docs only showed `from_plot` → documented **direct `p1 | p2` on `GG`**

### Verification

Docs-only session — no pytest run required. Sphinx: `pip install -e ".[docs]" && sphinx-build -W -b html docs docs/_build/html` (recommended follow-up).

---

## Audit + parity-correctness fixes — 2026-06-22

**Driver:** agent (review/refactor pass)
**Milestone:** v0.5/v1.0 — "all ggplot2 functions usable" verification
**Goal:** Phase A audit (read-only) then fix verified gaps to real R parity. User directive: "keep going until done."

### Audit method

Read AGENTS/STATUS/progress_log, RESEARCH_AND_PLAN, architecture/user_interface/validation docs, full `src/ggplotpy/` and `tests/`. Then **ran executable probes** (not just reading) against live R 4.5.2 to verify claims rather than trust them.

### Bugs found by probe (all previously GREEN in suite — validation gap)

1. **`geom_*(aes(...))` broken** — layer-level aesthetics raised `NotImplementedError` (DeferredRCall not convertible). Everyday ggplot2 idiom; biggest hole vs "all functions usable".
2. **`to_r()` emitted invalid R** for aes values containing commas (`label="paste(a, b)"`).
3. **Tuple/list kwargs failed** — `coord_cartesian(xlim=(0,5))`, etc.
4. **Direct Arrow/polars ingress failed** — `ggplot(pa.Table)` errored; Arrow "zero-copy" headline only reachable via manual `arrow_to_r()`.
5. **`aes("wt","mpg")` positional** unsupported.
   Root cause for 1–3: `format_r_value` round-tripped ggplotpy objects through rpy2 instead of emitting their R source.

### Files modified

- `src/ggplotpy/core/defer.py` — `format_r_value` handles `DeferredRCall`/`RObject` (emit `.code`) + `list`/`tuple` (→ `c(...)`)
- `src/ggplotpy/core/to_r_util.py` — replaced naive comma-split/`rstrip(")")` with balanced-paren, quote-aware `_convert_aes_calls` (also converts nested aes inside geoms)
- `src/ggplotpy/core/aes.py` — positional `x`,`y` args + duplicate/overflow guards
- `src/ggplotpy/core/gg.py` — `_coerce_data()` routes pandas/pyarrow/polars/rpy2 into `ggplot()`
- `tests/unit/test_layer_values_to_r.py` (new, 14 T0) — pure-function regressions
- `tests/edge/test_layer_aes.py` (new, 9 T2) — render-path regressions incl. direct Arrow ingress
- `scripts/run_tests.sh` — added tier2/tier3 (parity with `run_tests.ps1`)
- `.github/workflows/ci.yml` — integration job now runs tier2 (edge matrix) — previously **never CI-gated**
- `docs/guides/quickstart.md`, `docs/user_interface.md`, `docs/validation_strategy.md` — document layer aes, sequence args, multi-backend ingress; case 2b
- `project_memory/discoveries.md` — 3 dated entries

### Commands run + results (Windows, R 4.5.2)

```text
scripts/run_tests.ps1 -Tier tier0  → 58 passed, 1 skipped (was 45)
scripts/run_tests.ps1 -Tier tier1  → 11/11 files pass (parity golden unchanged)
scripts/run_tests.ps1 -Tier tier2  → 6/6 files pass (incl. 9 new layer-aes, direct Arrow)
scripts/run_tests.ps1 -Tier tier3  → see session-end (notebooks)
python scripts/generate_stubs.py   → 643 symbols (no staleness)
```

### Next actions (v1.0 remainder, unchanged by this pass)

1. sf/GeoArrow ingress; Rserve/subprocess backend.
2. PyPI wheel + conda-forge feedstock publish.
3. 4-OS CI + optional ggrepel/gganimate/gifski render job; expand T3 baselines.
4. Consider wiring optional `validate_aes_columns` (exists, unused) behind a flag.

---

## Data conversions + full-coverage verification — 2026-06-22 (cont.)

**Driver:** agent (review/refactor pass, cont.)
**Milestone:** "all Python→R conversions handled" + "all ggplot2 functionality usable, verified"
**Goal:** Per user: handle every Python→R data conversion; verify all ggplot2 functions work from Python; research RESEARCH_AND_PLAN thoroughly for UX. Directive: "keep going until done."

### Read

Full `RESEARCH_AND_PLAN.md` (12 phases). Phase 2.2 data plane = pandas2ri / Arrow zero-copy / numpy2ri; Phase 2.5 extension caveats; Phase 4 UX spec.

### Findings by probe (live R 4.5.2)

- **Ingress gaps:** `ggplot({"x":...})` (dict), `ggplot(np.ndarray)`, `ggplot(pd.Series)`, list-of-records all raised.
- **Value coercion gaps:** `format_r_value` mangled numpy scalars/arrays (`structure(1:3, dim=3L)`), `range`, `dict`.
- **Hang risk:** embedded R **deadlocked** on `geom_hex` without hexbin — rlang `check_installed()` stdin prompt.

### Files modified

- `core/gg.py` — `_coerce_data` now handles dict / list-of-records / Series / 1-D+2-D numpy (→ `V1..Vn`) / pyarrow / polars / rpy2.
- `core/defer.py` — `format_r_value` handles numpy scalars (→ builtin), ndarray/range (→ `c(...)`), dict (→ `list(k=v)`).
- `backend/inprocess.py` — `_force_noninteractive_r()`: `options(rlang_interactive=FALSE, menu.graphics=FALSE)` at init (**ADR D-P012**).
- `tests/edge/test_data_conversions.py` (new, 11 T2), `tests/edge/test_noninteractive_r.py` (new, 2 T2), `tests/gallery/test_category_coverage.py` (new, 30 T1), + numpy/dict/range cases in `tests/unit/test_layer_values_to_r.py`.
- `scripts/verify_ggplot_coverage.py` (new deliverable) — exhaustive sweep.
- Docs: `user_interface.md` (data inputs), `validation_strategy.md` (cases 13b/14/15), `decisions.md` D-P012, `discoveries.md` (2 entries).

### Verification (Windows, R 4.5.2)

```text
scripts/verify_ggplot_coverage.py → 108 OK, 5 SKIP (hexbin/sf/map), 0 real FAIL
run_tests.ps1 -Tier tier0 → 63 passed, 1 skipped
run_tests.ps1 -Tier tier1 → 12/12 files (category coverage 30/30)
run_tests.ps1 -Tier tier2 → 8/8 files (data_conversions 11, noninteractive 2)
run_tests.ps1 -Tier tier3 → 3/3 notebooks
```

**Coverage truth:** every renderable ggplot2 family works from Python (49/53 geoms; remaining 4 need sf/hexbin/map data). All 643 exports remain reflectively callable.

### Next actions (v1.0 remainder)

1. sf/GeoArrow ingress (would close the last 4 geom skips); Rserve/subprocess backend.
2. PyPI + conda-forge publish; 4-OS CI; optional hexbin/ggrepel/gganimate render job.
3. Sphinx `-W` build verification of doc edits.

---

## Gap-closing + beautiful docs — 2026-06-22 (cont. 2)

**Driver:** agent (review/refactor pass, cont.)
**Milestone:** close v1.0 gaps + ship documentation
**Goal:** Per user: fix all gaps; build beautiful docs with thorough examples on external data showing all functionality + data conversions; great setup/install guides; ease of use. Directive: "keep going until done."

### Gaps closed

- **sf/GeoArrow ingress** — `data/sf_bridge.py` rewritten: `sf_to_r` (GeoPackage → `sf::st_read`), `geoarrow_to_r` (via `GeoDataFrame.from_arrow`), `is_geodataframe`; wired into `ggplot()` `_coerce_data`; `pyproject` `geo` extra. Clear errors when geopandas/sf absent. (ADR D-P013)
- **Isolated subprocess render** — `backend/subprocess.py` `render_in_subprocess()` serialises plot via `saveRDS`, renders in fresh `Rscript` (crash isolation, base R only); `GG.save(isolated=True)` + `GG.render_isolated()`. Full IPC backend still future. (ADR D-P013)
- **Data conversions** (earlier this session) now documented end-to-end.

### Documentation (new + updated)

- `docs/gallery.md` — **20 figures** on real external data (Palmer Penguins, Gapminder) + ggplot2 `mpg`/`diamonds`/`economics`/`iris`, with runnable code + embedded renders.
- `docs/guides/data-conversions.md` — full Python→R ingress guide (pandas/dict/records/numpy/Series/Arrow/polars/GeoPandas) + argument-value coercion.
- `docs/scripts/build_gallery.py` — regenerates all images (**19 OK, 0 fail**); `docs/data/{penguins.csv,gapminder.tsv}` committed; PNGs in `docs/_static/gallery/`.
- `index.md` hero image + gallery/data-conversion cards + toctree; `getting-started.md`, `installation.md` (geo extra), `quickstart.md` (isolated render) updated.

### Verification (Windows, R 4.5.2)

```text
python docs/scripts/build_gallery.py → 19 images, 0 failures
python -m sphinx -W -b html docs ...  → build succeeded, 0 warnings
run_tests.ps1 -Tier tier0 → 64 passed
run_tests.ps1 -Tier tier1 → 12/12 files (category coverage 30/30)
run_tests.ps1 -Tier tier2 → 9/9 files (sf render skipped: sf absent; subprocess render 3/3)
run_tests.ps1 -Tier tier3 → notebooks (see session end)
```

Updated stale `test_v05_stubs.py` (sf no longer a stub). New tests: `test_sf_bridge.py` (4 T0), `test_subprocess_render.py` (3 T2), `test_data_conversions.py` geopandas case (needs_sf).

### Honest remaining (v1.0)

1. GeoArrow **zero-copy** path (current sf uses GeoPackage round-trip); full IPC subprocess/Rserve backend.
2. PyPI + conda-forge publish; 4-OS CI; optional render job with hexbin/sf/ggrepel installed (would lift gallery skips).

---

## Install everything + close all skips + easy cross-OS install — 2026-06-22 (cont. 3)

**Driver:** agent (review/refactor pass, cont.)
**Milestone:** zero-skip verification + ergonomic install
**Goal:** Per user: download/install whatever's needed and fix open gaps; make install easy on all OS; fix Furo `{contents}` doc warning. Directive: "keep going until done."

### Installed (this box)

- **R (binary from CRAN):** hexbin, ggrepel, ggthemes, maps, mapproj, sf (+ proxy/e1071/wk/classInt/s2/units), arrow.
- **Python (pip):** geopandas 1.1.3 (+ shapely/pyproj), polars 1.41.2, pyarrow.

### Fixes / features

- **sf converter bug** — `sf_to_r` read the sf object under the active pandas converter, which choked on the geometry list-column (`'NULLType' object is not iterable`). Now reads under `default_converter` so the sf object stays a raw R object. `geom_sf` from GeoPandas renders (points, polygons, choropleth).
- **`install_r()`** (new, `runtime/bootstrap.py`) — reticulate-style cross-OS provisioning: installs CRAN **binaries** on Windows/macOS (no compiler), source on Linux; profiles core/stretch/examples/**all**; clear per-OS guidance + conda one-liner when R absent. Exposed as `ggplotpy.install_r`. `ggplotpy-bootstrap --profile all` too.
- **Docs `{contents}` warning** — removed the Furo-discouraged `{contents}` directives from `gallery.md` / `data-conversions.md` (Furo has its own right-sidebar TOC).
- **Coverage sweep** now renders geom_sf/sf_label/sf_text (geopandas) + geom_map (maps + `R()` map=) → **113 OK, 0 SKIP, 0 FAIL**.
- **Gallery** +3 images: hexbin, ggrepel labels, **NC SIDS sf choropleth** (GeoPandas→sf→geom_sf). 22 images total.
- New `tests/unit/test_bootstrap.py` (install_r/profiles/guidance). Noted latent shadowing: `runtime/__init__` imports `bootstrap`/`check_setup` *functions*, shadowing the same-named submodules for `import X.Y as` (use `from`-imports / importlib).

### Verification (Windows, R 4.5.2 — all green)

```text
verify_ggplot_coverage.py → 113 OK, 0 skip, 0 fail
build_gallery.py          → 22 images, 0 failures
sphinx -W                 → build succeeded, 0 warnings
tier0 → 67 passed (polars now runs)
tier2 → 9/9 files (geom_sf render now executes: data_conversions 12)
tier1 → see session end (ggrepel now executes)
```

### Genuinely remaining (need external infra)

1. GeoArrow zero-copy geometry path; full IPC subprocess/Rserve backend.
2. PyPI wheel + conda-forge feedstock publish; 4-OS CI matrix.

---

## Animation/advanced docs + release machinery — 2026-06-22 (cont. 4)

**Driver:** agent (review/refactor pass, cont.)
**Milestone:** advanced gallery + release-ready packaging
**Goal:** Per user: add animation + complicated examples to the docs site; wire conda-forge + PyPI so a release is one command away. Directive: "keep going until done."

### Installed

R: gganimate, gifski, ggdist, ggridges, transformr (binary).

### Features / fixes

- **`animate()` refactor** (`core/animate.py`) — single-call `gganimate::animate(..., renderer=gifski_renderer(file))`; added `nframes`/`duration`/`**kwargs`. Cleaner + fixed the awkward two-step render.
- **gganimate × ggplot2 4.0** — found upstream incompat: `transition_states` default wrap-tweening errors (`order(ind) is not a vector`) on ggplot2 4.0.1 / gganimate 1.0.11. `transition_time` / `transition_reveal` / `transition_manual` work. Gallery uses `transition_time`; gganimate test uses `transition_manual` (no tween, bulletproof). Documented in gallery note.
- **Gallery +4** — ggdist half-eye, ggridges ridgeline, and an **animated Gapminder GIF** (251 KB, looped); 25 assets total. New gallery sections: Animation, Advanced statistical layers.
- **Release machinery:**
  - `pyproject` — `dynamic = ["version"]` from `__init__.__version__` (now **0.1.0**); full classifiers/URLs; **wheel force-includes `r-helper` → `ggplotpy/_r_helper/`** so PyPI installs can install the R helper. `_ggplotpy_r_helper_path()` prefers the packaged copy.
  - `.github/workflows/publish.yml` — build + **PyPI Trusted Publishing** on tag `ggplotpy-v*`.
  - `conda/recipe/meta.yaml` — sources PyPI sdist, maintainer `Aakarsh751`, full deps/test.
  - `scripts/pypi_sha256.py`, `RELEASING.md` (one-command flow), `CHANGELOG` 0.1.0.

### Verification (Windows, R 4.5.2)

```text
python -m build           → ggplotpy-0.1.0 sdist+wheel; wheel bundles ggplotpy/_r_helper/ggplotpy/*
python -m twine check     → both PASSED
build_gallery.py          → 25 assets incl. animation.gif (GIF89a, animated)
sphinx -W                 → build succeeded, 0 warnings
tier0 67 · tier1 12/12 (gganimate now passes) · tier2 9/9 (prev) · tier3 3/3 (prev)
```

### Genuinely remaining

1. First PyPI release (needs PyPI Trusted-Publisher config + tag) → then conda-forge staged-recipes PR (paste sdist sha256).
2. GeoArrow zero-copy; full IPC/Rserve backend; 4-OS CI matrix.
