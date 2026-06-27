# project_memory/

Live, append-only record of the **ggplotpy** project (`Ggplot2PY/`). Every work session must update at least `progress_log.md`.

| File | Purpose | Update cadence |
|------|---------|----------------|
| `decisions.md` | Architectural / process ADRs (`D-P001` …) | When a decision is made |
| `progress_log.md` | Chronological work log | **Every session** (start + end) |
| `discoveries.md` | Non-obvious findings about rpy2, ggplot2, NSE, packaging | When discovered |
| `blockers.md` | Open issues that prevent progress | When opened; move to Resolved, never delete |
| `lessons_learned.md` | Milestone-end insights | End of M0 / MVP / v0.1 / v0.5 / v1.0 |
| `resume_prompts.md` | Copy-paste LLM entry points (#1–#9) | When project state changes meaningfully |

## Mandatory session rules

1. **Append only.** Earlier entries are not edited or deleted — they form the audit trail.
2. **Start:** Read `STATUS.md`, last `progress_log` block, open `blockers.md`.
3. **End:** Append a session block; update `STATUS.md`; record pytest commands and pass/fail.
4. **Decisions:** New architecture or process choices → `decisions.md` before merge.
5. **Gotchas:** Reusable rpy2/ggplot2/NSE/packaging findings → `discoveries.md`.
6. **Blockers:** Open with ID (`B-P001` …); resolve by moving to Resolved section with date + fix.

## Session block template

Append to `progress_log.md`:

```markdown
## Session YYYY-MM-DD — <short title>
**Driver:** <human / agent>
**Milestone:** <M0/MVP/v0.1/…> · **Task ID:** <from STATUS.md>
**Goal:** …
### Started from
- Last completed: …
- Blockers consulted: …
### Files created/modified
- …
### Commands run + results
- `pytest …` → pass/fail
### Findings / discoveries
- → discoveries.md if reusable
### Decisions
- → decisions.md D-P00N if new
### Next actions (ordered)
1. …
```
