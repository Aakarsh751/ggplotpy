"""T3 visual regression — SVG hash baselines (pytest-mpl optional)."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.visual,
    pytest.mark.slow,
]

BASELINE_DIR = Path(__file__).resolve().parent / "baseline_images"


def _normalize_svg(svg: str) -> str:
    """Strip volatile svglite metadata for stable hashing."""
    svg = re.sub(r'id="[^"]*"', 'id="plot"', svg)
    svg = re.sub(r"\s+", " ", svg).strip()
    return svg


def _svg_sha256(svg: str) -> str:
    return hashlib.sha256(_normalize_svg(svg).encode("utf-8")).hexdigest()


def _assert_baseline(stem: str, svg: str) -> None:
    baseline_svg = BASELINE_DIR / f"{stem}.svg"
    baseline_sha = BASELINE_DIR / f"{stem}.svg.sha256"
    assert isinstance(svg, str) and len(svg) > 500
    digest = _svg_sha256(svg)
    if not baseline_sha.exists():
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        baseline_svg.write_text(svg, encoding="utf-8")
        baseline_sha.write_text(digest + "\n", encoding="utf-8")
        pytest.skip(f"baseline_images/{stem} seeded on first run — re-run to verify")
    expected = baseline_sha.read_text(encoding="utf-8").strip()
    assert digest == expected, (
        f"SVG hash mismatch for {stem} — intentional visual change? "
        f"Update {baseline_sha.name} after review."
    )


def _build_mtcars_scatter(mtcars_df: Any):
    from ggplotpy import aes, geom_point, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    return (
        ggplot(data)
        + aes(x="wt", y="mpg", color="factor(cyl)")
        + geom_point()
        + theme_minimal()
    )


def _build_mtcars_bar(mtcars_df: Any):
    from ggplotpy import aes, geom_bar, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    return ggplot(data) + aes(x="factor(cyl)") + geom_bar() + theme_minimal()


def _build_mtcars_histogram(mtcars_df: Any):
    from ggplotpy import aes, geom_histogram, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    return ggplot(data) + aes(x="hp") + geom_histogram(bins=10) + theme_minimal()


def _build_mtcars_facet(mtcars_df: Any):
    from ggplotpy import aes, facet_wrap, geom_point, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    return (
        ggplot(data)
        + aes(x="wt", y="mpg")
        + geom_point()
        + facet_wrap("~ cyl")
        + theme_minimal()
    )


def _build_mtcars_smooth(mtcars_df: Any):
    from ggplotpy import aes, geom_point, geom_smooth, ggplot, theme_minimal
    from ggplotpy.data.pandas_bridge import pandas_to_r

    data = pandas_to_r(mtcars_df)
    return (
        ggplot(data)
        + aes(x="wt", y="mpg")
        + geom_point()
        + geom_smooth(method="lm", se=False)
        + theme_minimal()
    )


_BASELINES: list[tuple[str, Callable[[Any], Any]]] = [
    ("mtcars_scatter", _build_mtcars_scatter),
    ("mtcars_bar", _build_mtcars_bar),
    ("mtcars_histogram", _build_mtcars_histogram),
    ("mtcars_facet", _build_mtcars_facet),
    ("mtcars_smooth", _build_mtcars_smooth),
]


@pytest.mark.parametrize("stem,builder", _BASELINES, ids=[b[0] for b in _BASELINES])
def test_visual_svg_baseline(stem: str, builder: Callable[[Any], Any], mtcars_df):
    """Compare rendered SVG hash to committed baseline (T3 gate)."""
    p = builder(mtcars_df)
    svg = p._repr_svg_()
    if stem == "mtcars_scatter":
        try:
            import pytest_mpl  # noqa: F401

            png = p._repr_png_()
            assert png[:8] == b"\x89PNG\r\n\x1a\n"
        except ImportError:
            pass
    _assert_baseline(stem, svg)
