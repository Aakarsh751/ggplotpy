from pathlib import Path
from datetime import date

root = Path(r"c:\ProfDM_Rproject\Ggplot2PY")
status = root / "STATUS.md"
text = status.read_text(encoding="utf-8")
old = "- [ ] T1"
new = "- [x] T1 integration green (OOM-safe tier1 runner; 3/3 files Windows R 4.5.2)"
if old in text and new not in text:
    # replace first T1 MVP line only
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("- [ ] T1") and "T2" in line:
            lines[i] = "- [x] T1 integration green (OOM-safe tier1 runner; Windows R 4.5.2)"
            lines.insert(i + 1, "- [ ] T2 parity green in CI")
            break
    text = "\n".join(lines) + "\n"
    status.write_text(text, encoding="utf-8", newline="\n")

log = root / "project_memory/progress_log.md"
block = f"""
---

## Session 2026-06-21 — OOM infrastructure + T1 validation

**Driver:** agent (OOM subagent)
**Milestone:** MVP
**Goal:** Stop subagent OOM from monolithic pytest; validate Tier0/Tier1 on Windows.

### OOM fixes

- `src/ggplotpy/core/gg.py` — UTF-8 docstring; `ro.r[\"+\"]` composition; `_render_plot` svglite/png + `try(dev.off(), silent=TRUE)` in `finally` always
- `r-helper/ggplotpy/R/aes.R` — `names(exprs) <- names(mapping)` (already present)
- `tests/conftest.py` — `GGPLOTPY_SKIP_INTEGRATION` collection gate; `GGPLOTPY_RUN_HEAVY`; module `mtcars_df`; `gc.collect()` after integration tests
- `scripts/run_tests.ps1`, `scripts/run_tests.sh` — Tier0 unit; Tier1 one subprocess per integration file; `heavy` opt-in full tree
- `pyproject.toml` — document env vars in pytest section
- `.github/workflows/ci.yml` — matrix `GGPLOTPY_SKIP_INTEGRATION=1`; separate `integration` job runs `run_tests.sh tier1`
- `docs/testing_guide.md` — OOM avoidance section
- `project_memory/discoveries.md` — root cause entry
- `src/ggplotpy/runtime/check_setup.py` — `CORE_R_PACKAGES`: ggplot2, rlang, svglite, ggplotpy

### Commands run + results (Windows, R 4.5.2)

```text
scripts/run_tests.ps1 -Tier tier0  -> exit 0 (26 passed, 1 skipped via direct pytest)
scripts/run_tests.ps1 -Tier tier1  -> exit 0
  PASS tests/integration/test_facets.py
  PASS tests/integration/test_r_escape.py
  PASS tests/integration/test_render_basic.py
```

### Next actions

1. Enable T2 parity in separate subprocess job (parity file isolated like T1).
2. Remove `continue-on-error` patterns once integration job stable on ubuntu.
"""
if "OOM infrastructure + T1 validation" not in log.read_text(encoding="utf-8"):
    log.write_text(log.read_text(encoding="utf-8").rstrip() + block, encoding="utf-8", newline="\n")
print("status/log updated")
