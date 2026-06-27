"""Representative render across every ggplot2 layer category (case 13b).

A committed, CI-fast guard that each functional family — geoms, stats, scales,
coords, facets, themes, positions, guides, annotations — renders from Python.
The exhaustive 108-layer sweep lives in `scripts/verify_ggplot_coverage.py`.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

_SKIP_INT = os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"
pytestmark = [
    pytest.mark.needs_ggplot2,
    pytest.mark.skipif(_SKIP_INT, reason="GGPLOTPY_SKIP_INTEGRATION=1"),
]

_rng = np.random.default_rng(11)
_N = 50
_DF = pd.DataFrame(
    {
        "x": _rng.normal(size=_N),
        "y": _rng.normal(size=_N),
        "z": _rng.uniform(size=_N),
        "g": _rng.choice(["a", "b", "c"], size=_N),
        "g2": _rng.choice(["p", "q"], size=_N),
        "ymin": _rng.normal(size=_N) - 1,
        "ymax": _rng.normal(size=_N) + 1,
        "lab": [f"r{i}" for i in range(_N)],
    }
)
_gx, _gy = np.meshgrid(np.linspace(-2, 2, 10), np.linspace(-2, 2, 10))
_GRID = pd.DataFrame({"x": _gx.ravel(), "y": _gy.ravel(), "z": (_gx * _gy).ravel()})


def _b():
    from ggplotpy import aes, ggplot

    return ggplot(_DF) + aes(x="x", y="y")


def _cases():
    import ggplotpy
    from ggplotpy import aes, ggplot

    return {
        # geoms
        "geom_point": _b() + ggplotpy.geom_point(),
        "geom_line": _b() + ggplotpy.geom_line(),
        "geom_bar": ggplot(_DF) + aes(x="g") + ggplotpy.geom_bar(),
        "geom_col": ggplot(_DF) + aes(x="g", y="z") + ggplotpy.geom_col(),
        "geom_histogram": ggplot(_DF) + aes(x="x") + ggplotpy.geom_histogram(bins=8),
        "geom_density": ggplot(_DF) + aes(x="x") + ggplotpy.geom_density(),
        "geom_boxplot": ggplot(_DF) + aes(x="g", y="y") + ggplotpy.geom_boxplot(),
        "geom_violin": ggplot(_DF) + aes(x="g", y="y") + ggplotpy.geom_violin(),
        "geom_smooth": _b() + ggplotpy.geom_smooth(method="lm"),
        "geom_text_layer_aes": _b() + ggplotpy.geom_text(aes(label="lab")),
        "geom_tile": ggplot(_GRID) + aes(x="x", y="y") + ggplotpy.geom_tile(aes(fill="z")),
        "geom_ribbon": ggplot(_DF) + aes(x="x") + ggplotpy.geom_ribbon(aes(ymin="ymin", ymax="ymax")),
        "geom_errorbar": ggplot(_DF) + aes(x="g") + ggplotpy.geom_errorbar(aes(ymin="ymin", ymax="ymax")),
        "geom_contour": ggplot(_GRID) + aes(x="x", y="y", z="z") + ggplotpy.geom_contour(),
        # stats
        "stat_summary": ggplot(_DF) + aes(x="g", y="y") + ggplotpy.stat_summary(fun=ggplotpy.R("mean")),
        "stat_ecdf": ggplot(_DF) + aes(x="x") + ggplotpy.stat_ecdf(),
        # scales
        "scale_y_log10": ggplot(_DF) + aes(x="x", y="z") + ggplotpy.geom_point() + ggplotpy.scale_y_log10(),
        "scale_color_brewer": ggplot(_DF) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.scale_color_brewer(palette="Set1"),
        "scale_fill_viridis_c": ggplot(_GRID) + aes(x="x", y="y", fill="z") + ggplotpy.geom_raster() + ggplotpy.scale_fill_viridis_c(),
        "scale_x_continuous_tuple": _b() + ggplotpy.geom_point() + ggplotpy.scale_x_continuous(limits=(-3, 3)),
        # coords
        "coord_flip": _b() + ggplotpy.geom_point() + ggplotpy.coord_flip(),
        "coord_polar": ggplot(_DF) + aes(x="g") + ggplotpy.geom_bar() + ggplotpy.coord_polar(),
        # facets
        "facet_wrap": _b() + ggplotpy.geom_point() + ggplotpy.facet_wrap("~ g"),
        "facet_grid": _b() + ggplotpy.geom_point() + ggplotpy.facet_grid("g2 ~ g"),
        # themes
        "theme_minimal": _b() + ggplotpy.geom_point() + ggplotpy.theme_minimal(),
        "theme_elements_dotted": _b() + ggplotpy.geom_point() + ggplotpy.theme(legend_position="bottom", axis_text_x=ggplotpy.element_text(angle=45)),
        # positions
        "position_dodge": ggplot(_DF) + aes(x="g", y="z", fill="g2") + ggplotpy.geom_col(position=ggplotpy.position_dodge()),
        # guides
        "guide_legend": ggplot(_DF) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.guides(color=ggplotpy.guide_legend(ncol=2)),
        # annotations / labels
        "annotate": _b() + ggplotpy.geom_point() + ggplotpy.annotate("text", x=0, y=0, label="hi"),
        "labs": _b() + ggplotpy.geom_point() + ggplotpy.labs(title="T", x="X", caption="c"),
    }


_KEYS = [
    "geom_point", "geom_line", "geom_bar", "geom_col", "geom_histogram", "geom_density",
    "geom_boxplot", "geom_violin", "geom_smooth", "geom_text_layer_aes", "geom_tile",
    "geom_ribbon", "geom_errorbar", "geom_contour", "stat_summary", "stat_ecdf",
    "scale_y_log10", "scale_color_brewer", "scale_fill_viridis_c", "scale_x_continuous_tuple",
    "coord_flip", "coord_polar", "facet_wrap", "facet_grid", "theme_minimal",
    "theme_elements_dotted", "position_dodge", "guide_legend", "annotate", "labs",
]


@pytest.fixture(scope="module")
def cases():
    return _cases()


@pytest.mark.parametrize("key", _KEYS)
def test_category_renders(cases, key):
    assert key in cases
    svg = cases[key]._repr_svg_()
    assert isinstance(svg, str) and "<svg" in svg.lower() and len(svg) > 200
