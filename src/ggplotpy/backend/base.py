"""Backend protocol for R communication."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Backend(ABC):
    """Abstract interface for ggplotpy R backends (in-process, Rserve, subprocess)."""

    @abstractmethod
    def r(self) -> Any:
        """Return the rpy2 robjects module (or backend equivalent)."""

    @abstractmethod
    def r_pkg(self, name: str) -> Any:
        """Return importr handle for an R package."""

    @abstractmethod
    def rcall(self, rfun: Any, *args: Any, _hint: str | None = None, **kwargs: Any) -> Any:
        """Call an R function with ggplotpy error translation."""

    @abstractmethod
    def rx2(self, robj: Any, name: str) -> Any:
        """Return robj[[name]] across rpy2 object types."""

    @abstractmethod
    def eval_r(self, code: str) -> Any:
        """Evaluate an R expression string."""

    @abstractmethod
    def set_last_r_code(self, code: str) -> None:
        """Record the last R code executed (for error diagnostics)."""

    @abstractmethod
    def last_r_code(self) -> str | None:
        """Return the last recorded R code, if any."""
