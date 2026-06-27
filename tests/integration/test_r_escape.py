"""T1 R() escape hatch smoke."""

import pytest

pytestmark = pytest.mark.needs_ggplot2


def test_r_annotate_layer(mtcars_df):
    from ggplotpy import R, aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    p = (
        ggplot(data)
        + aes(x="wt", y="mpg")
        + geom_point()
        + R('annotate("text", x=3, y=30, label="hi")')
    )
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100
