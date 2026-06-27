"""Introspect R ggplot2 exports and build Python callables."""

from __future__ import annotations

from typing import Any, Callable

from ggplotpy.backend.inprocess import set_last_r_code
from ggplotpy.core.defer import DeferredRCall, format_r_call, normalize_r_kwargs

_EXPORT_CACHE: dict[str, list[str]] = {}
_FORMALS_CACHE: dict[tuple[str, str], list[str]] = {}


def clear_reflect_cache() -> None:
    """Clear introspection caches (testing helper)."""
    _EXPORT_CACHE.clear()
    _FORMALS_CACHE.clear()


def list_namespace_exports(package: str, *, use_cache: bool = True) -> list[str]:
    """Return sorted export names for an installed R package."""
    if use_cache and package in _EXPORT_CACHE:
        return list(_EXPORT_CACHE[package])

    from ggplotpy.backend.inprocess import r

    ro = r()
    exports = sorted(str(x) for x in ro.r(f'getNamespaceExports("{package}")'))
    if use_cache:
        _EXPORT_CACHE[package] = exports
    return exports


def get_symbol_formals(package: str, symbol: str, *, use_cache: bool = True) -> list[str]:
    """Return formal parameter names for an R namespace export (includes ``...`` when present)."""
    key = (package, symbol)
    if use_cache and key in _FORMALS_CACHE:
        return list(_FORMALS_CACHE[key])

    from ggplotpy.backend.inprocess import r

    ro = r()
    names = ro.r(
        f"""
        (function() {{
          obj <- get("{symbol}", envir = asNamespace("{package}"))
          if (!is.function(obj)) return(character(0))
          nm <- names(formals(obj))
          if (is.null(nm)) character(0) else nm
        }})()
        """
    )
    formals = [str(x) for x in names]
    if use_cache:
        _FORMALS_CACHE[key] = formals
    return formals


def reflect_export(package: str, symbol: str) -> dict[str, Any]:
    """Return export metadata (formals + a short doc stub) for stub generation."""
    formals = get_symbol_formals(package, symbol)
    return {
        "name": symbol,
        "formals": formals,
        "doc": f"R {package}::{symbol}",
    }


def build_r_callable(package: str, symbol: str) -> Callable[..., Any]:
    """Build a Python callable that defers evaluation to R composition time."""

    def wrapper(*args: Any, **kwargs: Any) -> DeferredRCall:
        clean_kwargs = normalize_r_kwargs(kwargs)
        code = format_r_call(package, symbol, args, clean_kwargs)
        set_last_r_code(code)
        return DeferredRCall(code)

    wrapper.__name__ = symbol if symbol.isidentifier() else symbol.replace("%", "_")
    wrapper.__doc__ = f"R {package}::{symbol} (deferred wrapper)"
    return wrapper


def build_ggplot2_callable(symbol: str) -> Callable[..., Any]:
    """Build a callable for a ggplot2 export."""
    return build_r_callable("ggplot2", symbol)
