"""T2 to_r golden parity."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ggplotpy.core.to_r_util import normalize_r_code

_marks: list = [pytest.mark.needs_ggplot2, pytest.mark.parity]
if os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1":
    _marks.insert(0, pytest.mark.skip(reason="GGPLOTPY_SKIP_INTEGRATION=1"))
pytestmark = _marks

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "to_r" / "mtcars_scatter.r"


def test_to_r_mtcars_scatter_structure(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    p = ggplot(data) + aes(x="wt", y="mpg") + geom_point()
    script = normalize_r_code(p.to_r())
    golden = normalize_r_code(GOLDEN.read_text(encoding="utf-8"))
    assert script == golden, (
        "to_r() script differs from golden; update tests/golden/to_r/mtcars_scatter.r intentionally"
    )
