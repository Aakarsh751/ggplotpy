"""Environment checks for R, ggplot2, and ggplotpy R helper."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

CORE_R_PACKAGES = ["ggplot2", "rlang", "svglite", "ggplotpy"]

STRETCH_R_PACKAGES = ["ggrepel", "patchwork", "gganimate", "sf"]


@dataclass
class SetupReport:
    ok: bool
    r_version: str | None = None
    missing: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.ok


def _stdout_supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        "✓✗⚠".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _r_available() -> bool:
    try:
        from ggplotpy.backend.inprocess import r

        r()
        return True
    except Exception:
        return False


def _package_version(name: str) -> str | None:
    from ggplotpy.backend.inprocess import r

    ro = r()
    try:
        v = ro.r(
            f"tryCatch(as.character(packageVersion('{name}')), "
            f"error=function(e) NA_character_)"
        )
        s = v[0] if len(v) else None
        if s is None or (isinstance(s, str) and s in ("NA", "NA_character_")):
            return None
        return str(s)
    except Exception:
        return None


def _package_installed(name: str) -> bool:
    return _package_version(name) is not None


def _ggplotpy_helper_install_hint() -> str:
    from ggplotpy.runtime.bootstrap import _ggplotpy_r_helper_path

    path = _ggplotpy_r_helper_path()
    return (
        f'install.packages("{path}", repos = NULL, type = "source")  # ggplotpy R helper'
    )


def _format_report(
    *,
    r_version: str | None,
    core: list[tuple[str, str | None]],
    stretch: list[tuple[str, str | None]],
    missing_core: list[str],
    missing_stretch: list[str],
    r_error: str | None = None,
) -> list[str]:
    from ggplotpy import __version__ as ggplotpy_ver

    use_unicode = _stdout_supports_unicode()
    ok_mark = "✓" if use_unicode else "[OK]"
    bad_mark = "✗" if use_unicode else "[MISSING]"
    warn_mark = "⚠" if use_unicode else "[WARN]"

    lines = ["ggplotpy setup check", "=" * 16]
    lines.append(f"Python:  {sys.version.split()[0]}")
    lines.append(f"ggplotpy:    {ggplotpy_ver}")

    try:
        import rpy2

        rpy2_ver = getattr(rpy2, "__version__", "unknown")
    except ImportError:
        rpy2_ver = None
    lines.append(f"rpy2:    {rpy2_ver if rpy2_ver else '(missing — pip install rpy2>=3.6)'}")

    if r_error:
        lines.append(f"R:       (cannot start — {r_error})")
        lines.append("")
        lines.append("Fix R discovery:")
        if sys.platform == "win32":
            lines.append('  $env:R_HOME = "C:\\Program Files\\R\\R-4.x.x"')
            lines.append('  $env:PATH = "$env:R_HOME\\bin\\x64;" + $env:PATH')
        else:
            lines.append("  export R_HOME=$(R RHOME)")
        lines.append("  ggplotpy-bootstrap --profile core")
        lines.append("")
        lines.append("Result: NOT READY — R unavailable.")
        return lines

    lines.append(f"R:       {r_version or '(unknown)'}")

    for name, version in core:
        if version is None:
            lines.append(f"  {name:<12}  {'(not installed)':<28}  {bad_mark}")
        else:
            lines.append(f"  {name:<12}  {version:<28}  {ok_mark}")

    for name, version in stretch:
        if version is None:
            lines.append(
                f"  {name:<12}  {'(optional — not installed)':<28}  {warn_mark}"
            )
        else:
            lines.append(f"  {name:<12}  {version:<28}  {ok_mark}")

    if missing_core:
        cran = [p for p in missing_core if p != "ggplotpy"]
        lines.append("")
        lines.append("Missing CORE packages — run in R:")
        if cran:
            lines.append(f"  install.packages(c({', '.join(repr(p) for p in cran)}))")
        if "ggplotpy" in missing_core:
            lines.append(f"  {_ggplotpy_helper_install_hint()}")
        lines.append("")
        lines.append("Or from the shell:")
        lines.append("  ggplotpy-bootstrap --profile core")

    if missing_stretch:
        lines.append("")
        lines.append("Optional extension packages — install in R if needed:")
        lines.append(f"  install.packages(c({', '.join(repr(p) for p in missing_stretch)}))")

    lines.append("")
    if missing_core:
        lines.append("Result: NOT READY — core packages missing.")
    elif missing_stretch:
        lines.append("Result: READY for core plots. Some extensions unavailable.")
    else:
        lines.append("Result: READY — core and checked extensions installed.")
    return lines


def check_setup(*, profile: str = "core", verbose: bool = True) -> SetupReport:
    """Verify R runtime and required packages for the given profile."""
    missing: list[str] = []
    r_version: str | None = None

    if not _r_available():
        lines = _format_report(
            r_version=None,
            core=[(p, None) for p in CORE_R_PACKAGES],
            stretch=[],
            missing_core=["R"],
            missing_stretch=[],
            r_error="R is not available (set R_HOME and ensure rpy2 can start R)",
        )
        if verbose:
            print("\n".join(lines))
        return SetupReport(
            ok=False,
            missing=["R"],
            messages=lines,
        )

    from ggplotpy.backend.inprocess import r

    ro = r()
    try:
        r_version = str(ro.r("R.version.string")[0])
    except Exception as e:
        lines = _format_report(
            r_version=None,
            core=[(p, None) for p in CORE_R_PACKAGES],
            stretch=[],
            missing_core=["R"],
            missing_stretch=[],
            r_error=str(e),
        )
        if verbose:
            print("\n".join(lines))
        return SetupReport(ok=False, messages=lines)

    packages = list(CORE_R_PACKAGES)
    stretch_names: list[str] = []
    if profile == "stretch":
        stretch_names = list(STRETCH_R_PACKAGES)
        packages.extend(STRETCH_R_PACKAGES)
    elif profile == "examples":
        stretch_names = ["ggrepel", "patchwork"]
        packages.extend(stretch_names)

    core_status: list[tuple[str, str | None]] = []
    stretch_status: list[tuple[str, str | None]] = []
    for pkg in CORE_R_PACKAGES:
        version = _package_version(pkg)
        core_status.append((pkg, version))
        if version is None:
            missing.append(pkg)

    for pkg in stretch_names:
        version = _package_version(pkg)
        stretch_status.append((pkg, version))
        if version is None and profile == "stretch":
            missing.append(pkg)

    missing_core = [p for p in CORE_R_PACKAGES if not _package_installed(p)]
    missing_stretch = [p for p in stretch_names if not _package_installed(p)]

    lines = _format_report(
        r_version=r_version,
        core=core_status,
        stretch=stretch_status,
        missing_core=missing_core,
        missing_stretch=missing_stretch if stretch_names else [],
    )
    if verbose:
        print("\n".join(lines))

    ok = not missing_core
    return SetupReport(
        ok=ok,
        r_version=r_version,
        missing=missing_core if not ok else [],
        messages=lines,
    )
