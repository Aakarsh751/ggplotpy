"""patchwork composition operators."""

from __future__ import annotations

from typing import Any

from ggplotpy.core.errors import GgplotpySetupError
from ggplotpy.core.gg import GG


class PlotComposition:
    """Wraps patchwork compositions built with | and / operators."""

    __slots__ = ("_r_obj",)

    def __init__(self, r_obj: Any) -> None:
        self._r_obj = r_obj

    @property
    def r_obj(self) -> Any:
        return self._r_obj

    def _resolve(self, other: Any) -> Any:
        if isinstance(other, PlotComposition):
            return other._r_obj
        if isinstance(other, GG):
            return other.r_obj
        return other

    def _combine(self, other: Any, op: str) -> PlotComposition:
        from ggplotpy.backend.inprocess import r, r_pkg, set_last_r_code

        _require_patchwork()
        ro = r()
        left = self._r_obj
        right = self._resolve(other)
        set_last_r_code(f"left {op} right")
        r_pkg("patchwork")
        r_op = ro.r(f'get("{op}", envir=getNamespace("patchwork"))')
        combined = r_op(left, right)
        return PlotComposition(combined)

    def __or__(self, other: Any) -> PlotComposition:
        return self._combine(other, "|")

    def __truediv__(self, other: Any) -> PlotComposition:
        return self._combine(other, "/")

    def save(self, path: str, **kwargs: Any) -> None:
        from ggplotpy.core._options import get_options
        from ggplotpy.core.gg import _ggsave

        opts = get_options()
        _ggsave(
            self._r_obj,
            path,
            width=kwargs.get("width", opts.width),
            height=kwargs.get("height", opts.height),
            dpi=kwargs.get("dpi", opts.dpi),
        )

    def _repr_svg_(self) -> str:
        from ggplotpy.core.gg import _render_plot

        return _render_plot(self._r_obj, "svg")

    def _repr_png_(self) -> bytes:
        from ggplotpy.core.gg import _render_plot

        return _render_plot(self._r_obj, "png")


def from_plot(plot: GG | PlotComposition) -> PlotComposition:
    """Wrap a :class:`GG` plot for patchwork ``|`` and ``/`` composition."""
    if isinstance(plot, PlotComposition):
        return plot
    if isinstance(plot, GG):
        return PlotComposition(plot.r_obj)
    raise TypeError(f"Expected GG or PlotComposition, got {type(plot).__name__}")


def _require_patchwork() -> None:
    """Raise :class:`GgplotpySetupError` when the R patchwork package is missing."""
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        ok = bool(ro.r('isTRUE(requireNamespace("patchwork", quietly=TRUE))')[0])
    except Exception as e:
        raise GgplotpySetupError(
            "Could not check for R package 'patchwork'. Ensure R is configured."
        ) from e
    if not ok:
        raise GgplotpySetupError(
            "R package 'patchwork' is not installed. Run in R: install.packages('patchwork')",
            missing=["patchwork"],
        )
