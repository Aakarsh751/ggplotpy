"""Optional pyarrow zero-copy ingress."""

from __future__ import annotations

from typing import Any


def _zero_copy_via_rpy2(table: Any) -> Any | None:
    """Try rpy2's pyarrow converter (zero-copy when registered)."""
    try:
        from rpy2.robjects import conversion
    except ImportError:
        return None

    try:
        with conversion.localconverter(conversion.get_conversion()):
            return conversion.get_conversion().py2rpy(table)
    except (AttributeError, NotImplementedError, TypeError, ValueError):
        return None


def arrow_to_r(table: Any) -> Any:
    """Convert a pyarrow Table to an R data.frame.

    Preferred path: Arrow C interface via the R ``arrow`` package (zero-copy when
    both ``pyarrow`` and R ``arrow`` are installed). Falls back to pandas round-trip.
    """
    try:
        import pyarrow as pa
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for Arrow ingress. Install with `pip install ggplotpy[arrow]`."
        ) from e

    if not isinstance(table, (pa.Table, pa.RecordBatch)):
        raise TypeError(f"Expected pyarrow Table or RecordBatch, got {type(table).__name__}")

    zero_copy = _zero_copy_via_rpy2(table)
    if zero_copy is not None:
        return zero_copy

    from ggplotpy.backend.inprocess import r_pkg, rcall

    try:
        arrow_r = r_pkg("arrow")
        return rcall(arrow_r.as_data_frame, table)
    except Exception:
        import pandas as pd

        from ggplotpy.data.pandas_bridge import pandas_to_r

        return pandas_to_r(table.to_pandas() if hasattr(table, "to_pandas") else pd.DataFrame(table))
