"""Python-side aes string normalization (T0 goldens)."""

from __future__ import annotations


def normalize_aes_mapping(mapping: dict[str, str]) -> dict[str, str]:
    """Normalize aes kwargs for golden comparison (pure Python, R-free)."""
    out: dict[str, str] = {}
    for key, value in mapping.items():
        k = key.replace("colour", "color") if key == "colour" else key
        out[k] = " ".join(str(value).split())
    return dict(sorted(out.items()))


def _escape_r_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def format_aes_r_fragment(mapping: dict[str, str]) -> str:
    """Format mapping as an R aes_from_strings call fragment for goldens."""
    norm = normalize_aes_mapping(mapping)
    if not norm:
        return "aes_from_strings()"
    parts = [f'{k} = "{_escape_r_string(v)}"' for k, v in norm.items()]
    return "aes_from_strings(" + ", ".join(parts) + ")"
