# Data conversions (Python → R)

`ggplot(data)` accepts essentially **any** common Python data container and converts
it to an R `data.frame` for you. You never have to call a bridge function by hand.

## What `ggplot(data)` accepts

| Python input | Converted via | Notes |
|--------------|---------------|-------|
| `pandas.DataFrame` | `pandas2ri` | the default; categoricals → factors, datetimes → `Date`/`POSIXct` |
| `pandas.Series` | `pandas2ri` | becomes a one-column frame |
| `dict` of columns | pandas | `{"x": [...], "y": [...]}` |
| list of record `dict`s | pandas | `[{"x": 1, "y": 2}, ...]` |
| `numpy.ndarray` (1-D / 2-D) | pandas | 1-D → `V1`; 2-D → `V1..Vn` |
| `pyarrow.Table` / `RecordBatch` | Arrow C-interface (zero-copy where possible) | best for large data |
| `polars.DataFrame` | polars → Arrow → R | |
| `geopandas.GeoDataFrame` | GeoPackage → `sf::st_read` | for `geom_sf` (needs `sf` in R, `pip install ggplotpy[geo]`) |
| an rpy2 object | passed through unchanged | already in R |

Column types are handled automatically:

- **datetime** columns → R dates/times (plot directly on a time axis).
- **categorical** (`pd.Categorical`) → R **factor**, preserving level order.
- **NaN / NA** → R `NA` (use `geom_*(na_rm=True)` to drop quietly).

## pandas (the default)

```python
from ggplotpy import *
import pandas as pd

df = pd.read_csv("mtcars.csv")
ggplot(df) + aes(x="wt", y="mpg") + geom_point()
```

## A plain dict

Great for quick, ad-hoc plots — no DataFrame needed:

```python
import numpy as np

(ggplot({"month": list(range(1, 13)),
         "sales": [3, 5, 4, 7, 8, 6, 9, 11, 10, 8, 7, 12]})
 + aes(x="month", y="sales")
 + geom_col(fill="#e67e22")
 + scale_x_continuous(breaks=np.arange(1, 13)))
```

![From a dict](../_static/gallery/conv_dict.png)

## NumPy arrays

A 2-D array becomes columns `V1, V2, …` (matching R's `as.data.frame` convention);
a 1-D array becomes a single `V1` column.

```python
import numpy as np

arr = np.column_stack([np.random.normal(size=200),
                       np.random.normal(size=200) * 0.5 + 1])
ggplot(arr) + aes("V1", "V2") + geom_point() + geom_density2d()
```

![From a NumPy array](../_static/gallery/conv_numpy.png)

## List of records

```python
rows = [{"x": 1, "y": 2, "g": "a"},
        {"x": 3, "y": 4, "g": "b"}]
ggplot(rows) + aes("x", "y", color="g") + geom_point()
```

## Apache Arrow (fast path for large data)

When you already have a `pyarrow.Table` (or come from DuckDB/Parquet), pass it
directly — ggplotpy uses the Arrow C-interface, which is the recommended path beyond
~100k rows.

```python
import pyarrow as pa
table = pa.Table.from_pandas(big_df)
ggplot(table) + aes("x", "y") + geom_point()      # install: pip install ggplotpy[arrow]
```

## polars

```python
import polars as pl
df = pl.read_parquet("events.parquet")             # install: pip install ggplotpy[polars]
ggplot(df) + aes("x", "y") + geom_point()          # polars → Arrow → R
```

## Spatial data (GeoPandas → sf)

`geom_sf` plots maps from a GeoPandas `GeoDataFrame`; ggplotpy round-trips it through a
GeoPackage into R's `sf`, preserving geometry type and CRS.

```python
import geopandas as gpd                              # pip install ggplotpy[geo]; install.packages("sf") in R
gdf = gpd.read_file("districts.gpkg")
ggplot(gdf) + geom_sf(aes(fill="population"))
```

If `geopandas` (Python) or `sf` (R) is missing, you get a clear, actionable error
rather than a deep failure.

## Argument values, not just data

Python values you pass as **arguments** are converted too, so ranges/limits/palettes
read naturally:

```python
coord_cartesian(xlim=(0, 6))                 # tuple  → c(0, 6)
scale_color_manual(values=["red", "blue"])   # list   → c("red", "blue")
scale_x_continuous(breaks=np.arange(0, 11))  # array  → c(0, 1, ..., 10)
geom_smooth(method_args={"family": "symmetric"})  # dict → list(family = "symmetric")
```

## Already have an R data frame?

If you pass an rpy2 object (e.g. from `R("datasets::mtcars")`), it's used as-is —
no re-conversion.

```python
mtcars = R("datasets::mtcars")
ggplot(mtcars.eval()) + aes("wt", "mpg") + geom_point()
```

---

See the [Gallery](../gallery.md) for these conversions used on real datasets, and
[Quickstart](quickstart.md) for the full plotting API.
