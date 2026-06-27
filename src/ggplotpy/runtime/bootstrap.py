"""Bootstrap R dependencies for ggplotpy."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from ggplotpy.runtime.check_setup import CORE_R_PACKAGES, STRETCH_R_PACKAGES, check_setup

# Blessed extension packages installed by the "all" profile.
BLESSED_EXTENSIONS = ["ggrepel", "patchwork", "gganimate", "ggthemes", "ggdist", "ggpubr", "sf"]

_PROFILES: dict[str, list[str]] = {
    "core": CORE_R_PACKAGES,
    "stretch": CORE_R_PACKAGES + STRETCH_R_PACKAGES,
    "examples": CORE_R_PACKAGES + ["ggrepel", "patchwork"],
    "all": CORE_R_PACKAGES + BLESSED_EXTENSIONS,
}


def _ggplotpy_r_helper_path() -> str:
    from pathlib import Path

    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent / "_r_helper" / "ggplotpy",  # packaged inside the wheel
        here.parents[3] / "r-helper" / "ggplotpy",       # source/editable checkout
    ]
    for c in candidates:
        if (c / "DESCRIPTION").is_file():
            return str(c).replace("\\", "/")
    return str(candidates[0]).replace("\\", "/")


def _install_packages(
    packages: Sequence[str],
    *,
    repos: str = "https://cloud.r-project.org",
    quiet: bool = False,
) -> None:
    from ggplotpy.backend.inprocess import r
    from ggplotpy.runtime.check_setup import _package_installed

    ro = r()
    # Prefer prebuilt binaries on Windows/macOS (no compiler toolchain needed);
    # Linux installs from source as usual. This is the key cross-OS ease win.
    type_arg = ', type="binary"' if sys.platform in ("win32", "darwin") else ""
    q = ", quiet=TRUE" if quiet else ""
    cran = [p for p in packages if p != "ggplotpy" and not _package_installed(p)]
    if cran:
        pkgs = ", ".join(f'"{p}"' for p in cran)
        ro.r(f"install.packages(c({pkgs}), repos='{repos}'{type_arg}{q})")
    if "ggplotpy" in packages and not _package_installed("ggplotpy"):
        path = _ggplotpy_r_helper_path()
        ro.r(f'install.packages("{path}", repos=NULL, type="source"{q})')


def install_r(
    profile: str = "core",
    *,
    packages: Sequence[str] | None = None,
    repos: str = "https://cloud.r-project.org",
    quiet: bool = False,
) -> "SetupReport":
    """Provision R packages for ggplotpy from Python (reticulate-style, cross-platform).

    Verifies R is reachable, then installs the requested ``profile`` (or an explicit
    ``packages`` list) from CRAN — prebuilt **binaries** on Windows/macOS so no
    compiler is needed — plus ggplotpy's small R helper. Returns a
    :class:`~ggplotpy.runtime.check_setup.SetupReport`.

    Examples::

        import ggplotpy
        ggplotpy.install_r()            # core: ggplot2, rlang, svglite, ggplotpy helper
        ggplotpy.install_r("all")       # + ggrepel, patchwork, gganimate, sf, ...
        ggplotpy.install_r(packages=["ggridges"])

    If R itself is not found, raises :class:`GgplotpySetupError` with per-OS guidance —
    the fastest cross-platform path is ``conda install -c conda-forge r-base rpy2``.
    """
    from ggplotpy.core.errors import GgplotpySetupError
    from ggplotpy.runtime.check_setup import _r_available

    if not _r_available():
        raise GgplotpySetupError(_no_r_guidance())

    if packages is None:
        if profile not in _PROFILES:
            raise ValueError(f"Unknown profile {profile!r}. Choose from {list(_PROFILES)}")
        packages = _PROFILES[profile]
    else:
        packages = list(packages)
        if "ggplotpy" not in packages:
            packages = packages + ["ggplotpy"]

    _install_packages(packages, repos=repos, quiet=quiet)
    return check_setup(profile="core", verbose=False)


def _no_r_guidance() -> str:
    lines = [
        "R was not found. ggplotpy drives R's ggplot2, so an R runtime is required.",
        "",
        "Easiest cross-platform path (Windows / macOS / Linux):",
        "  conda install -c conda-forge r-base r-ggplot2 rpy2",
        "",
    ]
    if sys.platform == "win32":
        lines += [
            "Or install R from https://cran.r-project.org, then point ggplotpy at it:",
            '  $env:R_HOME = "C:\\Program Files\\R\\R-4.5.2"',
            '  $env:PATH   = "$env:R_HOME\\bin\\x64;" + $env:PATH',
        ]
    elif sys.platform == "darwin":
        lines += [
            "Or: brew install r   (or install rig: https://github.com/r-lib/rig)",
            "  export R_HOME=$(R RHOME)",
        ]
    else:
        lines += [
            "Or use your distro's R, or rig (https://github.com/r-lib/rig):",
            "  export R_HOME=$(R RHOME)",
        ]
    lines += ["", "Then run again:  python -m ggplotpy.runtime.bootstrap --profile core"]
    return "\n".join(lines)


def bootstrap(profile: str = "core", *, install: bool = True) -> bool:
    """Install and verify R packages for ggplotpy."""
    if profile not in _PROFILES:
        raise ValueError(f"Unknown profile {profile!r}. Choose from {list(_PROFILES)}")

    report = check_setup(profile=profile, verbose=False)
    if report.ok:
        print("ggplotpy bootstrap: environment OK")
        for msg in report.messages:
            print(f"  {msg}")
        return True

    if install and report.missing:
        print(f"Installing missing packages: {', '.join(report.missing)}")
        _install_packages(report.missing)

    report = check_setup(profile=profile, verbose=False)
    for msg in report.messages:
        print(f"  {msg}")
    if not report.ok:
        print("ggplotpy bootstrap: FAILED", file=sys.stderr)
        return False
    print("ggplotpy bootstrap: OK")
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Install R dependencies for ggplotpy")
    parser.add_argument(
        "--profile",
        choices=list(_PROFILES),
        default="core",
        help="Package set to install (default: core)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verify setup without installing",
    )
    args = parser.parse_args(argv)
    ok = bootstrap(args.profile, install=not args.check_only)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
