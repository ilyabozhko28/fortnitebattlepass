"""HARM module — 26 features. Subdivided by anatomical category for code
organization; the module identifier on each spec is always ``"HARM"``."""

from __future__ import annotations

from . import eyes, face, jaw, side


def specs():
    """All HARM measurement specs in display order."""
    return [
        *eyes.SPECS,
        *face.SPECS,
        *jaw.SPECS,
        *side.SPECS,
    ]
