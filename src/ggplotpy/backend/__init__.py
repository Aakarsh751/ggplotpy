"""Backend package."""

from ggplotpy.backend.inprocess import (
    InProcessBackend,
    eval_r,
    get_backend,
    last_r_code,
    r,
    r_pkg,
    rcall,
    r_started,
    rx2,
    set_last_r_code,
)

__all__ = [
    "InProcessBackend",
    "eval_r",
    "get_backend",
    "last_r_code",
    "r",
    "r_pkg",
    "rcall",
    "r_started",
    "rx2",
    "set_last_r_code",
]
