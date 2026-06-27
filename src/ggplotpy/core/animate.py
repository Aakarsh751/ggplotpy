"""gganimate wrapper — transition layers and ``animate()`` → GIF bytes."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from ggplotpy.core.defer import DeferredRCall, format_r_call, format_r_value
from ggplotpy.core.errors import GgplotpySetupError
from ggplotpy.core.gg import GG


def transition_states(*, states: str, **kwargs: Any) -> DeferredRCall:
    """Deferred ``gganimate::transition_states`` with string ``states`` aes."""
    kwargs = dict(kwargs)
    kwargs["states"] = states
    code = format_r_call("gganimate", "transition_states", (), kwargs)
    return DeferredRCall(code)


def _require_gganimate() -> None:
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        ok = bool(ro.r('isTRUE(requireNamespace("gganimate", quietly=TRUE))')[0])
    except Exception as e:
        raise GgplotpySetupError(
            "Could not check for R package 'gganimate'. Ensure R is configured."
        ) from e
    if not ok:
        raise GgplotpySetupError(
            "R package 'gganimate' is not installed. Run in R: install.packages('gganimate')",
            missing=["gganimate"],
        )


def _require_gifski() -> None:
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        ok = bool(ro.r('isTRUE(requireNamespace("gifski", quietly=TRUE))')[0])
    except Exception as e:
        raise GgplotpySetupError(
            "Could not check for R package 'gifski'. Ensure R is configured."
        ) from e
    if not ok:
        raise GgplotpySetupError(
            "R package 'gifski' is required for GIF output. "
            "Run in R: install.packages('gifski')",
            missing=["gifski"],
        )


def animate(
    plot: GG | Any,
    *,
    width: int = 480,
    height: int = 480,
    fps: int = 10,
    nframes: int | None = None,
    duration: float | None = None,
    **kwargs: Any,
) -> bytes:
    """Render a gganimate plot to GIF bytes (requires gganimate + gifski).

    Renders in a single ``gganimate::animate(..., renderer = gifski_renderer(file))``
    call. Extra keyword arguments are forwarded to ``animate()`` (e.g. ``res``,
    ``start_pause``, ``end_pause``).
    """
    _require_gganimate()
    _require_gifski()

    from ggplotpy.backend.inprocess import r, set_last_r_code

    r_obj = plot.r_obj if isinstance(plot, GG) else plot
    ro = r()
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
        path = tmp.name
    posix = path.replace("\\", "/")

    parts = [
        ".__ggplotpy_plot",
        f'renderer = gganimate::gifski_renderer("{posix}")',
        f"width = {width}",
        f"height = {height}",
        f"fps = {fps}",
    ]
    if nframes is not None:
        parts.append(f"nframes = {format_r_value(nframes)}")
    if duration is not None:
        parts.append(f"duration = {format_r_value(duration)}")
    parts.extend(f"{k} = {format_r_value(v)}" for k, v in kwargs.items())
    call = "gganimate::animate(" + ", ".join(parts) + ")"

    try:
        ro.r.assign(".__ggplotpy_plot", r_obj)
        set_last_r_code(call)
        ro.r(call)
        with open(path, "rb") as fh:
            data = fh.read()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    if len(data) < 8:
        raise GgplotpySetupError("gganimate produced empty GIF output")
    return data
