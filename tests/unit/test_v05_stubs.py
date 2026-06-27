"""Unit tests — animate transition_states + remaining v1.0 backend stubs (T0).

The sf bridge is now a real implementation (see ``test_sf_bridge.py``); the
isolated subprocess renderer is real too (see ``test_subprocess_render.py``).
"""

from __future__ import annotations

import pytest

from ggplotpy.core.animate import transition_states
from ggplotpy.core.defer import DeferredRCall


def test_transition_states_string_aes():
    layer = transition_states(states="species", transition_length=1)
    assert isinstance(layer, DeferredRCall)
    assert 'states = "species"' in layer.code


def test_rserve_backend_not_implemented():
    from ggplotpy.backend.rserve import RserveBackend

    backend = RserveBackend()
    with pytest.raises(NotImplementedError, match="v1.0"):
        backend.r()


def test_subprocess_backend_not_implemented():
    from ggplotpy.backend.subprocess import SubprocessBackend

    backend = SubprocessBackend()
    with pytest.raises(NotImplementedError, match="v1.0"):
        backend.eval_r("1+1")
