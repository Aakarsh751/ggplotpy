"""Rd JSON → markdown docstring fragment (v0.1 M2 stub).

Reads ``docs/_rd_json/*.json`` produced by ``extract_rd.py`` and emits a
minimal markdown fragment suitable for embedding in generated Python stubs.

Usage::

    python docs/scripts/render_rd.py --name geom_point
    python docs/scripts/render_rd.py --name geom_point --out /tmp/geom_point.md

Full M2 pipeline (inject into ``codegen/emit.py``) is not wired yet.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_DIR = ROOT / "docs" / "_rd_json"


def record_to_markdown(rec: dict) -> str:
    """Convert one Rd JSON record to a markdown docstring body."""
    lines: list[str] = []
    title = rec.get("title") or rec.get("name", "")
    if title:
        lines.append(title.strip())
        lines.append("")
    desc = rec.get("description", "").strip()
    if desc:
        lines.append(desc)
        lines.append("")
    usage = rec.get("usage", "").strip()
    if usage:
        lines.append("**Usage**")
        lines.append("")
        lines.append(f"    {usage}")
        lines.append("")
    args = rec.get("arguments") or []
    if args:
        lines.append("**Arguments**")
        lines.append("")
        for arg in args:
            name = arg.get("r_name", "")
            body = arg.get("description", "").strip()
            lines.append(f"- ``{name}`` — {body}" if body else f"- ``{name}``")
        lines.append("")
    examples = rec.get("examples_r", "").strip()
    if examples:
        lines.append("**Examples (R)**")
        lines.append("")
        lines.append("```r")
        lines.extend(examples.splitlines())
        lines.append("```")
    return "\n".join(lines).strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render Rd JSON to markdown fragment")
    ap.add_argument("--name", required=True, help="Rd basename (matches JSON filename)")
    ap.add_argument("--out", type=Path, help="write markdown here (default: stdout)")
    args = ap.parse_args(argv)

    src = JSON_DIR / f"{args.name}.json"
    if not src.exists():
        print(f"Error: {src} not found (run extract_rd.py first)", file=sys.stderr)
        return 1

    rec = json.loads(src.read_text(encoding="utf-8"))
    md = record_to_markdown(rec)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md + "\n", encoding="utf-8")
        print(f"Wrote {args.out.relative_to(ROOT)}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
