"""Extension smoke — patchwork."""

import pytest

pytestmark = pytest.mark.needs_patchwork


def test_patchwork_module_import():
    import ggplotpy.ext as ext

    patchwork = ext.patchwork
    assert patchwork is not None
