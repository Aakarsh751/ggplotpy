# Releasing ggplotpy

Version is single-sourced from `src/ggplotpy/__init__.py` (`__version__`) via Hatchling.
Publishing to PyPI is one tag push; conda-forge is one PR after that.

## 1. Pre-flight

```bash
cd Ggplot2PY
# bump the version in one place:
#   src/ggplotpy/__init__.py  ->  __version__ = "0.1.0"
python -m build                      # builds dist/ggplotpy-<version>.{tar.gz,whl}
python -m twine check dist/*         # metadata sanity
./scripts/run_tests.ps1 -Tier all    # (Windows) green tiers
python -m sphinx -W -b html docs docs/_build/html
```

Confirm the wheel bundles the R helper (needed for `ggplotpy-bootstrap` after a PyPI install):

```bash
python -c "import zipfile,glob;print([n for n in zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]).namelist() if '_r_helper' in n])"
```

## 2. PyPI (one command)

Tag and push — `.github/workflows/publish.yml` builds and publishes via **PyPI
Trusted Publishing** (no secrets once configured at
<https://pypi.org/manage/account/publishing/> for repo `Aakarsh751/ggplotpy`,
workflow `publish.yml`, environment `pypi`):

```bash
git tag ggplotpy-v0.1.0
git push origin ggplotpy-v0.1.0
```

(First release only: create the project on PyPI by uploading once with a token, or
pre-register the Trusted Publisher as a "pending publisher".)

## 3. conda-forge

```bash
python scripts/pypi_sha256.py 0.1.0        # copy the printed sha256
```

- Fork <https://github.com/conda-forge/staged-recipes>.
- Copy `conda/recipe/meta.yaml` to `recipes/ggplotpy/meta.yaml`, set `version` and
  paste the sha256 into `source.sha256`.
- Open a PR. The bot builds `noarch: python`; on merge a `ggplotpy-feedstock` is created.
- After that, `conda install -c conda-forge ggplotpy` pulls `r-base` + `r-ggplot2` +
  `rpy2` automatically (the easiest cross-OS path).

## 4. Post-release

- Update `CHANGELOG.md`.
- Bump `__version__` to the next `.devN` if desired.
- Verify a clean install:
  `pip install ggplotpy && python -c "import ggplotpy; ggplotpy.check_setup()"`.
