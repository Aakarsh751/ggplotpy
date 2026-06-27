# Google Colab guide

Google Colab runtimes ship with **system R** pre-installed. ggplotpy uses that R via rpy2 once ggplot2 and the ggplotpy R helper are installed.

## Setup

Run in a Colab cell:

```python
# %% [markdown]
# Run each section in order (Colab supports ! shell lines in code cells)

# 1. Install Python deps (PyPI when published; dev: pip install git+...)
# !pip install -q ggplotpy

# 2. Install R packages into Colab's system R
import rpy2.robjects as ro
ro.r('install.packages(c("ggplot2", "rlang", "svglite"), repos="https://cloud.r-project.org")')

# 3. Clone repo and install ggplotpy R helper (until the wheel bundles it)
# !git clone -q --depth 1 https://github.com/Aakarsh751/ggplotpy.git /tmp/ggplotpy-repo
ro.r('install.packages("/tmp/ggplotpy-repo/r-helper/ggplotpy", repos=NULL, type="source")')

# 4. Verify
from ggplotpy import check_setup
check_setup(profile="core")
```

Or run shell lines separately:

```bash
pip install -q ggplotpy
git clone -q --depth 1 https://github.com/Aakarsh751/ggplotpy.git /tmp/ggplotpy-repo
```

Colab's R lives under `/usr/lib/R` — rpy2 usually discovers it without setting `R_HOME`. If import fails:

```python
import os
os.environ["R_HOME"] = "/usr/lib/R"
```

For extension demos, also install `patchwork` / `ggrepel` in R and run `check_setup(profile="examples")`.

## First plot in Colab

Star-import style:

```python
import pandas as pd
from ggplotpy import *

mtcars = pd.read_csv(
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mtcars.csv"
)
p = ggplot(mtcars) + aes(x="wt", y="mpg", color="factor(cyl)") + geom_point()
p  # displays SVG in cell output
```

If the cell output is empty, use explicit display:

```python
from ggplotpy import display
display(p)
```

## Limitations

- Colab R version may lag CRAN; pin ggplot2 if parity tests fail.
- Extension packages (ggrepel, patchwork, gganimate, gifski) require extra `install.packages()` calls.
- Session resets wipe R library installs — re-run setup cells each session.
- `ggplotpy-bootstrap` is not available in Colab unless you install from source; manual R `install.packages()` above is the practical path.

For local development, see [Getting started](../getting-started.md) and [Quickstart](quickstart.md).
