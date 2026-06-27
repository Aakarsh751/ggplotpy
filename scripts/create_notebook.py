#!/usr/bin/env python3
"""Create notebooks/01_mvp_mtcars.ipynb via nbformat."""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# ggplotpy MVP — mtcars scatter\n", "\n", "Minimal notebook demonstrating real ggplot2 from Python."],
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "from ggplotpy import *\n",
                "import pandas as pd\n",
                "\n",
                "df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/mtcars.csv')\n",
                "p = (ggplot(df)\n",
                "     + aes(x='wt', y='mpg', color='factor(cyl)')\n",
                "     + geom_point()\n",
                "     + theme_minimal())\n",
                "p",
            ],
            "outputs": [],
            "execution_count": None,
        },
    ],
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "notebooks" / "01_mvp_mtcars.ipynb"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(NOTEBOOK, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
