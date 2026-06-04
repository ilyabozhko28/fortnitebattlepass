"""All measurement specs across 4 modules.

Each spec is a plain dict with keys:
    name, label, category, module ("HARM"/"DIMO"/"ANGU"/"MISC"),
    source ("frontal" | "side" | "manual"),
    compute (Callable or None for manual),
    needs_mask (bool, default False).
"""

from __future__ import annotations

from typing import Any, Callable

from ..schemas import MetricRaw


def _load_specs() -> list[dict]:
    from . import angu, dimo, misc
    from .harm import eyes, face, jaw, side

    out: list[dict] = []
    out.extend(eyes.SPECS)
    out.extend(face.SPECS)
    out.extend(jaw.SPECS)
    out.extend(side.SPECS)
    out.extend(dimo.specs())
    out.extend(angu.specs())
    out.extend(misc.specs())
    return out


_SPECS: list[dict] | None = None


def all_measurements() -> list[dict]:
    global _SPECS
    if _SPECS is None:
        _SPECS = _load_specs()
    return _SPECS


def specs_by_source(source: str) -> list[dict]:
    return [s for s in all_measurements() if s.get("source") == source]


def manual_features() -> list[dict]:
    return specs_by_source("manual")


__all__ = ["all_measurements", "specs_by_source", "manual_features", "MetricRaw"]
