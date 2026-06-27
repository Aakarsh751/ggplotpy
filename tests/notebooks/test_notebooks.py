"""Execute MVP and extension demo notebooks end-to-end (nbclient).

Set ``GGPLOTPY_SKIP_NOTEBOOKS=1`` to skip during fast loops (``run_tests.ps1`` sets this).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NB_DIR = _REPO_ROOT / "notebooks"

_NOTEBOOKS = [
    _NB_DIR / "01_mvp_mtcars.ipynb",
    _NB_DIR / "02_extensions_demo.ipynb",
    _NB_DIR / "03_synthetic_gallery.ipynb",
]

_SKIP_ALL = os.environ.get("GGPLOTPY_SKIP_NOTEBOOKS") == "1"


def _nb_id(p: Path) -> str:
    return p.name


@pytest.mark.needs_r
@pytest.mark.needs_ggplot2
@pytest.mark.slow
@pytest.mark.skipif(_SKIP_ALL, reason="GGPLOTPY_SKIP_NOTEBOOKS=1 set")
@pytest.mark.parametrize(
    "nb_path",
    [p for p in _NOTEBOOKS if p.is_file()],
    ids=[_nb_id(p) for p in _NOTEBOOKS if p.is_file()],
)
def test_notebook_executes_clean(nb_path: Path):
    """Run the notebook via nbclient; fail on any CellExecutionError."""
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")

    nb = nbformat.read(str(nb_path), as_version=4)
    client = nbclient.NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(nb_path.parent)}},
    )
    client.execute()
