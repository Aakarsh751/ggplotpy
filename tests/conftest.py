"""Shared pytest fixtures and skip helpers."""

from __future__ import annotations

import gc
import os
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"
_HEAVY_TEST_DIRS = frozenset({"integration", "gallery", "parity", "extensions"})


def _skip_heavy_integration() -> bool:
    """True when heavy suites should not be collected (OOM-safe default in CI)."""
    if os.environ.get("GGPLOTPY_RUN_HEAVY") == "1":
        return False
    return os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"


def pytest_ignore_collect(collection_path, config):
    if not _skip_heavy_integration():
        return False
    try:
        rel = collection_path.relative_to(Path(__file__).resolve().parent)
    except ValueError:
        return False
    return rel.parts and rel.parts[0] in _HEAVY_TEST_DIRS


def pytest_runtest_teardown(item, nextitem):
    fspath = getattr(item, "fspath", None)
    if fspath is not None and "integration" in str(fspath).replace("\\", "/"):
        gc.collect()



def _r_available() -> bool:
    try:
        from ggplotpy.backend.inprocess import r

        r()
        return True
    except Exception:
        return False


def _ggplot2_available() -> bool:
    if not _r_available():
        return False
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        return bool(ro.r("isTRUE(requireNamespace('ggplot2', quietly=TRUE))")[0])
    except Exception:
        return False


def _gganimate_render_available() -> bool:
    return _r_package_available("gganimate") and _r_package_available("gifski")


def _r_package_available(name: str) -> bool:
    if not _r_available():
        return False
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        return bool(ro.r(f"isTRUE(requireNamespace('{name}', quietly=TRUE))")[0])
    except Exception:
        return False


@pytest.fixture(scope="session")
def r_available() -> bool:
    return _r_available()


@pytest.fixture(scope="session")
def ggplot2_available() -> bool:
    return _ggplot2_available()


@pytest.fixture(scope="module")
def mtcars_df():
    import pandas as pd

    if _ggplot2_available():
        from ggplotpy.backend.inprocess import r
        from rpy2.robjects import conversion

        ro = r()
        with conversion.localconverter(conversion.get_conversion()):
            return conversion.get_conversion().rpy2py(ro.r("datasets::mtcars"))
    return pd.DataFrame(
        {
            "mpg": [21.0, 22.8],
            "cyl": [6, 4],
            "wt": [2.62, 2.875],
            "hp": [110, 110],
        }
    )


def assert_gg_is_plot(gg_obj) -> None:
    from ggplotpy.core.gg import GG

    assert isinstance(gg_obj, GG)
    assert gg_obj.r_obj is not None


def pytest_configure(config):
    config.addinivalue_line("markers", "needs_r: requires R")
    config.addinivalue_line("markers", "needs_ggplot2: requires ggplot2")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "needs_ggplot2" in item.keywords and not _ggplot2_available():
            item.add_marker(pytest.mark.skip(reason="ggplot2 not available"))
        elif "needs_r" in item.keywords and not _r_available():
            item.add_marker(pytest.mark.skip(reason="R not available"))
        elif "needs_ggrepel" in item.keywords and not _r_package_available("ggrepel"):
            item.add_marker(pytest.mark.skip(reason="ggrepel not available"))
        elif "needs_patchwork" in item.keywords and not _r_package_available("patchwork"):
            item.add_marker(pytest.mark.skip(reason="patchwork not available"))
        elif "needs_gganimate" in item.keywords and not _gganimate_render_available():
            item.add_marker(
                pytest.mark.skip(reason="gganimate and gifski required for animation render")
            )
        elif "needs_sf" in item.keywords and not _r_package_available("sf"):
            item.add_marker(pytest.mark.skip(reason="sf not available"))
        elif "needs_arrow" in item.keywords:
            try:
                import pyarrow  # noqa: F401
            except ImportError:
                item.add_marker(pytest.mark.skip(reason="pyarrow not available"))
