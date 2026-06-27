"""Polars → Arrow → R ingress."""

from __future__ import annotations

from typing import Any


def polars_to_r(df: Any) -> Any:
    """Convert a polars DataFrame to R via Arrow."""
    try:
        import polars as pl
    except ImportError as e:
        raise ImportError(
            "polars is required. Install with `pip install ggplotpy[polars]`."
        ) from e

    if not isinstance(df, pl.DataFrame):
        raise TypeError(f"Expected polars DataFrame, got {type(df).__name__}")

    from ggplotpy.data.arrow import arrow_to_r

    return arrow_to_r(df.to_arrow())
