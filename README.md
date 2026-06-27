# ggplotpy

Python interface to **real ggplot2** — not a reimplementation.

**ggplotpy** drives R's ggplot2 (and extensions like ggrepel, patchwork, gganimate) from Python via rpy2, with a faithful `ggplot(df) + geom_point()` grammar, Pythonic aesthetics (`aes(x="wt", y="mpg")`), Jupyter rendering, and auto-generated wrappers for **643** ggplot2 exports.

## Positioning

| Use ggplotpy when… | Use plotnine when… |
|----------------|-------------------|
| You need R extensions (ggtree, survminer, sf geoms) | You want pip-only, no R |
| Exact parity with R colleagues matters | ggplot-like syntax is enough |
| Mixed R/Python pipelines share figures | Pure Python portability |

Full feasibility study and 12-phase engineering plan: **[RESEARCH_AND_PLAN.md](RESEARCH_AND_PLAN.md)**.

## 60-second quickstart

**1. Install** (conda recommended — bundles R + rpy2):

```bash
conda env create -f environment.yml
conda activate ggplotpy
ggplotpy-bootstrap --profile core
```

When ggplotpy is published to conda-forge:

```bash
conda install -c conda-forge ggplotpy
ggplotpy-bootstrap --profile core
```

**2. Verify:**

```python
from ggplotpy import check_setup
check_setup()   # one-screen report; should end with "Result: READY"
```

**3. Plot** (star-import is the default in docs and gallery):

```python
from ggplotpy import *
import pandas as pd

df = pd.read_csv("mtcars.csv")

p = (ggplot(df)
     + aes(x="wt", y="mpg", color="factor(cyl)")
     + geom_point(size=2)
     + theme_minimal())

p                      # SVG in Jupyter
p.save("out.png", width=6, height=4, dpi=300)
print(p.to_r())        # readable R script for trust/debug
```

**Lazy exports:** symbols not in star-import (e.g. `geom_bar`) resolve on attribute access:

```python
import ggplotpy
p = ggplotpy.ggplot(df) + ggplotpy.aes(x="cat") + ggplotpy.geom_bar()
```

**Escape hatch:** `p + R('annotate("text", x=3, y=20, label="hi")')`

**After errors:** `last_r_code()` shows the failing R line.

## Guides

| Guide | Topic |
|-------|--------|
| [Getting started](docs/getting-started.md) | conda env, bootstrap, first plot |
| [Quickstart](docs/guides/quickstart.md) | facets, extensions, patchwork, Jupyter |
| [Installation](docs/guides/installation.md) | conda / pip / Docker matrix |
| [Troubleshooting](docs/guides/troubleshooting.md) | R_HOME, OOM, `last_r_code()` |
| [Colab](docs/guides/colab.md) · [Databricks](docs/guides/databricks.md) | cloud notebooks |

## Development status

See **[STATUS.md](STATUS.md)** — **v0.1 complete** (643-export reflection, strict T2 parity, Sphinx furo); **v0.5 mostly complete** (Arrow, `ggplotpy.ext`, patchwork, gganimate, tier3 notebooks); **v1.0** (PyPI/conda publish, sf, Rserve) remains.

Agent/contributor orientation: **[AGENTS.md](AGENTS.md)**.

## Testing (contributors)

Verification uses four **runner tiers** via `scripts/run_tests.ps1`:

| Tier | Scope | R required? |
|------|--------|-------------|
| **tier0** | `tests/unit` — API, aes goldens, codegen | No |
| **tier1** | integration, parity, gallery, extensions (one subprocess per file) | Yes |
| **tier2** | `tests/edge` — NSE matrix, facets, ingress edge cases | Yes |
| **tier3** | `tests/notebooks` — execute notebooks 01–03 | Yes |

```powershell
.\scripts\run_tests.ps1 -Tier tier0   # fast loop; sets GGPLOTPY_SKIP_NOTEBOOKS=1
.\scripts\run_tests.ps1 -Tier all     # full gate locally
```

**Honest coverage:** 15 common geoms have T1 render smoke; all **643** ggplot2 exports are callable via reflection — not individually render-tested. Details: [docs/testing_guide.md](docs/testing_guide.md), [docs/validation_strategy.md](docs/validation_strategy.md).

## License

Apache-2.0 — see [LICENSE](LICENSE). R and ggplot2 are separate GPL components provisioned by the user or conda.
