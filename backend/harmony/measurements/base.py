"""Shared imports / type aliases for measurement modules.

Each measurement module exposes a single ``compute(...)`` function returning a
:class:`harmony.schemas.MetricRaw`. Module-level constants (``NAME``,
``LABEL``, ``CATEGORY``, ``MODULE``, ``SOURCE``, ``IDEAL``) declare the
metadata used by the registry.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .. import cv as cv_mod  # noqa: F401 — used as namespace
from ..cv import geometry as geo
from ..cv import landmarks as L
from ..schemas import IdealSpec, MetricRaw, Sex


def midpoint(a, b) -> tuple[float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def pupil_xy(points: np.ndarray, outer_idx: int, inner_idx: int) -> tuple[float, float]:
    return midpoint(points[outer_idx], points[inner_idx])


def left_pupil(points: np.ndarray) -> tuple[float, float]:
    return pupil_xy(points, L.LEFT_EYE_OUTER, L.LEFT_EYE_INNER)


def right_pupil(points: np.ndarray) -> tuple[float, float]:
    return pupil_xy(points, L.RIGHT_EYE_INNER, L.RIGHT_EYE_OUTER)


def make_raw(
    name: str,
    label: str,
    category: str,
    raw_value: float | None,
    *,
    module: str,
    source: str,
    ideal: IdealSpec | None,
    extra: dict[str, Any] | None = None,
) -> MetricRaw:
    debug: dict[str, Any] = {"module": module, "source": source}
    if ideal is not None:
        debug["ideal"] = ideal
    if extra:
        debug.update(extra)
    return MetricRaw(name=name, label=label, category=category,
                     raw_value=raw_value, debug=debug)


__all__ = [
    "np", "MetricRaw", "Sex", "geo", "L", "IdealSpec", "Any",
    "midpoint", "pupil_xy", "left_pupil", "right_pupil", "make_raw",
]
