"""ggplotpy error hierarchy and R diagnostic helpers."""

from __future__ import annotations


class GgplotpyError(Exception):
    """Base exception for ggplotpy."""


class GgplotpySetupError(GgplotpyError):
    """Environment or R package setup failure."""

    def __init__(self, message: str, *, missing: list[str] | None = None) -> None:
        super().__init__(message)
        self.missing = missing or []


class GgplotpyRError(GgplotpyError):
    """R runtime error surfaced through rpy2."""

    def __init__(
        self,
        message: str,
        *,
        r_traceback: str | None = None,
        hint: str | None = None,
        r_code: str | None = None,
    ) -> None:
        if r_code is None:
            r_code = last_r_code()
        super().__init__(message)
        self.r_traceback = r_traceback
        self.hint = hint
        self.r_code = r_code

    def __str__(self) -> str:
        msg = str(self.args[0])
        if "Offending R line:" in msg:
            return msg
        return format_r_error(msg, r_code=self.r_code, hint=self.hint)


def set_last_r_code(code: str) -> None:
    """Record the most recent R code line for diagnostics."""
    from ggplotpy.backend.inprocess import set_last_r_code as _set

    _set(code)


def last_r_code() -> str | None:
    """Return the most recent R code line, if recorded."""
    from ggplotpy.backend.inprocess import last_r_code as _last

    return _last()


def format_r_error(
    message: str,
    *,
    r_code: str | None = None,
    hint: str | None = None,
) -> str:
    """Build a concise user-facing R error string."""
    if r_code is None:
        r_code = last_r_code()
    lines = [message.rstrip()]
    if r_code:
        lines.extend(["", "Offending R line:", f"  {r_code}"])
    if hint:
        lines.extend(["", f"Hint: {hint}"])
    return "\n".join(lines)
