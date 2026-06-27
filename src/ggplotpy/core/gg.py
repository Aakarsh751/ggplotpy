"""GG - ggplot2 plot wrapper."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from ggplotpy.backend.inprocess import r, r_pkg, rcall, set_last_r_code
from ggplotpy.core._options import get_options
from ggplotpy.core.defer import DeferredRCall, simplify_layer_code
from ggplotpy.core.raw import RObject
from ggplotpy.core.to_r_util import format_layer_for_to_r, normalize_r_code


def _r_add(left: Any, right: Any) -> Any:
    """Apply ggplot2 composition via R's + operator."""
    ro = r()
    set_last_r_code("`+`(plot, layer)")
    return ro.r["+"](left, right)


def _r_add_fragment(left: Any, r_fragment: str) -> Any:
    """Add an R-side layer without pulling S7 intermediates through Python."""
    ro = r()
    ro.r.assign(".__ggplotpy_left", left)
    set_last_r_code(f"p + {r_fragment}")
    ro.r(f".__ggplotpy_out <- .__ggplotpy_left + {r_fragment}")
    return ro.r(".__ggplotpy_out")


def _layer_code_hint(obj: Any) -> str:
    cls = type(obj).__name__
    if cls in {"ListVector", "NamedList"}:
        return "aes(...)"
    return repr(obj)


class GG:
    """Python wrapper around an R ggplot object."""

    __slots__ = ("_r_obj", "_layer_codes")

    def __init__(self, r_obj: Any, *, layer_codes: list[str] | None = None) -> None:
        self._r_obj = r_obj
        self._layer_codes = layer_codes or []

    @property
    def r_obj(self) -> Any:
        return self._r_obj

    @property
    def layer_codes(self) -> list[str]:
        return list(self._layer_codes)

    def __add__(self, other: Any) -> GG:
        left = self._r_obj
        codes = list(self._layer_codes)

        if isinstance(other, GG):
            result = _r_add(left, other._r_obj)
            codes.extend(other._layer_codes)
            return GG(result, layer_codes=codes)

        if isinstance(other, DeferredRCall):
            result = _r_add_fragment(left, other.code)
            codes.append(simplify_layer_code(other.code))
            return GG(result, layer_codes=codes)

        if isinstance(other, RObject):
            right = other.eval()
            codes.append(other.code)
            result = _r_add(left, right)
            return GG(result, layer_codes=codes)

        result = _r_add(left, other)
        codes.append(_layer_code_hint(other))
        return GG(result, layer_codes=codes)

    def __radd__(self, other: Any) -> GG:
        if other == 0:
            return self
        return NotImplemented

    def _patchwork_op(self, other: Any, op: str) -> Any:
        from ggplotpy.core.patchwork import PlotComposition, _require_patchwork

        _require_patchwork()
        comp = PlotComposition(self._r_obj)
        if op == "|":
            return comp | other
        return comp / other

    def __or__(self, other: Any) -> Any:
        """Side-by-side patchwork composition (``|``) when patchwork is installed."""
        return self._patchwork_op(other, "|")

    def __truediv__(self, other: Any) -> Any:
        """Stacked patchwork composition (``/``) when patchwork is installed."""
        return self._patchwork_op(other, "/")

    def to_r(self) -> str:
        lines = ["library(ggplot2)"]
        if not self._layer_codes:
            lines.append("p <- ggplot(data)")
            return normalize_r_code("\n".join(lines))

        first = format_layer_for_to_r(self._layer_codes[0])
        if first.startswith("ggplot("):
            lines.append(f"p <- {first}")
            rest = self._layer_codes[1:]
        else:
            lines.append("p <- ggplot(data)")
            rest = self._layer_codes

        for code in rest:
            display = format_layer_for_to_r(code)
            if display.startswith("ggplot("):
                continue
            lines.append(f"p <- p + {display}")
        return normalize_r_code("\n".join(lines))

    def save(
        self,
        path: str,
        *,
        width: float | None = None,
        height: float | None = None,
        dpi: int | None = None,
        isolated: bool = False,
    ) -> None:
        """Write the plot to ``path``.

        With ``isolated=True`` the render runs in a fresh ``Rscript`` process
        (crash isolation) instead of in-process ggsave.
        """
        opts = get_options()
        w = width or opts.width
        h = height or opts.height
        d = dpi or opts.dpi
        if isolated:
            device = "svg" if path.lower().endswith(".svg") else "png"
            data = self.render_isolated(device=device, width=w, height=h, dpi=d)
            mode = "w" if device == "svg" else "wb"
            encoding = "utf-8" if device == "svg" else None
            with open(path, mode, encoding=encoding) as fh:
                fh.write(data)
            return
        _ggsave(self._r_obj, path, width=w, height=h, dpi=d)

    def render_isolated(
        self,
        *,
        device: str = "png",
        width: float | None = None,
        height: float | None = None,
        dpi: int | None = None,
    ) -> str | bytes:
        """Render this plot in an isolated subprocess (crash-safe). Returns bytes/str."""
        from ggplotpy.backend.subprocess import render_in_subprocess

        opts = get_options()
        return render_in_subprocess(
            self._r_obj,
            device=device,
            width=width or opts.width,
            height=height or opts.height,
            dpi=dpi or opts.dpi,
        )

    def _repr_svg_(self) -> str:
        return _render_plot(self._r_obj, "svg")

    def _repr_png_(self) -> bytes:
        return _render_plot(self._r_obj, "png")

    def _repr_mimebundle_(self, include: Any = None, exclude: Any = None) -> dict[str, Any]:
        fmt = get_options().format
        if fmt == "png":
            return {"image/png": self._repr_png_()}
        return {"image/svg+xml": self._repr_svg_()}


def _coerce_data(data: Any) -> Any:
    """Route any common Python data container to an R data.frame.

    Accepts pandas DataFrame/Series, ``dict`` of columns, list-of-record dicts,
    numpy arrays (1-D → ``V1``; 2-D → ``V1..Vn``), pyarrow Tables/RecordBatches,
    and polars DataFrames so ``ggplot(data)`` works directly for any of them.
    Objects already living in R (rpy2) or anything unrecognised pass through.
    """
    if data is None:
        return None
    top_module = type(data).__module__.split(".", 1)[0]
    if top_module == "rpy2":
        return data

    # GeoPandas GeoDataFrame → R sf (must precede the pandas branch: GeoDataFrame
    # subclasses pandas.DataFrame).
    if top_module == "geopandas":
        from ggplotpy.data.sf_bridge import is_geodataframe, sf_to_r

        if is_geodataframe(data):
            return sf_to_r(data)

    def _pandas() -> Any:
        import pandas as pd  # noqa: PLC0415

        return pd

    try:
        pd = _pandas()
    except ImportError:
        pd = None

    if pd is not None:
        from ggplotpy.data.pandas_bridge import pandas_to_r

        if isinstance(data, pd.DataFrame):
            return pandas_to_r(data)
        if isinstance(data, pd.Series):
            return pandas_to_r(data.to_frame())
        if isinstance(data, dict):
            return pandas_to_r(pd.DataFrame(data))
        if isinstance(data, list) and data and all(isinstance(r, dict) for r in data):
            return pandas_to_r(pd.DataFrame.from_records(data))

    np = _maybe_numpy_local()
    if np is not None and isinstance(data, np.ndarray) and pd is not None:
        from ggplotpy.data.pandas_bridge import pandas_to_r

        if data.ndim == 1:
            frame = pd.DataFrame({"V1": data})
        elif data.ndim == 2:
            frame = pd.DataFrame(
                data, columns=[f"V{i + 1}" for i in range(data.shape[1])]
            )
        else:
            raise ValueError(
                f"ggplot() cannot use a {data.ndim}-D numpy array; pass a 2-D array, "
                "DataFrame, or dict of columns."
            )
        return pandas_to_r(frame)

    if top_module == "pyarrow":
        from ggplotpy.data.arrow import arrow_to_r

        return arrow_to_r(data)
    if top_module == "polars":
        from ggplotpy.data.polars_bridge import polars_to_r

        return polars_to_r(data)
    return data


def _maybe_numpy_local() -> Any:
    try:
        import numpy as np
    except ImportError:
        return None
    return np


def ggplot(data: Any = None, mapping: Any = None, **kwargs: Any) -> GG:
    data = _coerce_data(data)
    if isinstance(mapping, DeferredRCall):
        fragment = mapping.code
        set_last_r_code(f"ggplot2::ggplot(..., {fragment})")
        ro = r()
        if data is not None:
            ro.r.assign(".__ggplotpy_data", data)
            r_obj = ro.r(f"ggplot2::ggplot(.__ggplotpy_data, {fragment})")
        else:
            r_obj = ro.r(f"ggplot2::ggplot({fragment})")
        mapping_hint = format_layer_for_to_r(fragment)
        return GG(r_obj, layer_codes=[f"ggplot(data, mapping = {mapping_hint})"])

    ggplot2 = r_pkg("ggplot2")
    args: list[Any] = []
    if data is not None:
        args.append(data)
    if mapping is not None:
        args.append(mapping)
    set_last_r_code("ggplot2::ggplot(...)")
    r_obj = rcall(ggplot2.ggplot, *args, **kwargs)
    if mapping is None:
        layer = "ggplot(data)"
    elif isinstance(mapping, DeferredRCall):
        layer = f"ggplot(data, mapping = {format_layer_for_to_r(mapping.code)})"
    else:
        layer = "ggplot(data, mapping = aes(...))"
    return GG(r_obj, layer_codes=[layer])


def _ggsave(plot: Any, path: str, *, width: float, height: float, dpi: int) -> None:
    ggplot2 = r_pkg("ggplot2")
    set_last_r_code(f'ggplot2::ggsave("{path}", ...)')
    rcall(
        ggplot2.ggsave,
        filename=path,
        plot=plot,
        width=width,
        height=height,
        dpi=dpi,
    )


def _render_plot(plot: Any, device: str) -> str | bytes:
    """Render via open graphics device + print(plot) (robstatm Path-A pattern)."""
    opts = get_options()
    ext = "svg" if device == "svg" else "png"
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        path = tmp.name
    posix = path.replace("\\", "/")
    ro = r()
    w, h, dpi = opts.width, opts.height, opts.dpi
    device_open = False
    try:
        if device == "svg":
            set_last_r_code(f'svglite::svglite("{posix}", width={w}, height={h})')
            ro.r(f'svglite::svglite("{posix}", width={w}, height={h})')
        else:
            set_last_r_code(f'png("{posix}", width={w}, height={h}, units="in", res={dpi})')
            ro.r(
                f'png("{posix}", width={w}, height={h}, units="in", res={dpi}, bg="white")'
            )
        device_open = True
        ro.r["print"](plot)
        ro.r("dev.off()")
        device_open = False
        if device == "svg":
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        with open(path, "rb") as fh:
            return fh.read()
    finally:
        try:
            ro.r("try(dev.off(), silent=TRUE)")
        except Exception:
            pass
        try:
            os.unlink(path)
        except OSError:
            pass
