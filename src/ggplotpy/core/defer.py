"""Deferred R evaluation for ggplot2 S7 objects that break via rpy2 conversion."""

from __future__ import annotations

from typing import Any


class DeferredRCall:
    """An R expression evaluated only when composed onto a plot in R."""

    __slots__ = ("_code",)

    def __init__(self, code: str) -> None:
        self._code = code.strip()

    @property
    def code(self) -> str:
        return self._code

    def __repr__(self) -> str:
        return f"DeferredRCall({self._code!r})"


def normalize_r_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Map Python kwarg names to R parameter names (ADR D-P011).

    Strips a single trailing ``_`` (reserved-word escape, ``class_`` → ``class``),
    then converts remaining underscores to dots so idiomatic Python reaches R's
    dotted parameters (``na_rm`` → ``na.rm``, ``legend_position`` → ``legend.position``).
    """
    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        name = key[:-1] if key.endswith("_") else key
        name = name.replace("_", ".")
        out[name] = value
    return out


def _maybe_numpy() -> Any:
    try:
        import numpy as np
    except ImportError:
        return None
    return np


def format_r_value(value: Any) -> str:
    """Format a Python value for embedding in generated R code.

    Handles scalars (incl. numpy scalars), sequences/arrays (``c(...)``), dicts
    (``list(k = v)``), and ggplotpy's deferred/raw R wrappers so that ``aes(...)`` and
    ``R(...)`` objects can be passed as arguments to any other wrapper (e.g.
    ``geom_point(aes(color="cyl"))``) without rpy2 trying to convert the Python
    object directly.
    """
    if value is None:
        return "NULL"
    # Normalise numpy scalars (np.int64, np.float64, np.bool_) to Python builtins.
    np = _maybe_numpy()
    if np is not None and isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, DeferredRCall):
        return value.code
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, (int, float)):
        return str(value)
    # Raw R escape hatch (ggplotpy.R) — emit the source verbatim.
    from ggplotpy.core.raw import RObject

    if isinstance(value, RObject):
        return value.code
    if isinstance(value, dict):
        items = ", ".join(f"{k} = {format_r_value(v)}" for k, v in value.items())
        return f"list({items})"
    if np is not None and isinstance(value, np.ndarray):
        return "c(" + ", ".join(format_r_value(v) for v in value.tolist()) + ")"
    if isinstance(value, (list, tuple, range)):
        return "c(" + ", ".join(format_r_value(v) for v in value) + ")"
    from ggplotpy.backend.inprocess import r

    ro = r()
    return str(ro.r("deparse")(value)[0])


def format_r_call(package: str, symbol: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Build ``package::symbol(...)`` from Python call arguments."""
    parts = [format_r_value(a) for a in args]
    parts.extend(f"{k} = {format_r_value(v)}" for k, v in kwargs.items())
    inner = ", ".join(parts)
    if inner:
        return f"{package}::{symbol}({inner})"
    return f"{package}::{symbol}()"


def simplify_layer_code(code: str) -> str:
    """Normalize deferred layer code for to_r() bookkeeping."""
    from ggplotpy.core.to_r_util import format_layer_for_to_r

    return format_layer_for_to_r(code)
