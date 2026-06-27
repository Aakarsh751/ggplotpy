"""Embedded R must be non-interactive so optional-package prompts can't hang.

ggplot2/rlang call check_installed() for optional packages (hexbin for geom_hex,
etc.) which otherwise prompts on stdin and deadlocks an embedded session.
"""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.needs_r,
    pytest.mark.skipif(
        os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1", reason="GGPLOTPY_SKIP_INTEGRATION=1"
    ),
]


def test_rlang_interactive_is_false():
    from ggplotpy.backend.inprocess import r

    ro = r()
    assert bool(ro.r("isFALSE(getOption('rlang_interactive'))")[0])


def test_missing_optional_pkg_does_not_hang():
    """geom_hex without hexbin must degrade gracefully (warn + render), never
    block on an install prompt. In non-interactive mode ggplot2 turns the prompt
    into a non-fatal warning, so the plot still renders without the hex layer."""
    import pandas as pd

    import ggplotpy
    from ggplotpy import aes, ggplot
    from ggplotpy.backend.inprocess import r

    ro = r()
    if bool(ro.r('isTRUE(requireNamespace("hexbin", quietly=TRUE))')[0]):
        pytest.skip("hexbin installed; cannot test the missing-package path")

    df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [2.0, 1.0, 4.0, 3.0]})
    p = ggplot(df) + aes(x="x", y="y") + ggplotpy.geom_hex()
    svg = p._repr_svg_()  # returns instead of deadlocking on a stdin prompt
    assert isinstance(svg, str) and "<svg" in svg.lower()
