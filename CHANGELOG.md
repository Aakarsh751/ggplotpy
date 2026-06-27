# Changelog

All notable changes to **ggplotpy** are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

Supported **ggplot2** versions: 3.5.x+ (CI pins 3.5.2 and 4.0.0).

---

## [0.1.0] — Unreleased

### Added (0.1.0)

- **Layer-level `aes()`** — `geom_*(aes(...))` / `mapping=` now work (deferred objects emit R source)
- **Python kwargs → R dotted params** — `na_rm`→`na.rm`, `legend_position`→`legend.position` (ADR D-P011)
- **Any data in `ggplot()`** — pandas, `dict`, list-of-records, NumPy, Series, pyarrow, polars, GeoPandas
- **Spatial** — `geom_sf` from a GeoPandas `GeoDataFrame` (GeoPackage → R `sf`); `ggplotpy[geo]` extra (ADR D-P013)
- **Crash-isolated rendering** — `GG.save(isolated=True)` / `render_isolated()` via a child `Rscript` (ADR D-P013)
- **Non-interactive embedded R** — optional-package prompts can't deadlock the session (ADR D-P012)
- **`install_r()`** — cross-OS R-package provisioning (CRAN binaries on Win/macOS); `ggplotpy-bootstrap --profile all`
- **Sequence/dict arg values** — tuples/lists → `c(...)`, dict → `list(k=v)`, NumPy arrays/scalars handled
- **Comprehensive docs** — 22-figure gallery on real external data (penguins, gapminder) incl. sf choropleth, hexbin, ggrepel, ggdist, ridgeline, and a gganimate **animated GIF**; data-conversions guide
- **Release machinery** — dynamic version, PyPI Trusted-Publishing workflow, conda-forge recipe, `RELEASING.md`; R helper bundled in the wheel
- **Coverage** — 113-layer render sweep (0 skips); validation cases 13b–17

## [0.0.1.dev0]

### Added

- **Hybrid G architecture** — hand-written core + reflection codegen + rpy2 in-process backend
- **`ggplot`, `aes`, `+`, `R()`, `to_r()`, `.save()`** — faithful ggplot2 grammar from Python
- **643 ggplot2 exports** — lazy `ggplotpy.__getattr__` + `load_ggplot2_symbol()` + committed `ggplot2_reflected.pyi`
- **14 star-import core** — common geoms, facets, themes, guides in `ggplotpy.__all__`
- **NSE bridge** — `aes(x="log(wt)")` via `r-helper/ggplotpy` and `rlang::parse_expr`
- **Jupyter rendering** — `_repr_svg_`, `_repr_png_`, `_repr_mimebundle_`; `display()` for Databricks
- **`set_options()`** — global figure size, dpi, svg/png format
- **`check_setup()`** and **`ggplotpy-bootstrap`** CLI — R/ggplot2 verification and CRAN helper install
- **Error translation** — `GgplotpyRError` + `last_r_code()` for debuggable R failures
- **Data plane** — pandas ingress; Arrow/polars zero-copy path (v0.5)
- **Extensions** — `ggplotpy.ext.*` lazy reflection; patchwork `|` `/` on `GG`; gganimate `animate()` → GIF
- **Tiered test suite** — T0 unit, tier1 integration/parity/gallery/extensions, tier2 edge matrix, tier3 notebooks
- **15-geom render smoke** — common geoms in `test_geoms_smoke.py` (not full 643 namespace)
- **5 SVG visual baselines** — hash regression in `test_visual_baseline.py`
- **Strict T2 parity** — normalized full-script golden compare for `to_r()`
- **Gallery notebooks** — `01_mvp_mtcars`, `02_extensions_demo`, `03_synthetic_gallery` + nbclient CI
- **Sphinx user site** — furo theme, getting-started + guides (conda, Colab, Databricks)
- **CI** — ubuntu/windows/macos T0; ggplot2 3.5 + 4.0 pin job; codegen staleness
- **Packaging skeleton** — `environment.yml`, `Dockerfile`, `conda/recipe/meta.yaml`
- Phase 0 governance — `project_memory/`, engineering docs, Cursor rules, ADRs D-P001–D-P010

### Not yet shipped (v1.0)

- PyPI / conda-forge published wheels
- `install_r()` auto-provisioning on first import
- sf / GeoArrow ingress; Rserve/subprocess backends
- Rd → docstrings wired into codegen emit
- Full T3 gallery (10+ plot baselines)

[0.1.0]: https://github.com/Aakarsh751/ggplotpy/releases/tag/ggplotpy-v0.1.0
[0.0.1.dev0]: https://github.com/Aakarsh751/ggplotpy/compare/v0.0.0...HEAD
