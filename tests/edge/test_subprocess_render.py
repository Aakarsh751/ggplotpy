"""Isolated subprocess rendering (crash-safe render path)."""

from __future__ import annotations

import os

import pandas as pd
import pytest

_SKIP_INT = os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"
pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(_SKIP_INT, reason="GGPLOTPY_SKIP_INTEGRATION=1"),
]

_DF = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [2.0, 1.0, 4.0, 3.0], "g": ["a", "b", "a", "b"]})


def _plot():
    import ggplotpy
    from ggplotpy import aes, ggplot

    return ggplot(_DF) + aes(x="x", y="y", color="g") + ggplotpy.geom_point()


def test_render_isolated_png_returns_bytes():
    data = _plot().render_isolated(device="png")
    assert isinstance(data, (bytes, bytearray)) and len(data) > 100
    assert data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic


def test_render_isolated_svg_returns_text():
    svg = _plot().render_isolated(device="svg")
    assert isinstance(svg, str) and "<svg" in svg.lower()


def test_save_isolated_writes_file(tmp_path):
    out = tmp_path / "iso.png"
    _plot().save(str(out), isolated=True)
    assert out.exists() and out.stat().st_size > 100
