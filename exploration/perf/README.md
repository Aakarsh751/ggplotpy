# Phase 8 — performance benchmarks

> **Status:** v0.5 stub — not a CI gate. Promotion to `tests/` requires ADR + SLO sign-off.

## Implemented harness

| Script | Question | Requires |
|--------|----------|----------|
| `benchmark_ingress.py` | pandas vs Arrow row handoff to R (`nrow`) | R when `GGPLOTPY_BENCH_R=1`; pyarrow optional |

```bash
conda activate ggplotpy
pip install -e ".[arrow]"   # optional Arrow path

# Smoke without R (Python-side row counts only)
python exploration/perf/benchmark_ingress.py

# Full compare (10k rows → R nrow)
GGPLOTPY_BENCH_R=1 python exploration/perf/benchmark_ingress.py
```

Default `N_ROWS = 10_000` in the script — not the 100k case in `validation_strategy.md` case 8 (that remains T-X exploratory).

## Planned benchmarks

| Benchmark | Question | Harness (planned) |
|-----------|----------|-------------------|
| **Cold start** | Time from `import ggplotpy` to first SVG byte | lazy `importr` vs eager init |
| **Render latency** | `ggplot` build + `ggsave` / `_repr_svg_` | mtcars scatter, faceted synthetic |
| **Memory** | Peak RSS during render | large faceted plot |
| **Codegen reflection** | `ext.*` namespace cold vs warm | ggrepel, patchwork smoke |

## Target SLOs (draft — not enforced)

- First plot (warm R): **< 2 s** on laptop (mtcars scatter)
- 100k-row Arrow handoff: competitive with `pandas2ri` baseline
- No unbounded R object retention across repeated renders (D-P004 lazy init)

## Results

Log under `exploration/perf/results/` (gitignored when created) and summarize in `project_memory/discoveries.md`.

## References

- [architecture.md](../../docs/architecture.md) — data plane, Arrow v0.5
- [validation_strategy.md](../../docs/validation_strategy.md) — case 8–9 (T-X)
- robstatm-py `exploration/perf/` — adapt patterns, do not import
