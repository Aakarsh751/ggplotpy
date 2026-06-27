# API reference

Reference for **ggplotpy** v0.0.1.dev0. Narrative guides: [Getting started](../getting-started.md), [Quickstart](../guides/quickstart.md).

## Top-level (`ggplotpy`)

| Symbol | Role |
|--------|------|
| `ggplot` / `GG` | Build plots; `+` composition; `\|` `/` patchwork; `to_r()`, `.save()`, Jupyter repr |
| `aes` | Pythonic `aes(x="col")` → R NSE via `r-helper/ggplotpy` |
| `R` | Escape hatch — arbitrary R ggplot2 fragments |
| `check_setup` | One-screen R/ggplot2/extension report |
| `display` | Explicit IPython/Databricks display |
| `last_r_code` | Last R line executed (debug after `GgplotpyRError`) |
| `set_options` | Global figure size, dpi, svg/png format |
| `_GGLOT2_CORE` (14 names) | Star-import exports: `geom_point`, `geom_smooth`, `facet_*`, `labs`, themes, etc. |

**643 ggplot2 exports** resolve lazily:

```python
import ggplotpy
ggplotpy.geom_bar          # __getattr__ → load_ggplot2_symbol
```

Star-import does **not** bind all 643 names — use attribute access or namespaced imports.

## Core modules

| Module | Role |
|--------|------|
| `ggplotpy.core.gg` | `GG`, `ggplot()`, render + save pipeline |
| `ggplotpy.core.aes` | NSE bridge |
| `ggplotpy.core.raw` | `R()`, `RObject` |
| `ggplotpy.core.errors` | `GgplotpyRError`, `last_r_code()` |
| `ggplotpy.core.patchwork` | `PlotComposition`, `from_plot()` |
| `ggplotpy.core.animate` | `transition_states()`, `animate()` → GIF bytes |
| `ggplotpy.core.defer` | Deferred R call formatting for layers |
| `ggplotpy.display` | Notebook `display()` helper |

## Codegen (`ggplotpy.codegen`)

Build-time introspection of installed R packages:

| Module | Role |
|--------|------|
| `ggplotpy.codegen.reflect` | `list_namespace_exports()`, `get_symbol_formals()`, `reflect_export()`, `build_r_callable()` |
| `ggplotpy.codegen.emit` | `emit_pyi_stub()`, `emit_pyi_module()`, `formals_to_signature()` |

Reflection uses `getNamespaceExports()` and R `formals()` via the in-process backend. Tests clear caches via `clear_reflect_cache()`.

## Generated ggplot2 (`ggplotpy.generated`)

| Artifact | Role |
|----------|------|
| `ggplot2_reflected.pyi` | **643-export** typing stub (regenerated from R) |
| `load_ggplot2_symbol(name)` | Runtime lazy callable cache per export name |

```python
from ggplotpy.generated import load_ggplot2_symbol

geom_point = load_ggplot2_symbol("geom_point")
```

CI staleness job fails when introspection drifts from committed `.pyi`.

## Extensions (`ggplotpy.ext`)

Lazy `__getattr__` reflection for installed R packages:

```python
from ggplotpy.ext import ggrepel, patchwork

ggrepel.geom_text_repel(...)
```

Known extensions: `ggrepel`, `patchwork`, `gganimate`, `ggthemes`, `ggpubr`, `ggdist`, `survminer`, `ggtree`.

`list_installed_extensions()` returns which are present in the current R library.

## Data plane

| Module | Role |
|--------|------|
| `ggplotpy.data.pandas_bridge` | pandas → R (pandas2ri) |
| `ggplotpy.data.arrow` | Arrow / Polars → R (zero-copy path) |

## Runtime

| Module | Role |
|--------|------|
| `ggplotpy.runtime.check_setup` | Environment verification |
| `ggplotpy.runtime.bootstrap` | `ggplotpy-bootstrap` CLI |

## Regenerating stubs

```bash
python scripts/generate_stubs.py
```

Requires R with **ggplot2** installed. Use `--skip-if-no-r` to no-op when R is absent. Default emits full namespace (643 symbols).

## Test coverage honesty

| Surface | Verification |
|---------|----------------|
| 643 callable exports | T0 codegen + lazy resolution tests |
| 15 common geoms | T1 render smoke (`tests/integration/test_geoms_smoke.py`) |
| NSE / facets / scales | T1 + T2 edge matrix |
| Extensions | Optional T1 smoke (skip if package missing) |

Not every geom/stat/scale is individually render-tested — reflection + spot smoke is the v0.1 contract.

## Status

- **v0.1** — reflection codegen, 643 `.pyi`, strict T2 `to_r()` parity, Sphinx furo site
- **v0.5** — Arrow ingress, `ggplotpy.ext`, patchwork, gganimate
- **Next (v1.0)** — Rd injected docstrings, full autodoc pages, sf/GeoArrow
