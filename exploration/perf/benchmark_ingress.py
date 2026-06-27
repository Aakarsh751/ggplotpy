#!/usr/bin/env python3
"""Stub: compare pandas vs Arrow ingress row counts (10k rows, no 1M sweep).

Set ``GGPLOTPY_BENCH_R=1`` to push tables through R and compare ``nrow()`` when R is available.
"""

from __future__ import annotations

import os

N_ROWS = 10_000


def make_pandas():
    import pandas as pd

    return pd.DataFrame({"x": range(N_ROWS), "y": range(N_ROWS)})


def make_arrow():
    import pyarrow as pa

    return pa.table({"x": range(N_ROWS), "y": range(N_ROWS)})


def _r_nrow(r_df) -> int:
    from ggplotpy.backend.inprocess import r

    return int(r().r("nrow")(r_df)[0])


def bench_pandas_r(df) -> int:
    from ggplotpy.data.pandas_bridge import pandas_to_r

    return _r_nrow(pandas_to_r(df))


def bench_arrow_r(table) -> int:
    from ggplotpy.data.arrow import arrow_to_r

    return _r_nrow(arrow_to_r(table))


def main() -> None:
    pdf = make_pandas()
    print(f"pandas source rows: {len(pdf)}")

    try:
        table = make_arrow()
    except ImportError:
        print("pyarrow not installed — skip Arrow path")
        table = None
    else:
        print(f"arrow source rows: {table.num_rows}")

    if os.environ.get("GGPLOTPY_BENCH_R") != "1":
        print("Set GGPLOTPY_BENCH_R=1 to compare R nrow (requires R + ggplot2 + optional R arrow)")
        return

    try:
        pandas_n = bench_pandas_r(pdf)
        print(f"pandas → R nrow: {pandas_n}")
    except Exception as exc:
        print(f"pandas → R failed: {exc}")

    if table is not None:
        try:
            arrow_n = bench_arrow_r(table)
            print(f"arrow → R nrow: {arrow_n}")
        except Exception as exc:
            print(f"arrow → R failed: {exc}")


if __name__ == "__main__":
    main()
