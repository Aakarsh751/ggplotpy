# Troubleshooting

Common ggplotpy setup and runtime issues. Run `check_setup()` first — it prints a one-screen report with install commands.

## Windows: R_HOME and PATH

rpy2 on Windows needs R's DLL directory on the search path.

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "$env:R_HOME\bin\x64;" + $env:PATH
python -c "from ggplotpy import check_setup; check_setup()"
```

Prefer **conda** (`conda env create -f environment.yml`) to avoid manual `R_HOME` wiring.

Symptoms without correct `R_HOME`:

- `R is not available` in `check_setup()`
- `Error in initEmbeddedR` or DLL load failures on import

## Missing R packages

```python
from ggplotpy import check_setup
check_setup()
```

Install core packages:

```r
install.packages(c("ggplot2", "rlang", "svglite"))
```

Install the ggplotpy R helper from a source checkout:

```r
install.packages("/path/to/Ggplot2PY/r-helper/ggplotpy", repos = NULL, type = "source")
```

Or from the shell:

```bash
ggplotpy-bootstrap --profile core
```

Extension packages (`patchwork`, `ggrepel`, `gganimate`, `gifski`) are optional — install in R when using those features.

## OOM during tests or heavy notebooks

Integration tests spawn **one subprocess per file** via `scripts/run_tests.ps1` to avoid rpy2 memory growth. For local runs:

```powershell
$env:GGPLOTPY_SKIP_NOTEBOOKS = "1"
$env:GGPLOTPY_SKIP_INTEGRATION = "1"
pytest tests/unit -q
```

Or use the tier runner (recommended):

```powershell
.\scripts\run_tests.ps1 -Tier tier0   # unit only; sets GGPLOTPY_SKIP_NOTEBOOKS=1
.\scripts\run_tests.ps1 -Tier tier1   # integration/parity/gallery/extensions
.\scripts\run_tests.ps1 -Tier tier2   # tests/edge matrix
.\scripts\run_tests.ps1 -Tier tier3   # notebook execute (01–03)
.\scripts\run_tests.ps1 -Tier all       # full local gate
```

**Do not** run `pytest tests/` in one process unless you set `GGPLOTPY_RUN_HEAVY=1` and have enough RAM.

See [testing_guide.md on GitHub](https://github.com/Aakarsh751/ggplotpy/blob/main/docs/testing_guide.md) for the OOM policy.

## R errors in plots

ggplotpy surfaces the R message and the **offending line** (no full R traceback dump):

```python
from ggplotpy import last_r_code
from ggplotpy.core.errors import GgplotpyRError

try:
    p + aes(x="not_a_column")
except GgplotpyRError as e:
    print(e)
    print("Last code:", last_r_code())
```

Inspect the equivalent R script:

```python
print(p.to_r())
```

## Jupyter: blank or missing output

1. Confirm `svglite` is installed (`check_setup()`).
2. Try PNG: `set_options(format="png")` then re-run the cell.
3. In Databricks or non-Jupyter frontends, use `from ggplotpy import display; display(p)`.

## Lazy export not found

Star-import only exposes names in `ggplotpy.__all__`. For other ggplot2 exports:

```python
import ggplotpy
ggplotpy.geom_histogram   # lazy via __getattr__
```

If R reports the symbol missing, upgrade ggplot2 in R — not every export exists in older versions.

## Still stuck?

1. `check_setup(profile="core")` — paste the full report in an issue.
2. `python -c "import rpy2; print(rpy2.__version__)"`
3. [Installation guide](installation.md) for conda vs pip paths.
4. [Getting started](../getting-started.md) for bootstrap and first plot.
