"""Tiny, vectorized geometry helpers (NumPy only).

Kept pure and side-effect-free so they can be unit-tested without any image
dependencies.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

Point = tuple[float, float]


def to_np(points: Sequence[Point] | np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(f"expected (N, 2) points, got shape {arr.shape}")
    return arr


def distance(a: Point | np.ndarray, b: Point | np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return float(np.linalg.norm(a - b))


def midpoint(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def signed_angle_from_horizontal(a: Point, b: Point) -> float:
    """Return signed degrees of the line a->b vs the +X axis.

    Image coordinates have y growing downward, so we negate dy so that "tilted
    upward to the right" yields a positive angle.
    """
    dx = b[0] - a[0]
    dy = -(b[1] - a[1])
    return math.degrees(math.atan2(dy, dx))


def angle_between(a: Point, vertex: Point, b: Point) -> float:
    """Interior angle at ``vertex`` between rays vertex->a and vertex->b, in degrees."""
    v1 = np.array([a[0] - vertex[0], a[1] - vertex[1]], dtype=np.float64)
    v2 = np.array([b[0] - vertex[0], b[1] - vertex[1]], dtype=np.float64)
    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 == 0 or n2 == 0:
        return float("nan")
    cos_t = float(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0))
    return math.degrees(math.acos(cos_t))


def horizontal_span(points: np.ndarray, idxs: Sequence[int]) -> float:
    sub = points[list(idxs)]
    return float(sub[:, 0].max() - sub[:, 0].min())


def vertical_span(points: np.ndarray, idxs: Sequence[int]) -> float:
    sub = points[list(idxs)]
    return float(sub[:, 1].max() - sub[:, 1].min())


def safe_div(num: float, denom: float, default: float | None = None) -> float | None:
    if denom == 0 or denom is None or num is None:
        return default
    return num / denom
