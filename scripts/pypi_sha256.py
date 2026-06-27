"""Print the SHA256 of ggplotpy's sdist on PyPI (for the conda-forge recipe).

Usage:  python scripts/pypi_sha256.py 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    version = argv[1]
    url = f"https://pypi.org/pypi/ggplotpy/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
        data = json.load(resp)
    for f in data["urls"]:
        if f["packagetype"] == "sdist":
            # PyPI already provides the digest, but recompute to be safe.
            with urllib.request.urlopen(f["url"], timeout=60) as r:  # noqa: S310
                digest = hashlib.sha256(r.read()).hexdigest()
            print(f"{f['filename']}  sha256:")
            print(digest)
            return 0
    print("No sdist found for that version on PyPI.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
