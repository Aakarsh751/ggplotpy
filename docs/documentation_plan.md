# Documentation Plan

User-facing docs ship with Sphinx (furo) from `docs/`. Engineering docs stay in `docs/` but are **excluded** from the Sphinx toctree (see `conf.py`).

Pattern adapted from robstatm-py Rd pipeline (D-P017 analogue).

---

## Pipeline overview

```
ggplot2 .Rd  →  extract_rd.py  →  JSON (docs/_rd_json/)
JSON + formals()  →  render_rd.py  →  markdown fragments (M2 stub)
Python modules  →  autodoc (future)  →  Sphinx HTML
Hand-curated MyST  →  guides + getting-started  →  Sphinx HTML (today)
```

**Dual source of truth (target):**

- R `.Rd` — what the function *does* (description, params, examples)
- Python autodoc — how to call from Python (signature, `aes` strings, ergonomic extras)

---

## Milestones

| ID | Deliverable | Status | Release |
|----|-------------|--------|---------|
| M1 | `docs/scripts/extract_rd.py` → JSON per ggplot2 export | **Done** (pilot; `--limit 50` default) | v0.1 |
| M2 | `docs/scripts/render_rd.py` + Jinja → markdown fragments | **Stub** — not wired into `codegen/emit.py` | v0.1 |
| M3 | Sphinx scaffold (`docs/`, furo, `conf.py`) | **Done** — builds `-W` without R | v0.1 |
| M4 | Render all exports; `validate_docs.py` for broken links | **Not started** | v0.1+ |
| M5 | Gallery notebooks → nbsphinx; mirror ggplot2 gallery subset | **Partial** — tier3 nbclient for 01–03 | v0.5 |
| M6 | Extension pages via reflection metadata | **Not started** | v0.5+ |

---

## CI

- **`docs.yml`:** `sphinx-build -W -b html docs docs/_build/html` — **must not import R**
- Autodoc stubs only for generated modules (future); narrative from hand guides + rendered Rd
- `help(geom_point)` passthrough to ggplot2 R help (stretch)

---

## User doc sections (current)

| Section | Path | Status |
|---------|------|--------|
| Landing | `docs/index.md` | Done |
| Getting started | `docs/getting-started.md` | Done |
| Quickstart | `docs/guides/quickstart.md` | Done |
| Installation | `docs/guides/installation.md` | Done |
| Troubleshooting | `docs/guides/troubleshooting.md` | Done |
| Colab / Databricks | `docs/guides/colab.md`, `databricks.md` | Done |
| API reference stub | `docs/api/index.md` | Done — 643-export table |
| NSE bridge | `docs/nse_bridge.md` | Engineering (excluded from Sphinx TOC) |
| User interface spec | `docs/user_interface.md` | Engineering (excluded) |

---

## Resume

Doc-heavy sessions: `project_memory/resume_prompts.md` Prompt #5 (codegen) and Prompt #8 (gates).
