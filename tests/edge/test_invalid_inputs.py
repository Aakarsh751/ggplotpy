"""Case 7 — invalid inputs rejected before rpy2 (T0)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from ggplotpy.data.validate import validate_aes_columns, validate_pandas_df


def test_empty_dataframe_raises_value_error():
    df = pd.DataFrame({"x": [], "y": []})
    with pytest.raises(ValueError, match="must not be empty"):
        validate_pandas_df(df)


def test_empty_dataframe_pandas_to_r_never_calls_r():
    from ggplotpy.data.pandas_bridge import pandas_to_r

    df = pd.DataFrame({"x": pd.Series([], dtype=float)})
    with patch("ggplotpy.backend.inprocess.r") as mock_r:
        with pytest.raises(ValueError, match="must not be empty"):
            pandas_to_r(df)
        mock_r.assert_not_called()


def test_non_dataframe_raises_type_error_before_r():
    from ggplotpy.data.pandas_bridge import pandas_to_r

    with patch("ggplotpy.backend.inprocess.r") as mock_r:
        with pytest.raises(TypeError, match="Expected pandas DataFrame"):
            pandas_to_r({"x": [1, 2]})
        mock_r.assert_not_called()


def test_missing_aes_column_raises_value_error():
    df = pd.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
    with pytest.raises(ValueError, match="Missing columns.*no_such_col"):
        validate_aes_columns(df, {"x": "no_such_col", "y": "y"})
