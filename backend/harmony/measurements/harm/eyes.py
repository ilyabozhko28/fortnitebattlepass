"""HARM eye+brow features (frontal landmarks)."""

from __future__ import annotations

import math

from ..base import IdealSpec, L, MetricRaw, geo, left_pupil, make_raw, np, right_pupil


# ---------------------------------------------------------------------------
# Eye Separation Ratio = IPD / bizygomatic * 100, ideal 44.3-47.4 % (M/F average)
# ---------------------------------------------------------------------------

_ESR_IDEAL_M = IdealSpec(44.3, 47.7, "range")
_ESR_IDEAL_F = IdealSpec(45.0, 47.9, "range")


def compute_eye_separation(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    ipd = geo.distance(left_pupil(points), right_pupil(points))
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (ipd / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw(
        "eye_separation_ratio", "Eye Separation Ratio", "eyes", pct,
        module="HARM", source="frontal",
        ideal=_ESR_IDEAL_M if sex == "male" else _ESR_IDEAL_F,
        extra={"ipd_px": ipd, "bizyg_px": bizyg},
    )


# ---------------------------------------------------------------------------
# Eye Aspect Ratio = eye width / eye height, ideal 2.8-3.6 male, 2.5-3.3 female
# ---------------------------------------------------------------------------

_EAR_M = IdealSpec(2.8, 3.6, "range")
_EAR_F = IdealSpec(2.5, 3.3, "range")


def _eye_aspect_one(points, outer, inner, top, bottom):
    w = geo.distance(points[outer], points[inner])
    h = abs(points[top][1] - points[bottom][1])
    return (w / h) if h > 0 else float("nan")


def compute_eye_aspect_ratio(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    left = _eye_aspect_one(points, L.LEFT_EYE_OUTER, L.LEFT_EYE_INNER, L.LEFT_EYE_TOP, L.LEFT_EYE_BOTTOM)
    right = _eye_aspect_one(points, L.RIGHT_EYE_OUTER, L.RIGHT_EYE_INNER, L.RIGHT_EYE_TOP, L.RIGHT_EYE_BOTTOM)
    avg = float(np.nanmean([left, right]))
    return make_raw(
        "eye_aspect_ratio", "Eye Aspect Ratio", "eyes", avg,
        module="HARM", source="frontal",
        ideal=_EAR_M if sex == "male" else _EAR_F,
        extra={"left": left, "right": right},
    )


# ---------------------------------------------------------------------------
# Lateral Canthal Tilt = degrees (lateral canthus above medial), ideal 5.2-8.5
# ---------------------------------------------------------------------------

_LCT_M = IdealSpec(5.2, 8.5, "range")
_LCT_F = IdealSpec(6.0, 9.5, "range")


def _canthal_one(points, outer_idx, inner_idx):
    outer = points[outer_idx]
    inner = points[inner_idx]
    width = abs(inner[0] - outer[0])
    if width <= 0:
        return float("nan")
    return math.degrees(math.atan2(inner[1] - outer[1], width))


def compute_lateral_canthal_tilt(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    left = _canthal_one(points, L.LEFT_EYE_OUTER, L.LEFT_EYE_INNER)
    right = _canthal_one(points, L.RIGHT_EYE_OUTER, L.RIGHT_EYE_INNER)
    avg = float(np.nanmean([left, right]))
    return make_raw(
        "lateral_canthal_tilt", "Lateral Canthal Tilt", "eyes", avg,
        module="HARM", source="frontal",
        ideal=_LCT_M if sex == "male" else _LCT_F,
        extra={"left_deg": left, "right_deg": right},
    )


# ---------------------------------------------------------------------------
# Eye-to-Eyebrow Distance ("Eye Setness") = (brow_y - eye_top_y) / eye_width
# Ideal range "0 - 0.65 (eyebrow position index)" per v2 spec.
# ---------------------------------------------------------------------------

_ETB_M = IdealSpec(0.0, 0.65, "range")
_ETB_F = IdealSpec(0.40, 0.85, "range")  # spec slightly higher band for females


def _eye_to_brow_one(points, eye_outer, eye_inner, eye_top, brow_inner, brow_outer):
    eye_width = abs(points[eye_inner][0] - points[eye_outer][0])
    if eye_width <= 0:
        return float("nan")
    brow_y = (points[brow_inner][1] + points[brow_outer][1]) / 2.0
    gap = abs(points[eye_top][1] - brow_y)
    return gap / eye_width


def compute_eye_to_brow_distance(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    left = _eye_to_brow_one(
        points, L.LEFT_EYE_OUTER, L.LEFT_EYE_INNER, L.LEFT_EYE_TOP,
        L.LEFT_BROW_INNER, L.LEFT_BROW_OUTER,
    )
    right = _eye_to_brow_one(
        points, L.RIGHT_EYE_OUTER, L.RIGHT_EYE_INNER, L.RIGHT_EYE_TOP,
        L.RIGHT_BROW_INNER, L.RIGHT_BROW_OUTER,
    )
    avg = float(np.nanmean([left, right]))
    return make_raw(
        "eye_to_brow_distance", "Eye-to-Eyebrow Distance", "eyes", avg,
        module="HARM", source="frontal",
        ideal=_ETB_M if sex == "male" else _ETB_F,
        extra={"left": left, "right": right},
    )


# ---------------------------------------------------------------------------
# Eyebrow Tilt — signed degrees of brow line vs horizontal, ideal slight positive
# ---------------------------------------------------------------------------

_BROW_TILT_M = IdealSpec(5.0, 13.0, "range")
_BROW_TILT_F = IdealSpec(11.0, 19.0, "range")


def compute_eyebrow_tilt(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    left = geo.signed_angle_from_horizontal(points[L.LEFT_BROW_OUTER], points[L.LEFT_BROW_INNER])
    right = geo.signed_angle_from_horizontal(points[L.RIGHT_BROW_INNER], points[L.RIGHT_BROW_OUTER])
    avg = (left + right) / 2.0
    return make_raw(
        "eyebrow_tilt", "Eyebrow Tilt", "eyes", avg,
        module="HARM", source="frontal",
        ideal=_BROW_TILT_M if sex == "male" else _BROW_TILT_F,
        extra={"left_deg": left, "right_deg": right},
    )


# ---------------------------------------------------------------------------
# Medial Canthal Angle = angle at glabella between rays to each medial canthus
# Ideal ~ 20.42°
# ---------------------------------------------------------------------------

_MCA = IdealSpec(20.42, 20.42, "center")


def compute_medial_canthal_angle(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    angle = geo.angle_between(
        points[L.LEFT_EYE_INNER], points[L.BROW_MID], points[L.RIGHT_EYE_INNER],
    )
    return make_raw(
        "medial_canthal_angle", "Medial Canthal Angle", "eyes", angle,
        module="HARM", source="frontal", ideal=_MCA,
    )


SPECS = [
    {"name": "eye_separation_ratio",  "label": "Eye Separation Ratio (IPD)",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_eye_separation},
    {"name": "eye_aspect_ratio", "label": "Eye Aspect Ratio",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_eye_aspect_ratio},
    {"name": "lateral_canthal_tilt", "label": "Lateral Canthal Tilt",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_lateral_canthal_tilt},
    {"name": "eye_to_brow_distance", "label": "Eye-to-Eyebrow Distance",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_eye_to_brow_distance},
    {"name": "eyebrow_tilt", "label": "Eyebrow Tilt",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_eyebrow_tilt},
    {"name": "medial_canthal_angle", "label": "Medial Canthal Angle",
     "category": "eyes", "module": "HARM", "source": "frontal",
     "compute": compute_medial_canthal_angle},
]
