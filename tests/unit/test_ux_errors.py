"""T0 UX tests: last_r_code, error message shape (R-free)."""

from __future__ import annotations

import pytest

from ggplotpy.core.errors import GgplotpyRError, format_r_error, last_r_code, set_last_r_code


def test_last_r_code_public_export():
    import ggplotpy

    set_last_r_code("ggplot2::geom_point()")
    assert ggplotpy.last_r_code() == "ggplot2::geom_point()"


def test_last_r_code_roundtrip():
    set_last_r_code('aes(x = "wt", y = "mpg")')
    assert last_r_code() == 'aes(x = "wt", y = "mpg")'
    set_last_r_code("ggplot2::theme_minimal()")
    assert last_r_code() == "ggplot2::theme_minimal()"


def test_ggplotpy_r_error_str_includes_offending_line():
    set_last_r_code('ggplot2::geom_foo(size = 2)')
    err = GgplotpyRError("object 'geom_foo' not found")
    text = str(err)
    assert "object 'geom_foo' not found" in text
    assert "Offending R line:" in text
    assert "ggplot2::geom_foo(size = 2)" in text


def test_format_r_error_with_hint():
    msg = format_r_error(
        "bad mapping",
        r_code='aes(x = "missing_col")',
        hint="Check column names in your DataFrame.",
    )
    assert "bad mapping" in msg
    assert 'aes(x = "missing_col")' in msg
    assert "Check column names" in msg


def test_rcall_wraps_r_runtime_error(monkeypatch):
    from rpy2.rinterface_lib.embedded import RRuntimeError

    from ggplotpy.backend.inprocess import rcall, set_last_r_code as backend_set

    backend_set("ggplot2::geom_invalid()")

    def _boom(*args, **kwargs):
        raise RRuntimeError("there is no package called 'invalid'")

    with pytest.raises(GgplotpyRError) as excinfo:
        rcall(_boom)

    text = str(excinfo.value)
    assert "there is no package called 'invalid'" in text
    assert "Offending R line:" in text
    assert "ggplot2::geom_invalid()" in text
    assert excinfo.value.r_code == "ggplot2::geom_invalid()"


def test_format_layer_for_to_r_expands_aes():
    from ggplotpy.core.to_r_util import format_layer_for_to_r

    code = 'ggplotpy::aes_from_strings(x = "wt", y = "mpg", color = "factor(cyl)")'
    assert format_layer_for_to_r(code) == "aes(x = wt, y = mpg, color = factor(cyl))"


def test_gg_to_r_readable_aes_layers():
    from ggplotpy.core.gg import GG
    from ggplotpy.core.to_r_util import normalize_r_code

    gg = GG(
        None,
        layer_codes=[
            "ggplot(data, mapping = aes(x = wt, y = mpg))",
            "geom_point(size = 2)",
        ],
    )
    script = normalize_r_code(gg.to_r())
    assert "mapping = aes(x = wt, y = mpg)" in script
    assert "geom_point(size = 2)" in script
    assert script.count("p <- p +") == 1
