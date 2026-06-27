# User Interface

API specification from `RESEARCH_AND_PLAN.md` Phase 4. **Implementation status as of v0.1/v0.5 (2026-06-21).**

---

## Import styles

| Style | Example | Status |
|-------|---------|--------|
| **Star-import (primary)** | `from ggplotpy import *` | **Implemented** — 14 curated exports in `__all__` |
| Namespaced | `import ggplotpy as gg; gg.ggplot(df)` | **Implemented** |
| Lazy ggplot2 export | `ggplotpy.geom_bar` or `load_ggplot2_symbol("geom_bar")` | **Implemented** — 643 exports via `__getattr__` |
| Extension lazy | `from ggplotpy.ext import ggrepel` or `ggplotpy.ext.ggrepel.geom_text_repel` | **Implemented** (v0.5) |

---

## Basic plot

```python
from ggplotpy import *
import pandas as pd

df = pd.read_csv("mtcars.csv")

p = (ggplot(df)
     + aes(x="wt", y="mpg", color="factor(cyl)")
     + geom_point(size=2)
     + geom_smooth(method="lm")
     + theme_minimal())

p                      # auto-renders SVG in Jupyter
p.save("out.png", width=6, height=4, dpi=300)
print(p.to_r())        # idiomatic R script
```

| API | Status |
|-----|--------|
| `ggplot(data)` + pandas ingress | **Implemented** |
| `+` layer composition | **Implemented** |
| `.save()` / `ggsave` path | **Implemented** |
| `to_r()` | **Implemented** — layered script with normalized formatting |

---

## Aesthetics (NSE via strings)

```python
aes(x="wt", y="mpg")                    # column names
aes("wt", "mpg")                        # positional → x, y
aes(x="log(wt)", color="factor(cyl)")   # expressions
```

Layer-level mappings work like ggplot2 — pass `aes()` to any layer (positional or
`mapping=`), including expressions that contain commas:

```python
geom_point(aes(color="factor(cyl)"))
geom_text(aes(label="paste(name, cyl)"))
```

Python sequences map to R vectors, so tuple/list arguments work:
`coord_cartesian(xlim=(0, 6))`, `scale_color_manual(values=["red", "blue"])`.

See `docs/nse_bridge.md`. Golden matrix in `tests/golden/aes/`.

---

## Faceting

```python
p + facet_wrap("~ cyl")
p + facet_grid("gear ~ cyl")
```

**Implemented** — formula strings on synthetic and mtcars data (T1 + edge tests).

---

## Scales and guides

```python
p + scale_color_brewer(palette="Set1") + guides(color=guide_legend(ncol=2))
```

**Implemented** via reflection + hand-listed star-import names.

---

## Extensions (automatic when installed)

```python
from ggplotpy.ext import ggrepel, patchwork
from ggplotpy.core.animate import animate, transition_states

p2 = p + ggrepel.geom_text_repel(aes(label="name"))
dashboard = p1 | p2              # patchwork on GG (direct | and /)
# dashboard = from_plot(p1) | from_plot(p2)  # explicit PlotComposition

anim_plot = p + transition_states(states="year")
gif_bytes = animate(anim_plot, fps=10)   # module function, not p.animate()
```

| Feature | Status |
|---------|--------|
| `ggplotpy.ext.*` reflection | **Implemented** |
| patchwork `\|` `/` on `GG` | **Implemented** — returns `PlotComposition` |
| `from_plot()` wrapper | **Implemented** — optional explicit composition |
| gganimate `transition_states` | **Implemented** — deferred R layer |
| `animate(plot, ...)` → GIF bytes | **Implemented** — requires gganimate + gifski |

---

## Escape hatch and transparency

```python
p + R('annotate("text", x=3, y=20, label="hi")')
print(p.to_r())
```

After errors: `last_r_code()` shows the failing R line. **Implemented** — `GgplotpyRError` with R message translation.

---

## Jupyter / notebook

| Hook | Behavior | Status |
|------|----------|--------|
| `_repr_svg_` | Default — crisp vector | **Implemented** |
| `_repr_png_` | Retina raster fallback | **Implemented** |
| `_repr_mimebundle_` | Frontend picks best | **Implemented** |
| `display(p)` | IPython publish (Databricks) | **Implemented** |
| `set_options(figure_size, dpi, format)` | Global defaults | **Implemented** |

---

## Developer experience

| Feature | Status |
|---------|--------|
| `.pyi` stubs (643 exports) | **Implemented** — `ggplot2_reflected.pyi` |
| Rd → docstrings | **Stub** — M1 extract + M2 render scripts; not wired into emit |
| `help(geom_point)` R passthrough | **Planned** (stretch) |
| Errors: R message + line | **Implemented** |

---

## Data inputs

All non-`sf` inputs are accepted by `ggplot(data)` directly — `_coerce_data()`
routes every common Python container to R automatically; rpy2 objects pass through.

| Type | Path | Status |
|------|------|--------|
| pandas DataFrame / Series | `data/pandas_bridge.py` | **Implemented** — `ggplot(df)` default |
| `dict` of columns / list-of-record `dict`s | `core/gg.py` `_coerce_data` | **Implemented** — via pandas |
| numpy array (1-D → `V1`; 2-D → `V1..Vn`) | `core/gg.py` `_coerce_data` | **Implemented** |
| pyarrow Table / RecordBatch | `data/arrow.py` | **Implemented** (v0.5) — `ggplot(table)` direct |
| polars DataFrame | `data/polars_bridge.py` | **Implemented** (v0.5) — via Arrow |
| sf / GeoArrow | `data/sf_bridge.py` | **Stub** (v1.0) |

datetime, categorical (→ factor), and NaN/NA columns convert via pandas2ri.
Python scalars, numpy scalars/arrays, `range`, `list`/`tuple` (→ `c(...)`), and
`dict` (→ `list(k=v)`) are all valid argument values (e.g. `scale_x_continuous(breaks=np.arange(5))`).

---

## Non-goals

No `.add_scatter()` method API. No plotnine backend. See `AGENTS.md`.
