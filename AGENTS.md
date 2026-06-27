# AGENTS.md — ggplotpy agent orientation

**Read this file first** in every session working on `Ggplot2PY/`.

## Mission

**ggplotpy** exposes R's **real ggplot2** (and its extension ecosystem) to Python via rpy2 — faithful `+` grammar, Pythonic `aes(x="col")`, Jupyter rendering, auto-generated wrappers for installed extensions.

## Non-goals

- **Not** a plotnine/matplotlib Grammar-of-Graphics reimplementation
- **Not** competing with plotnine for casual "ggplot syntax in Python"
- **Not** a method-call API (no `.add_scatter()` — pyggplot anti-pattern)
- **Not** vendored R in v1 wheels without legal review

**Audience:** biostat/academia/mixed R–Python teams needing ggrepel, patchwork, ggtree, survminer, exact R parity.

## Current milestone (2026-06-21)

| Release | Status |
|---------|--------|
| M0, MVP, **v0.1** | **Complete** locally |
| **v0.5** | **Mostly complete** — Arrow, `ggplotpy.ext`, patchwork, gganimate, tier3 notebooks |
| **v1.0** | In progress — PyPI/conda publish, sf, Rserve, expanded T3 gallery |

See `STATUS.md` for test counts and open v1.0 items.

## Architecture (Hybrid G — locked, D-P001)

Ergonomic core (hand-written) → reflection/codegen (643-export `.pyi`) → data plane (Arrow + pandas2ri) → backend (rpy2 in-process default) → R runtime (ggplot2 + `r-helper/ggplotpy`).

Full diagram: `docs/architecture.md`. Divergences require ADR before merge.

## 12-phase research map (summary)

| Phase | Topic | Status | Artifact |
|-------|-------|--------|----------|
| 1 | Market & competitive | Done (doc) | README positioning |
| 2 | Technical feasibility | Done (doc) | D-P001, NSE, data plane |
| 3 | Architecture (7 candidates) | **G Hybrid locked** | `docs/architecture.md` |
| 4 | API design | Spec + implementation | `docs/user_interface.md` |
| 5 | Wrapper generation | **Done** | `codegen/`, `generated/` — 643 exports |
| 6 | Packaging | Mostly done | `docs/packaging_plan.md` — bootstrap + recipe skeleton |
| 7 | Jupyter integration | Done | `_repr_svg_`, `display()` |
| 8 | Performance | Stub | `exploration/perf/` |
| 9 | OSS strategy | Active | CI, Apache-2, tier runners |
| 10 | Roadmap | Active | `docs/implementation_plan.md`, `STATUS.md` |
| 11 | Risk analysis | Living | `validation_strategy.md` |
| 12 | Go/No-Go | **Qualified GO** | Niche = R ecosystem + exact parity |

Full research: `RESEARCH_AND_PLAN.md`.

## Mandatory read order (resume)

1. `STATUS.md` — milestone, blockers, test counts
2. `project_memory/progress_log.md` — **last session block**
3. `project_memory/blockers.md`
4. `docs/implementation_plan.md` — current week/task
5. `docs/validation_strategy.md` — if touching tests
6. `project_memory/decisions.md` — active ADRs (`D-P001` …)

Optional: paste `project_memory/resume_prompts.md` #1.

## Session checklists

### Start

- [ ] Read files above
- [ ] State: milestone, task ID, files to touch, tier(s) that must pass
- [ ] Run fast loop: `GGPLOTPY_SKIP_NOTEBOOKS=1 pytest tests/unit -q`
- [ ] Wait for user OK on non-trivial work

### End

- [ ] Run task-appropriate tiers via `scripts/run_tests.ps1` (min tier0; render → tier1; aes/to_r/edge → tier2; notebooks → tier3)
- [ ] Append `project_memory/progress_log.md` session block
- [ ] Update `STATUS.md`
- [ ] Record discoveries / decisions / blockers as needed

## Test protocol (agents)

| Touch path | Minimum verification |
|------------|---------------------|
| `core/`, `aes`, errors | tier0 + relevant tier2 edge |
| render, geoms, integration | tier1 (subprocess runner) |
| `to_r()`, parity goldens | tier1 parity + tier2 NSE |
| notebooks | tier3 |
| docs only | Sphinx `-W` if user-facing site changed |

**Runner commands (Windows):**

```powershell
$env:R_HOME = "C:\Program Files\R\R-4.5.2"
$env:PATH = "C:\Program Files\R\R-4.5.2\bin\x64;" + $env:PATH
.\scripts\run_tests.ps1 -Tier tier0   # fast
.\scripts\run_tests.ps1 -Tier all     # full gate
```

**Env vars:** `GGPLOTPY_SKIP_INTEGRATION=1` (T0 CI), `GGPLOTPY_SKIP_NOTEBOOKS=1` (fast loop), `GGPLOTPY_RUN_HEAVY=1` (single-process — avoid on Windows).

**Honesty:** 15 geoms smoke-tested; 643 exports callable via reflection — do not claim full render coverage.

## Repository layout

```
Ggplot2PY/
├── AGENTS.md, STATUS.md, CHANGELOG.md, README.md, LICENSE
├── RESEARCH_AND_PLAN.md
├── project_memory/
├── docs/                    # Sphinx user site + engineering docs (see conf.py excludes)
├── src/ggplotpy/
│   ├── core/ backend/ data/ runtime/ codegen/ generated/ ext/
├── r-helper/ggplotpy/           # R companion (aes_from_strings)
├── tests/ unit/ integration/ parity/ edge/ extensions/ gallery/ notebooks/ golden/
├── exploration/             # perf, version sweeps (local/nightly)
├── notebooks/               # 01–03 gallery notebooks
└── .cursor/rules/ + .cursor/skills/ggplotpy-dev/
```

## Reference sibling project

[robstatm-py](../robstatm-py/) — rpy2 patterns: `_r.py`, lazy R, Windows R_HOME, Rd→JSON codegen, strict/exploration tiers, plot→bytes rendering. **Adapt, do not import.**

## Cursor rules & skill

- `.cursor/rules/ggplotpy-*.mdc` — layering, session, verification, R bridge, codegen, tests
- `.cursor/skills/ggplotpy-dev/SKILL.md` — workflow trigger for ggplotpy work
