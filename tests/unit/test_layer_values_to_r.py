"""T0 (R-free) regression tests for layer-argument formatting and to_r() rewriting.

These cover bugs found in the 2026-06-22 audit:
- aes()/R() objects passed as arguments to another wrapper (geom_point(aes(...)))
- Python sequences as kwargs (coord_cartesian(xlim=(0, 5)))
- aes values containing commas (label = "paste(a, b)") mangling to_r() output
- aes() positional arguments (aes("wt", "mpg"))
"""

from __future__ import annotations

import pytest

from ggplotpy.core.aes_util import format_aes_r_fragment
from ggplotpy.core.defer import (
    DeferredRCall,
    format_r_call,
    format_r_value,
    normalize_r_kwargs,
)
from ggplotpy.core.raw import RObject
from ggplotpy.core.to_r_util import format_layer_for_to_r


def test_normalize_r_kwargs_dots_and_reserved_escape():
    out = normalize_r_kwargs(
        {"na_rm": True, "legend_position": "bottom", "class_": "x", "size": 2}
    )
    assert out == {
        "na.rm": True,
        "legend.position": "bottom",
        "class": "x",
        "size": 2,
    }


def test_reflected_wrapper_emits_dotted_param():
    from ggplotpy.codegen.reflect import build_r_callable

    geom_point = build_r_callable("ggplot2", "geom_point")
    assert geom_point(na_rm=True).code == "ggplot2::geom_point(na.rm = TRUE)"
    theme = build_r_callable("ggplot2", "theme")
    assert theme(legend_position="bottom").code == (
        'ggplot2::theme(legend.position = "bottom")'
    )


def test_format_r_value_scalars():
    assert format_r_value(None) == "NULL"
    assert format_r_value(True) == "TRUE"
    assert format_r_value(False) == "FALSE"
    assert format_r_value(3) == "3"
    assert format_r_value(2.5) == "2.5"
    assert format_r_value("hi") == '"hi"'


def test_format_r_value_sequences():
    assert format_r_value([1, 2, 3]) == "c(1, 2, 3)"
    assert format_r_value((0, 5)) == "c(0, 5)"
    assert format_r_value(["red", "blue"]) == 'c("red", "blue")'
    assert format_r_value([]) == "c()"


def test_format_r_value_numpy_scalars():
    np = pytest.importorskip("numpy")
    assert format_r_value(np.int64(5)) == "5"
    assert format_r_value(np.float64(2.5)) == "2.5"
    assert format_r_value(np.bool_(True)) == "TRUE"
    assert format_r_value(np.bool_(False)) == "FALSE"


def test_format_r_value_numpy_array_and_range():
    np = pytest.importorskip("numpy")
    assert format_r_value(np.array([1, 2, 3])) == "c(1, 2, 3)"
    assert format_r_value(range(3)) == "c(0, 1, 2)"


def test_format_r_value_dict_becomes_named_list():
    assert format_r_value({"family": "symmetric"}) == 'list(family = "symmetric")'
    assert format_r_value({"a": 1, "b": [1, 2]}) == "list(a = 1, b = c(1, 2))"


def test_format_r_value_deferred_and_raw_emit_code():
    d = DeferredRCall('ggplotpy::aes_from_strings(color = "factor(cyl)")')
    assert format_r_value(d) == 'ggplotpy::aes_from_strings(color = "factor(cyl)")'
    raw = RObject('annotate("text", x = 3, y = 20)')
    assert format_r_value(raw) == 'annotate("text", x = 3, y = 20)'


def test_format_r_call_nests_aes_argument():
    aes_arg = DeferredRCall('ggplotpy::aes_from_strings(color = "factor(cyl)")')
    code = format_r_call("ggplot2", "geom_point", (aes_arg,), {})
    assert code == 'ggplot2::geom_point(ggplotpy::aes_from_strings(color = "factor(cyl)"))'


def test_format_r_call_tuple_kwarg():
    code = format_r_call("ggplot2", "coord_cartesian", (), {"xlim": (0, 5)})
    assert code == "ggplot2::coord_cartesian(xlim = c(0, 5))"


def test_to_r_converts_nested_aes_call():
    code = 'ggplot2::geom_point(ggplotpy::aes_from_strings(color = "factor(cyl)"))'
    assert format_layer_for_to_r(code) == "geom_point(aes(color = factor(cyl)))"


def test_to_r_preserves_comma_in_aes_value():
    code = 'ggplotpy::aes_from_strings(label = "paste(lab, cyl)", x = "wt")'
    out = format_layer_for_to_r(code)
    assert out == "aes(label = paste(lab, cyl), x = wt)"
    # The previous naive split produced invalid R like `aes(... = , ...)`.
    assert "= ," not in out


def test_to_r_value_with_trailing_paren():
    code = 'ggplotpy::aes_from_strings(x = "f()")'
    assert format_layer_for_to_r(code) == "aes(x = f())"


def test_aes_positional_fragment():
    from ggplotpy.core.aes import aes

    frag = aes("wt", "mpg").code
    assert frag == 'ggplotpy::aes_from_strings(x = "wt", y = "mpg")'


def test_aes_positional_then_keyword():
    from ggplotpy.core.aes import aes

    frag = aes("wt", "mpg", color="factor(cyl)").code
    assert "x = \"wt\"" in frag and "y = \"mpg\"" in frag
    assert 'color = "factor(cyl)"' in frag


def test_aes_too_many_positional_raises():
    from ggplotpy.core.aes import aes

    with pytest.raises(TypeError):
        aes("a", "b", "c")


def test_aes_duplicate_positional_keyword_raises():
    from ggplotpy.core.aes import aes

    with pytest.raises(TypeError):
        aes("wt", x="mpg")


def test_empty_aes_fragment_roundtrips():
    assert format_aes_r_fragment({}) == "aes_from_strings()"
    assert format_layer_for_to_r("ggplotpy::aes_from_strings()") == "aes()"
