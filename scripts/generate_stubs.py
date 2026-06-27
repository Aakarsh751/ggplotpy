#!/usr/bin/env python3
"""Introspect ggplot2 exports and write generated .pyi stubs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "src" / "ggplotpy" / "generated" / "ggplot2_reflected.pyi"
DEFAULT_LIMIT: int | None = None  # None = all getNamespaceExports("ggplot2")


def _r_runtime_available() -> bool:
    try:
        from ggplotpy.backend.inprocess import r

        r()
        return True
    except Exception:
        return False


def _ggplot2_available() -> bool:
    if not _r_runtime_available():
        return False
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        return bool(ro.r("isTRUE(requireNamespace('ggplot2', quietly=TRUE))")[0])
    except Exception:
        return False


def collect_exports(package: str, limit: int | None = None) -> list[dict]:
    from ggplotpy.codegen.reflect import list_namespace_exports, reflect_export

    exports = list_namespace_exports(package)
    selected = exports if limit is None else exports[:limit]
    return [reflect_export(package, name) for name in selected]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate ggplot2 .pyi stubs from R introspection")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output .pyi path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum exports to include (default: all getNamespaceExports)",
    )
    parser.add_argument(
        "--skip-if-no-r",
        action="store_true",
        help="Exit 0 without writing when R or ggplot2 is unavailable",
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(ROOT / "src"))

    if not _ggplot2_available():
        if args.skip_if_no_r:
            print("Skipping stub generation: R or ggplot2 not available", file=sys.stderr)
            return 0
        print(
            "Error: R with ggplot2 is required for stub generation "
            "(use --skip-if-no-r to no-op)",
            file=sys.stderr,
        )
        return 1

    from ggplotpy.codegen.emit import emit_pyi_module

    reflected = collect_exports("ggplot2", args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    emit_pyi_module("ggplot2", reflected, output_path=str(args.output))
    print(f"Wrote {len(reflected)} symbols to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
