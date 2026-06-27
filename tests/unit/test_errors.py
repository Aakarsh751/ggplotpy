"""T0 error hierarchy tests."""

import pytest

from ggplotpy.core.errors import GgplotpyError, GgplotpyRError, GgplotpySetupError


def test_ggplotpy_setup_error_missing_packages():
    err = GgplotpySetupError("missing ggplot2", missing=["ggplot2"])
    assert err.missing == ["ggplot2"]
    assert isinstance(err, GgplotpyError)


def test_ggplotpy_r_error_fields():
    err = GgplotpyRError("boom", r_traceback="trace", hint="check aes")
    assert err.r_traceback == "trace"
    assert err.hint == "check aes"
