# Coverage Matrix — ggplot2 core

Tracks implementation status for ggplot2 exports and blessed extensions. Reconcile weekly against `generated/` and `STATUS.md`.

**Status values:** `not_started` | `in_progress` | `blocked` | `done` (generated/reflected/hand)

**Last updated:** 2026-06-21 (documentation sync)

---

## Core ggplot2 export coverage

| Metric | Value | Notes |
|--------|-------|-------|
| `getNamespaceExports("ggplot2")` (R 4.5.2 / ggplot2 local) | **643** | Live introspection via `list_namespace_exports` |
| `ggplot2_reflected.pyi` stub count | **643** | `python scripts/generate_stubs.py` (no `--limit`) |
| Runtime resolution | **all exports** | `load_ggplot2_symbol(name)` + `ggplotpy.__getattr__` cache |
| Hand-curated top-level re-exports | **14** | `ggplotpy.__init__` `_GGLOT2_CORE` |
| T1 geom render smoke | **15 geoms** | `tests/integration/test_geoms_smoke.py` — not full namespace |

---

## Core ggplot2 (representative exports)

| Category | Examples | Status | Notes |
|----------|----------|--------|-------|
| Init | `ggplot`, `ggproto` | done | Reflection + hand `ggplot` |
| Aesthetics | `aes`, `aes_string` (compat) | done | NSE via helper |
| Geoms | `geom_point`, `geom_line`, `geom_bar`, … | done | Reflection; 15 smoke-rendered |
| Stats | `stat_summary`, `stat_bin`, … | done | Reflection |
| Scales | `scale_*`, `xlim`, `ylim` | done | Reflection |
| Coords | `coord_flip`, `coord_fixed`, … | done | Reflection + edge tests |
| Facets | `facet_wrap`, `facet_grid` | done | Formula strings |
| Themes | `theme`, `theme_*`, `element_*` | done | Reflection |
| Guides | `guides`, `guide_*` | done | Reflection |
| Labels | `labs`, `ggtitle`, `xlab`, `ylab` | done | Reflection |
| Save | `.save()` on `GG` | done | `ggsave` via backend |
| Utilities | `annotate`, `borders`, `lims` | done | Reflection |

*Full export list: `src/ggplotpy/generated/ggplot2_reflected.pyi` (643 symbols).*

---

## Ergonomic core (hand-written)

| Component | Module | Status |
|-----------|--------|--------|
| `GG` + `+` | `core/gg.py` | done |
| `aes()` | `core/aes.py` | done |
| `R()` | `core/raw.py` | done |
| Errors / `last_r_code()` | `core/errors.py` | done |
| Jupyter repr + `display()` | `core/gg.py`, `display.py` | done |
| patchwork `\|` `/` on `GG` | `core/gg.py`, `core/patchwork.py` | done |
| `from_plot()` | `core/patchwork.py` | done |
| `to_r()` | `core/gg.py` | done |
| `set_options()` | `core/_options.py` | done |
| gganimate shim | `core/animate.py` | done |

---

## Infrastructure

| Component | Status |
|-----------|--------|
| `backend/inprocess.py` | done |
| `backend/subprocess.py` | stub (v1.0) |
| `backend/rserve.py` | stub (v1.0) |
| `data/pandas_bridge.py` | done |
| `data/arrow.py` | done |
| `data/sf_bridge.py` | stub (v1.0) |
| `runtime/bootstrap.py` + `ggplotpy-bootstrap` | done |
| `runtime/check_setup.py` | done |
| `runtime/install_r()` | not_started (v1.0) |
| `codegen/*` | done |
| `generated/ggplot2_reflected.pyi` | done (643 exports) |
| `ext/` lazy reflection | done |
| `r-helper/ggplotpy` | done |

---

## Blessed extensions (v0.5+)

| Package | Key symbols | Status | Tests |
|---------|-------------|--------|-------|
| ggrepel | `geom_text_repel`, … | done (reflection) | optional skip |
| patchwork | `\|`, `/`, `from_plot` | done (shim + reflection) | T1 when installed |
| gganimate | `transition_states`, `animate()` | done (shim) | optional skip |
| ggthemes | `theme_*` | done (reflection) | optional |
| ggpubr | geoms/stats | done (reflection) | optional |
| sf | `geom_sf` | stub (v1.0) | `needs_sf` skip |

---

## Documentation (packaging & platform)

| Doc | Path | Status | Notes |
|-----|------|--------|-------|
| Getting started | `docs/getting-started.md` | done | conda-first, bootstrap, first plot |
| Quickstart | `docs/guides/quickstart.md` | done | facets, patchwork, animate |
| Installation matrix | `docs/guides/installation.md` | done | conda vs pip vs Docker |
| Troubleshooting | `docs/guides/troubleshooting.md` | done | tier runners, OOM |
| Google Colab | `docs/guides/colab.md` | done | system R + `display()` |
| Databricks | `docs/guides/databricks.md` | done | Arrow + `display()` |
| Sphinx user site | `docs/` + furo | done | engineering docs excluded |
| Phase 8 perf | `exploration/perf/` | in_progress | `benchmark_ingress.py` stub |

---

## Update protocol

When a symbol moves to `done`, update this table + `STATUS.md` in the same PR.
