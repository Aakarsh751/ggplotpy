"""Global figure / render options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class FigureOptions:
    width: float = 6.0
    height: float = 4.0
    dpi: int = 144
    format: Literal["svg", "png"] = "svg"


_OPTIONS = FigureOptions()


def get_options() -> FigureOptions:
    return _OPTIONS


def set_options(
    *,
    figure_size: tuple[float, float] | None = None,
    dpi: int | None = None,
    format: Literal["svg", "png"] | None = None,
) -> None:
    """Set global defaults for Jupyter rendering and save()."""
    global _OPTIONS
    opts = FigureOptions(
        width=_OPTIONS.width,
        height=_OPTIONS.height,
        dpi=_OPTIONS.dpi,
        format=_OPTIONS.format,
    )
    if figure_size is not None:
        opts.width, opts.height = figure_size
    if dpi is not None:
        opts.dpi = dpi
    if format is not None:
        opts.format = format
    _OPTIONS = opts
