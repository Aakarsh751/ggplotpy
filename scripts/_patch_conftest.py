from pathlib import Path
root = Path(r"c:\ProfDM_Rproject\Ggplot2PY")
path = root / "tests/conftest.py"
text = path.read_text(encoding="utf-8")
# Add imports if missing
if "import gc" not in text:
    text = text.replace("from pathlib import Path\n\nimport pytest", "import gc\nimport os\nfrom pathlib import Path\n\nimport pytest")
elif "import os" not in text:
    text = text.replace("import gc\nfrom pathlib import Path", "import gc\nimport os\nfrom pathlib import Path")

HEAVY = '''
_HEAVY_TEST_DIRS = frozenset({"integration", "gallery", "parity", "extensions"})


def _skip_heavy_integration() -> bool:
    """True when heavy suites should not be collected (OOM-safe default in CI)."""
    if os.environ.get("GGPLOTPY_RUN_HEAVY") == "1":
        return False
    return os.environ.get("GGPLOTPY_SKIP_INTEGRATION") == "1"


def pytest_ignore_collect(collection_path, config):
    if not _skip_heavy_integration():
        return False
    try:
        rel = collection_path.relative_to(Path(__file__).resolve().parent)
    except ValueError:
        return False
    return rel.parts and rel.parts[0] in _HEAVY_TEST_DIRS


def pytest_runtest_teardown(item, nextitem):
    fspath = getattr(item, "fspath", None)
    if fspath is not None and "integration" in str(fspath).replace("\\\\", "/"):
        gc.collect()
'''
if "_HEAVY_TEST_DIRS" not in text:
    text = text.replace("GOLDEN_DIR = Path(__file__).resolve().parent / \"golden\"", "GOLDEN_DIR = Path(__file__).resolve().parent / \"golden\"" + HEAVY)

# Change mtcars_df scope to module
text = text.replace('@pytest.fixture\ndef mtcars_df():', '@pytest.fixture(scope="module")\ndef mtcars_df():')

path.write_text(text, encoding="utf-8", newline="\n")
print("conftest updated")
