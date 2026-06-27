"""Push pandas DataFrames to R."""

from __future__ import annotations

from typing import Any


def pandas_to_r(df: Any) -> Any:
    """Convert a pandas DataFrame to an R data.frame via pandas2ri."""
    from ggplotpy.backend.inprocess import r
    from ggplotpy.data.validate import validate_pandas_df

    validate_pandas_df(df)
    ro = r()
    from rpy2.robjects import conversion

    with conversion.localconverter(conversion.get_conversion()):
        return conversion.get_conversion().py2rpy(df)
