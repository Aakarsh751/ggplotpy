"""Pre-rpy2 data validation (validation_strategy case 7)."""

from __future__ import annotations

import re
from typing import Any

_SIMPLE_IDENT = re.compile(r"^[A-Za-z.][A-Za-z0-9_.]*$")
_DATA_DQ = re.compile(r'\.data\[\["([^"]+)"\]\]')
_DATA_SQ = re.compile(r"\.data\[\['([^']+)'\]\]")


def validate_pandas_df(df: Any) -> None:
    """Raise before contacting R when the frame cannot be plotted."""
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    if df.empty or len(df.columns) == 0:
        raise ValueError("DataFrame must not be empty")


def extract_column_refs(expr: str) -> set[str]:
    """Collect bare identifiers and .data[[\"col\"]] names from an aes string."""
    refs: set[str] = set()
    for pattern in (_DATA_DQ, _DATA_SQ):
        refs.update(pattern.findall(expr))
    stripped = expr.strip()
    if _SIMPLE_IDENT.match(stripped):
        refs.add(stripped)
    return refs


def validate_aes_columns(df: Any, mapping: dict[str, str]) -> None:
    """Raise when simple aes column references are absent from ``df``."""
    validate_pandas_df(df)
    cols = set(df.columns)
    missing: set[str] = set()
    for expr in mapping.values():
        for ref in extract_column_refs(expr):
            if ref not in cols:
                missing.add(ref)
    if missing:
        raise ValueError(
            f"Missing columns in aes mapping: {', '.join(sorted(missing))}"
        )
