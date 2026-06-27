"""Emit .pyi stubs from R namespace exports."""

from __future__ import annotations

import keyword
from pathlib import Path
from typing import Any

_PY_KEYWORDS = keyword.kwlist


def _r_param_to_python(name: str) -> str:
    """Map an R formal name to a valid Python parameter identifier."""
    if name == "...":
        return "..."
    if name.isidentifier() and name not in _PY_KEYWORDS:
        return name
    if name in _PY_KEYWORDS:
        return f"{name}_"
    safe = name.replace(".", "_").replace("-", "_")
    if safe.isidentifier() and safe not in _PY_KEYWORDS:
        return safe
    return f'"{name}"'


def _function_def_name(name: str) -> str:
    if name.isidentifier():
        return name
    return f'"{name}"'


def formals_to_signature(formals: list[str] | None) -> str:
    """Build a Python parameter list from R ``formals()`` names."""
    if formals is None:
        return "*args: Any, **kwargs: Any"
    if not formals:
        return ""

    params: list[str] = []
    has_dots = "..." in formals
    for formal in formals:
        if formal == "...":
            continue
        py_name = _r_param_to_python(formal)
        if py_name.startswith('"'):
            params.append(f"{py_name}: Any = ...")
        else:
            params.append(f"{py_name}: Any = ...")

    if has_dots:
        tail = "*args: Any, **kwargs: Any"
        return ", ".join(params + [tail]) if params else tail
    if params:
        return ", ".join(params)
    return ""


def emit_pyi_stub(name: str, formals: list[str] | None = None, doc: str | None = None) -> str:
    """Return stub source for a single reflected R export."""
    sig = formals_to_signature(formals)
    def_name = _function_def_name(name)
    lines = [f"def {def_name}({sig}) -> Any:"]
    if doc:
        escaped = doc.replace('"""', '\\"\\"\\"')
        lines.append(f'    """{escaped}"""')
    lines.append("    ...")
    return "\n".join(lines)


def emit_pyi_module(
    module_name: str,
    exports: list[dict[str, Any]] | list[str],
    *,
    output_path: str | Path | None = None,
    header: str | None = None,
) -> str:
    """Return a full .pyi module and optionally write it to disk."""
    lines = [
        header or f"# Auto-generated stub for {module_name}",
        "# Regenerate with: python scripts/generate_stubs.py",
        "from typing import Any",
        "",
    ]
    for item in exports:
        if isinstance(item, str):
            lines.append(emit_pyi_stub(item))
        else:
            lines.append(
                emit_pyi_stub(
                    item["name"],
                    item.get("formals"),
                    item.get("doc"),
                )
            )
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return content
