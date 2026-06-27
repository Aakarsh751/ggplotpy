# Architecture — Hybrid G

Locked per **D-P001** and `RESEARCH_AND_PLAN.md` Phase 3. Divergence requires ADR before merge.

## Layer diagram

```
┌──────────────────────────────────────────────────────────────────┐
│  USER:  ggplot(df) + aes(x="wt", y="mpg") + geom_point() ...     │
├──────────────────────────────────────────────────────────────────┤
│  ERGONOMIC CORE (hand-written)                                     │
│   GG + __add__    aes() NSE bridge    patchwork | / on GG         │
│   repr_png/svg    R() escape          error translation           │
│   to_r()          animate() shim      display()                   │
├──────────────────────────────────────────────────────────────────┤
│  REFLECTION + CODEGEN + generated .pyi (643 ggplot2 exports)       │
│   inspect R namespaces → Python callables + stubs + docstrings     │
├──────────────────────────────────────────────────────────────────┤
│  DATA PLANE              │  BACKEND ABSTRACTION                    │
│   Arrow (zero-copy)      │  InProcess(rpy2) [default]            │
│   pandas2ri fallback     │  Rserve / subprocess [v1.0 optional]  │
├──────────────────────────────────────────────────────────────────┤
│  R RUNTIME: ggplot2 + extensions + r-helper/ggplotpy                   │
├──────────────────────────────────────────────────────────────────┤
│  RUNTIME BOOTSTRAP: ggplotpy-bootstrap, check_setup()                  │
└──────────────────────────────────────────────────────────────────┘
```

## Module boundaries

| Path | Responsibility | May import |
|------|----------------|------------|
| `core/` | `GG`, `aes`, `+`, patchwork ops, Jupyter repr, `to_r()`, errors, animate shim | `backend`, `data` (interfaces) |
| `backend/` | rpy2 session, lazy `importr`, R calls, device render | rpy2 only here (+ `runtime` for paths) |
| `data/` | pandas / Arrow / polars → R frame | `backend` for conversion hooks |
| `runtime/` | `check_setup()`, `ggplotpy-bootstrap`, R discovery | OS, subprocess; no ggplot API |
| `codegen/` | Namespace introspection, Rd→md, emit `.py`/`.pyi` | R via `backend` at codegen time |
| `generated/` | Committed ggplot2 wrappers + `.pyi` (CI staleness check) | `backend`, `core` types |
| `ext/` | Lazy `__getattr__` for arbitrary installed packages | `backend`, `codegen` reflect |
| `r-helper/ggplotpy/` | R: `aes_from_strings`, render helpers | (R package, not Python) |

**Rule:** No `importr("ggplot2")` outside `backend/`. User code never touches rpy2 directly.

## Object model

- **`GG`**: wraps R ggplot object; supports `+` (append layers), `|`, `/` (patchwork when installed).
- **`PlotComposition`**: patchwork result; supports `|`, `/`, `.save()`, Jupyter repr.
- **Layer-like returns**: generated `geom_*`, `scale_*`, etc. return composable proxies supporting `+`.
- **Rendering**: `print(plot)` → R graphics device → bytes/string → `_repr_svg_` / `_repr_png_` / `.save()`.

## Data ingress (Phase 2.2)

1. **Preferred (v0.5):** pyarrow/polars → Arrow C-Data Interface → zero-copy R tibble.
2. **Default MVP:** pandas → `pandas2ri` (copy; categoricals → factors).
3. Plot output is small; optimize **ingress** only.

## NSE (Phase 2.4)

Python `aes(x="log(wt)")` → R `ggplotpy:::aes_from_strings(...)` → `rlang::parse_expr` → `ggplot2::aes()`. See `docs/nse_bridge.md`.

## Extension strategy (Phase 2.5)

| Path | When |
|------|------|
| `ggplotpy.ext.<pkg>.<fn>` | Most CRAN extensions — runtime reflection |
| Hand shims | patchwork operators, gganimate `animate()`, sf (v1.0) |

## Backends

| Backend | When | Module |
|---------|------|--------|
| In-process rpy2 | Default interactive/notebook | `backend/inprocess.py` |
| Subprocess Rscript | Isolation experiments | `backend/subprocess.py` (v1.0) |
| Rserve | Multi-tenant / remote | `backend/rserve.py` (v1.0) |

## Tiered testing (verification)

Operational runners: `scripts/run_tests.ps1` (see `testing_guide.md`).

| Runner tier | Directories | Purpose |
|-------------|-------------|---------|
| **tier0** | `tests/unit` | R-free API, aes goldens, codegen emit |
| **tier1** | `integration/`, `parity/`, `gallery/`, `extensions/` | Render smoke, `to_r()` parity, 5 SVG baselines, extension skips |
| **tier2** | `tests/edge/` | 13-case matrix edge coverage (NSE, facets, ingress) |
| **tier3** | `tests/notebooks/` | Execute gallery notebooks 01–03 |

Semantic mapping to validation cases: `validation_strategy.md` §13-case matrix.

## Anti-patterns (prohibited)

- plotnine/matplotlib GoG engine
- Method-call API (`.add_scatter()`)
- Hand-maintaining every ggplot2 export without reflection
- Vendored R in wheels (v1) without legal review

## Reference

Sibling patterns: `robstatm-py/src/robstatm_py/_r.py` (lazy R, Windows DLL, render→bytes).
