"""Rserve backend stub (planned v1.0).

``RserveBackend`` will connect to a remote R session over TCP (Rserve protocol)
so ggplotpy can run in environments where in-process rpy2 is undesirable (e.g.
Databricks driver isolation, shared R pool).

Planned surface (mirrors :class:`ggplotpy.backend.base.Backend`):

* ``r()`` — rpy2-compatible proxy bound to the remote session
* ``r_pkg(name)`` — lazy namespace import on the remote side
* ``rcall(rfun, *args, **kwargs)`` — marshalled function calls
* ``eval_r(code)`` — evaluate R source remotely
* ``set_last_r_code`` / ``last_r_code`` — diagnostics parity with in-process

Not implemented in v0.x — use :mod:`ggplotpy.backend.inprocess` (default).
"""

from __future__ import annotations

from typing import Any

from ggplotpy.backend.base import Backend

_MSG = "Rserve backend is planned for ggplotpy v1.0; use backend.inprocess for now."


class RserveBackend(Backend):
    """Remote R via Rserve — stub until v1.0."""

    def r(self) -> Any:
        """Return rpy2 robjects module backed by an Rserve connection."""
        raise NotImplementedError(_MSG)

    def r_pkg(self, name: str) -> Any:
        """Import an R package namespace on the remote Rserve session."""
        raise NotImplementedError(_MSG)

    def rcall(self, rfun: Any, *args: Any, _hint: str | None = None, **kwargs: Any) -> Any:
        """Call an R function on the remote session with ggplotpy error translation."""
        raise NotImplementedError(_MSG)

    def rx2(self, robj: Any, name: str) -> Any:
        """Return ``robj[[name]]`` from a remote R object."""
        raise NotImplementedError(_MSG)

    def eval_r(self, code: str) -> Any:
        """Evaluate an R expression string on the remote session."""
        raise NotImplementedError(_MSG)

    def set_last_r_code(self, code: str) -> None:
        """Record the last R code sent to Rserve (for error diagnostics)."""
        raise NotImplementedError(_MSG)

    def last_r_code(self) -> str | None:
        """Return the last recorded R code, if any."""
        raise NotImplementedError(_MSG)
