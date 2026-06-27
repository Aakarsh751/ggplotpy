"""Lazy-loaded ggplot2 symbol cache via reflection."""

from __future__ import annotations

from typing import Any, Callable

_SYMBOLS: dict[str, Callable[..., Any]] = {}
_EXPORTS_CACHE: list[str] | None = None


def _ggplot2_exports() -> list[str]:
    global _EXPORTS_CACHE
    if _EXPORTS_CACHE is not None:
        return _EXPORTS_CACHE
    from ggplotpy.codegen.reflect import list_namespace_exports

    _EXPORTS_CACHE = list_namespace_exports("ggplot2")
    return _EXPORTS_CACHE


def load_ggplot2_symbol(name: str) -> Callable[..., Any]:
    """Return a Python callable for a ggplot2 export, building on first use."""
    if name in _SYMBOLS:
        return _SYMBOLS[name]

    exports = _ggplot2_exports()
    if name not in exports:
        global _EXPORTS_CACHE
        from ggplotpy.codegen.reflect import list_namespace_exports

        _EXPORTS_CACHE = list_namespace_exports("ggplot2", use_cache=False)
        exports = _EXPORTS_CACHE
        if name not in exports:
            raise AttributeError(f"ggplot2 has no export {name!r}")

    from ggplotpy.codegen.reflect import build_ggplot2_callable

    _SYMBOLS[name] = build_ggplot2_callable(name)
    return _SYMBOLS[name]


def clear_symbol_cache() -> None:
    """Clear the reflection cache (testing helper)."""
    global _EXPORTS_CACHE
    _SYMBOLS.clear()
    _EXPORTS_CACHE = None
    from ggplotpy.codegen.reflect import clear_reflect_cache

    clear_reflect_cache()


__all__ = ["clear_symbol_cache", "load_ggplot2_symbol"]
