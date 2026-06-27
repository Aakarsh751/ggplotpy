# Resume Prompts

Copy-paste entry points for a fresh LLM session. Use the prompt whose trigger matches your state.

---

## Prompt #1 — General resume (always safe)

> I am resuming **ggplotpy** at `Ggplot2PY/` (`C:\ProfDM_Rproject\Ggplot2PY`, Windows PowerShell).
> **Goal:** Python package driving **real ggplot2** via rpy2 (Hybrid G architecture). Not plotnine.
>
> Before acting:
> 1. Read `AGENTS.md`, `STATUS.md`, `project_memory/progress_log.md` (last block), `project_memory/blockers.md`.
> 2. Read `docs/implementation_plan.md` (current milestone) and `docs/architecture.md`.
> 3. State: research phase relevance, release (M0/MVP/…), verification tier(s) required.
>
> Propose the next concrete action; wait for confirmation on non-trivial work. Follow `docs/implementation_rules.md` and `docs/quality_gates.md`. Append a session block to `progress_log.md` before stopping.

---

## Prompt #2 — Scaffold / M0

**Trigger:** No `pyproject.toml` yet.

> Execute M0 scaffold per `docs/implementation_plan.md` and `AGENTS.md` file layout.
>
> Create: `pyproject.toml`, `src/ggplotpy/` stubs, `r-helper/ggplotpy/`, `tests/` layout + markers, `.github/workflows/ci.yml` + `docs.yml`, minimal T0 smoke tests.
>
> **Do not** implement MVP plotting yet. Exit gate: `pip install -e ".[dev]"` OK; T0 collects/passes; `import ggplotpy` cheap; docs CI R-free.
>
> Windows (before rpy2): `$env:R_HOME = "C:\Program Files\R\R-4.5.2"`; add R `bin\x64` to PATH.
>
> Append `progress_log.md`; update `STATUS.md`.

---

## Prompt #3 — MVP core

**Trigger:** M0 done; implement first real plot.

> Implement MVP core (research Phases 4, 7 partial):
> - `backend/inprocess.py` (adapt robstatm-py `_r.py` patterns)
> - `core/gg.py`, `aes.py`, `raw.py`, `errors.py` — `ggplot()`, `aes()`, `+`, `R()`, `last_r_code()`
> - pandas2ri ingress; `_repr_svg_`, `.save()`
> - T0 aes goldens + T1 mtcars render + T2 first `to_r()` parity
>
> Run: `GGPLOTPY_SKIP_NOTEBOOKS=1 pytest tests/unit tests/integration -q -m "not slow"`. Touch render → T1; touch `to_r()`/aes → T2.
>
> Append session block; update `STATUS.md` and `coverage_matrix.md`.

---

## Prompt #4 — NSE / R helper package

**Trigger:** `aes()` bridge not yet wired to R.

> Ship `r-helper/ggplotpy/` with `aes_from_strings()` per `docs/nse_bridge.md` (D-P003).
>
> Wire `core/aes.py` → R helper. Add T0 golden files: bare column, `factor(cyl)`, `log(wt)`, `.data[["odd-name"]]`, multi-aes, facet formula strings.
>
> Verification: T0 + T2 for all NSE goldens. Append `progress_log.md`.

---

## Prompt #5 — Codegen pipeline

**Trigger:** MVP core green; start v0.1 reflection.

> Implement reflection codegen per `docs/architecture.md` and research Phase 5:
> - `codegen/reflect.py`, `emit.py`, `rd_to_md.py`
> - Committed `generated/` + `.pyi`; CI staleness check
> - Runtime fallback via `ext/` lazy `__getattr__`
>
> Run T0 codegen tests + T1 smoke on generated geoms. Do not hand-wrap every geom if reflection covers exports.

---

## Prompt #6 — Packaging bootstrap

**Trigger:** v0.5 packaging track.

> Implement `runtime/bootstrap.py`, `install_r()`, `check_setup()` per `docs/packaging_plan.md` (D-P002).
> Add conda recipe sketch, Docker image, `environment.yml`. Tests: `tests/test_bootstrap.py`.
>
> Document conda-first install in README. Optional extensions must not break core CI (D-P009).

---

## Prompt #7 — Extension smoke

**Trigger:** Core ggplot2 path green; validate ecosystem.

> Add integration smoke tests: ggrepel, patchwork (`/` `|`), ggthemes, gganimate (skip if gifski/ffmpeg absent).
> Demo notebook under `notebooks/`. Markers: `@needs_ggrepel`, `@needs_patchwork`, `@needs_gganimate`.
>
> Run T1 extension module; record skips in session block.

---

## Prompt #8 — Phase gate check

**Trigger:** End of milestone (M0 / MVP / v0.1 / v0.5 / v1.0).

> Run exit gate from `docs/quality_gates.md` for current release.
> Execute tier matrix from `docs/validation_strategy.md` for that release.
> Report pass/fail per criterion; append `lessons_learned.md` if milestone complete; update `CHANGELOG.md` supported ggplot2 versions.

---

## Prompt #9 — Verification pass

**Trigger:** Before release tag or after large refactor.

> Full verification pass for current release per `docs/testing_guide.md`:
> - T0: `pytest tests/unit -q`
> - T1+T2: matrix per `STATUS.md` release
> - T3 if v1.0 / gallery touched
> - Notebooks: `pytest tests/notebooks -q` (unless `GGPLOTPY_SKIP_NOTEBOOKS=1`)
>
> Record all commands + results in `progress_log.md`. Fix failures before tagging.
