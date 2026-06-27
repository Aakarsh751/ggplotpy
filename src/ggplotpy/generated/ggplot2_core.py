"""Hand-curated ggplot2 core re-exports (M0)."""

from __future__ import annotations

from typing import Any, Callable

from ggplotpy.generated import load_ggplot2_symbol

_CORE_SYMBOLS = (
    "geom_point",
    "geom_smooth",
    "theme_minimal",
    "scale_color_brewer",
    "facet_wrap",
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


def __getattr__(name: str) -> Callable[..., Any]:
    if name in _CORE_SYMBOLS:
        fn = load_ggplot2_symbol(name)
        globals()[name] = fn
        return fn
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_CORE_SYMBOLS))
