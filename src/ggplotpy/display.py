"""Notebook display helpers (Jupyter, Databricks, IPython)."""

from __future__ import annotations

from typing import Any

from ggplotpy.core.gg import GG


def display(
    plot: GG,
    *,
    include: Any = None,
    exclude: Any = None,
) -> None:
    """Render a ggplotpy plot in the active notebook frontend.

    Uses the same mime bundle as ``GG._repr_mimebundle_`` (SVG by default,
    PNG when ``ggplotpy.set_options(format=\"png\")``). Works in Jupyter,
    Databricks notebook cells, and any IPython kernel with display support.
    """
    bundle = plot._repr_mimebundle_(include=include, exclude=exclude)
    try:
        from IPython.display import publish_display_data
    except ImportError as e:
        raise RuntimeError(
            "ggplotpy.display() requires IPython (Jupyter or Databricks notebook). "
            "Use p.save('out.png') or print(p.to_r()) in plain Python."
        ) from e
    publish_display_data(data=bundle, raw=True)
