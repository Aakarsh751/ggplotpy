"""Sphinx configuration for the ggplotpy user documentation site.

Built from hand-curated Markdown in ``docs/``. The build does **not** import
``ggplotpy`` or require R/rpy2 — suitable for CI and Read the Docs.

Build locally::

    cd Ggplot2PY
    pip install -e ".[docs]"
    sphinx-build -W -b html docs docs/_build/html

Rd JSON for future docstring rendering lives in ``docs/_rd_json/`` (generated
by ``docs/scripts/extract_rd.py`` when R + ggplot2 are available).
"""
from __future__ import annotations

# -- Project information -----------------------------------------------------
project = "ggplotpy"
author = "Aakarsh Gupta"
copyright = "2026, Aakarsh Gupta"
release = "0.0.1.dev0"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
]
myst_heading_anchors = 3

source_suffix = {".md": "markdown"}
master_doc = "index"

exclude_patterns = [
    "_build",
    "_rd_json",
    "scripts",
    "templates",
    # engineering / governance docs — in-repo only (robstatm-py pattern)
    "architecture.md",
    "coverage_matrix.md",
    "documentation_plan.md",
    "implementation_plan.md",
    "implementation_rules.md",
    "nse_bridge.md",
    "packaging_plan.md",
    "quality_gates.md",
    "testing_guide.md",
    "user_interface.md",
    "validation_strategy.md",
    # user guides are included via index toctree (guides/*.md)
]

# -- HTML output (furo) ------------------------------------------------------
html_theme = "furo"
html_title = "ggplotpy"
html_static_path = ["_static"]
html_baseurl = "https://aakarsh751.github.io/ggplotpy/"
html_theme_options = {
    "source_repository": "https://github.com/Aakarsh751/ggplotpy",
    "source_branch": "main",
    "source_directory": "docs/",
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#336699",
        "color-brand-content": "#336699",
    },
}
pygments_style = "friendly"
pygments_dark_style = "monokai"
