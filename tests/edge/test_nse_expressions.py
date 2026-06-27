"""Case 2 — NSE aes expression matrix (T0 goldens + T1 render)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ggplotpy.core.aes_util import format_aes_r_fragment
from tests.edge.conftest import make_synthetic_df

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "aes"


def test_nse_log_wt_golden():
    fragment = format_aes_r_fragment({"x": "log(wt)", "y": "y"})
    expected = (GOLDEN / "nse_log_wt.txt").read_text(encoding="utf-8").strip()
    assert fragment == expected


def test_nse_factor_cyl_golden():
    fragment = format_aes_r_fragment({"x": "x", "y": "y", "color": "factor(cyl)"})
    expected = (GOLDEN / "nse_factor_cyl.txt").read_text(encoding="utf-8").strip()
    assert fragment == expected


def test_nse_data_odd_col_golden():
    fragment = format_aes_r_fragment({"x": '.data[["weird-col"]]', "y": "y"})
    expected = (GOLDEN / "nse_data_odd_col.txt").read_text(encoding="utf-8").strip()
    assert fragment == expected


def test_nse_multi_aes_golden():
    fragment = format_aes_r_fragment({"x": "log(wt)", "y": "mpg", "color": "factor(cyl)"})
    expected = (GOLDEN / "nse_multi_aes.txt").read_text(encoding="utf-8").strip()
    assert fragment == expected


@pytest.mark.parametrize(
    "kwargs",
    [
        {"x": "log(wt)", "y": "y"},
        {"x": "x", "y": "y", "color": "factor(cyl)"},
        {"x": '.data[["weird-col"]]', "y": "y"},
    ],
    ids=["log_wt", "factor_cyl", "data_odd_col"],
)
@pytest.mark.needs_ggplot2
@pytest.mark.skipif(
    os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1",
    reason="GGPLOTPY_SKIP_INTEGRATION=1",
)
def test_nse_expressions_render_svg(kwargs):
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    df = make_synthetic_df(n=80, seed=7)
    data = pandas_to_r(df)
    p = ggplot(data) + aes(**kwargs) + geom_point()
    svg = p._repr_svg_()
    assert isinstance(svg, str) and len(svg) > 100
    assert "<svg" in svg.lower()
