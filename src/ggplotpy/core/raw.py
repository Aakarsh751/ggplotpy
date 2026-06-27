"""R code escape hatch — composable raw R snippets."""

from __future__ import annotations

from typing import Any


class RObject:
    """Wrapper around evaluated or deferred R code."""

    __slots__ = ("_code", "_obj")

    def __init__(self, code: str, obj: Any | None = None) -> None:
        self._code = code.strip()
        self._obj = obj

    @property
    def code(self) -> str:
        return self._code

    def eval(self) -> Any:
        if self._obj is not None:
            return self._obj
        from ggplotpy.backend.inprocess import eval_r

        self._obj = eval_r(self._code)
        return self._obj

    def __repr__(self) -> str:
        return f"RObject({self._code!r})"


def R(code: str) -> RObject:
    """Evaluate R code and return a composable wrapper."""
    from ggplotpy.backend.inprocess import eval_r, set_last_r_code

    code = code.strip()
    set_last_r_code(code)
    return RObject(code, eval_r(code))
