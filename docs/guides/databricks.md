# Databricks guide

Databricks notebooks run on cluster workers. ggplotpy needs R + ggplot2 on each worker (or an optional Rserve backend in v1.0).

## Components

1. **Cluster init script** — conda or apt R + `ggplot2`, `svglite`, `rlang`, and `r-helper/ggplotpy`.
2. **Arrow ingress** — export Spark DataFrames via `ggplotpy.data.arrow` for zero-copy handoff to R (v0.5 path).
3. **Notebook display** — `ggplotpy.display(p)` publishes SVG/PNG mime bundles (same render path as `_repr_svg_`).
4. **Optional Rserve backend** — isolated R workers for multi-tenant clusters (see `backend/rserve.py` stub — v1.0).

## `ggplotpy.display()`

Databricks notebook frontends do not always auto-call `_repr_svg_`. Use explicit display:

```python
from ggplotpy import display, ggplot, aes, geom_point

p = ggplot(df) + aes(x="wt", y="mpg") + geom_point()
display(p)  # publishes SVG/PNG mime bundle
```

Uses the same render path as `_repr_mimebundle_`. Requires IPython on the kernel.

Global format:

```python
from ggplotpy import set_options
set_options(format="png")  # if SVG rendering fails on the cluster
display(p)
```

## Init script sketch

Use the repo [Dockerfile](../../Dockerfile) as a reference image, or an init script equivalent to:

```bash
conda env create -f /dbfs/path/to/environment.yml
conda activate ggplotpy
ggplotpy-bootstrap --profile core
```

Install the wheel on the driver; ensure workers share the same R library path or use cluster-scoped init scripts.

**v1.0:** documented Colab/Databricks init automation and PyPI wheel — today follow manual bootstrap above.

## Arrow ingress (Spark)

When `pyarrow` is available:

```python
import pyarrow as pa
from ggplotpy.data.arrow import arrow_to_r
from ggplotpy import ggplot, aes, geom_point

# table = spark_df.toArrow()  # or pa.table(...)
r_df = arrow_to_r(table)
p = ggplot(r_df) + aes(x="col_a", y="col_b") + geom_point()
display(p)
```

## Local development

Develop and test locally with conda — see [Getting started](../getting-started.md), [Installation](installation.md), and [Troubleshooting](troubleshooting.md).
