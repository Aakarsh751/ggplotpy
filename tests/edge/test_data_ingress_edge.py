"""Cases 8–9 — data ingress edge types and moderate-size frames (T0 + T1)."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from tests.edge.conftest import make_synthetic_df

_LARGE_N = 5000


def test_pandas_categorical_dtype_roundtrip_t0():
    df = make_synthetic_df(n=50)
    df["group"] = df["group"].astype("category")
    assert str(df["group"].dtype) == "category"


@pytest.mark.needs_ggplot2
@pytest.mark.skipif(
    os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
    reason="GGPLOTPY_SKIP_INTEGRATION=1",
)
def test_pandas_categorical_renders():
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    df = make_synthetic_df(n=80)
    df["group"] = df["group"].astype("category")
    data = pandas_to_r(df)
    p = ggplot(data) + aes(x="x", y="y", color="group") + geom_point()
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100


def test_nullable_int_column_t0():
    df = make_synthetic_df(n=30)
    df["nullable_n"] = pd.array(np.arange(30), dtype="Int64")
    assert df["nullable_n"].dtype.name == "Int64"


@pytest.mark.needs_ggplot2
@pytest.mark.skipif(
    os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
    reason="GGPLOTPY_SKIP_INTEGRATION=1",
)
def test_nullable_int_renders():
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    df = make_synthetic_df(n=60)
    df["nullable_n"] = pd.array(np.arange(60), dtype="Int64")
    data = pandas_to_r(df)
    p = ggplot(data) + aes(x="nullable_n", y="y") + geom_point()
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100


@pytest.mark.slow
@pytest.mark.needs_ggplot2
@pytest.mark.skipif(
    os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
    reason="GGPLOTPY_SKIP_INTEGRATION=1",
)
def test_large_pandas_subset_renders():
    """Case 8 smoke at 5k rows (OOM-safe; full 100k is T-X exploration)."""
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    df = make_synthetic_df(n=_LARGE_N, seed=99)
    data = pandas_to_r(df)
    p = ggplot(data) + aes(x="x", y="y") + geom_point(alpha=0.3)
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100


@pytest.mark.needs_arrow
@pytest.mark.needs_ggplot2
@pytest.mark.skipif(
    os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
    reason="GGPLOTPY_SKIP_INTEGRATION=1",
)
def test_arrow_table_ingress_renders():
    """Case 9 — Arrow path when pyarrow is installed."""
    pytest.importorskip("pyarrow")
    import pyarrow as pa

    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.arrow import arrow_to_r

    df = make_synthetic_df(n=200, seed=11)
    table = pa.Table.from_pandas(df)
    data = arrow_to_r(table)
    p = ggplot(data) + aes(x="x", y="y", color="group") + geom_point()
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100
