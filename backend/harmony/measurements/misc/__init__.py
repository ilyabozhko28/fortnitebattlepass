"""MISC module — 50 features, all manual."""

from __future__ import annotations

from ..subjective import _SUBJECTIVE_FEATURES


def specs():
    return [
        {"name": n, "label": l, "category": cat,
         "module": "MISC", "source": "manual", "compute": None}
        for n, l, mod, cat, _desc in _SUBJECTIVE_FEATURES
        if mod == "MISC"
    ]
