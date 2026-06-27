# exploration/

Ad-hoc experiments, version sweeps, and benchmarks that **do not** gate CI.

| Subdirectory | Purpose | CI? |
|--------------|---------|-----|
| `perf/` | Phase 8 performance benchmarks (Arrow vs pandas ingress) | No |
| (future) | ggplot2 version matrix, rpy2 ABI sweeps | No |

## Conventions

- Scripts here may require R, network, or long runtimes — not run in PR CI.
- Findings feed into `docs/` and `project_memory/discoveries.md`; promote stable harnesses into `tests/` when they become gates.
- Official verification tiers: `docs/validation_strategy.md` (T0–T3) and `scripts/run_tests.ps1` (tier0–tier3).

## Running perf benchmarks

```bash
conda activate ggplotpy
python exploration/perf/benchmark_ingress.py              # row-count smoke (no R)
GGPLOTPY_BENCH_R=1 python exploration/perf/benchmark_ingress.py   # compare pandas vs Arrow nrow in R
```

See [perf/README.md](perf/README.md) for scope and draft SLOs.

## Related docs

- [packaging_plan.md](../docs/packaging_plan.md) — install paths
- [implementation_plan.md](../docs/implementation_plan.md) — Phase 8 performance milestone
- [testing_guide.md](../docs/testing_guide.md) — PR-blocking tiers vs exploration
