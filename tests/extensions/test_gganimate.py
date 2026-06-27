"""Extension smoke — gganimate transition + animate() GIF bytes."""

from __future__ import annotations

import pytest

from ggplotpy.core.animate import transition_states
from ggplotpy.core.defer import DeferredRCall

pytestmark = [pytest.mark.needs_ggplot2, pytest.mark.needs_gganimate]


def test_transition_states_deferred_code():
    layer = transition_states(states="year", transition_length = 2)
    assert isinstance(layer, DeferredRCall)
    assert "gganimate::transition_states" in layer.code
    assert 'states = "year"' in layer.code


def test_gganimate_animate_gif_bytes(mtcars_df):
    from ggplotpy import R, aes, geom_point, ggplot, theme_minimal
    from ggplotpy.core.animate import animate

    df = mtcars_df.copy()
    if "year" not in df.columns:
        df["year"] = [1970 + (i % 4) for i in range(len(df))]

    # transition_manual does no tweening, so it renders reliably across gganimate /
    # ggplot2 versions (the tweening transitions break against ggplot2 4.0 internals).
    p = (
        ggplot(df)
        + aes(x="wt", y="mpg", color="factor(cyl)")
        + geom_point()
        + R("gganimate::transition_manual(year)")
        + theme_minimal()
    )
    gif = animate(p, width=320, height=240, fps=5, nframes=4)
    assert isinstance(gif, bytes)
    assert len(gif) > 100
    assert gif[:6] in (b"GIF87a", b"GIF89a")
