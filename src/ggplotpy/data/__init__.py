"""Data plane."""

from __future__ import annotations

from typing import Any

from ggplotpy.data.pandas_bridge import pandas_to_r

__all__ = ["pandas_to_r", "arrow_to_r", "polars_to_r"]


def __getattr__(name: str) -> Any:
    if name == "arrow_to_r":
        from ggplotpy.data.arrow import arrow_to_r as fn

        return fn
    if name == "polars_to_r":
        from ggplotpy.data.polars_bridge import polars_to_r as fn

        return fn
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
