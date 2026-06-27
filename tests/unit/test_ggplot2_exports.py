"""T0 tests for full ggplot2 namespace export coverage."""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ggplotpy.codegen.reflect import clear_reflect_cache, list_namespace_exports

PYI_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "ggplotpy" / "generated" / "ggplot2_reflected.pyi"
)


def _pyi_export_count() -> int:
    text = PYI_PATH.read_text(encoding="utf-8")
    return len(re.findall(r"^def ", text, flags=re.MULTILINE))


def test_pyi_export_count_at_least_100():
    """Committed stub must reflect full ggplot2 namespace (not the old 50-export cap)."""
    assert _pyi_export_count() >= 100


@patch("ggplotpy.backend.inprocess.r")
def test_load_ggplot2_symbol_resolves_mocked_export(mock_r_fn):
    from ggplotpy.generated import clear_symbol_cache, load_ggplot2_symbol

    clear_reflect_cache()
    clear_symbol_cache()
    mock_exports = [f"export_{i}" for i in range(120)]
    mock_exports.extend(["geom_point", "ggplot", "aes"])

    mock_ro = MagicMock()
    mock_ro.r.return_value = mock_exports
    mock_r_fn.return_value = mock_ro

    with patch("ggplotpy.codegen.reflect.build_ggplot2_callable") as build_mock:
        sentinel = object()
        build_mock.return_value = sentinel
        fn = load_ggplot2_symbol("export_99")
        assert fn is sentinel
        build_mock.assert_called_once_with("export_99")


@pytest.mark.needs_ggplot2
def test_pyi_export_count_matches_live_namespace():
    clear_reflect_cache()
    live = list_namespace_exports("ggplot2", use_cache=False)
    pyi_count = _pyi_export_count()
    assert pyi_count == len(live), f"pyi has {pyi_count} exports, R has {len(live)}"


@pytest.mark.needs_ggplot2
def test_load_ggplot2_symbol_resolves_any_live_export():
    from ggplotpy.generated import clear_symbol_cache, load_ggplot2_symbol

    clear_reflect_cache()
    clear_symbol_cache()
    fn = load_ggplot2_symbol("geom_violin")
    assert callable(fn)
    assert fn.__name__ == "geom_violin"


@pytest.mark.needs_ggplot2
def test_ggplotpy_getattr_resolves_ggplot2_export():
    import ggplotpy
    from ggplotpy.generated import clear_symbol_cache

    clear_reflect_cache()
    clear_symbol_cache()
    fn = ggplotpy.geom_bar
    assert callable(fn)
    assert fn.__name__ == "geom_bar"
    assert ggplotpy.geom_bar is fn


@pytest.mark.needs_ggplot2
def test_ggplotpy_getattr_unknown_raises():
    import ggplotpy

    with pytest.raises(AttributeError, match="has no attribute 'not_a_real_export'"):
        _ = ggplotpy.not_a_real_export
