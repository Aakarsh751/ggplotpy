"""T0 (R-free) tests for the install/bootstrap surface."""

from __future__ import annotations

import sys

import pytest


def test_install_r_exposed_on_package():
    import ggplotpy

    assert callable(ggplotpy.install_r)


def test_profiles_include_all_and_core():
    from ggplotpy.runtime.bootstrap import _PROFILES

    assert {"core", "stretch", "examples", "all"} <= set(_PROFILES)
    assert "ggplot2" in _PROFILES["core"]
    assert "ggrepel" in _PROFILES["all"] and "sf" in _PROFILES["all"]


def test_no_r_guidance_is_cross_platform_and_mentions_conda():
    from ggplotpy.runtime.bootstrap import _no_r_guidance

    msg = _no_r_guidance()
    assert "conda install -c conda-forge" in msg
    # platform-specific hint present for the current OS
    if sys.platform == "win32":
        assert "R_HOME" in msg
    elif sys.platform == "darwin":
        assert "brew" in msg or "rig" in msg
    else:
        assert "R RHOME" in msg or "rig" in msg


def test_install_r_unknown_profile_raises():
    import importlib

    cs = importlib.import_module("ggplotpy.runtime.check_setup")
    from ggplotpy.runtime.bootstrap import install_r

    if not cs._r_available():
        pytest.skip("R not available; install_r would raise GgplotpySetupError first")
    with pytest.raises(ValueError, match="Unknown profile"):
        install_r("does-not-exist")
