"""T0 — ggplotpy.ext lazy reflection (R-free checks)."""

from __future__ import annotations

import pytest


def test_ext_known_extensions_tuple():
    from ggplotpy.ext import KNOWN_EXTENSIONS

    assert "ggrepel" in KNOWN_EXTENSIONS
    assert "patchwork" in KNOWN_EXTENSIONS


def test_ext_dir_includes_known():
    import ggplotpy.ext as ext

    names = ext.__dir__()
    assert "ggrepel" in names
    assert "patchwork" in names


@pytest.mark.needs_r
def test_ext_missing_package_raises():
    import ggplotpy.ext as ext

    with pytest.raises(AttributeError, match="not installed"):
        _ = ext.this_package_should_not_exist_ggplotpy_test_12345
