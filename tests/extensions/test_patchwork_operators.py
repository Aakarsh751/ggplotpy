"""Extension smoke — patchwork | and / operators on PlotComposition."""

from __future__ import annotations

import pytest

from ggplotpy.core.patchwork import PlotComposition, from_plot

pytestmark = [pytest.mark.needs_ggplot2, pytest.mark.needs_patchwork]


def test_from_plot_wraps_gg(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot

    p = ggplot(mtcars_df) + aes(x="wt", y="mpg") + geom_point()
    wrapped = from_plot(p)
    assert isinstance(wrapped, PlotComposition)
    assert wrapped.r_obj is not None


def test_patchwork_or_operator(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot, theme_minimal

    p1 = from_plot(ggplot(mtcars_df) + aes(x="wt", y="mpg") + geom_point())
    p2 = from_plot(
        ggplot(mtcars_df) + aes(x="hp", y="mpg") + geom_point() + theme_minimal()
    )
    comp = p1 | p2
    assert isinstance(comp, PlotComposition)
    assert comp.r_obj is not None


def test_patchwork_truediv_operator(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot

    p1 = from_plot(ggplot(mtcars_df) + aes(x="wt", y="mpg") + geom_point())
    p2 = from_plot(ggplot(mtcars_df) + aes(x="hp", y="mpg") + geom_point())
    comp = p1 / p2
    assert isinstance(comp, PlotComposition)
    assert comp.r_obj is not None


def test_gg_or_operator_direct(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot

    p1 = ggplot(mtcars_df) + aes(x="wt", y="mpg") + geom_point()
    p2 = ggplot(mtcars_df) + aes(x="hp", y="mpg") + geom_point()
    comp = p1 | p2
    assert isinstance(comp, PlotComposition)
    assert comp.r_obj is not None


def test_gg_truediv_operator_direct(mtcars_df):
    from ggplotpy import aes, geom_point, ggplot

    p1 = ggplot(mtcars_df) + aes(x="wt", y="mpg") + geom_point()
    p2 = ggplot(mtcars_df) + aes(x="hp", y="mpg") + geom_point()
    comp = p1 / p2
    assert isinstance(comp, PlotComposition)
    assert comp.r_obj is not None
