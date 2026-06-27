"""T0 tests for GG layer chain bookkeeping (R-free)."""

from ggplotpy.core.gg import GG


def test_gg_layer_codes_preserved():
    gg = GG(None, layer_codes=["ggplot(data, mapping)"])
    assert gg.layer_codes == ["ggplot(data, mapping)"]


def test_gg_radd_zero_identity():
    gg = GG(None, layer_codes=["ggplot(data)"])
    assert (0 + gg) is gg


def test_gg_to_r_includes_layers():
    gg = GG(None, layer_codes=["ggplot(data, mapping)", "geom_point()"])
    script = gg.to_r()
    assert "library(ggplot2)" in script
    assert "geom_point()" in script
