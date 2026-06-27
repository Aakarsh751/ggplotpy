"""T1 basic render smoke."""

import pytest

pytestmark = pytest.mark.needs_ggplot2


def test_mtcars_scatter_renders_svg(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    p = ggplot(data) + aes(x="wt", y="mpg") + geom_point()
    svg = p._repr_svg_()
    assert isinstance(svg, str)
    assert len(svg) > 100
    assert "<svg" in svg.lower()
