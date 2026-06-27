"""Isolated subprocess rendering + subprocess backend stub.

The default in-process backend (:mod:`ggplotpy.backend.inprocess`) renders in the same
process as Python, so an R crash during a pathological render takes Python with it.
:func:`render_in_subprocess` renders a *finished* plot in a fresh ``Rscript`` child
process for crash isolation: the plot object is serialised with ``saveRDS`` (full
fidelity — factors, dates, CRS all preserved), then a tiny R script reads it back
and writes the image. Only base R + the plot's own packages are needed.

``GG.save(path, isolated=True)`` and ``GG.render_isolated()`` use this path.

The full IPC :class:`SubprocessBackend` (a persistent child R speaking a wire
protocol for *every* call) remains a v1.0 design target — see the class docstring.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from typing import Any

from ggplotpy.backend.base import Backend
from ggplotpy.core.errors import GgplotpyRError, GgplotpySetupError


def _rscript_path() -> str:
    """Locate the ``Rscript`` executable from R_HOME or rpy2."""
    r_home = os.environ.get("R_HOME")
    if not r_home:
        try:
            from rpy2.situation import get_r_home

            r_home = get_r_home()
        except Exception:
            r_home = None
    candidates = []
    if r_home:
        r_home = os.path.normpath(r_home)
        if sys.platform == "win32":
            candidates += [
                os.path.join(r_home, "bin", "x64", "Rscript.exe"),
                os.path.join(r_home, "bin", "Rscript.exe"),
            ]
        else:
            candidates.append(os.path.join(r_home, "bin", "Rscript"))
    candidates.append("Rscript.exe" if sys.platform == "win32" else "Rscript")
    for c in candidates:
        if os.path.sep in c and os.path.isfile(c):
            return c
    return candidates[-1]  # bare name; rely on PATH


def render_in_subprocess(
    plot_r_obj: Any,
    *,
    device: str = "png",
    width: float = 6.0,
    height: float = 4.0,
    dpi: int = 144,
    timeout: int = 120,
) -> str | bytes:
    """Render a built ggplot R object in an isolated ``Rscript`` process.

    Returns SVG text (``device="svg"``) or PNG bytes (``device="png"``). The plot is
    serialised in-process via ``saveRDS`` and rendered in a child process so a render
    crash cannot kill the Python interpreter.
    """
    from ggplotpy.backend.inprocess import r, set_last_r_code

    ro = r()
    rds = tempfile.NamedTemporaryFile(suffix=".rds", delete=False)
    rds.close()
    ext = "svg" if device == "svg" else "png"
    out = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
    out.close()
    rds_posix = rds.name.replace("\\", "/")
    out_posix = out.name.replace("\\", "/")

    if device == "svg":
        open_dev = f'svglite::svglite("{out_posix}", width={width}, height={height})'
    else:
        open_dev = (
            f'grDevices::png("{out_posix}", width={width}, height={height}, '
            f'units="in", res={dpi}, bg="white")'
        )
    script = (
        f'p <- readRDS("{rds_posix}"); '
        "suppressMessages(library(ggplot2)); "
        f"{open_dev}; print(p); grDevices::dev.off()"
    )

    try:
        ro.r.assign(".__ggplotpy_render_obj", plot_r_obj)
        set_last_r_code(f'saveRDS(plot, "{rds_posix}")')
        ro.r(f'saveRDS(.__ggplotpy_render_obj, "{rds_posix}")')

        rscript = _rscript_path()
        env = dict(os.environ)
        proc = subprocess.run(
            [rscript, "--vanilla", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if proc.returncode != 0 or not os.path.getsize(out.name):
            set_last_r_code(script)
            raise GgplotpyRError(
                "Isolated render failed in subprocess Rscript.\n"
                + (proc.stderr or proc.stdout or "no output"),
                r_code=script,
            )
        if device == "svg":
            with open(out.name, encoding="utf-8") as fh:
                return fh.read()
        with open(out.name, "rb") as fh:
            return fh.read()
    except FileNotFoundError as e:
        raise GgplotpySetupError(
            "Could not find Rscript. Set R_HOME or add R's bin directory to PATH."
        ) from e
    finally:
        for p in (rds.name, out.name):
            try:
                os.unlink(p)
            except OSError:
                pass


_MSG = (
    "Full subprocess IPC backend is a v1.0 design target; use backend.inprocess "
    "(default) for calls and render_in_subprocess() for isolated rendering."
)


class SubprocessBackend(Backend):
    """Persistent-child IPC backend — design target for v1.0.

    For *isolated rendering* today, use :func:`render_in_subprocess` (or
    ``GG.save(..., isolated=True)``), which renders a finished plot in a fresh
    ``Rscript`` process. A full call-level IPC backend (marshalling every
    ``rcall`` to a long-lived child over a wire protocol) is not yet implemented.
    """

    def r(self) -> Any:
        raise NotImplementedError(_MSG)

    def r_pkg(self, name: str) -> Any:
        raise NotImplementedError(_MSG)

    def rcall(self, rfun: Any, *args: Any, _hint: str | None = None, **kwargs: Any) -> Any:
        raise NotImplementedError(_MSG)

    def rx2(self, robj: Any, name: str) -> Any:
        raise NotImplementedError(_MSG)

    def eval_r(self, code: str) -> Any:
        raise NotImplementedError(_MSG)

    def set_last_r_code(self, code: str) -> None:
        raise NotImplementedError(_MSG)

    def last_r_code(self) -> str | None:
        raise NotImplementedError(_MSG)
