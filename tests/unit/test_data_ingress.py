"""T0 — data ingress helpers (R-free where possible)."""

from __future__ import annotations

import pytest


def test_arrow_to_r_requires_pyarrow():
    pytest.importorskip("pyarrow", reason="pyarrow not installed")
    import pyarrow as pa

    from ggplotpy.data.arrow import arrow_to_r

    with pytest.raises(TypeError, match="Expected pyarrow"):
        arrow_to_r([1, 2, 3])

    table = pa.table({"x": [1, 2], "y": [3, 4]})
    assert table.num_rows == 2


def test_polars_to_r_requires_polars():
    pytest.importorskip("polars", reason="polars not installed")
    import polars as pl

    from ggplotpy.data.polars_bridge import polars_to_r

    with pytest.raises(TypeError, match="Expected polars"):
        polars_to_r({"a": 1})

    df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    assert df.height == 2
    assert hasattr(df, "to_arrow")


def test_data_lazy_exports():
    from ggplotpy import data

    assert data.pandas_to_r is not None
    assert callable(data.__getattr__("arrow_to_r"))
    assert callable(data.__getattr__("polars_to_r"))


def test_ext_private_attr_raises():
    import ggplotpy.ext as ext

    with pytest.raises(AttributeError):
        _ = ext._missing_private
