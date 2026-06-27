"""Case 2b/4b — layer-level aes, sequence kwargs, and direct ingress (render).

Regression coverage for the 2026-06-22 audit: these paths were previously broken
yet the suite was green because every other test pre-converted data and only used
top-level ``+ aes(...)``.
"""

from __future__ import annotations

import os

import pytest

from tests.edge.conftest import make_synthetic_df

_SKIP_INT = os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"
pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(_SKIP_INT, reason="GGPLOTPY_SKIP_INTEGRATION=1"),
]


def _svg(p) -> str:
    svg = p._repr_svg_()
    assert isinstance(svg, str) and "<svg" in svg.lower()
    return svg


def test_layer_level_aes_positional():
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=60)
    p = ggplot(df) + aes(x="x", y="y") + geom_point(aes(color="group"))
    _svg(p)


def test_layer_level_aes_mapping_kwarg():
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=60)
    p = ggplot(df) + aes(x="x", y="y") + geom_point(mapping=aes(color="group"))
    _svg(p)


def test_geom_text_aes_label_with_comma_expression():
    import ggplotpy
    from ggplotpy import aes, ggplot

    df = make_synthetic_df(n=20)
    p = ggplot(df) + aes(x="x", y="y") + ggplotpy.geom_text(aes(label="paste(group, cyl)"))
    _svg(p)


def test_coord_cartesian_tuple_limits():
    import ggplotpy
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=40)
    p = (
        ggplot(df)
        + aes(x="x", y="y")
        + geom_point()
        + ggplotpy.coord_cartesian(xlim=(-2, 2), ylim=(-2, 2))
    )
    _svg(p)


def test_scale_color_manual_list_values():
    import ggplotpy
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=40)
    p = (
        ggplot(df)
        + aes(x="x", y="y", color="group")
        + geom_point()
        + ggplotpy.scale_color_manual(values=["red", "green", "blue"])
    )
    _svg(p)


def test_direct_pandas_ingress_no_manual_conversion():
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=30)
    p = ggplot(df) + aes(x="x", y="y") + geom_point()
    _svg(p)


def test_aes_positional_render():
    from ggplotpy import geom_point, ggplot
    from ggplotpy.core.aes import aes

    df = make_synthetic_df(n=30)
    p = ggplot(df) + aes("x", "y") + geom_point()
    _svg(p)


def test_to_r_with_layer_aes_is_valid_structure():
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=10)
    p = ggplot(df) + aes(x="x", y="y") + geom_point(aes(color="group"))
    code = p.to_r()
    assert "geom_point(aes(color = group))" in code
    assert "aes_from_strings" not in code
    assert "= ," not in code


def test_dotted_params_reach_r():
    """na.rm / legend.position must be reachable via Python underscores (D-P011)."""
    import ggplotpy
    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=30)
    df.loc[df.index[:3], "x"] = float("nan")
    p = (
        ggplot(df)
        + aes(x="x", y="y")
        + geom_point(na_rm=True)
        + ggplotpy.theme(legend_position="bottom")
    )
    _svg(p)


@pytest.mark.needs_arrow
def test_direct_arrow_ingress():
    import pyarrow as pa

    from ggplotpy import aes, geom_point, ggplot

    df = make_synthetic_df(n=30)
    table = pa.Table.from_pandas(df)
    p = ggplot(table) + aes(x="x", y="y") + geom_point()
    _svg(p)
