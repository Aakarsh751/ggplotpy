"""T0 golden tests for aes string building (R-free)."""

from pathlib import Path

from ggplotpy.core.aes_util import format_aes_r_fragment, normalize_aes_mapping

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "aes" / "basic.txt"


def test_normalize_aes_mapping_sorts_keys():
    mapping = normalize_aes_mapping({"y": "mpg", "x": "wt"})
    assert list(mapping.keys()) == ["x", "y"]


def test_normalize_aes_collapses_whitespace():
    mapping = normalize_aes_mapping({"x": "  log( wt )  "})
    assert mapping["x"] == "log( wt )"


def test_format_aes_r_fragment_matches_golden():
    fragment = format_aes_r_fragment({"x": "wt", "y": "mpg", "color": "factor(cyl)"})
    expected = GOLDEN.read_text(encoding="utf-8").strip()
    assert fragment == expected
