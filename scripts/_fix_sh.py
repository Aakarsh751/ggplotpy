from pathlib import Path
p = Path(r"c:\ProfDM_Rproject\Ggplot2PY\scripts\run_tests.sh")
t = p.read_text(encoding="utf-8")
t = t.replace(
    "  unset GGPLOTPY_SKIP_INTEGRATION\n  export GGPLOTPY_RUN_HEAVY=1\n",
    "  unset GGPLOTPY_SKIP_INTEGRATION\n  unset GGPLOTPY_RUN_HEAVY 2>/dev/null || true\n",
)
if "run_heavy" not in t:
    t = t.replace(
        "code=0\ncase",
        """run_heavy() {
  echo "=== Heavy (full tree, single process - may OOM) ==="
  export GGPLOTPY_RUN_HEAVY=1
  unset GGPLOTPY_SKIP_INTEGRATION 2>/dev/null || true
  python -m pytest tests/ -q -m "not slow"
}

code=0
case""",
    )
    t = t.replace("  all)\n", "  heavy) run_heavy || code=$? ;;\n  all)\n")
    t = t.replace("[tier0|tier1|all]", "[tier0|tier1|all|heavy]")
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
