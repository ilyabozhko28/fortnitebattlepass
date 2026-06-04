"""DIMO module — 11 features mixing automatic (frontal/side) and manual."""

from __future__ import annotations

from . import auto, manual_specs


def specs():
    return [*auto.SPECS, *manual_specs.SPECS]
