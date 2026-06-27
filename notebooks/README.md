# Gallery notebooks

End-to-end examples executed by **tier3** CI (`tests/notebooks/test_notebooks.py`).

## Notebooks

| Notebook | Topic | Requires |
|----------|-------|----------|
| [01_mvp_mtcars.ipynb](01_mvp_mtcars.ipynb) | MVP scatter — star-import, save, `to_r()` | ggplot2 |
| [02_extensions_demo.ipynb](02_extensions_demo.ipynb) | ggrepel, patchwork composition | ggrepel, patchwork (optional cells may skip) |
| [03_synthetic_gallery.ipynb](03_synthetic_gallery.ipynb) | Multi-geom synthetic gallery | ggplot2 |

## How to run locally

**Prerequisites:** conda env from `environment.yml`, `ggplotpy-bootstrap --profile core`, Jupyter or nbconvert.

```bash
conda activate ggplotpy
jupyter notebook notebooks/01_mvp_mtcars.ipynb
```

Or execute headless (same as CI):

```bash
pytest tests/notebooks/test_notebooks.py -q
```

Skip during fast dev loops:

```powershell
$env:GGPLOTPY_SKIP_NOTEBOOKS = "1"
pytest tests/unit -q
```

Full gate including notebooks:

```powershell
.\scripts\run_tests.ps1 -Tier tier3
# or
.\scripts\run_tests.ps1 -Tier all
```

## CI (tier3)

- Runner: `scripts/run_tests.ps1 -Tier tier3`
- Engine: nbclient, 600s timeout per notebook
- Skipped when `GGPLOTPY_SKIP_NOTEBOOKS=1` (tier0–tier2 runner sets this)

## Related docs

- [Quickstart](../docs/guides/quickstart.md) — copy-paste equivalents
- [Getting started](../docs/getting-started.md) — install + first plot
- [testing_guide.md](../docs/testing_guide.md) — tier0–tier3 overview
