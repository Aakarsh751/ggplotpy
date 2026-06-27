"""Runtime utilities."""

from ggplotpy.runtime.bootstrap import bootstrap, install_r, main
from ggplotpy.runtime.check_setup import CORE_R_PACKAGES, STRETCH_R_PACKAGES, SetupReport, check_setup

__all__ = [
    "CORE_R_PACKAGES",
    "STRETCH_R_PACKAGES",
    "SetupReport",
    "bootstrap",
    "check_setup",
    "install_r",
    "main",
]
