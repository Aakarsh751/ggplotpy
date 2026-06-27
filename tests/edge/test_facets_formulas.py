"""Case 3 — facet_wrap and facet_grid formula strings (T1)."""

from __future__ import annotations

import os

import pytest

from tests.edge.conftest import make_synthetic_df

pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(
        os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
        reason="GGPLOTPY_SKIP_INTEGRATION=1",
    ),
]


def test_facet_wrap_formula_string(synthetic_df):
    from ggplotpy import aes, facet_wrap, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(synthetic_df)
    p = (
        ggplot(data)
        + aes(x="x", y="y", color="group")
        + geom_point()
        + facet_wrap("~ group")
    )
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100


def test_facet_grid_formula_string(synthetic_df):
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r
    from ggplotpy.generated import load_ggplot2_symbol

    facet_grid = load_ggplot2_symbol("facet_grid")
    data = pandas_to_r(synthetic_df)
    p = (
        ggplot(data)
        + aes(x="x", y="y")
        + geom_point()
        + facet_grid("facet_row ~ group")
    )
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100
