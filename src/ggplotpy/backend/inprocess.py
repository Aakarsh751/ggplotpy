"""In-process rpy2 backend (default)."""

from __future__ import annotations

import os
import sys
import threading
from typing import Any

from ggplotpy.core.errors import GgplotpyRError, GgplotpySetupError

_init_lock = threading.Lock()
_pkg_cache: dict[str, Any] = {}
_conversion_installed = False
_r_started = False
_windows_dll_path_done = False
_last_r_code: str | None = None


def set_last_r_code(code: str) -> None:
    """Record the most recent R code line for diagnostics."""
    global _last_r_code
    _last_r_code = code


def last_r_code() -> str | None:
    """Return the most recent R code line, if recorded."""
    return _last_r_code


def r_started() -> bool:
    """True once rpy2 conversion context is installed (side-effect free)."""
    return _r_started


def _ensure_windows_r_dll_path() -> None:
    """Prepend R bin/x64 to DLL search path on Windows."""
    global _windows_dll_path_done
    if _windows_dll_path_done or sys.platform != "win32":
        return
    _windows_dll_path_done = True

    r_home = os.environ.get("R_HOME")
    if not r_home:
        try:
            from rpy2.situation import get_r_home

            r_home = get_r_home()
        except Exception:
            return
    if not r_home:
        return

    r_bin = os.path.join(os.path.normpath(r_home), "bin", "x64")
    if not os.path.isdir(r_bin):
        return

    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(r_bin)
        except OSError:
            pass

    path = os.environ.get("PATH", "")
    if r_bin.lower() not in path.lower():
        os.environ["PATH"] = r_bin + os.pathsep + path


def _install_conversion() -> None:
    """Install default + numpy + pandas conversion context once."""
    global _conversion_installed, _r_started
    if _conversion_installed:
        return
    _ensure_windows_r_dll_path()
    try:
        from rpy2.robjects import default_converter, numpy2ri, pandas2ri
        from rpy2.robjects.conversion import set_conversion
    except ImportError as e:
        raise GgplotpySetupError(
            "rpy2 is not installed. Install with `pip install rpy2>=3.6`."
        ) from e
    cv = default_converter + numpy2ri.converter + pandas2ri.converter
    set_conversion(cv)
    _conversion_installed = True
    _r_started = True
    _force_noninteractive_r()


def _force_noninteractive_r() -> None:
    """Stop embedded R from blocking on interactive prompts.

    ggplot2/rlang call ``check_installed()`` for optional packages (e.g. hexbin
    for ``geom_hex``), which prompts "Would you like to install it?" and hangs an
    embedded session waiting on stdin. Forcing non-interactive mode turns those
    prompts into catchable errors instead of deadlocks.
    """
    try:
        import rpy2.robjects as ro

        ro.r(
            "options(rlang_interactive = FALSE, menu.graphics = FALSE, "
            "install.packages.check.source = 'no')"
        )
    except Exception:
        pass


def r() -> Any:
    """Return rpy2 robjects, initialising conversion if needed."""
    _install_conversion()
    import rpy2.robjects as ro

    return ro


def r_pkg(name: str) -> Any:
    """Return importr handle for an R package, caching after first call."""
    with _init_lock:
        if name in _pkg_cache:
            return _pkg_cache[name]

        _install_conversion()
        from rpy2.robjects.packages import PackageNotInstalledError, importr

        try:
            pkg = importr(name)
        except PackageNotInstalledError as e:
            raise GgplotpySetupError(
                f"R package '{name}' is not installed. "
                f"Run in R: install.packages('{name}')",
                missing=[name],
            ) from e
        except Exception as e:
            raise GgplotpySetupError(f"Failed to load R package '{name}': {e}") from e

        _pkg_cache[name] = pkg
        return pkg


def rcall(rfun: Any, *args: Any, _hint: str | None = None, **kwargs: Any) -> Any:
    """Call an R function, translating rpy2 errors into GgplotpyRError."""
    from rpy2.rinterface_lib.embedded import RRuntimeError

    from ggplotpy.core.defer import normalize_r_kwargs
    from ggplotpy.core.errors import format_r_error

    clean_kwargs = normalize_r_kwargs(kwargs)
    try:
        return rfun(*args, **clean_kwargs)
    except RRuntimeError as e:
        tb = None
        try:
            tb_obj = r().r("paste(geterrmessage())")
            tb = str(tb_obj[0]) if len(tb_obj) else None
        except Exception:
            tb = None
        code = last_r_code()
        msg = format_r_error(str(e), r_code=code, hint=_hint)
        raise GgplotpyRError(msg, r_traceback=tb, hint=_hint, r_code=code) from e


def rx2(robj: Any, name: str) -> Any:
    """Return robj[[name]] for rpy2 ListVectors or dict-like objects."""
    rx2_fn = getattr(robj, "rx2", None)
    if callable(rx2_fn):
        return rx2_fn(name)
    getbyname = getattr(robj, "getbyname", None)
    if callable(getbyname):
        return getbyname(name)
    if hasattr(robj, "__getitem__"):
        try:
            return robj[name]
        except (KeyError, TypeError):
            pass
    raise KeyError(f"field {name!r} not found on {type(robj).__name__}")


def eval_r(code: str) -> Any:
    """Evaluate an R expression string."""
    set_last_r_code(code)
    return r().r(code)


class InProcessBackend:
    """Concrete backend delegating to module-level rpy2 helpers."""

    def r(self) -> Any:
        return r()

    def r_pkg(self, name: str) -> Any:
        return r_pkg(name)

    def rcall(self, rfun: Any, *args: Any, _hint: str | None = None, **kwargs: Any) -> Any:
        return rcall(rfun, *args, _hint=_hint, **kwargs)

    def rx2(self, robj: Any, name: str) -> Any:
        return rx2(robj, name)

    def eval_r(self, code: str) -> Any:
        return eval_r(code)

    def set_last_r_code(self, code: str) -> None:
        set_last_r_code(code)

    def last_r_code(self) -> str | None:
        return last_r_code()


_DEFAULT_BACKEND = InProcessBackend()


def get_backend() -> InProcessBackend:
    """Return the active in-process backend singleton."""
    return _DEFAULT_BACKEND
