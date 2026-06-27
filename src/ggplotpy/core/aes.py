"""ggplot2 aes() bridge via ggplotpy R helper."""

from __future__ import annotations

from ggplotpy.core.aes_util import format_aes_r_fragment, normalize_aes_mapping
from ggplotpy.core.defer import DeferredRCall


_POSITIONAL_AES = ("x", "y")


def aes(*args: str, **kwargs: str) -> DeferredRCall:
    """Build a deferred ggplot2 aes mapping from string expressions.

    Positional arguments map to ``x`` then ``y`` (matching ggplot2's
    ``aes(wt, mpg)`` idiom); keyword arguments set named aesthetics::

        aes("wt", "mpg")                     # x = wt, y = mpg
        aes(x="wt", y="mpg", color="factor(cyl)")
    """
    if len(args) > len(_POSITIONAL_AES):
        raise TypeError(
            f"aes() takes at most {len(_POSITIONAL_AES)} positional arguments "
            f"(x, y); got {len(args)}. Use keywords for other aesthetics."
        )
    mapping: dict[str, str] = {}
    for name, value in zip(_POSITIONAL_AES, args):
        mapping[name] = value
    for name in _POSITIONAL_AES[: len(args)]:
        if name in kwargs:
            raise TypeError(f"aes() got multiple values for aesthetic {name!r}")
    mapping.update(kwargs)
    mapping = normalize_aes_mapping(mapping)
    return DeferredRCall(f"ggplotpy::{format_aes_r_fragment(mapping)}")
