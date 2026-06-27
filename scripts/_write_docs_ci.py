from pathlib import Path
root = Path(r"c:\ProfDM_Rproject\Ggplot2PY")

pp = root / "pyproject.toml"
text = pp.read_text(encoding="utf-8")
comment = (
    "# OOM-safe pytest env (see docs/testing_guide.md):\n"
    "#   GGPLOTPY_SKIP_INTEGRATION=1  skip integration/gallery/parity/extensions collection (CI matrix default)\n"
    "#   GGPLOTPY_RUN_HEAVY=1         collect and run all suites in one process (local only; may OOM)\n"
    "#   GGPLOTPY_SKIP_NOTEBOOKS=1    skip notebook execute tests during fast loops\n"
)
if "GGPLOTPY_SKIP_INTEGRATION" not in text:
    text = text.replace("[tool.pytest.ini_options]\n", "[tool.pytest.ini_options]\n" + comment)
    pp.write_text(text, encoding="utf-8", newline="\n")

ci_path = root / ".github/workflows/ci.yml"
ci_path.write_text(
    """name: CI

on:
  push:
    branches: [main, master]
    paths:
      - "Ggplot2PY/**"
  pull_request:
    paths:
      - "Ggplot2PY/**"

defaults:
  run:
    working-directory: Ggplot2PY

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: "4.4"

      - name: Install R packages
        shell: bash
        run: |
          Rscript -e 'install.packages(c("ggplot2", "rlang", "svglite"), repos="https://cloud.r-project.org")'
          Rscript -e 'install.packages("r-helper/ggplotpy", repos=NULL, type="source")'

      - name: Install ggplotpy (dev)
        run: pip install -e ".[dev]"

      - name: Unit tests (T0, OOM-safe)
        env:
          GGPLOTPY_SKIP_NOTEBOOKS: "1"
          GGPLOTPY_SKIP_INTEGRATION: "1"
        run: pytest tests/unit -q

  integration:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: "4.4"

      - name: Install R packages
        shell: bash
        run: |
          Rscript -e 'install.packages(c("ggplot2", "rlang", "svglite"), repos="https://cloud.r-project.org")'
          Rscript -e 'install.packages("r-helper/ggplotpy", repos=NULL, type="source")'

      - name: Install ggplotpy (dev)
        run: pip install -e ".[dev]"

      - name: Integration tests (T1, one subprocess per file)
        env:
          GGPLOTPY_SKIP_NOTEBOOKS: "1"
        shell: bash
        run: bash scripts/run_tests.sh tier1
""",
    encoding="utf-8",
    newline="\n",
)

guide = root / "docs/testing_guide.md"
g = guide.read_text(encoding="utf-8")
oom = """
---

## OOM avoidance (rpy2 + ggplot2 render)

Running `pytest tests/` in a **single Python process** loads rpy2 once and keeps R graphics state and heap growth across many render tests. On Windows and in CI agents this often triggers **OOM kills** (subagent / runner crashes).

**Defaults (safe):**

| Mechanism | Behavior |
|-----------|----------|
| `GGPLOTPY_SKIP_INTEGRATION=1` | Skips collecting `tests/integration`, `gallery`, `parity`, `extensions` (matrix T0 job) |
| `scripts/run_tests.ps1` / `run_tests.sh` | **Tier0:** unit only; **Tier1:** each `tests/integration/test_*.py` in its own subprocess |
| `GGPLOTPY_RUN_HEAVY=1` | Opt-in: full tree in one process (local machines with enough RAM only) |
| `conftest.py` | Module-scoped `mtcars_df`; `gc.collect()` after each integration test |
| `_render_plot` | `svglite` / `png()` + `try(dev.off(), silent=TRUE)` in `finally` always |

**Recommended local loop (Windows):**

```powershell
$env:R_HOME = "C:\\Program Files\\R\\R-4.5.2"
$env:PATH = "C:\\Program Files\\R\\R-4.5.2\\bin\\x64;" + $env:PATH
.\\scripts\\run_tests.ps1 -Tier all
```

Do **not** run `python -m pytest tests/ -q` unless `GGPLOTPY_RUN_HEAVY=1`.

"""
if "## OOM avoidance" not in g:
    g = g.replace("## Markers", oom + "## Markers")
    guide.write_text(g, encoding="utf-8", newline="\n")

disc = root / "project_memory/discoveries.md"
d = disc.read_text(encoding="utf-8") if disc.exists() else "# Discoveries\n\n"
entry = """
## 2026-06-21 — Integration test OOM (rpy2 + graphics devices)

**Symptom:** Subagents and local pytest runs die with OOM when executing `pytest tests/` in one process.

**Root cause:** Cumulative R heap + leaked graphics devices when many `_repr_svg_` / `_repr_png_` renders run sequentially in one rpy2 session; Windows agents are especially sensitive.

**Mitigations shipped:** per-file subprocess Tier1 runner; `GGPLOTPY_SKIP_INTEGRATION` collection gate; always `try(dev.off(), silent=TRUE)` in `_render_plot` finally; module-scoped fixtures + `gc.collect()` after integration tests.

"""
if "Integration test OOM" not in d:
    if not d.strip().endswith("\n"):
        d += "\n"
    d += entry
    disc.write_text(d, encoding="utf-8", newline="\n")

print("docs/ci done")
