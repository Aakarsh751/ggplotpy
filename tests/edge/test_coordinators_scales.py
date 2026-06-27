"""Case 4 — scales, themes, and coords on synthetic data (T1)."""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(
        os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
        reason="GGPLOTPY_SKIP_INTEGRATION=1",
    ),
]


def test_scale_theme_coord_smoke(synthetic_df):
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r
    from ggplotpy.generated import load_ggplot2_symbol

    scale_color_manual = load_ggplot2_symbol("scale_color_manual")
    theme_void = load_ggplot2_symbol("theme_void")
    coord_flip = load_ggplot2_symbol("coord_flip")

    data = pandas_to_r(synthetic_df)
    p = (
        ggplot(data)
        + aes(x="x", y="y", color="group")
        + geom_point()
        + scale_color_manual(values=["#E41A1C", "#377EB8", "#4DAF4A"])
        + theme_void()
        + coord_flip()
    )
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 50
