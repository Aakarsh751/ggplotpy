"""T0 tests for reflection codegen (R-free via mocks)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ggplotpy.codegen.emit import emit_pyi_module, emit_pyi_stub, formals_to_signature
from ggplotpy.codegen.reflect import clear_reflect_cache, list_namespace_exports


def test_formals_to_signature_with_dots():
    sig = formals_to_signature(["mapping", "data", "..."])
    assert "mapping: Any" in sig
    assert "data: Any" in sig
    assert "*args: Any" in sig
    assert "**kwargs: Any" in sig


def test_formals_to_signature_empty():
    assert formals_to_signature(None) == "*args: Any, **kwargs: Any"
    assert formals_to_signature([]) == ""


def test_emit_pyi_stub_includes_formals_and_doc():
    stub = emit_pyi_stub("ggplot", ["data", "mapping", "..."], "R ggplot2::ggplot")
    assert "def ggplot(" in stub
    assert "mapping: Any" in stub
    assert '"""R ggplot2::ggplot"""' in stub
    assert stub.strip().endswith("...")


def test_emit_pyi_stub_non_identifier_operator():
    stub = emit_pyi_stub("%+%", ["e1", "e2"], doc=None)
    assert 'def "%+%"(e1: Any' in stub


def test_emit_pyi_module_roundtrip(tmp_path):
    exports = [
        {"name": "geom_point", "formals": ["mapping", "data", "..."], "doc": "R ggplot2::geom_point"},
        {"name": "aes", "formals": ["x", "y", "..."], "doc": None},
    ]
    out = tmp_path / "test.pyi"
    content = emit_pyi_module("ggplot2", exports, output_path=out)
    assert out.exists()
    assert "geom_point" in content
    assert "from typing import Any" in content


@patch("ggplotpy.backend.inprocess.r")
def test_list_namespace_exports_mock(mock_r_fn):
    clear_reflect_cache()
    mock_ro = MagicMock()
    mock_ro.r.return_value = ["ggplot", "aes", "geom_point"]
    mock_r_fn.return_value = mock_ro

    first = list_namespace_exports("ggplot2")
    second = list_namespace_exports("ggplot2")

    assert first == ["aes", "geom_point", "ggplot"]
    assert second == first
    mock_ro.r.assert_called_once()


@patch("ggplotpy.backend.inprocess.r")
def test_list_namespace_exports_bypass_cache(mock_r_fn):
    clear_reflect_cache()
    mock_ro = MagicMock()
    mock_ro.r.return_value = ["ggplot"]
    mock_r_fn.return_value = mock_ro

    list_namespace_exports("ggplot2", use_cache=False)
    list_namespace_exports("ggplot2", use_cache=False)

    assert mock_ro.r.call_count == 2


def test_load_ggplot2_symbol_uses_reflect_cache():
    from ggplotpy.generated import clear_symbol_cache, load_ggplot2_symbol

    clear_symbol_cache()
    with patch("ggplotpy.codegen.reflect.list_namespace_exports", return_value=["geom_point"]):
        with patch("ggplotpy.codegen.reflect.build_ggplot2_callable") as build_mock:
            build_mock.return_value = lambda: None
            fn1 = load_ggplot2_symbol("geom_point")
            fn2 = load_ggplot2_symbol("geom_point")
            assert fn1 is fn2
            build_mock.assert_called_once_with("geom_point")


def test_load_ggplot2_symbol_unknown_export():
    from ggplotpy.generated import clear_symbol_cache, load_ggplot2_symbol

    clear_symbol_cache()
    with patch("ggplotpy.codegen.reflect.list_namespace_exports", return_value=["ggplot"]):
        with pytest.raises(AttributeError, match="no export"):
            load_ggplot2_symbol("not_a_real_export")


@pytest.mark.needs_ggplot2
def test_list_namespace_exports_live():
    clear_reflect_cache()
    exports = list_namespace_exports("ggplot2", use_cache=False)
    assert "ggplot" in exports
    assert "geom_point" in exports
    assert len(exports) > 50
