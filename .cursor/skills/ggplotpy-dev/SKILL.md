---
name: ggplotpy-dev
description: >-
  Workflow for implementing or resuming ggplotpy (Ggplot2PY): Hybrid G ggplot2 bridge,
  governance memory, verification tiers T0–T3. Use when working in Ggplot2PY/,
  implementing ggplotpy features, or resuming ggplotpy sessions.
---

# ggplotpy development workflow

## When to use

- Working under `Ggplot2PY/`
- Implementing ggplotpy backend, core API, codegen, tests, or packaging
- Resuming after a break (paste `project_memory/resume_prompts.md` #1)

## Mandatory reads (in order)

1. `AGENTS.md`
2. `STATUS.md`
3. `project_memory/progress_log.md` (last block)
4. `project_memory/blockers.md`
5. `docs/implementation_plan.md` (current milestone)
6. `docs/validation_strategy.md` (if touching tests)

## Implement loop

1. **Plan** — state milestone, files, tier(s); user OK if non-trivial.
2. **Rules** — `docs/implementation_rules.md`; no `importr` outside `backend/`.
3. **Test first** — T0 goldens or T1 smoke as appropriate.
4. **Implement** — match layer in `docs/architecture.md`.
5. **Verify** — fast loop then full tier for touched paths (`docs/testing_guide.md`).
6. **Record** — `progress_log.md`, `STATUS.md`, `coverage_matrix.md` if API surface changed.

## Resume prompts

| # | Use when |
|---|----------|
| 1 | General resume |
| 2 | M0 scaffold (no pyproject.toml) |
| 3 | MVP core plot |
| 4 | NSE / R helper |
| 5 | Codegen pipeline |
| 6 | Packaging bootstrap |
| 7 | Extension smoke |
| 8 | Milestone gate |
| 9 | Pre-release verification |

## Windows rpy2

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
```

## Reference project

`../robstatm-py/` — rpy2, lazy R, Rd pipeline, strict tests. Adapt patterns; do not depend on robstatm_py.

## Non-goals

plotnine reimplementation; pyggplot method API; vendored R in v1 wheels.
