"""ggplotpy — real ggplot2 from Python via rpy2.

Primary import style (recommended in docs and gallery)::

    from ggplotpy import *

    p = (ggplot(df)
         + aes(x="wt", y="mpg")
         + geom_point()
         + theme_minimal())

Namespaced imports are always supported::

    import ggplotpy as gg

    p = gg.ggplot(df) + gg.aes(x="wt", y="mpg") + gg.geom_point()

After an R error, inspect the failing line with ``last_r_code()`` or read
``str(exception)`` on :class:`ggplotpy.core.errors.GgplotpyRError`.

ggplot2 symbols not listed in ``__all__`` (e.g. ``geom_bar``) resolve lazily via
``__getattr__`` → :func:`ggplotpy.generated.load_ggplot2_symbol` when accessed as
``ggplotpy.geom_bar``. Star-import exposes only ``__all__``; use attribute access or
add names to your namespace explicitly for other exports.
"""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"

_GGLOT2_CORE = (
    "geom_point",
    "geom_smooth",
    "theme_minimal",
    "scale_color_brewer",
    "facet_wrap",
    "facet_grid",
    "labs",
    "ggtitle",
    "xlab",
    "ylab",
    "guides",
    "guide_legend",
    "coord_fixed",
    "stat_summary",
    "element_text",
    "element_blank",
)

_LAZY_EXPORTS = {
    "aes": "ggplotpy.core.aes",
    "ggplot": "ggplotpy.core.gg",
    "GG": "ggplotpy.core.gg",
    "R": "ggplotpy.core.raw",
    "check_setup": "ggplotpy.runtime.check_setup",
    "install_r": "ggplotpy.runtime.bootstrap",
    "display": "ggplotpy.display",
    "last_r_code": "ggplotpy.core.errors",
    "set_options": "ggplotpy.core._options",
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        import importlib

        mod_name = _LAZY_EXPORTS[name]
        mod = importlib.import_module(mod_name)
        if name == "last_r_code":
            obj = mod.last_r_code
        elif name == "set_options":
            obj = mod.set_options
        elif name == "check_setup":
            obj = mod.check_setup
        elif name == "install_r":
            obj = mod.install_r
        elif name == "display":
            obj = mod.display
        elif name in ("ggplot", "GG"):
            obj = getattr(mod, name)
        elif name == "R":
            obj = mod.R
        else:
            obj = mod.aes
        globals()[name] = obj
        return obj
    try:
        from ggplotpy.generated import load_ggplot2_symbol

        fn = load_ggplot2_symbol(name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    globals()[name] = fn
    return fn


def __dir__() -> list[str]:
    return sorted(
        set(globals())
        | set(_GGLOT2_CORE)
        | set(_LAZY_EXPORTS)
        | {"__version__"}
    )


__all__ = [
    "GG",
    "R",
    "aes",
    "check_setup",
    "install_r",
    "display",
    "ggplot",
    "last_r_code",
    "set_options",
    "__version__",
    *_GGLOT2_CORE,
]
