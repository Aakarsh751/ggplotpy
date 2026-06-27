"""T1 smoke: common geoms render on a small synthetic DataFrame."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = [pytest.mark.needs_ggplot2, pytest.mark.slow]

GEOM_NAMES = [
    "geom_point",
    "geom_line",
    "geom_bar",
    "geom_histogram",
    "geom_boxplot",
    "geom_tile",
    "geom_text",
    "geom_smooth",
    "geom_violin",
    "geom_density",
    "geom_area",
    "geom_col",
    "geom_abline",
    "geom_hline",
    "geom_vline",
]


@pytest.fixture(scope="module")
def synth_df():
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "x": np.linspace(1, 10, 20),
            "y": rng.normal(5, 1, 20),
            "cat": (["A", "B"] * 10),
            "val": np.linspace(0, 1, 20),
            "label": [f"L{i}" for i in range(20)],
            "tile_x": np.repeat([1, 2, 3, 4], 5),
            "tile_y": list(range(1, 6)) * 4,
        }
    )


def _build_plot(geom_name: str, data, geom_fn):
    from ggplotpy import aes, ggplot

    base = ggplot(data)

    builders = {
        "geom_point": lambda: base + aes(x="x", y="y") + geom_fn(),
        "geom_line": lambda: base + aes(x="x", y="y") + geom_fn(),
        "geom_bar": lambda: base + aes(x="cat") + geom_fn(),
        "geom_histogram": lambda: base + aes(x="val") + geom_fn(),
        "geom_boxplot": lambda: base + aes(x="cat", y="y") + geom_fn(),
        "geom_tile": lambda: base + aes(x="tile_x", y="tile_y", fill="val") + geom_fn(),
        "geom_text": lambda: base + aes(x="x", y="y", label="label") + geom_fn(),
        "geom_smooth": lambda: base + aes(x="x", y="y") + geom_fn(),
        "geom_violin": lambda: base + aes(x="cat", y="y") + geom_fn(),
        "geom_density": lambda: base + aes(x="val") + geom_fn(),
        "geom_area": lambda: base + aes(x="x", y="y") + geom_fn(),
        "geom_col": lambda: base + aes(x="cat", y="y") + geom_fn(),
        "geom_abline": lambda: base + aes(x="x", y="y") + geom_fn(intercept=0, slope=1),
        "geom_hline": lambda: base + aes(x="x", y="y") + geom_fn(yintercept=5),
        "geom_vline": lambda: base + aes(x="x", y="y") + geom_fn(xintercept=5),
    }
    return builders[geom_name]()


@pytest.mark.parametrize("geom_name", GEOM_NAMES)
def test_geom_renders_svg(geom_name, synth_df):
    from ggplotpy.data.pandas_bridge import pandas_to_r
    from ggplotpy.generated import load_ggplot2_symbol

    data = pandas_to_r(synth_df)
    geom_fn = load_ggplot2_symbol(geom_name)
    p = _build_plot(geom_name, data, geom_fn)
    svg = p._repr_svg_()
    assert isinstance(svg, str)
    assert len(svg) > 100
    assert "<svg" in svg.lower()
