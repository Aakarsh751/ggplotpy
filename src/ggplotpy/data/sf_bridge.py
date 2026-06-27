"""Spatial (sf) data ingress — GeoPandas / GeoArrow → R ``sf``.

Two paths (see ``docs/architecture.md`` data plane):

* **GeoPandas** — write the ``GeoDataFrame`` to a temporary GeoPackage and read it
  back with ``sf::st_read``. Robust, preserves CRS and geometry types, and needs no
  GeoArrow build on either side.
* **GeoArrow** — a ``pyarrow.Table`` carrying a geometry extension column is routed
  through GeoPandas (``geopandas.GeoDataFrame.from_arrow``) and then the path above.

Both raise a clear, actionable error when GeoPandas (Python) or ``sf`` (R) is absent
rather than failing deep inside rpy2. ``ggplot(gdf)`` uses this automatically.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

from ggplotpy.core.errors import GgplotpySetupError


def _require_r_sf() -> None:
    from ggplotpy.backend.inprocess import r

    ro = r()
    try:
        ok = bool(ro.r('isTRUE(requireNamespace("sf", quietly=TRUE))')[0])
    except Exception as e:  # pragma: no cover - R unavailable
        raise GgplotpySetupError("Could not check for R package 'sf'. Ensure R is configured.") from e
    if not ok:
        raise GgplotpySetupError(
            "R package 'sf' is required for spatial plots (geom_sf). "
            "Run in R: install.packages('sf')",
            missing=["sf"],
        )


def sf_to_r(gdf: Any) -> Any:
    """Convert a GeoPandas ``GeoDataFrame`` to an R ``sf`` object.

    Round-trips through a temporary GeoPackage so geometry type and CRS survive.
    """
    try:
        import geopandas as gpd  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "geopandas is required for spatial ingress. "
            "Install with `pip install ggplotpy[geo]` (or `pip install geopandas`)."
        ) from e
    _require_r_sf()

    from rpy2.robjects import default_converter
    from rpy2.robjects.conversion import localconverter

    from ggplotpy.backend.inprocess import r, r_pkg, set_last_r_code

    r_pkg("sf")
    ro = r()
    tmp = tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False)
    tmp.close()
    path = tmp.name
    posix = path.replace("\\", "/")
    try:
        # layer name must be stable for st_read; default to the file stem.
        gdf.to_file(path, driver="GPKG", layer="ggplotpy")
        set_last_r_code(f'sf::st_read("{posix}", quiet = TRUE)')
        # Read under the default (non-converting) converter so the sf object — whose
        # geometry list-column is not pandas-convertible — stays a raw R object.
        with localconverter(default_converter):
            return ro.r(f'sf::st_read("{posix}", layer = "ggplotpy", quiet = TRUE)')
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def geoarrow_to_r(table: Any) -> Any:
    """Convert a GeoArrow ``pyarrow.Table`` (geometry extension column) to R ``sf``.

    Routed through GeoPandas, which understands GeoArrow geometry extension types.
    """
    try:
        import geopandas as gpd
    except ImportError as e:
        raise ImportError(
            "geopandas is required for GeoArrow ingress. Install with `pip install ggplotpy[geo]`."
        ) from e
    try:
        gdf = gpd.GeoDataFrame.from_arrow(table)
    except AttributeError as e:  # pragma: no cover - older geopandas
        raise GgplotpySetupError(
            "This geopandas version lacks GeoDataFrame.from_arrow; upgrade geopandas, "
            "or pass a GeoDataFrame directly."
        ) from e
    return sf_to_r(gdf)


def is_geodataframe(obj: Any) -> bool:
    """True for a GeoPandas GeoDataFrame without importing geopandas eagerly."""
    cls = type(obj)
    for base in cls.__mro__:
        if base.__module__.split(".", 1)[0] == "geopandas" and base.__name__ == "GeoDataFrame":
            return True
    return False
