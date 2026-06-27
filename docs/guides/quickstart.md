# Quickstart

Copy-paste examples aligned with the user interface spec ([engineering doc on GitHub](https://github.com/Aakarsh751/ggplotpy/blob/main/docs/user_interface.md)).

## Star import (primary)

```python
from ggplotpy import *
import pandas as pd

df = pd.read_csv("mtcars.csv")

p = (ggplot(df)
     + aes(x="wt", y="mpg", color="factor(cyl)")
     + geom_point(size=2)
     + geom_smooth(method="lm")
     + theme_minimal())

p
```

Namespaced style is always supported:

```python
import ggplotpy as gg

p = gg.ggplot(df) + gg.aes(x="wt", y="mpg") + gg.geom_point()
```

## Lazy ggplot2 exports (643 symbols)

Star-import exposes 14 curated ggplot2 names in `__all__`. Every other export (e.g. `geom_bar`, `scale_x_log10`) resolves lazily:

```python
import ggplotpy

p = ggplotpy.ggplot(df) + ggplotpy.aes(x="cyl") + ggplotpy.geom_bar()
# or after: from ggplotpy.generated import load_ggplot2_symbol
geom_bar = load_ggplot2_symbol("geom_bar")
```

IDE stubs: `src/ggplotpy/generated/ggplot2_reflected.pyi` (643 functions).

## Check your environment

```python
from ggplotpy import check_setup

check_setup()                    # core: ggplot2, rlang, svglite, ggplotpy helper
check_setup(profile="examples")  # + ggrepel, patchwork for extension demos
```

## Aes expressions (NSE)

Column names and R expressions pass as Python strings:

```python
from ggplotpy import *

p = (ggplot(df)
     + aes(x="log(wt)", y="mpg", color="factor(cyl)")
     + geom_point())
```

NSE details: [nse_bridge.md on GitHub](https://github.com/Aakarsh751/ggplotpy/blob/main/docs/nse_bridge.md).

Positional aesthetics work like ggplot2 (`aes(wt, mpg)` → `x`, `y`):

```python
p = ggplot(df) + aes("wt", "mpg") + geom_point()
```

## Layer-level aesthetics

Pass `aes(...)` directly to any layer for per-geom mappings — exactly as in R.
Both the positional `mapping` and `mapping=` keyword forms work:

```python
from ggplotpy import *

p = (ggplot(df)
     + aes(x="wt", y="mpg")
     + geom_point(aes(color="factor(cyl)"))          # layer-specific color
     + geom_text(aes(label="paste(name, cyl)")))      # commas in expressions are safe
```

Python sequences become R vectors, so range/limit arguments accept tuples and lists:

```python
p = (ggplot(df) + aes(x="wt", y="mpg") + geom_point()
     + coord_cartesian(xlim=(0, 6), ylim=(10, 35))
     + scale_color_manual(values=["red", "green", "blue"]))
```

`print(p.to_r())` renders these as idiomatic R (`aes(color = factor(cyl))`,
`c(0, 6)`), so the emitted script is copy-paste runnable.

## Data inputs (pandas, dict, numpy, Arrow, polars)

`ggplot()` accepts any common Python container directly — no manual conversion:

```python
import pandas as pd, numpy as np, pyarrow as pa

ggplot(pd.read_csv("mtcars.csv")) + aes("wt", "mpg") + geom_point()
ggplot({"x": [1, 2, 3], "y": [4, 5, 6]}) + aes("x", "y") + geom_point()   # dict of columns
ggplot([{"x": 1, "y": 2}, {"x": 3, "y": 4}]) + aes("x", "y") + geom_point()  # records
ggplot(np.array([[1, 2], [3, 4]])) + aes("V1", "V2") + geom_point()      # 2-D array → V1..Vn
ggplot(pa.Table.from_pandas(df)) + aes("wt", "mpg") + geom_point()       # Arrow path
# ggplot(polars_df) + ...                                                # polars → Arrow → R
```

datetime, categorical (→ factor), and NaN columns are handled automatically.
Numpy scalars/arrays, `range`, lists/tuples, and dicts are valid argument values too
(e.g. `scale_x_continuous(breaks=np.arange(0, 6))`).

## Faceting

```python
from ggplotpy import *

p = ggplot(df) + aes(x="wt", y="mpg") + geom_point()
p + facet_wrap("~ cyl")
p + facet_grid("gear ~ cyl")
```

## Extensions (when installed)

```python
from ggplotpy import *
from ggplotpy.ext import ggrepel, patchwork

p2 = p + ggrepel.geom_text_repel(aes(label="name"))
```

### patchwork composition

`GG` supports patchwork `|` and `/` directly when the R **patchwork** package is installed:

```python
from ggplotpy import *

p1 = ggplot(df) + aes(x="wt", y="mpg") + geom_point()
p2 = ggplot(df) + aes(x="hp", y="mpg") + geom_point() + theme_minimal()

dashboard = p1 | p2          # side by side
stacked = p1 / p2            # vertical stack
```

For explicit wrapping (e.g. mixing `PlotComposition` with new plots):

```python
from ggplotpy.core.patchwork import from_plot

comp = from_plot(p1) | from_plot(p2)
```

## gganimate

Requires R packages **gganimate** and **gifski**:

```python
from ggplotpy import *
from ggplotpy.core.animate import animate, transition_states

df["year"] = [1970 + (i % 4) for i in range(len(df))]

anim_plot = (
    ggplot(df)
    + aes(x="wt", y="mpg", color="factor(cyl)")
    + geom_point()
    + transition_states(states="year")
)

gif_bytes = animate(anim_plot, fps=10, width=480, height=480)
with open("out.gif", "wb") as f:
    f.write(gif_bytes)
```

## R() escape hatch

```python
from ggplotpy import *

p = ggplot(df) + aes(x="wt", y="mpg") + geom_point()
p = p + R('annotate("text", x=3, y=20, label="from R")')
print(p.to_r())
```

## Save to file

```python
p.save("out.png", width=6, height=4, dpi=300)
p.save("out.svg")
```

### Crash-isolated rendering

For pathological plots (or untrusted input) render in a fresh R subprocess, so an
R crash can't take down your Python process:

```python
p.save("out.png", isolated=True)        # renders via a child Rscript
png_bytes = p.render_isolated(device="png")
```

Global defaults:

```python
from ggplotpy import set_options

set_options(figure_size=(8, 5), dpi=144, format="svg")
```

## Jupyter

Plots auto-render via `_repr_svg_` when a cell ends with `p`:

```python
from ggplotpy import *

p = ggplot(df) + aes(x="wt", y="mpg") + geom_point()
p
```

Explicit display (Databricks / IPython):

```python
from ggplotpy import display

display(p)
```

## Debug R errors

```python
from ggplotpy import last_r_code
from ggplotpy.core.errors import GgplotpyRError

try:
    p + aes(x="not_a_column")
except GgplotpyRError as e:
    print(e)           # R message + offending line
    print(last_r_code())
```

## Next steps

- [Installation](installation.md)
- [Troubleshooting](troubleshooting.md)
- [Colab](colab.md) · [Databricks](databricks.md)
- [API reference](../api/index.md)
