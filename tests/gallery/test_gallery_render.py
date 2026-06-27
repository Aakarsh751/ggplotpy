"""Gallery render smoke."""

import pytest

pytestmark = [pytest.mark.needs_ggplot2, pytest.mark.visual]


def test_gallery_mtcars_render(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    p = ggplot(data) + aes(x="wt", y="mpg", color="factor(cyl)") + geom_point() + theme_minimal()
    png = p._repr_png_()
    assert isinstance(png, bytes)
    assert len(png) > 500
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
