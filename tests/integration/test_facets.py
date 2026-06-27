"""T1 facet_wrap smoke."""

import pytest

pytestmark = pytest.mark.needs_ggplot2


def test_facet_wrap_smoke(mtcars_df):
    from ggplotpy import aes, facet_wrap, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    p = ggplot(data) + aes(x="wt", y="mpg") + geom_point() + facet_wrap("~ cyl")
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100
