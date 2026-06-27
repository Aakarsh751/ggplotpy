# Implementation Rules

Mandatory checklist before writing or changing ggplotpy code. Skipping steps causes silent drift from real ggplot2 behavior.

---

## Pre-coding checklist (every feature)

1. **Read active ADRs** in `project_memory/decisions.md` (`D-P001` …).
2. **Confirm layer** — code belongs in `core/`, `backend/`, `data/`, etc. per `architecture.md`. No `importr` outside `backend/`.
3. **Identify verification tier** — state T0/T1/T2/T3 before coding (`validation_strategy.md`).
4. **Write or update tests first** when behavior is specifiable without R (T0) or with golden files (T2).
5. **State files to touch** and exit test command; wait for user OK on non-trivial work.

---

## Prohibitions

| Do not | Why |
|--------|-----|
| Reimplement ggplot2 in matplotlib/plotnine | Out of scope (AGENTS.md) |
| `.add_scatter()`-style method APIs | pyggplot anti-pattern |
| `importr("ggplot2")` at module import | D-P004; use lazy backend |
| Vendored R in wheels without legal review | D-P002, D-P010 |
| Catch bare `Exception` at API boundary | Translate specific R errors only |
| Skip pytest markers for R/extension deps | D-P009 |
| Update golden files without PR diff + log note | D-P007 |
| Hand-wrap every ggplot2 export long-term | Use reflection (Phase 5) |

---

## Backend / R bridge rules

- All R calls go through `backend/inprocess.py` (or pluggable backend interface).
- **Lazy init:** first plot pays R startup; `import ggplotpy` stays cheap.
- **Windows:** set `R_HOME` and R `bin` on PATH before rpy2 (see `testing_guide.md`).
- **Errors:** strip R traceback noise; expose message + `ggplotpy.last_r_code()`.
- **Rendering:** device → bytes in backend; core calls `_render(fmt=...)`.

---

## Core API rules

- **Star-import primary:** `from ggplotpy import *` must work for gallery notebooks.
- **`aes()`:** strings only on Python side; delegate to R helper (D-P003).
- **`+`:** append layers; return new `GG` or layer-composable type consistently.
- **`R("...")`:** escape hatch for 100% coverage; must work in integration tests.
- **`to_r()`:** emit idiomatic R script; T2 goldens are the contract.

---

## Codegen rules

- Build-time codegen for ggplot2 → committed `generated/` + `.pyi`.
- Runtime reflection for other packages → `ext/` lazy load.
- CI fails if generated tree stale vs introspection.
- Regenerate on ggplot2 version bump; test 3.5.x and 4.0.x.

---

## Session hygiene

- Append `project_memory/progress_log.md` session block.
- Update `STATUS.md`.
- Discoveries → `discoveries.md`; blockers → `blockers.md`; architecture changes → ADR.

---

## Reference

RobStatTM-Py patterns: `robstatm-py/docs/implementation_rules.md` (adapted for plotting, not wrappers).
