"""Python → R data ingress matrix (RESEARCH_AND_PLAN Phase 2.2).

Confirms every common Python data container is accepted by ``ggplot(data)`` and
renders. Complements `test_data_ingress_edge.py` (which pre-converts manually).
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

_SKIP_INT = os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"
pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(_SKIP_INT, reason="GGPLOTPY_SKIP_INTEGRATION=1"),
]


def _render(data, x, y, **aes_extra):
    from ggplotpy import aes, geom_point, ggplot

    p = ggplot(data) + aes(x=x, y=y, **aes_extra) + geom_point(na_rm=True)
    svg = p._repr_svg_()
    assert isinstance(svg, str) and "<svg" in svg.lower()
    return svg


def test_dict_of_lists():
    _render({"x": [1, 2, 3], "y": [4, 5, 6]}, "x", "y")


def test_dict_of_ndarrays():
    _render({"x": np.arange(5), "y": np.arange(5) ** 2}, "x", "y")


def test_list_of_record_dicts():
    rows = [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 5, "y": 6}]
    _render(rows, "x", "y")


def test_pandas_series():
    s = pd.Series([1, 2, 3, 4], name="V1")
    from ggplotpy import aes, geom_point, ggplot

    p = ggplot(s) + aes(x="V1", y="V1") + geom_point()
    assert "<svg" in p._repr_svg_().lower()


def test_numpy_2d_array_default_colnames():
    arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    _render(arr, "V1", "V2")


def test_numpy_1d_array():
    from ggplotpy import aes, geom_point, ggplot

    p = ggplot(np.array([1.0, 2.0, 3.0])) + aes(x="V1", y="V1") + geom_point()
    assert "<svg" in p._repr_svg_().lower()


def test_datetime_column():
    df = pd.DataFrame(
        {"t": pd.date_range("2020-01-01", periods=6, freq="D"), "y": [1, 2, 3, 4, 5, 6]}
    )
    _render(df, "t", "y")


def test_categorical_column_maps_to_factor():
    df = pd.DataFrame({"x": [1, 2, 3, 4], "g": pd.Categorical(["a", "b", "a", "b"])})
    _render(df, "x", "x", color="g")


def test_nan_values_with_na_rm():
    df = pd.DataFrame({"x": [1.0, np.nan, 3.0], "y": [1.0, 2.0, 3.0]})
    _render(df, "x", "y")


def test_3d_array_rejected_clearly():
    from ggplotpy import ggplot

    with pytest.raises(ValueError, match="3-D numpy array|2-D array"):
        ggplot(np.zeros((2, 2, 2)))


@pytest.mark.needs_arrow
def test_pyarrow_recordbatch():
    import pyarrow as pa

    batch = pa.RecordBatch.from_pydict({"x": [1, 2, 3], "y": [4, 5, 6]})
    _render(batch, "x", "y")


@pytest.mark.needs_sf
def test_geopandas_geodataframe_renders_geom_sf():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import Point

    import ggplotpy
    from ggplotpy import ggplot

    gdf = gpd.GeoDataFrame(
        {"name": ["a", "b", "c"], "geometry": [Point(0, 0), Point(1, 1), Point(2, 0)]},
        crs="EPSG:4326",
    )
    p = ggplot(gdf) + ggplotpy.geom_sf()
    svg = p._repr_svg_()
    assert isinstance(svg, str) and "<svg" in svg.lower()
