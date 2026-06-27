"""ggplot2 Rd → JSON extractor (v0.1 stub).

Pilot for the Rd → docstrings pipeline (``docs/documentation_plan.md`` M1).
Parses installed ggplot2 ``man/*.Rd`` files into JSON under ``docs/_rd_json/``.

Adapted minimally from robstatm-py ``docs/scripts/extract_rd.py`` — same JSON
schema so a future ``render_rd.py`` can stay extractor-agnostic.

Usage::

    python docs/scripts/extract_rd.py --name geom_point
    python docs/scripts/extract_rd.py --all --limit 50
    python docs/scripts/extract_rd.py --all --skip-if-no-r

Requires R with **ggplot2** installed (or ``GGPLOTPY_GGLOT2_MAN_DIR`` pointing at
``ggplot2/man``).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "_rd_json"
DEFAULT_LIMIT = 50


def _r_runtime_available() -> bool:
    try:
        sys.path.insert(0, str(ROOT / "src"))
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


def _ggplot2_man_dir() -> Path | None:
    override = os.environ.get("GGPLOTPY_GGLOT2_MAN_DIR")
    if override:
        path = Path(override)
        return path if path.is_dir() else None
    if not _ggplot2_available():
        return None
    try:
        from ggplotpy.backend.inprocess import r

        ro = r()
        raw = ro.r('system.file("man", package="ggplot2")')[0]
        path = Path(str(raw))
        return path if path.is_dir() else None
    except Exception:
        return None


def _read_balanced(text: str, start: int) -> tuple[str, int]:
    assert text[start] == "{"
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
        i += 1
    raise ValueError(f"unbalanced braces starting at {start}")


def _find_macro(text: str, name: str) -> tuple[str, int, int] | None:
    pat = re.compile(r"\\" + re.escape(name) + r"\{")
    m = pat.search(text)
    if m is None:
        return None
    inside, end = _read_balanced(text, m.end() - 1)
    return inside, m.start(), end


def _find_all_macros(text: str, name: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    pat = re.compile(r"\\" + re.escape(name) + r"\{")
    pos = 0
    while True:
        m = pat.search(text, pos)
        if m is None:
            break
        inside, end = _read_balanced(text, m.end() - 1)
        out.append((inside, m.start(), end))
        pos = end
    return out


_INLINE_PATTERNS = [
    (re.compile(r"\\code\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\verb\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\emph\{([^{}]*)\}"), r"*\1*"),
    (re.compile(r"\\bold\{([^{}]*)\}"), r"**\1**"),
    (re.compile(r"\\strong\{([^{}]*)\}"), r"**\1**"),
    (re.compile(r"\\pkg\{([^{}]*)\}"), r"**\1**"),
    (re.compile(r"\\link\[[^\]]*\]\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\link\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\url\{([^{}]*)\}"), r"<\1>"),
    (re.compile(r"\\R\b"), "R"),
]


def _to_text(rd_fragment: str) -> str:
    s = rd_fragment
    for _ in range(5):
        prev = s
        for pat, repl in _INLINE_PATTERNS:
            s = pat.sub(repl, s)
        if s == prev:
            break
    s = re.sub(r"^%.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _split_items(block: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    pos = 0
    while True:
        m = re.search(r"\\item\{", block[pos:])
        if m is None:
            break
        start = pos + m.start()
        name_inside, name_end = _read_balanced(block, start + len("\\item"))
        i = name_end
        while i < len(block) and block[i].isspace():
            i += 1
        if i >= len(block) or block[i] != "{":
            pos = name_end
            continue
        desc_inside, desc_end = _read_balanced(block, i)
        items.append((name_inside.strip(), _to_text(desc_inside)))
        pos = desc_end
    return items


@dataclass
class RdRecord:
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    title: str = ""
    description: str = ""
    usage: str = ""
    arguments: list[dict] = field(default_factory=list)
    value: list[dict] = field(default_factory=list)
    details: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    examples_r: str = ""
    seealso: list[str] = field(default_factory=list)
    references: str = ""
    keywords: list[str] = field(default_factory=list)
    author: str = ""


def parse_rd(path: Path) -> RdRecord:
    text = path.read_text(encoding="utf-8")
    rec = RdRecord()

    if (m := _find_macro(text, "name")):
        rec.name = m[0].strip()
    rec.aliases = [inside.strip() for inside, _, _ in _find_all_macros(text, "alias")]
    if (m := _find_macro(text, "title")):
        rec.title = _to_text(m[0])
    if (m := _find_macro(text, "description")):
        rec.description = _to_text(m[0])
    if (m := _find_macro(text, "usage")):
        rec.usage = m[0].strip()
    if (m := _find_macro(text, "arguments")):
        rec.arguments = [{"r_name": n, "description": d} for n, d in _split_items(m[0])]
    if (m := _find_macro(text, "value")):
        rec.value = [{"r_name": n, "description": d} for n, d in _split_items(m[0])]
    if (m := _find_macro(text, "details")):
        rec.details = _to_text(m[0])
    if (m := _find_macro(text, "references")):
        rec.references = _to_text(m[0])
    if (m := _find_macro(text, "author")):
        rec.author = _to_text(m[0])
    if (m := _find_macro(text, "examples")):
        rec.examples_r = m[0].strip()

    pos = 0
    while True:
        m = re.search(r"\\section\{", text[pos:])
        if m is None:
            break
        start = pos + m.start()
        name_inside, name_end = _read_balanced(text, start + len("\\section"))
        i = name_end
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            pos = name_end
            continue
        body_inside, body_end = _read_balanced(text, i)
        rec.sections[name_inside.strip()] = _to_text(body_inside)
        pos = body_end

    if (m := _find_macro(text, "seealso")):
        rec.seealso = [inside for inside, _, _ in _find_all_macros(m[0], "link")]

    rec.keywords = [inside for inside, _, _ in _find_all_macros(text, "keyword")]
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Extract ggplot2 Rd pages to JSON")
    ap.add_argument("--name", help="single Rd to extract (without .Rd)")
    ap.add_argument("--all", action="store_true", help="extract every Rd (respect --limit)")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="max files for --all")
    ap.add_argument(
        "--skip-if-no-r",
        action="store_true",
        help="Exit 0 without writing when R or ggplot2 is unavailable",
    )
    args = ap.parse_args(argv)

    man_dir = _ggplot2_man_dir()
    if man_dir is None:
        if args.skip_if_no_r:
            print("Skipping Rd extraction: R or ggplot2 not available", file=sys.stderr)
            return 0
        print(
            "Error: ggplot2 man/ directory not found "
            "(install ggplot2 or set GGPLOTPY_GGLOT2_MAN_DIR)",
            file=sys.stderr,
        )
        return 1

    if args.name:
        targets = [man_dir / f"{args.name}.Rd"]
    elif args.all:
        targets = sorted(man_dir.glob("*.Rd"))[: args.limit]
    else:
        ap.error("pass --name <RName> or --all")
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for rd in targets:
        if not rd.exists():
            print(f"[MISS] {rd.name}")
            continue
        rec = parse_rd(rd)
        out = OUT_DIR / f"{rec.name or rd.stem}.json"
        out.write_text(json.dumps(asdict(rec), indent=2), encoding="utf-8")
        written += 1
        print(f"[OK]   {rd.name:<35s} -> {out.relative_to(ROOT)}")

    print(f"\nwrote {written} JSON file(s) to {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
