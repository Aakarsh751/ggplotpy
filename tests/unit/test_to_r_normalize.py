"""T0 whitespace normalization for to_r() parity."""

from ggplotpy.core.to_r_util import normalize_r_code


def test_normalize_r_code_collapses_blank_lines():
    raw = """
    library(ggplot2)

    ggplot(data)
    """
    assert normalize_r_code(raw) == "library(ggplot2)\nggplot(data)"


def test_normalize_r_code_collapses_internal_whitespace():
    raw = "p  <-  p  +   geom_point()"
    assert normalize_r_code(raw) == "p <- p + geom_point()"
