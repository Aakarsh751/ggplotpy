# ggplotpy: Exposing R's ggplot2 Ecosystem to Python — Research Report & Engineering Plan

**Author:** Principal-architect review · **Date:** 2026-06-21
**Scope:** Feasibility study + competitive analysis + 12-phase engineering plan for a Python package that drives *real* ggplot2 (not a reimplementation) under the hood.

> **Reading guide.** Phases 1–2 are research/feasibility. Phases 3–10 are design and roadmap. Phase 11 is risk. Phase 12 is the go/no-go. Claims are tagged **[VERIFIED]** (checked against a cited source this session) or **[ASSESSED]** (my engineering judgment / general domain knowledge). Where I'm guessing, I say so.

---

## TL;DR / Founder's verdict (read this first)

- **Has it been built?** *Partially, yes.* rpy2 ships a hand-maintained `rpy2.robjects.lib.ggplot2` wrapper, and `pyggplot` exists but is dormant (13 stars). **Neither** delivers the trifecta that would make this compelling: (1) an ergonomic `ggplot(df) + geom_point()` grammar with Pythonic aesthetics, (2) *automatic* coverage of the whole extension ecosystem (ggrepel, patchwork, gganimate, ggtree, survminer…), and (3) zero-friction install that doesn't make the user hand-install R. **That three-way gap is the actual product.** **[VERIFIED]** for (1)/(2) existence; **[ASSESSED]** for the gap framing.
- **Is near-100% ggplot2 compatibility achievable?** For *rendering* — **yes**, because you run actual ggplot2. For the *Python API surface* — **~90–95%** via reflection + a raw-R escape hatch. The last 5% (deep NSE, some extension internals, ggplot2 4.0's S7 transition) is where effort concentrates. **[ASSESSED]**
- **Recommended architecture:** **Hybrid** = embedded R (rpy2) execution engine **+** dynamic namespace reflection for auto-generated wrappers **+** Arrow-based data transfer **+** a thin hand-written ergonomic core (the `+` grammar, `aes`, Jupyter rendering) **+** a managed-R bootstrap. **[ASSESSED]**
- **Effort:** Solo dev → **~6–9 months** to a credible v0.5; **~8k–15k LOC** of hand-written code + generated wrappers. **[ASSESSED]**
- **Biggest risk:** **Packaging.** A true `pip install ggplotpy` with *bundled* R, cross-platform (Win/macOS-Intel/macOS-ARM/Linux), is the single hardest part and the reason nobody has nailed this. Realistic answer: depend on a managed R (conda-forge `r-base` or auto-install via `rig`), not a self-contained wheel, at least for v1.0.
- **Go/No-Go:** **Qualified GO** as an open-source project *if* the mission is "the extension ecosystem + exact R parity for mixed R/Python teams," not "beat plotnine for casual users." It will own a focused, valuable niche; it will not replace plotnine for people who just want ggplot syntax. **[ASSESSED]**

---

# PHASE 1 — Market & Competitive Research

## 1.1 The incumbents, dissected

### rpy2 (+ `rpy2.robjects.lib.ggplot2`) — the real incumbent
- **Architecture:** CPython C-extension embedding the R shared library (`libR`) **in-process**. R objects are exposed as Python proxy objects; conversion layers (`pandas2ri`, `numpy2ri`) move data across. Ships a curated OO wrapper `rpy2.robjects.lib.ggplot2` modeling `GGplot`, `Aes`/`AesString`, `Layer`, `Stat`. Current line is **rpy2 3.6.x**. **[VERIFIED]** (rpy2 docs, latest = 3.6.6).
- **Strengths:** Runs *actual* ggplot2; fastest possible transport (same process, no IPC); mature, the de-facto standard for R-from-Python; the ggplot2 wrapper's class hierarchy is explicitly designed to make extensions "easy." **[VERIFIED]**
- **Weaknesses:** (a) API is functional-but-clunky — `ggplot2.ggplot(df) + ggplot2.geom_point()` with `AesString(x="wt")`; (b) the bundled wrapper is **hand-maintained and incomplete** — it cannot track every ggplot2 method or extension; (c) **packaging pain** — needs a working R install + compiler toolchain; notoriously fiddly on Windows; (d) one R per process, GIL-bound, not thread-safe; (e) lagging ggplot2 4.0's S7 changes is a live concern. **[VERIFIED]** for (a)(b)(e); **[ASSESSED]** for (c)(d).
- **Adoption / maintenance:** High adoption, actively maintained (single-maintainer-dominated, Laurent Gautier). **[ASSESSED]**
- **Lesson:** rpy2 *is* the engine you'd build on. The opportunity is a **better skin + better packaging + auto-coverage**, not a new engine.

### pyggplot (TyberiusPrime)
- **Architecture:** Thin Pythonic wrapper over rpy2+pandas; "shove the DataFrame into R." Method-based API (`plot.add_scatter(...)`) rather than the `+` grammar. **[VERIFIED]**
- **Status:** **Dormant**, 13 stars, 1 release, authors acknowledge weak stats support and poor errors, and even redirect users elsewhere. **[VERIFIED]**
- **Lesson:** A method-call API (`.add_scatter`) loses the thing people love about ggplot2 — the algebraic `+`. Don't repeat that. Low adoption shows that "thin wrapper, no packaging story, no ecosystem coverage" doesn't attract users.

### plotnine — the reimplementation (the thing we are explicitly *not* building)
- **Architecture:** Pure-Python reimplementation of the Grammar of Graphics on Matplotlib. **Current 0.15.x**, actively maintained, 30+ geoms, layout manager, etc. **[VERIFIED]**
- **Strengths:** No R dependency, pip-installs trivially, great for the 90% case ("I want ggplot syntax in Python"), Matplotlib-native output. **[VERIFIED]**
- **Weaknesses (the wedge for our project):** **"not part of a larger ecosystem"** — it cannot use ggrepel, patchwork, gganimate, ggtree, survminer, sf-based geoms, ggpubr, etc.; it always lags ggplot2 features; subtle rendering differences break exact reproducibility with R colleagues. **[VERIFIED]** (the ecosystem gap is called out explicitly by comparisons).
- **Lesson:** plotnine *defines* our positioning. We win **only** where the R extension ecosystem and exact-parity matter. We lose everywhere else (install simplicity, pure-Python portability).

### reticulate (the mirror image)
- **Architecture:** R package embedding **Python** in R (the reverse of rpy2). Same in-process-embedding philosophy; pioneered slick auto-conversion and, with Arrow, near-zero-copy transfer. **[VERIFIED]** (Arrow R↔Python article: reticulate 26 s → Arrow 0.2 s).
- **Lesson:** Proves bidirectional embedding is production-grade; its environment-management UX (`reticulate` auto-provisions Python via `miniconda`/`uv`) is the **gold standard we should copy for the reverse problem** (auto-provisioning R).

### pyRserve / Rserve
- **Architecture:** Client/server. R runs as a **separate process/daemon** (Rserve); Python talks over TCP with a binary protocol. **[ASSESSED]**
- **Strengths:** Process isolation (crash in R ≠ crash in Python), can be remote, multiple clients. **Weaknesses:** serialization overhead per call, must marshal plots as files/bytes, extra moving part to deploy, latency. **[ASSESSED]**
- **Lesson:** The right model for a **"render service"** fallback or for hardened multi-tenant deployments — *not* the default for interactive notebook use.

### rchitect / radian
- **rchitect:** The Python↔R FFI library underneath **radian** (a modern R console written in Python). Embeds R via cffi. **[ASSESSED]**
- **radian:** A polished R REPL; proves a Python process can host a high-quality interactive R experience. **[ASSESSED]**
- **Lesson:** rchitect is an existence proof of an *alternative* embedding FFI to rpy2 (cffi-based, arguably simpler to build against). Worth knowing as a Plan-B engine if rpy2's C-extension packaging proves too painful.

### Arrow / DuckDB interop (the data plane, not a bridge)
- **Arrow:** Identical columnar memory layout in R and Python ⇒ **zero-copy** in-process transfer (pointers only). pandas↔Arrow is zero-copy only in limited cases (numeric, no nulls). nanoarrow gives a minimal C-ABI interface. **[VERIFIED]**
- **DuckDB:** Speaks Arrow natively in both languages; can be a neutral data exchange + pushdown engine. **[ASSESSED]**
- **Lesson:** **Arrow is the data-transfer answer**, decoupled from the call mechanism. Whether you embed (rpy2) or RPC (Rserve), moving the DataFrame as an Arrow buffer is the fast path.

### RCall.jl (cross-language analogue)
- Julia's R bridge: embeds R in-process, `@rput`/`@rget` move data, `R"..."` string macro runs raw R. Mature, widely used. **[ASSESSED]**
- **Lesson:** Its `R"...."` **raw-string escape hatch** is the single most important UX pattern to steal — it guarantees 100% coverage as a fallback even when the Pythonic wrapper doesn't model something.

### Comparison table

| Project | Mechanism | Runs real ggplot2? | Ecosystem coverage | Install ease | Status | Role for us |
|---|---|---|---|---|---|---|
| rpy2 + lib.ggplot2 | In-process embed | ✅ | Partial (hand-curated) | Hard | Active | **Engine + baseline** |
| pyggplot | rpy2 wrapper | ✅ | Low, method API | Medium | Dormant | Anti-pattern to avoid |
| plotnine | Reimplementation | ❌ | None (no R) | ✅ Easy | Active | Positioning foil |
| reticulate | Embed Python-in-R | n/a | n/a | ✅ (auto-provisions) | Active | UX model to copy |
| pyRserve/Rserve | RPC daemon | ✅ | via raw R | Medium | Niche | Render-service fallback |
| rchitect/radian | cffi embed | ✅ | via raw R | Medium | Active | Plan-B engine |
| Arrow/nanoarrow | Data layout | n/a | n/a | ✅ | Active | **Data plane** |
| RCall.jl | Embed (Julia) | ✅ | via `R"..."` | Medium | Active | Escape-hatch pattern |

## 1.2 Has this been built? Why did attempts under-deliver?
- **Built partially**, never *completely*. rpy2's ggplot2 module is the closest and is genuinely usable, but: clunky API, manual maintenance, no packaging story, no auto-extension support. pyggplot tried and stalled.
- **Why incomplete:** (1) the ergonomic-API problem and the auto-coverage problem and the packaging problem are *each* substantial, and nobody funded all three; (2) plotnine "good enough"-ed the casual market, sapping motivation; (3) R packaging across 4 platforms is a perennial tar pit. **[ASSESSED]**

## 1.3 Gaps that remain (the product thesis)
1. **Ergonomic, faithful `+` grammar** with Pythonic aesthetics and IDE/autocomplete support.
2. **Automatic, total ecosystem coverage** via reflection — *any* installed ggplot2 extension becomes callable, with generated stubs.
3. **Frictionless install** — `pip install ggplotpy` provisions R for you (à la reticulate/miniconda), or ships a conda package.
4. **First-class notebook rendering** (crisp SVG/PNG/retina) across Jupyter/VSCode/Colab/Databricks.

## 1.4 Who would use it? (honest segmentation)

| Segment | Need | Fit | Size signal |
|---|---|---|---|
| **Biostatisticians / bioinformaticians** | ggtree, survminer, ComplexHeatmap-adjacent, Bioconductor plots; exact parity with R pipelines | **★★★ Strongest** | Bioconductor/ggtree huge in genomics |
| **Academic researchers (mixed R/Python labs)** | Reproduce a collaborator's exact R figure from Python | ★★★ | Large, durable |
| **Quant researchers** | patchwork dashboards, ggdist, financial ggplot extensions, R parity with risk teams | ★★ | Moderate, high-value |
| **Data scientists (general)** | "ggplot syntax in Python" | ★ (plotnine already serves them) | Large but **already served** |
| **ML engineers** | quick EDA viz | ★ (matplotlib/plotly/plotnine suffice) | Low intent to add R |
| **Jupyter/Colab users** | inline rich plots | cross-cutting enabler, not a segment | — |

**Real problem or niche?** **A real problem for a focused audience.** The "I want ggplot syntax" problem is *solved* by plotnine. The "I need the actual R extension ecosystem and byte-for-byte parity from Python" problem is **unsolved and painful** — but its audience is narrower (biostat, academia, mixed-language quant). Size the ambition to that truth. **[ASSESSED]**

---

# PHASE 2 — Technical Feasibility

**Headline:** Near-100% *rendering* fidelity is achievable because you execute real ggplot2. The work is in API ergonomics, data transport, NSE, and packaging — not in graphics correctness.

## 2.1 R runtime embedding options

```
            in-process  <----------------- coupling ----------------->  out-of-process
  rpy2 (C-ext)   rchitect (cffi)     |     subprocess Rscript     Rserve/pyRserve     container/microservice     WASM (webR)
  fastest, fragile packaging         |     simplest, slow, file-based   isolated, RPC overhead   reproducible, heavy   sandboxed, immature for full pkgs
```

| Option | Pros | Cons | Perf (call overhead) | Packaging complexity |
|---|---|---|---|---|
| **rpy2 (in-process C-ext)** | Fastest, mature, rich object model, Arrow-ready | Build/ABI fragility, GIL-bound, R crash kills process | ~µs–ms | **High** (compiled against libR + Python ABI) |
| **rchitect (cffi embed)** | In-process, simpler build than C-ext | Smaller community, less batteries-included | ~µs–ms | Medium-High |
| **Subprocess `Rscript`** | Trivial, robust isolation | Re-spawn cost, marshal via files, no live objects | 100s ms/call | **Low** |
| **Rserve RPC** | Isolation, remote, multi-client | Serialize per call, daemon lifecycle | ms–10s ms | Medium |
| **Container/microservice** | Reproducible, scalable, secure | Ops heavy, latency, not laptop-friendly | ms + network | Medium-High (ops) |
| **WASM (webR)** | Browser/sandbox, no native install | Limited package set, no arbitrary CRAN/compiled extensions, memory caps | n/a interactive | Medium but **capability-limited** |

**Verdict:** Default **rpy2 in-process** for interactivity; provide a **subprocess/Rserve "isolated" backend** as an opt-in for robustness/multi-tenant; treat WASM as a future "playground/docs" target only (it can't load arbitrary compiled extensions). **[ASSESSED]**

## 2.2 Data transfer layer

```
 pandas/polars/numpy/pyarrow                         R data.frame/tibble/data.table
        │                                                       ▲
        │   (A) pandas2ri/numpy2ri  → element copy              │
        ├───────────────────────────────────────────────────────
        │   (B) Arrow C-Data Interface (nanoarrow) → ZERO-COPY  │  ← preferred
        └───────────────────────────────────────────────────────
```

| Source → R | Path | Copy? | Notes |
|---|---|---|---|
| pandas → data.frame | rpy2 `pandas2ri` | copy | mature, default; categoricals→factors |
| polars/pyarrow → R | Arrow C-Data Interface via `arrow`/`nanoarrow` | **zero-copy** | fastest; needs Arrow on both sides |
| numpy → R matrix/vector | `numpy2ri` | mostly copy (copy-free for contiguous numeric in some cases) | beware 0-d/1-d edge cases |
| R result → Python | reverse of above | varies | for plotting, result is a *plot object*, not tabular — only the input df is large |

**Key insight:** For a plotting library the **expensive transfer is one-directional** (DataFrame in; the output is a rendered image, which is small). So optimize the *ingress* path: prefer Arrow zero-copy when the user passes polars/pyarrow, fall back to `pandas2ri` for pandas. **[ASSESSED]** Reticulate's 26s→0.2s Arrow result is the proof the Arrow path matters at scale. **[VERIFIED]**

## 2.3 ggplot2 internals — how Python touches each component
ggplot2 is built from composable R objects; **every one is just an R function call returning an R object**, so a reflective bridge can reach all of them:

| Component | R surface | Python interaction strategy |
|---|---|---|
| Layers (`geom_*`, `stat_*`) | functions returning `Layer`/`LayerInstance` | auto-wrapped funcs; `+` appends |
| Stats | `stat_*` | same; params pass through `**kwargs` → R named args |
| Scales (`scale_*`) | functions | auto-wrapped |
| Coords (`coord_*`) | functions | auto-wrapped |
| Facets (`facet_wrap/grid`) | functions; **formulas** (`~var`) | translate Python `facet_wrap("~ a + b")` string → R formula via `stats::as.formula` |
| Themes (`theme_*`, `theme()`) | functions; many element args | auto-wrapped; element helpers (`element_text`) wrapped too |
| Guides/legends | `guide_*`, `guides()` | auto-wrapped |
| Rendering pipeline | `ggplot_build` → `ggplot_gtable` → grid device | call `ggplot2::ggsave`/print to a graphics device (svg/png/pdf), read bytes back |

The **rendering pipeline** is what we exploit for output: render to an in-memory or temp device and return bytes (Phase 7). **[ASSESSED]**

**ggplot2 4.0 / S7 caveat [VERIFIED]:** 4.0 rewrote internals S3→S7 with double dispatch and a rewritten guide system; *typical* `ggplot()+geom_*()` use is unaffected, but packages poking internals may break. Because we mostly *call public functions and `+`*, we sit in the safe zone — **but** any feature that inspects/mutates plot internals (e.g., to extract built layer data) must handle both `$data` (compat shim) and `@data` (S7). Pin/test against both 3.5.x and 4.0.x.

## 2.4 NSE (non-standard evaluation) — the genuinely hard part

ggplot2's `aes(x = wt, y = mpg)` uses **tidy evaluation**: `wt`/`mpg` are *unquoted symbols* captured as **quosures** (expression + environment) via rlang, not strings. Python has no unquoted-symbol syntax, so we must bridge.

**Why hard:** Python can't pass `wt` as a bare symbol; and modern ggplot2 deprecated the old `aes_string()`. Aesthetics can also be *expressions* (`aes(x = log(wt), color = factor(cyl))`), which must survive translation.

**Solutions (use a layered approach):**
1. **String → quosure via rlang.** Build aes by injecting parsed expressions: in R, ``aes(!!!rlang::parse_exprs(c(x="wt", y="mpg")))``. From Python: pass the user's strings to a small R helper `ggplotpy_aes(x="log(wt)", y="mpg", colour="factor(cyl)")` that does `rlang::parse_expr` per value and splices with `!!!`. This supports **full expressions**, not just column names. **[ASSESSED — this is the recommended core trick]**
2. **`.data[[...]]` pronoun** for ambiguous names: `aes(x = .data[["wt"]])` is robust to columns with odd names.
3. **Escape hatch:** `aes(R("interaction(a, b)"))` and a top-level `R("...")` for anything unmodeled.

```python
# Python
aes(x="wt", y="mpg", color="factor(cyl)")
# →  emit R:  ggplotpy:::aes_from_strings(list(x="wt", y="mpg", colour="factor(cyl)"))
#    where the helper parses each string as an R expression and splices into aes()
```

This makes NSE a **solved problem** for our purposes — at the cost of one small R-side helper package shipped with ggplotpy. **[ASSESSED]**

## 2.5 Extension ecosystem — can arbitrary extensions work automatically?

**Mostly yes, by construction**, because extensions are *also* just R packages exporting functions that return ggplot-composable objects.

| Extension | Mechanism | Auto-support? | Caveats |
|---|---|---|---|
| **ggrepel** | extra geoms (`geom_text_repel`) | ✅ auto | none |
| **patchwork** | operators `+`,`/`,`|` to compose *plots* | ⚠️ needs operator modeling | `/` and `|` aren't ggplot's `+`; model `Plot.__truediv__/__or__` |
| **cowplot** | `plot_grid()` functions | ✅ auto (function call) | layout args |
| **ggthemes** | `theme_*`, `scale_*` | ✅ auto | none |
| **gganimate** | `transition_*` + `animate()`→gif/mp4 | ⚠️ needs renderer | output is animation; needs gifski/ffmpeg + bytes return |
| **ggpubr** | geoms/stats + stat tests | ✅ auto | some return non-plot objects |
| **sf** | `geom_sf`, CRS handling | ⚠️ data path | need to pass sf geometries (Arrow GeoArrow or WKB) — harder than tabular |
| **survminer/ggtree** | complex objects | ✅ for calls; ⚠️ for object mutation | ggtree touches internals (S7 risk) |

**Conclusion:** A reflective bridge gives **automatic call-level support for the vast majority** of extensions. The exceptions need small bespoke shims: **operator-based composition (patchwork)**, **animation rendering (gganimate)**, and **non-tabular spatial data (sf)**. Budget explicit work for those three. **[ASSESSED]**

---

# PHASE 3 — Architecture Design (7 candidates, ranked)

For each: description, ±, complexity, est. LOC (hand-written, excluding generated), timeline to usable, perf, maintainability.

### A. Thin Wrapper (curate by hand, like rpy2's module but nicer)
- **Desc:** Hand-write Python classes for the common geoms/scales/themes over rpy2.
- **+** Predictable, fully typed, great docs for what's covered. **−** Never complete; constant manual upkeep; misses extensions; *this is the rpy2 status quo*.
- **Complexity:** Low. **LOC:** 3–5k. **Timeline:** 1–2 mo. **Perf:** rpy2-native. **Maint:** poor (treadmill).

### B. Dynamic Namespace Reflection (auto-wrap every exported function)
- **Desc:** At import, introspect the R `ggplot2` (and any extension) namespace; generate Python callables that forward `*args/**kwargs` to R, returning proxy objects supporting `+`.
- **+** **Total coverage**, near-zero per-function maintenance, extensions free. **−** Weak static typing/autocomplete unless you *also* generate stubs; error messages need translation.
- **Complexity:** Medium. **LOC:** 2–4k (engine) + generated stubs. **Timeline:** 2–3 mo. **Perf:** rpy2-native. **Maint:** **excellent**.

### C. AST-Based Translation Layer (compile Python plot DSL → R code string)
- **Desc:** Parse a Python expression tree and emit equivalent R `ggplot2` source, then `eval` in R.
- **+** Clean separation; could target non-rpy2 backends; transparent generated R (great for "show me the R code"). **−** You re-implement ggplot2's API grammar in a translator; brittle; high effort for marginal gain over B.
- **Complexity:** High. **LOC:** 6–10k. **Timeline:** 4–6 mo. **Perf:** good. **Maint:** medium (translator must track API).

### D. Embedded Runtime Bridge (rpy2/rchitect as the substrate) — *substrate, not full design*
- **Desc:** The execution engine layer that B/C/G sit on. Not a complete UX by itself.
- **+** Fast, in-process. **−** Packaging fragility; this is a *component*, combine with B.

### E. Remote Rendering Service (Rserve/HTTP microservice)
- **Desc:** R runs as a service; Python sends plot spec/data, gets back image bytes.
- **+** Isolation, scalable, secure multi-tenant, language-agnostic, R crash contained. **−** Latency, ops burden, serialization, not laptop-friendly for tight loops.
- **Complexity:** Medium-High (ops). **LOC:** 4–7k (client+server+protocol). **Timeline:** 3–5 mo. **Perf:** ms+network. **Maint:** medium. **Best as an *optional backend*, not the default.**

### F. WASM Runtime (webR)
- **Desc:** Run R compiled to WASM in-browser/sandbox.
- **+** No native install, sandboxed, great for docs/playground. **−** **Cannot load arbitrary compiled CRAN extensions**, memory/threading limits — kills the "whole ecosystem" promise.
- **Complexity:** High. **LOC:** 4–8k. **Timeline:** 4–6 mo. **Perf:** interactive-OK. **Maint:** medium. **Niche only.**

### G. **Hybrid (RECOMMENDED)** = B (reflection) + D (rpy2 engine) + Arrow data plane + thin hand-written ergonomic core + pluggable backends (in-process default; Rserve/subprocess optional) + raw-`R()` escape hatch + generated type stubs
- **Desc:** Reflection gives total coverage; a small hand-written core gives the *beautiful* `ggplot()+geom_point()` UX, `aes` NSE handling, patchwork operators, and Jupyter rendering; Arrow handles big-data ingress; backends are swappable; `.pyi` stubs give autocomplete.
- **+** Coverage **and** ergonomics **and** future-proofing; matches the product thesis exactly. **−** Most moving parts; needs disciplined layering.
- **Complexity:** Medium-High. **LOC:** **8–15k** hand-written + generated. **Timeline:** 6–9 mo to v0.5. **Perf:** rpy2-native + Arrow fast path. **Maint:** good (reflection absorbs API churn).

### Ranking

| Rank | Arch | Coverage | Ergonomics | Maint | Effort | Overall |
|---|---|---|---|---|---|---|
| **1** | **G Hybrid** | ★★★ | ★★★ | ★★★ | ★★ | **Best** |
| 2 | B Reflection | ★★★ | ★★ | ★★★ | ★★★ | Strong base |
| 3 | E Render service | ★★★ | ★★ | ★★ | ★★ | Best *optional* backend |
| 4 | A Thin wrapper | ★ | ★★★ | ★ | ★★★ | = status quo |
| 5 | C AST translate | ★★ | ★★★ | ★★ | ★ | High cost |
| 6 | F WASM | ★ | ★★ | ★★ | ★ | Niche/docs |
| 7 | D Embed only | ★★★ | ★ | ★★ | — | Component |

**Recommendation: G (Hybrid).** Build B as the engine inside G. Ship E as an optional `backend="rserve"`. **[ASSESSED]**

### Recommended layered architecture (diagram)

```
┌──────────────────────────────────────────────────────────────────┐
│  USER CODE:  ggplot(df) + aes(x="wt", y="mpg") + geom_point() ...  │
├──────────────────────────────────────────────────────────────────┤
│  ERGONOMIC CORE (hand-written, ~3–4k LOC)                          │
│   • GG object + __add__ chain    • aes() NSE→quosure helper        │
│   • patchwork operators (/ |)    • repr_png_/_svg_ for Jupyter     │
│   • R() raw escape hatch         • error translation               │
├──────────────────────────────────────────────────────────────────┤
│  REFLECTION + CODEGEN (~2–4k LOC + generated .pyi)                 │
│   • inspect R namespaces (ls/getNamespaceExports, formals, .Rd)    │
│   • build Python callables + type stubs + docstrings               │
├──────────────────────────────────────────────────────────────────┤
│  DATA PLANE                          BACKEND ABSTRACTION           │
│   • Arrow zero-copy (polars/pa)       • InProcess(rpy2) [default]  │
│   • pandas2ri/numpy2ri fallback       • Rserve / subprocess (opt)  │
├──────────────────────────────────────────────────────────────────┤
│  R RUNTIME  (ggplot2 + extensions + tiny ggplotpy-R helper package)    │
├──────────────────────────────────────────────────────────────────┤
│  RUNTIME BOOTSTRAP: find/provision R (rig | conda r-base | system) │
└──────────────────────────────────────────────────────────────────┘
```

---

# PHASE 4 — API Design

## 4.1 Chosen surface: faithful `+` grammar, `from ggplotpy import *`

```python
from ggplotpy import *
import pandas as pd
df = pd.read_csv("mtcars.csv")

# Basic
p = (ggplot(df)
     + aes(x="wt", y="mpg", color="factor(cyl)")   # expressions allowed
     + geom_point(size=2)
     + geom_smooth(method="lm")
     + theme_minimal())
p                      # auto-renders in Jupyter (SVG)
p.save("out.png", width=6, height=4, dpi=300)

# Faceting (formula via string)
p + facet_wrap("~ cyl") + facet_grid("gear ~ cyl")

# Scales / guides
p + scale_color_brewer(palette="Set1") + guides(color=guide_legend(ncol=2))

# Extensions — automatic
from ggplotpy.ext import ggrepel, patchwork, gganimate
p2 = p + ggrepel.geom_text_repel(aes(label="name"))
dashboard = (p | p2) / p3          # patchwork operators
anim = p + gganimate.transition_states("year"); anim.animate(fps=10)  # → gif bytes

# Escape hatch — guaranteed 100% coverage
p + R('annotate("text", x=3, y=20, label="hi")')
print(p.to_r())        # show the generated R source
```

## 4.2 Naming/import options compared

| Option | Example | Pros | Cons | Verdict |
|---|---|---|---|---|
| **A. `+` grammar, star-import** | `from ggplotpy import *; ggplot(df)+geom_point()` | Familiar to every ggplot user; muscle-memory | namespace pollution | **Primary** |
| B. namespaced | `import ggplotpy; ggplotpy.ggplot(df)+ggplotpy.geom_point()` | clean ns, explicit | verbose, less ggplot-y | **Offer too** (both work) |
| C. auto namespace import (lazy attribute) | `ggplotpy.ggrepel.geom_text_repel` | total coverage incl. extensions | discoverability/typing | **For extensions** |

Ship **A as the headline**, **B always available**, **C for extensions** (`ggplotpy.ext.<pkg>.<fn>` lazily reflects the package).

## 4.3 Developer experience
- **Autocomplete/IDE/typing:** generate **`.pyi` stub files** from R `formals()` + `.Rd` so editors show real parameter names and docstrings (Phase 5). Core objects (`GG`, `aes`) hand-typed.
- **Docs generation:** render R `.Rd` help → Markdown into the Python docstrings and the Sphinx site; one "R help passthrough" so `help(geom_point)` shows ggplot2's own docs.
- **Errors:** wrap R errors, strip R tracebacks, surface the R message + the offending generated R line; `ggplotpy.last_r_code()` for debugging.
- **"Show the R":** every plot supports `.to_r()` — huge for trust, teaching, and bug reports.

---

# PHASE 5 — Automatic Wrapper Generation

**Feasible and central to the design.** Everything in R is introspectable.

## 5.1 Inspection primitives (all standard R)
- **Discover exports:** `getNamespaceExports("ggplot2")`, `ls("package:ggplot2")`.
- **Signatures:** `formals(fn)` → arg names + defaults; `args(fn)`.
- **Docs:** parse installed `.Rd` (via `tools::Rd2txt`/`Rd2HTML` or the `Rdpack`/`tools` API) for descriptions, params, examples.
- **Classify return type:** call once with defaults in a sandbox and inspect `class()` to tag geoms/scales/themes vs. non-plot helpers (or maintain a small curated category map for the ~20 prefixes: `geom_`, `stat_`, `scale_`, `coord_`, `facet_`, `theme`, `guide_`, `element_`, `annotation_`).

## 5.2 Generation pipeline

```
getNamespaceExports(pkg) ─▶ for each fn:
   formals(fn) ──▶ param names + defaults ──▶ Python signature + .pyi
   Rd(fn)      ──▶ description/params/examples ──▶ docstring
   class probe ──▶ tag (geom/scale/theme/other) ──▶ choose wrapper template
                                              └────▶ emit Python callable:
        def geom_point(*args, **kwargs) -> Layer:
            return _call_r("ggplot2", "geom_point", args, kwargs)
```

```python
# pseudocode — generator (build-time + runtime fallback)
def generate_package(pkg):
    exports = r(f'getNamespaceExports("{pkg}")')
    for name in exports:
        formals = r(f'names(formals(`{pkg}`::`{name}`))')
        doc     = rd_to_markdown(pkg, name)
        kind    = classify(pkg, name)            # geom/scale/theme/other
        emit_py(name, formals, doc, kind)        # .py wrapper
        emit_pyi(name, formals, doc)             # .pyi stub for IDEs
```

- **Two modes:** (1) **build-time codegen** for ggplot2 + a curated "blessed" extension set → committed `.py`/`.pyi` (fast import, real typing, browsable on GitHub). (2) **runtime reflection** for *any* other installed package via `ggplotpy.ext.<pkg>` (lazy `__getattr__`), so nothing is ever truly unsupported.
- **Docstrings/type hints auto-generated** from `formals` + `.Rd`. Defaults that are R expressions are rendered as strings; `...` maps to `**kwargs`.
- **Versioning:** regenerate per ggplot2 release in CI; snapshot the generated tree so users get stable stubs; reflection covers drift between releases. Handles the S3→S7 4.0 churn without per-function rewrites. **[ASSESSED]**

---

# PHASE 6 — Packaging & Distribution (the hardest phase)

**Brutal truth:** A true `pip install ggplotpy` that *also* silently installs a full R + compiled extensions, on all four platforms, with no system R, is **the reason this class of project is hard**. Be honest about tiers.

## 6.1 Platform matrix

| Platform | System R common? | rpy2 build pain | Recommended provisioning |
|---|---|---|---|
| Linux x86_64 | sometimes | medium (needs `R` headers) | conda `r-base`, or `rig`, or distro R |
| macOS Intel | sometimes | medium | conda, `rig` (CRAN pkg), Homebrew |
| macOS ARM (Apple Silicon) | sometimes | medium (arm64 R) | conda arm64, `rig` |
| Windows | rarely | **high** (Rtools/ABI) | conda `r-base` (cleanest), or `rig` + Rtools |

## 6.2 Distribution strategies

| Strategy | "No manual R"? | Effort | Robustness | Verdict |
|---|---|---|---|---|
| **conda-forge `ggplotpy` (deps: `r-base`, `r-ggplot2`, `rpy2`)** | ✅ | Low-Med | **High** | **Primary recommendation** |
| **pip + auto-provision R via `rig`/miniconda on first use** (reticulate-style) | ✅ (downloads on first run) | Med | Med-High | **Primary for pip users** |
| pip wheels relying on **system R** | ❌ (user installs R) | Low | Med | baseline/fallback |
| **Bundle R inside the wheel** (vendored libR + base pkgs) | ✅ | **Very High** | fragile across OS/arch; licensing (R = GPL-2) bloats wheel | **Avoid for v1**; revisit later |
| Docker image (`ggplotpy` + R preinstalled) | ✅ | Low | High | **Ship one** for servers/CI |

## 6.3 Recommended packaging plan
1. **`pip install ggplotpy`** installs the Python code + rpy2 dependency. On first run, if no usable R is found, `ggplotpy.install_r()` (and an opt-in auto-trigger) provisions R via **`rig`** or a private **miniforge** env, then `install.packages("ggplot2", ...)` / blessed extensions — **exactly the reticulate UX, mirrored.** **[ASSESSED; reticulate proves the pattern — VERIFIED that reticulate auto-provisions.]**
2. **`conda install -c conda-forge ggplotpy`** pulls `r-base` + `r-ggplot2` + `rpy2` as real dependencies — the **most reliable** path, especially on Windows. **Make this the recommended install in docs.**
3. **Official Docker image** for servers/Colab/Databricks/CI.
4. **GPL note:** R is GPL-2; ggplotpy (Apache-2/MIT) merely *drives* R via rpy2 (also GPL — link/IPC boundary). Don't statically bundle R into a wheel without legal review; the conda/system-R/auto-download paths keep R as a separate component and sidestep the issue. **[ASSESSED — flag for legal review, not legal advice.]**

---

# PHASE 7 — Jupyter / Notebook Integration

## 7.1 Output formats

| Format | How | Use |
|---|---|---|
| **SVG** | render to svg device, return string; impl `_repr_svg_` | **default** — crisp, scalable |
| **PNG (retina)** | `ragg`/`Cairo`/`png()` device → bytes; `_repr_png_` with 2× dpi | raster fallback, large plots |
| **HTML** | wrap SVG/PNG, or for `girafe`/`plotly::ggplotly` return interactive HTML via `_repr_html_` | interactivity |
| **Animation** | gganimate → gif/mp4 bytes; display via HTML `<video>`/img | gganimate |

```python
class GG:
    def _repr_svg_(self):  return self._render(fmt="svg")
    def _repr_png_(self):  return self._render(fmt="png", dpi=144)   # retina
    def _repr_mimebundle_(self, **kw):  # let frontend pick best
        return {"image/svg+xml": self._render("svg")}
    def _render(self, fmt, **kw):
        # open R graphics device → print(plot) → read bytes/string back
        ...
```

## 7.2 Targets
- **Jupyter / JupyterLab:** `_repr_svg_`/`_repr_png_` "just work."
- **VSCode notebooks:** same mime hooks; prefer PNG retina if SVG sizing misbehaves.
- **Google Colab:** works if R is provisioned (Colab has system R! — big win; document it). PNG default there.
- **Databricks:** use `displayHTML` integration; ship a `ggplotpy.display()` helper that emits HTML for Databricks' renderer.
- **Sizing:** expose `ggplotpy.set_options(figure_size=(6,4), dpi=144, format="svg")`; honor per-plot overrides.

---

# PHASE 8 — Performance Analysis

**Model:** total = plot-construction overhead + data-transfer (ingress) + R render. Construction is cheap; **data ingress dominates at scale**, render is roughly data-independent until the geom itself is expensive (overplotting 10M points is slow *in any tool*).

| Rows | pandas2ri ingress (est.) | Arrow ingress (est.) | ggplot2 render (est.) | Dominant cost |
|---|---|---|---|---|
| 10k | <50 ms | <10 ms | 50–150 ms | render/startup |
| 100k | ~0.2–0.5 s | ~20–50 ms | 0.1–0.4 s | transfer (pandas) / render |
| 1M | ~2–5 s (copy) | ~0.1–0.3 s | 0.3–1.5 s (geom-dependent) | **transfer (pandas)** |
| 10M | ~20–50 s (copy, may thrash) | ~0.3–1 s (zero-copy) | seconds+ (overplotting) | **transfer (pandas) → use Arrow** |

(Estimates **[ASSESSED]**; anchored by the reticulate 26 s → 0.2 s Arrow result at large size **[VERIFIED]**.)

**Bottlenecks & mitigations:**
1. **Ingress copy (pandas):** mitigate with **Arrow zero-copy** for polars/pyarrow; advise passing Arrow tables for >100k rows; cache the transferred R object across `+`/re-renders.
2. **R startup:** amortized — embed once per session (in-process), not per plot.
3. **Overplotting at 10M:** a *visualization* problem, not a bridge problem — recommend aggregation/`geom_hex`/sampling (same advice ggplot2 itself gives).
4. **Per-call rpy2 marshaling:** batch the plot build; only one device render at the end.

---

# PHASE 9 — Open-Source Strategy

## 9.1 Repo structure
```
ggplotpy/
├─ pyproject.toml                  # build (hatchling), deps: rpy2; extras: [arrow], [polars]
├─ src/ggplotpy/
│  ├─ __init__.py                  # star-export of core + generated ggplot2
│  ├─ core/                        # hand-written
│  │  ├─ gg.py        # GG object, __add__, save, to_r, _repr_*
│  │  ├─ aes.py       # NSE → quosure bridge
│  │  ├─ patchwork.py # / and | operators
│  │  ├─ raw.py       # R() escape hatch
│  │  └─ errors.py    # R error translation
│  ├─ backend/
│  │  ├─ base.py  inprocess.py(rpy2)  rserve.py  subprocess.py
│  ├─ data/           # arrow.py, pandas_bridge.py, polars_bridge.py
│  ├─ runtime/        # bootstrap.py (find/provision R), install_r()
│  ├─ codegen/        # reflect.py, rd_to_md.py, emit.py
│  ├─ generated/      # committed ggplot2 wrappers + .pyi (built in CI)
│  └─ ext/            # lazy __getattr__ reflection for any extension
├─ r-helper/ggplotpy/                  # tiny R companion pkg (aes_from_strings, render helpers)
├─ tests/                          # pytest; R-required + R-free tiers
├─ docs/                           # Sphinx + gallery (mirrors ggplot2 gallery)
└─ .github/workflows/              # CI matrix
```

## 9.2 CI/CD
- **Matrix:** {ubuntu, macos-13 (Intel), macos-14 (ARM), windows} × {R 4.3, 4.4} × {ggplot2 3.5.x, 4.0.x} × {py 3.10–3.13}.
- Use conda/`r-lib/actions` (setup-r) to install R; run R-required tests; separate R-free tier for codegen/unit logic (mirrors how RobStatTM-Py splits strict vs. exploration tiers).
- **Codegen step** regenerates `generated/` and fails CI if stale.
- Image-diff tests (pixel/SVG tolerance) for a curated gallery to catch rendering regressions across ggplot2 versions.

## 9.3 Testing strategy
- **Unit (R-free):** API construction, `to_r()` string equality (golden files), aes parsing.
- **Integration (R-required):** render every gallery example, assert no error + snapshot.
- **Parity:** compare `to_r()` output to expected idiomatic R.
- **Extension smoke tests:** ggrepel/patchwork/ggthemes/gganimate render.

## 9.4 Release strategy
- SemVer; `0.x` until API stable. Conda-forge feedstock + PyPI on tag. Changelog tracks supported ggplot2 versions explicitly.

## 9.5 License
| License | Implication |
|---|---|
| **MIT** | simplest, max adoption; fine since ggplotpy only *links/drives* R |
| **Apache-2** | MIT + explicit patent grant; preferred for larger/standard-track projects |
| BSD-3 | similar to MIT |

**Recommendation: Apache-2.0** for the patent grant and "standard-track" signaling. (Note: the *R runtime* you drive is GPL-2; that constrains *bundling*, not your own code's license — keep R as a separate, user-installed/conda component. **Flag for legal review before any vendored-R wheel.**) **[ASSESSED]**

---

# PHASE 10 — Implementation Roadmap

| Release | Features | Milestones | Key deps | Risks |
|---|---|---|---|---|
| **MVP (wk 1–6)** | rpy2 in-process backend; `ggplot`,`aes`(NSE bridge),`+`, core `geom_*`/`scale_*`/`theme_*` hand+reflected; `_repr_svg_`; `.save()`; `R()` escape hatch; pandas ingress | First Jupyter plot identical to R | rpy2, ggplot2 | NSE bridge correctness |
| **v0.1 (wk 6–12)** | Full reflection codegen for ggplot2; `.pyi` stubs + docstrings from `.Rd`; error translation; `to_r()`; pip + system-R install; CI on 2 OSes | Autocomplete works; all ggplot2 fns callable | tools/Rd, codegen | API churn, S7/4.0 |
| **v0.5 (mo 3–6)** | Arrow zero-copy ingress (polars/pyarrow); `ggplotpy.ext.*` runtime reflection; patchwork operators; gganimate; ggthemes/ggrepel/ggpubr blessed; `install_r()` auto-provision; conda-forge pkg; docs gallery; 4-OS CI | "pip install + first run provisions R"; extension demos | Arrow, rig/conda | **packaging** |
| **v1.0 (mo 6–12)** | sf/geom_sf data path; optional Rserve/subprocess backend; interactive (girafe/ggplotly→HTML); image-diff test suite; perf-tuned caching; full docs/typing; ggplot2 4.0 parity | Stable API; reproducible installs across platforms; Databricks/Colab guides | GeoArrow, Rserve | maintenance load |

**Timeline estimates [ASSESSED]:**
- **Solo dev:** MVP ~6 wk; v0.5 ~6 mo; v1.0 ~9–12 mo.
- **Small team (2–3):** v0.5 ~3 mo; v1.0 ~6 mo (parallelize packaging vs. codegen vs. docs).
- **OSS community:** depends on a committed maintainer; realistically a 1–2 person core for the first year, contributors for extensions/docs after traction.

---

# PHASE 11 — Risk Analysis

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| **Packaging across 4 OSes / no manual R** | **High** | High | Lead with conda-forge; reticulate-style auto-provision via `rig`; Docker image; accept "system R" fallback for v0.x; defer vendored-R wheel |
| **rpy2 build/ABI fragility (esp. Windows)** | High | Med | conda binary rpy2; pin versions; offer Rserve backend as escape; CI catches breaks early |
| **ggplot2 4.0 S7 transition breaks internals-touching features** | Med | Med | Stay on public API + `+`; handle `$data`/`@data`; test against 3.5.x **and** 4.0.x; reflection absorbs signature churn | **[VERIFIED risk source]** |
| **NSE/quosure edge cases (expressions, odd names)** | Med | Med | `rlang::parse_expr` + `.data[[]]` + `R()` escape hatch; golden `to_r()` tests |
| **Performance at 1M–10M rows (pandas copy)** | Med | Med | Arrow zero-copy path; cache transferred frame; aggregation guidance |
| **Maintenance treadmill (extensions, R releases)** | Med | High | Reflection minimizes per-fn work; CI codegen; "blessed vs. reflected" tiering |
| **Adoption: plotnine already "good enough"** | **High** (to *impact*) | High | Position narrowly: ecosystem + parity; target biostat/academia/quant; killer demos (ggtree, patchwork, survminer from Python) |
| **R crash kills Python process (in-process)** | Med | Low-Med | Optional out-of-process backend; guard rendering in try/except; subprocess isolation mode |
| **Single-maintainer bus factor** | Med | Med | Strong docs, codegen lowers contributor barrier, conda-forge feedstock co-maintainers |
| **GPL/bundling licensing** | Med | Low (if not vendored) | Keep R separate (conda/system/download); legal review before any bundle |

---

# PHASE 12 — Final Recommendation

1. **Worth building?** **Yes, conditionally.** It solves a *real, unsolved* problem (the R extension ecosystem + exact parity, from Python) for a *focused* audience. It is **not** a plotnine replacement and shouldn't be sold as one. As an open-source project with a clear niche and great demos, it's worth a solo dev's 6–9 months. As a VC-scale company, the TAM is too narrow — **OSS, not startup.**
2. **Architecture:** **G — Hybrid:** rpy2 in-process engine + dynamic namespace reflection (auto-wrappers + `.pyi`) + Arrow data plane + a thin hand-written ergonomic core (`+` grammar, `aes` NSE bridge, patchwork ops, Jupyter rendering, `R()` escape hatch) + reticulate-style R provisioning + optional Rserve backend.
3. **Engineering effort:** ~**8k–15k LOC** hand-written (plus generated wrappers/stubs); 1 strong generalist who's comfortable in both Python and R internals. (Your RobStatTM-Py experience — rpy2, numpy2ri gotchas, codegen from `.Rd`, multi-OS CI, conda packaging — maps almost 1:1 onto this.)
4. **LOC:** core ~3–4k; reflection/codegen ~2–4k; data plane ~1–2k; runtime/bootstrap ~1k; backends ~1–2k; tests/docs substantial. **Total hand-written ≈ 8–15k.**
5. **Dev time:** v0.5 in ~6 months solo; v1.0 in 9–12.
6. **Probability of success:**
   - *Technical success* (it works, covers ecosystem, installs reasonably): **~80%.**
   - *Becoming "the standard" Python↔ggplot2 interface:* **~35–45%** — rpy2 already occupies the niche; success hinges on dramatically better ergonomics + packaging *and* sustained maintenance.
   - **[ASSESSED]**
7. **Biggest risks:** (1) cross-platform packaging without manual R; (2) sustained maintenance/bus-factor; (3) adoption ceiling because plotnine covers the casual majority.
8. **Biggest opportunities:** (1) become the bridge biostat/genomics Python users reach for (ggtree/survminer/ComplexUpset from Python); (2) the reflection+codegen engine **generalizes** — see #10; (3) "exact-parity reproducibility" for mixed R/Python teams is a genuinely unmet need.
9. **Could it be the standard Python interface to ggplot2?** **Plausibly yes for the "real ggplot2 from Python" niche**, *if* it decisively out-ergonomics rpy2's module and solves install. It will **coexist** with (not replace) plotnine, which owns the no-R market.
10. **Could it grow into a general Python↔R interop platform?** **Yes — this is the strongest strategic upside.** The reflection/codegen/data-plane/runtime-bootstrap machinery is **package-agnostic**; ggplot2 is just the flagship consumer. A `pyr` core ("drive any R package from Python with auto-wrappers, Arrow transport, and managed R") with `ggplotpy` as its first-class showcase is the bigger prize — and is essentially a productized, ergonomically-modern, auto-provisioning rpy2. That platform play is where this could matter most.

## Go / No-Go

> **GO** — as an **open-source project** built on the **Hybrid (G)** architecture, scoped to the **R-ecosystem + exact-parity niche**, with **packaging treated as the #1 engineering risk** (conda-forge + reticulate-style auto-provision, *not* a bundled-R wheel for v1). Frame it from day one as the flagship of a **general Python↔R interop layer**, because that reframing is what turns a nice ggplot2 wrapper into a potentially standard piece of infrastructure.
>
> **NO-GO** if the goal is to beat plotnine for casual users, or to build a venture-scale company — the addressable need is real but narrow.

---

## Assumptions vs. verified facts (explicit)
**Verified this session (cited):** rpy2 ships `lib.ggplot2`, latest 3.6.6; pyggplot dormant (13★); plotnine 0.15.x active, *not* in the R extension ecosystem; ggplot2 4.0.0 (Sep 2025) S7 rewrite + 4.0.1; Arrow R↔Python zero-copy (reticulate 26 s→0.2 s), pandas↔Arrow zero-copy limited to numeric/no-null; nanoarrow minimal interface.
**Assessed (engineering judgment):** all LOC/timeline/probability/perf-ms estimates; the NSE-via-`rlang::parse_expr` recommendation; packaging tier rankings; adoption-segment sizing; licensing/GPL framing (not legal advice — flagged for review).

### Sources
- rpy2 ggplot2 / graphics docs: https://rpy2.github.io/doc/latest/html/graphics.html
- pyggplot: https://github.com/TyberiusPrime/pyggplot
- plotnine: https://github.com/has2k1/plotnine · https://plotnine.org/changelog.html
- ggplot2 4.0.0 / S7: https://tidyverse.org/blog/2025/09/ggplot2-4-0-0/ · https://opensource.posit.co/blog/2025-09-11_ggplot2-4-0-0/ · https://ggplot2.tidyverse.org/news/index.html
- Bioconductor on ggplot2 4.0 breakage: https://blog.bioconductor.org/posts/2025-07-07-ggplot2-update/index.html
- Arrow R↔Python interop: https://arrow.apache.org/docs/r/articles/python.html · https://arrow.apache.org/docs/python/pandas.html
- ggplot2 repo/releases: https://github.com/tidyverse/ggplot2 · https://github.com/tidyverse/ggplot2/releases
