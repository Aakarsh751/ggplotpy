"""T0 (R-free) tests for the sf spatial bridge graceful-degradation paths."""

from __future__ import annotations

import pytest


def _geopandas_installed() -> bool:
    import importlib.util

    return importlib.util.find_spec("geopandas") is not None


def test_is_geodataframe_false_for_plain_objects():
    from ggplotpy.data.sf_bridge import is_geodataframe

    import pandas as pd

    assert not is_geodataframe(pd.DataFrame({"x": [1]}))
    assert not is_geodataframe({"x": [1]})
    assert not is_geodataframe([1, 2, 3])


@pytest.mark.skipif(_geopandas_installed(), reason="geopandas installed")
def test_sf_to_r_without_geopandas_raises_clear_error():
    from ggplotpy.data.sf_bridge import sf_to_r

    with pytest.raises(ImportError, match="geopandas is required"):
        sf_to_r(object())


@pytest.mark.skipif(_geopandas_installed(), reason="geopandas installed")
def test_geoarrow_to_r_without_geopandas_raises_clear_error():
    from ggplotpy.data.sf_bridge import geoarrow_to_r

    with pytest.raises(ImportError, match="geopandas is required"):
        geoarrow_to_r(object())


def test_coerce_data_ignores_non_geo_objects():
    """_coerce_data must not misroute plain pandas/dict through the sf path."""
    import pandas as pd

    from ggplotpy.core.gg import _coerce_data

    # A plain DataFrame is not geopandas; this should attempt pandas conversion,
    # which needs R — so just assert the geo branch is not taken (no ImportError
    # about geopandas).
    try:
        _coerce_data(pd.DataFrame({"x": [1, 2]}))
    except Exception as e:  # R may be absent in pure-unit runs
        assert "geopandas" not in str(e)
