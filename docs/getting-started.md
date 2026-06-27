# Getting started with ggplotpy

ggplotpy exposes **real ggplot2** from Python via rpy2 — same `+` grammar, exact R parity.

## Install (conda recommended)

**Conda-forge** is the primary install path: it pulls `r-base`, `r-ggplot2`, and binary **rpy2** together (see [Installation guide](guides/installation.md)).

```bash
git clone https://github.com/Aakarsh751/ggplotpy.git
cd ggplotpy
conda env create -f environment.yml
conda activate ggplotpy
ggplotpy-bootstrap --profile core
```

When ggplotpy is published to conda-forge:

```bash
conda install -c conda-forge ggplotpy
ggplotpy-bootstrap --profile core
```

### pip + bootstrap (alternative)

If you already have R 4.x with dev headers (or use rig/miniforge provisioning):

```bash
pip install -e ".[dev,arrow]"
ggplotpy-bootstrap --profile core
```

`ggplotpy-bootstrap` installs missing CRAN packages and the local `r-helper/ggplotpy` R companion. Opt-in `install_r()` auto-provisioning is planned for v1.0 — use the CLI today.

### Windows note

Set `R_HOME` and put R's `bin\x64` on `PATH` when using a standalone R install:

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
```

Conda `r-base` on Windows avoids most rpy2 ABI friction — prefer conda when possible.

## Install the R packages from Python

If you have R but not the ggplot2 stack yet, provision it in one call — binaries on
Windows/macOS, no compiler needed:

```python
import ggplotpy

ggplotpy.install_r()         # ggplot2, rlang, svglite + ggplotpy helper
ggplotpy.install_r("all")    # + ggrepel, patchwork, gganimate, sf, ggthemes, ggdist, ggpubr
```

## Verify setup

```python
from ggplotpy import check_setup

check_setup()                    # core: ggplot2, rlang, svglite, ggplotpy helper
check_setup(profile="examples")  # + ggrepel, patchwork for extension demos
```

Or from the shell:

```bash
ggplotpy-bootstrap --profile core    # or --profile all
```

## First plot

Star-import (recommended in docs and gallery):

```python
from ggplotpy import *
import pandas as pd

mtcars = pd.read_csv(
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mtcars.csv"
)

p = ggplot(mtcars) + aes(x="wt", y="mpg", color="factor(cyl)") + geom_point()
p.save("mtcars.png")
```

`ggplot()` accepts pandas DataFrames directly — and also `dict`s, NumPy arrays,
Arrow tables, polars, and GeoPandas. See [Data conversions](guides/data-conversions.md).
Browse the [Gallery](gallery.md) for 20 worked examples on real datasets.

In Jupyter, `p` renders as SVG by default (`_repr_svg_`). On Databricks or when auto-display fails, use `display(p)` — see [Quickstart](guides/quickstart.md#jupyter).

## Escape hatch

Use `R("...")` for arbitrary R expressions when you prefer raw ggplot2 code:

```python
from ggplotpy import R

p = p + R('annotate("text", x=3, y=20, label="from R")')
print(p.to_r())
```

## Extensions

Installed R extension packages are available via lazy reflection on `ggplotpy.ext`:

```python
from ggplotpy.ext import ggrepel, patchwork

p2 = p + ggrepel.geom_text_repel(aes(label="name"))
dashboard = p | p2   # patchwork when installed (see Quickstart)
```

Known extensions: `ggrepel`, `patchwork`, `gganimate`, `ggthemes`, `ggpubr`, `ggdist`, `survminer`, `ggtree`.

## Platform guides

- [Installation matrix](guides/installation.md) — conda vs pip vs Docker
- [Quickstart](guides/quickstart.md) — facets, save, animate, lazy exports
- [Gallery](gallery.md) — 20 figures on real-world data
- [Data conversions](guides/data-conversions.md) — pandas, dict, NumPy, Arrow, polars, GeoPandas
- [Troubleshooting](guides/troubleshooting.md) — R_HOME, OOM, tier runners
- [Google Colab](guides/colab.md)
- [Databricks](guides/databricks.md)

## Next steps

- [API reference](api/index.md) — core modules, 643-export reflection, `ggplotpy.ext`
- User interface spec, architecture, testing guide — [engineering docs on GitHub](https://github.com/Aakarsh751/ggplotpy/tree/main/docs) (excluded from this site)
