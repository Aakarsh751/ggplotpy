# Implementation Plan

Derived from `RESEARCH_AND_PLAN.md` Phase 10. Update `STATUS.md` checkboxes as tasks complete.

## Timeline overview

```
M0 (wk 0) → MVP (wk 1–6) → v0.1 (wk 6–12) → v0.5 (mo 3–6) → v1.0 (mo 6–12)
```

Solo estimate: MVP ~6 wk; v0.5 ~6 mo; v1.0 ~9–12 mo.

---

## M0 — Repository scaffold (week 0)

| Task | Deliverable |
|------|-------------|
| Package metadata | `pyproject.toml` (hatchling; rpy2; extras: arrow, polars, dev, docs) |
| Python stubs | `src/ggplotpy/` layout per `architecture.md` |
| R helper skeleton | `r-helper/ggplotpy/` (DESCRIPTION, NAMESPACE, `R/aes.R` stub) |
| Test scaffold | `tests/unit`, `integration`, `golden/`, `conftest.py`, markers |
| CI | `ci.yml` (ubuntu T0), `docs.yml` (Sphinx R-free) |
| Exploration | `exploration/README.md` |

**Exit:** `pip install -e ".[dev]"`; T0 smoke green; `import ggplotpy` cheap; governance done.

---

## MVP — weeks 1–6

Research phases: **4** (API), **7** (Jupyter partial), **10** MVP row.

| Week | Focus |
|------|-------|
| 1–2 | `backend/inprocess.py`; lazy ggplot2; Windows R_HOME |
| 2–3 | `r-helper` `aes_from_strings`; `core/aes.py`, `core/gg.py`, `+` |
| 3–4 | Core geoms/scales/themes (reflection seed or hand-pilot); pandas ingress |
| 4–5 | `_repr_svg_`, `.save()`, `R()`, error translation, `last_r_code()` |
| 5–6 | T0 aes goldens; T1 mtcars; T2 first `to_r()`; `notebooks/01_mvp_mtcars.ipynb` |

**Exit:** Notebook SVG; `check_setup()` OK; verification cases 1–7; T0+T1+T2 core on ubuntu+windows.

---

## v0.1 — weeks 6–12

Research phases: **5** (codegen), **9** (OSS/CI), **10** v0.1.

| Focus | Deliverable |
|-------|-------------|
| Full reflection | `generated/` + `.pyi` for all ggplot2 exports |
| Docs pipeline | Rd extract → JSON → docstrings (robstatm pattern) |
| CI expansion | 2+ OS; ggplot2 **3.5.x + 4.0.x** |
| User docs | Sphinx skeleton (furo); getting-started |
| Parity | T2 suite for core plots |

**Exit:** All ggplot2 exports callable; autocomplete; codegen staleness CI; T2 green.

---

## v0.5 — months 3–6

Research phases: **6** (packaging), **8** (perf), **10** v0.5.

| Focus | Deliverable |
|-------|-------------|
| Arrow ingress | `data/arrow.py`; cache frame across `+` |
| Extensions | `ggplotpy.ext.*`; patchwork `/`|`; gganimate render |
| Blessed ext tests | ggrepel, ggthemes, ggpubr smoke |
| Packaging | `install_r()`, conda recipe, Docker |
| CI | 4-OS × R 4.3/4.4 × py 3.10–3.13 |
| Perf | `exploration/perf/` pandas vs Arrow |

**Exit:** conda/pip bootstrap documented; extension notebooks; Arrow perf documented.

---

## v1.0 — months 6–12

Research phases: **2.5** (sf), **7** (HTML), **10** v1.0, **11** mitigations.

| Focus | Deliverable |
|-------|-------------|
| Spatial | sf / GeoArrow data path |
| Backends | Rserve/subprocess optional |
| Interactive | girafe/ggplotly → HTML repr |
| Quality | T3 visual gallery; full typing |
| Guides | Colab, Databricks install docs |

**Exit:** Full CI matrix; T3 baselines; platform guides; Phase 11 risks mitigated.

---

## Task ID convention

Use `STATUS.md` component + milestone: e.g. `M0-pyproject`, `MVP-aes`, `v01-codegen`.
