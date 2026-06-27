"""Whitespace normalization and readable R script helpers for to_r()."""

from __future__ import annotations

import re


def normalize_r_code(code: str) -> str:
    """Collapse whitespace and normalize line endings for golden comparison."""
    lines = [re.sub(r"\s+", " ", line.strip()) for line in code.strip().splitlines()]
    return "\n".join(line for line in lines if line)


def _unquote_aes_value(value: str) -> str:
    """Turn ``"wt"`` into ``wt`` for idiomatic ggplot2 aes() display."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"')
    return value


def _matching_paren(s: str, open_idx: int) -> int:
    """Return the index of the ``)`` matching the ``(`` at ``open_idx`` (quote-aware)."""
    depth = 0
    in_str = False
    i = open_idx
    while i < len(s):
        ch = s[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _split_top_level(inner: str) -> list[str]:
    """Split on top-level commas only — never inside nested parens or strings."""
    parts: list[str] = []
    cur: list[str] = []
    depth = 0
    in_str = False
    i = 0
    while i < len(inner):
        ch = inner[i]
        if in_str:
            cur.append(ch)
            if ch == "\\" and i + 1 < len(inner):
                cur.append(inner[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            cur.append(ch)
        elif ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    if cur:
        parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _render_aes_from_segments(inner: str) -> str:
    segments = _split_top_level(inner)
    if not segments:
        return "aes()"
    parts: list[str] = []
    for segment in segments:
        key, _, raw = segment.partition("=")
        parts.append(f"{key.strip()} = {_unquote_aes_value(raw.strip())}")
    return "aes(" + ", ".join(parts) + ")"


_AES_MARKER = "ggplotpy::aes_from_strings("


def _convert_aes_calls(code: str) -> str:
    """Rewrite every ``ggplotpy::aes_from_strings(...)`` to idiomatic ``aes(...)``.

    Handles top-level aes layers and aes nested inside another call such as
    ``geom_point(ggplotpy::aes_from_strings(color = "factor(cyl)"))`` and aes values
    that themselves contain commas (``label = "paste(a, b)"``).
    """
    while True:
        idx = code.find(_AES_MARKER)
        if idx == -1:
            return code
        open_idx = idx + len(_AES_MARKER) - 1
        close = _matching_paren(code, open_idx)
        if close == -1:
            return code
        inner = code[open_idx + 1 : close]
        replacement = _render_aes_from_segments(inner)
        code = code[:idx] + replacement + code[close + 1 :]


def format_layer_for_to_r(code: str) -> str:
    """Convert internal deferred layer code to readable ggplot2 R."""
    code = code.strip()
    if code.startswith("ggplot2::"):
        code = code[len("ggplot2::") :]
    return _convert_aes_calls(code)
