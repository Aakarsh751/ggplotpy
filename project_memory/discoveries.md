# Discoveries

Non-obvious findings about rpy2, ggplot2, NSE, packaging, and CI. Append dated blocks; do not delete earlier entries.

---

## Template

```markdown
### YYYY-MM-DD — <short title>
**Context:** …
**Finding:** …
**Implication:** …
**Applies to:** <module / milestone>
```

## 2026-06-22 — `format_r_value` must emit `.code` for deferred/raw wrappers

**Context:** Audit probe found `geom_point(aes(...))` raising `NotImplementedError:
Conversion 'py2rpy' not defined for objects of type DeferredRCall`.
**Finding:** `format_r_call` formatted every argument through `format_r_value`,
which had no branch for `DeferredRCall`/`RObject` and fell through to
`ro.r("deparse")(value)` — rpy2 then tried (and failed) to convert the Python
wrapper directly. So **any** ggplotpy wrapper passed as an argument to another wrapper
(layer-level aes, nested `R()`) broke. Same root cause made tuple/list kwargs fail
(`coord_cartesian(xlim=(0,5))`). The suite was green only because every test
pre-converted data and used top-level `+ aes(...)` exclusively.
**Implication:** Code-generated R must be built from *source strings*, never by
round-tripping ggplotpy objects through rpy2 conversion. `format_r_value` now handles
`DeferredRCall`/`RObject` (emit `.code`) and `list`/`tuple` (emit `c(...)`).
**Applies to:** `core/defer.py`, `core/to_r_util.py`; validation case 2b.

## 2026-06-22 — `to_r()` aes rewriting must be paren/quote-aware

**Context:** `to_r()` for `aes(label="paste(a, b)")` emitted invalid R
(`aes(label = "paste(a, b)" = , ...)`).
**Finding:** `format_layer_for_to_r` split the aes inner string on every comma and
used `rstrip(")")`, both of which break on commas-in-values and values ending in
`)`. Rewrote with a balanced-paren, quote-aware scanner (`_convert_aes_calls`) that
also converts aes nested inside another call (`geom_point(aes(...))`).
**Applies to:** `core/to_r_util.py`; trust contract D-P007.

## 2026-06-22 — Embedded R hangs on interactive install prompts

**Context:** Coverage sweep rendering `geom_hex` without the `hexbin` package
**deadlocked** — ggplot2/rlang's `check_installed()` printed "Would you like to
install it? 1: Yes 2: No  Selection:" and blocked the embedded session on stdin.
**Finding:** rpy2's embedded R reports `interactive()`-ish behavior to rlang, so
optional-package prompts hang instead of erroring. Fix: at backend init set
`options(rlang_interactive = FALSE, menu.graphics = FALSE)` in
`_force_noninteractive_r()`. The prompt then degrades to a **non-fatal warning** and
the plot still renders (minus that layer) — verified by `test_noninteractive_r.py`.
**Implication:** Any embedded-R bridge must force non-interactive mode or risk
hard hangs from extension/optional-package checks. Never assume a prompt errors.
**Applies to:** `backend/inprocess.py`; all render paths.

## 2026-06-22 — Python→R ingress: dict/numpy/Series and value coercion gaps

**Context:** RESEARCH_AND_PLAN Phase 2.2 lists pandas2ri / Arrow / numpy2ri as the
data plane. Probe found `ggplot({"x":[...]})`, `ggplot(np.ndarray)`,
`ggplot(pd.Series)` all raised, and `format_r_value` mangled numpy scalars/arrays
(`structure(1:3, dim=3L)`), `range`, and `dict`.
**Finding:** `_coerce_data` only handled pandas/arrow/polars; `format_r_value` had
no numpy/dict/range branch. Extended `_coerce_data` (dict→DataFrame, list-of-records,
Series, 1-D/2-D ndarray→`V1..Vn`) and `format_r_value` (numpy scalar→builtin,
ndarray/range→`c(...)`, dict→`list(k=v)`). datetime/categorical/NaN already worked
via pandas2ri.
**Applies to:** `core/gg.py`, `core/defer.py`; validation cases 7–9.

## 2026-06-22 — sf objects must be read under the default (non-converting) converter

**Context:** `ggplot(geodataframe)` raised `TypeError: 'NULLType' object is not iterable`
after `sf_to_r` read the GeoPackage back with `sf::st_read`.
**Finding:** the active conversion context (default+numpy+pandas) auto-converts R
return values to Python; an `sf` data.frame's geometry **list-column** is not
pandas-convertible, so pandas2ri produced a NULLType and the downstream iteration
failed. Fix: wrap the `st_read` call in `localconverter(default_converter)` so the sf
object stays a raw rpy2 object, which `ggplot()` then passes straight back into R.
**Implication:** any rpy2 path that returns a non-tabular/list-column R object must
read it under `default_converter`, not the global pandas converter.
**Applies to:** `data/sf_bridge.py`.

## 2026-06-22 — runtime submodule/function name shadowing

**Context:** `monkeypatch.setattr(ggplotpy.runtime.check_setup, "_r_available", ...)` failed
with "function check_setup has no attribute _r_available".
**Finding:** `runtime/__init__.py` does `from .bootstrap import bootstrap` and
`from .check_setup import check_setup`, so the package attributes
`ggplotpy.runtime.bootstrap` / `ggplotpy.runtime.check_setup` resolve to the **functions**, not
the submodules. `import ggplotpy.runtime.check_setup as cs` (attribute-based) then binds the
function. Use `from ggplotpy.runtime.check_setup import name` or
`importlib.import_module("ggplotpy.runtime.check_setup")` to get the real module.
**Implication:** latent footgun; harmless for normal use (`ggplotpy.install_r`, CLI entry via
importlib) but bites `import X.Y as` and `setattr`. Left as-is (renaming the public
functions is riskier than documenting).
**Applies to:** `runtime/__init__.py`; tests.

## 2026-06-22 — CI never ran the edge matrix (tier2) or notebooks (tier3)

**Context:** New regression tests for the above bugs landed in `tests/edge/`.
**Finding:** `ci.yml` only ran tier0 + tier1; `run_tests.sh` only implemented
tier0/tier1. The entire T2 edge matrix and T3 notebooks were never CI-gated, so the
layer-aes bugs could never have been caught upstream. Added tier2/tier3 to
`run_tests.sh` and a tier2 step to the integration job.
**Applies to:** `.github/workflows/ci.yml`, `scripts/run_tests.sh`.


## 2026-06-21 — Integration test OOM (rpy2 + graphics devices)

**Symptom:** Subagents and local pytest runs die with OOM when executing `pytest tests/` in one process.

**Root cause:** Cumulative R heap + leaked graphics devices when many `_repr_svg_` / `_repr_png_` renders run sequentially in one rpy2 session; Windows agents are especially sensitive.

**Mitigations shipped:** per-file subprocess Tier1 runner; `GGPLOTPY_SKIP_INTEGRATION` collection gate; always `try(dev.off(), silent=TRUE)` in `_render_plot` finally; module-scoped fixtures + `gc.collect()` after integration tests.


---

### 2026-06-21 — Integration pytest OOM on Windows

**Context:** T1 integration tests importing ggplot2 via rpy2 in one pytest worker.

**Finding:** A single process running all `tests/integration/` files can OOM; orphaned R graphics devices after failed renders also leak until `dev.off()`.

**Implication:** Run integration **one file per subprocess** (`scripts/run_tests.ps1` / `.sh` tier1); use `GGPLOTPY_SKIP_INTEGRATION=1` for fast jobs; `_render_plot` must `try/finally` call `dev.off()`; prefer `svglite` for SVG; read SVG with UTF-8 on Windows.

**Applies to:** `tests/conftest.py`, `core/gg.py`, CI `test-integration` job.
