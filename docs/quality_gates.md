# Quality Gates

Definition of Done for ggplotpy features and milestone exits. Canonical verification spec: `validation_strategy.md`.

---

## Per-feature checklist (core / generated wrapper / shim)

```
Feature: <name>   Milestone: <MVP/v0.1/…>
PR: #...

[ ]  Spec traced to RESEARCH_AND_PLAN or ADR
[ ]  Correct layer (no importr outside backend)
[ ]  Tests written at appropriate tier(s)
[ ]  T0 green (if applicable)
[ ]  T1 render smoke (if touches ggplot2)
[ ]  T2 to_r() golden updated (if touches API/aes)
[ ]  Error path tested (Python pre-check or R translation)
[ ]  Docstring or Rd-derived docs
[ ]  coverage_matrix.md row updated
[ ]  progress_log.md session block appended
[ ]  No plotnine / vendored R violations
```

---

## Milestone exit gates

### M0 — scaffold

- [x] Governance + engineering docs + Cursor rules
- [x] `pip install -e ".[dev]"` succeeds
- [x] `import ggplotpy` without loading ggplot2
- [x] T0 tests collect and pass
- [x] `docs.yml` R-free docs check passes
- [x] `tests/` layout + markers registered in `pyproject.toml`

### MVP

- [x] `ggplot`, `aes`, `+`, `R()`, `.save()`, `_repr_svg_`
- [x] pandas ingress; R helper `aes_from_strings`
- [x] `check_setup()` reports R/ggplot2 status
- [x] Verification cases **1–7** pass (T0+T1+T2 as specified)
- [x] `notebooks/01_mvp_mtcars.ipynb` executes clean
- [x] CI: ubuntu + windows; T0+T1 core

### v0.1

- [x] All ggplot2 namespace exports callable (643 via reflection + lazy `__getattr__`)
- [x] `.pyi` stubs for IDE autocomplete (643 symbols)
- [x] T2 parity suite green (strict normalized golden compare)
- [x] Codegen staleness CI job
- [x] ggplot2 3.5.x **and** 4.0.x smoke on CI
- [x] Sphinx user site builds `-W` (furo in `docs/`)

### v0.5

- [x] Arrow ingress path + `exploration/perf/benchmark_ingress.py` stub
- [x] `ggplotpy.ext.*` runtime reflection
- [x] patchwork + gganimate shims with extension tests
- [x] `ggplotpy-bootstrap` CLI + conda recipe skeleton + Docker documented
- [ ] `install_r()` auto-provision; **conda-forge feedstock publish**
- [ ] Full 4-OS CI matrix
- [x] Extension gallery notebooks 01–03 + tier3 nbclient
- [x] Verification cases **8–11** (edge smoke + extensions; perf exploratory)
- [x] Colab + Databricks guides

### v1.0

- [ ] sf/GeoArrow path (optional marker)
- [ ] Rserve/subprocess backend (optional marker)
- [x] T3 visual baselines (**5** SVG hashes — expand to 10+ plots)
- [ ] Full CI matrix + PyPI wheel + platform install automation
- [ ] Case **13** full gallery at tol 1e-3 across expanded baselines
- [ ] `lessons_learned.md` entry for v1.0

---

## Gate re-check triggers

- ggplot2 minor/major bump
- rpy2 version bump
- Changes to `aes`, `to_r()`, or render pipeline
- New OS added to CI matrix
