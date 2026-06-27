# STATUS.md - ggplotpy progress dashboard

**Updated:** 2026-06-22  
**Current milestone:** **v0.1** and **v0.5** gates met locally; **v1.0** platform work remains  
**Latest session:** parity fixes + full data-conversion coverage + non-interactive R; sf spatial ingress, isolated subprocess rendering; installed all optional R/Python pkgs → **113-layer sweep with 0 skips**; `install_r()` cross-OS provisioning; **22-figure gallery** incl. sf choropleth/hexbin/ggrepel (Sphinx -W clean, no `{contents}` warning) (2026-06-22)

## Active blockers

None — see [project_memory/blockers.md](project_memory/blockers.md).

---

## Release milestones

| Release | Target | Status | Exit doc |
|---------|--------|--------|----------|
| **M0** | Week 0 | **complete** | `docs/quality_gates.md` § M0 |
| **MVP** | Weeks 1–6 | **complete** | § MVP |
| **v0.1** | Weeks 6–12 | **complete** (local gates) | § v0.1 |
| **v0.5** | Months 3–6 | **mostly complete** | § v0.5 |
| **v1.0** | Months 6–12 | **in progress** | § v1.0 |

### M0 – scaffold

- [x] Phase 0 governance docs + memory system
- [x] Engineering docs skeleton
- [x] Cursor rules + ggplotpy-dev skill
- [x] `pyproject.toml` + package skeleton (hatchling)
- [x] `tests/` layout + T0 smoke
- [x] CI: ubuntu + windows workflows
- [x] R-helper package skeleton (`r-helper/ggplotpy/`)

### MVP – first Jupyter plot identical to R

- [x] rpy2 in-process backend (robstatm patterns)
- [x] `ggplot`, `aes`, `+`, core geoms/scales/themes (hand list + reflection)
- [x] `_repr_svg_`, `.save()`, `R()` escape hatch
- [x] pandas ingress; T0 unit green
- [x] `notebooks/01_mvp_mtcars.ipynb`
- [x] T1 integration green (`scripts/run_tests.ps1` tier1)
- [x] T2 parity + CI integration job stable

### v0.1 – full reflection + typing

- [x] Codegen → `generated/` + `.pyi` (**643-export** full `ggplot2_reflected.pyi`)
- [x] Rd → docstrings pipeline (M1 stub)
- [x] CI: 2+ OS; ggplot2 3.5.x + 4.0.x pin job
- [x] T2 parity suite — **strict** normalized golden compare
- [x] Codegen staleness CI
- [x] Sphinx user site skeleton
- [x] `ggplotpy.__getattr__` resolves **any** ggplot2 export (e.g. `ggplotpy.geom_bar`)

### v0.5 – ecosystem + packaging

- [x] Arrow zero-copy ingress
- [x] `ggplotpy.ext.*` runtime reflection
- [x] patchwork operators
- [x] gganimate wrapper
- [x] `install_r()` cross-OS provisioning; **conda-forge recipe release-ready** (submit after first PyPI release)
- [ ] 4-OS CI
- [x] extension + synthetic gallery notebooks (**tier3** nbclient: 01–03)
- [x] Rd → markdown stub (M2)
- [x] Colab + Databricks guides (polished; not full v1.0 cluster automation)

### v1.0 – stable platform (remainder)

- [x] sf spatial ingress — GeoPandas→sf via GeoPackage (`pip install ggplotpy[geo]` + R `sf`); GeoArrow zero-copy still open
- [x] Isolated **subprocess rendering** (`GG.save(isolated=True)` / `render_isolated`); full IPC backend + Rserve still open
- [x] T3 visual regression gallery (**5 SVG hash baselines**)
- [ ] Full static typing / `py.typed` coverage for generated surface
- [ ] ggplot2 4.0 parity sign-off across OS matrix
- [x] Extension render smoke now runs locally (ggrepel/gganimate/gifski/sf/hexbin/ggdist/ggridges installed)
- [x] PyPI release machinery — dynamic version, `python -m build` (twine-clean), Trusted-Publishing workflow, R helper in wheel

---

## Component status

| Component | Status |
|-----------|--------|
| Governance / memory | done |
| Ergonomic core (`core/`) | done (+ animate, patchwork on GG) |
| Backend (`backend/`) | in-process done; Rserve/subprocess v1.0 |
| Data plane (`data/`) | pandas + arrow/polars; sf stub |
| Runtime bootstrap (`runtime/`) | done |
| Codegen (`codegen/`, `generated/`) | **643-export** namespace + lazy `__getattr__` |
| Extensions (`ext/`) | lazy reflection |
| R helper (`r-helper/ggplotpy/`) | done |
| Tests T0–T3 | see table below |
| CI matrix | ubuntu + windows + macos (4-OS open) |
| User docs (Sphinx) | furo site — guides + getting-started synced (2026-06-21) |
| UX (Phase 4 polish) | done |

---

## Tests & CI

| Tier | Scope | Last verify (R 4.5.2, Windows, 2026-06-22) |
|------|--------|--------------------------------|
| **T0** | `tests/unit` | **64 passed**, 1 skipped (polars) |
| **T1** | integration + parity + gallery (12 files/subprocess) | **12/12 files** green (category coverage 30/30) |
| **T2** | `tests/edge` (9 files/subprocess) | **9/9 files** green (layer-aes, data conversions, non-interactive R, subprocess render) |
| **T3** | `tests/gallery/test_visual_baseline.py` | **5 SVG baselines** |
| **Notebooks** | `tests/notebooks` (tier3; `GGPLOTPY_SKIP_NOTEBOOKS=1` in tier0–2 runner) | **3/3** notebooks execute |
| **Coverage sweep** | `scripts/verify_ggplot_coverage.py` | **113 layers OK, 0 skip, 0 fail** (incl. geom_sf/sf_label/sf_text/map/hex) |

**Commands:** `scripts/run_tests.ps1 -Tier tier0|tier1|tier2|tier3|all` (bash runner now mirrors all tiers)

**CI:** integration job runs tier1 **and tier2** (edge matrix was previously not CI-gated).

**Data ingress:** `ggplot(data)` accepts pandas / dict / list-of-records / numpy / Series / pyarrow / polars / GeoPandas (sf).

**Docs:** Sphinx furo site builds `-W` clean; **25-asset [gallery](docs/gallery.md)** on real external data (penguins, gapminder) + ggplot2 datasets — incl. sf choropleth, hexbin, ggrepel, **ggdist**, **ridgeline**, and a **gganimate animated GIF**; [data-conversions guide](docs/guides/data-conversions.md). Regenerate: `python docs/scripts/build_gallery.py`.

**Release:** `python -m build` → `ggplotpy-0.1.0` (twine-clean); tag `ggplotpy-v*` publishes via [`publish.yml`](.github/workflows/publish.yml) Trusted Publishing; conda recipe + [`RELEASING.md`](RELEASING.md) ready. See `ggplotpy.install_r("all")` for R provisioning.

**Supported ggplot2:** 3.5.x+ (CI pins 3.5.2 + 4.0.0 on ubuntu)

---
