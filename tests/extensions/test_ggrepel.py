"""Extension smoke — ggrepel label repulsion."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.needs_ggplot2, pytest.mark.needs_ggrepel]


def test_ggrepel_geom_text_repel_import():
    import ggplotpy.ext as ext

    ggrepel = ext.ggrepel
    assert hasattr(ggrepel, "geom_text_repel")


def test_ggrepel_geom_text_repel_render(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot, theme_minimal
    import ggplotpy.ext as ext

    df = mtcars_df.copy()
    if "name" not in df.columns:
        df["name"] = [f"row{i}" for i in range(len(df))]

    p = (
        ggplot(df)
        + aes(x="wt", y="mpg", label="name")
        + geom_point()
        + ext.ggrepel.geom_text_repel()
        + theme_minimal()
    )
    svg = p._repr_svg_()
    assert isinstance(svg, str)
    assert len(svg) > 500
    assert "<svg" in svg.lower()
