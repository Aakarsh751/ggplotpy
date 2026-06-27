"""Shared fixtures for validation-strategy edge matrix (cases 2–9)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def make_synthetic_df(n: int = 100, seed: int = 42) -> pd.DataFrame:
    """Synthetic frame with numeric, categorical, and awkward column names."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "x": rng.normal(size=n),
            "y": rng.normal(size=n),
            "wt": rng.uniform(1.0, 5.0, size=n),
            "cyl": rng.choice([4, 6, 8], size=n),
            "group": rng.choice(["A", "B", "C"], size=n),
            "facet_row": rng.choice(["r1", "r2"], size=n),
            "weird-col": rng.integers(1, 10, size=n),
            "a b": rng.choice(["low", "high"], size=n),
        }
    )


@pytest.fixture
def synthetic_df():
    return make_synthetic_df()
