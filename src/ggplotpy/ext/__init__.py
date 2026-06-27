"""Lazy extension package access via R namespace reflection."""

from __future__ import annotations

from typing import Any, Callable

_EXT_CACHE: dict[str, Any] = {}

# Documented blessed extensions (import via ``ggplotpy.ext.<name>`` when installed).
KNOWN_EXTENSIONS = (
    "ggrepel",
    "patchwork",
    "gganimate",
    "ggthemes",
    "ggpubr",
    "ggdist",
    "survminer",
    "ggtree",
)


def _package_installed(name: str) -> bool:
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        return bool(ro.r(f'isTRUE(requireNamespace("{name}", quietly=TRUE))')[0])
    except Exception:
        return False


def list_installed_extensions(*, known_only: bool = True) -> list[str]:
    """Return extension package names that are installed in the current R library."""
    candidates = KNOWN_EXTENSIONS if known_only else sorted(_EXT_CACHE.keys())
    return [name for name in candidates if _package_installed(name)]


def __getattr__(name: str) -> Any:
    if name.startswith("_"):
        raise AttributeError(name)
    if name in {"KNOWN_EXTENSIONS", "list_installed_extensions"}:
        raise AttributeError(name)
    if name not in _EXT_CACHE:
        if not _package_installed(name):
            hint = f" Run in R: install.packages('{name}')"
            if name not in KNOWN_EXTENSIONS:
                hint += (
                    f". Known extensions: {', '.join(KNOWN_EXTENSIONS)}."
                )
            raise AttributeError(
                f"Extension package {name!r} is not installed.{hint}"
            )

        from ggplotpy.codegen.reflect import build_r_callable, list_namespace_exports

        try:
            exports = list_namespace_exports(name)
        except Exception as e:
            raise AttributeError(
                f"Extension package {name!r} has no namespace exports or failed to load"
            ) from e

        class _ExtModule:
            __slots__ = ("_package", "_exports")

            def __init__(self, package: str, export_names: list[str]) -> None:
                self._package = package
                self._exports = export_names

            def __getattr__(self, sym: str) -> Callable[..., Any]:
                if sym.startswith("_"):
                    raise AttributeError(sym)
                if sym not in self._exports:
                    raise AttributeError(f"{self._package} has no export {sym!r}")
                return build_r_callable(self._package, sym)

            def __dir__(self) -> list[str]:
                return sorted(self._exports)

            def __repr__(self) -> str:
                return f"<ggplotpy.ext.{self._package} ({len(self._exports)} exports)>"

        _EXT_CACHE[name] = _ExtModule(name, exports)
    return _EXT_CACHE[name]


def __dir__() -> list[str]:
    return sorted(set(_EXT_CACHE) | set(KNOWN_EXTENSIONS))
