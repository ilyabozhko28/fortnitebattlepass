"""HARM jaw / lower-third features (frontal landmarks; gonial+ramus live in side.py)."""

from __future__ import annotations

from ..base import IdealSpec, L, MetricRaw, geo, make_raw, np


# ---------------------------------------------------------------------------
# Jaw Width = bigonial / bizygomatic × 100, ideal 85.5-92 % male, 82-89 % female
# ---------------------------------------------------------------------------

_JW_M = IdealSpec(85.5, 92.0, "range")
_JW_F = IdealSpec(82.0, 89.0, "range")


def compute_jaw_width(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    bigonial = geo.distance(points[L.GONION_LEFT], points[L.GONION_RIGHT])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (bigonial / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw("jaw_width", "Jaw Width", "lower", pct,
                    module="HARM", source="frontal",
                    ideal=_JW_M if sex == "male" else _JW_F)


# ---------------------------------------------------------------------------
# Jaw Frontal Angle — interior angle at chin between gonions, ideal 84.5-95
# ---------------------------------------------------------------------------

_JFA_M = IdealSpec(84.5, 95.0, "range")
_JFA_F = IdealSpec(86.0, 97.0, "range")


def compute_jaw_frontal_angle(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    deg = geo.angle_between(points[L.GONION_LEFT], points[L.CHIN], points[L.GONION_RIGHT])
    return make_raw("jaw_frontal_angle", "Jaw Frontal Angle", "lower", deg,
                    module="HARM", source="frontal",
                    ideal=_JFA_M if sex == "male" else _JFA_F)


# ---------------------------------------------------------------------------
# Chin to Philtrum Ratio = chin height / philtrum length, ideal 2.05-2.55 male
# ---------------------------------------------------------------------------

_CP_M = IdealSpec(2.05, 2.55, "range")
_CP_F = IdealSpec(2.0, 2.5, "range")


def compute_chin_to_philtrum(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    chin_h = abs(points[L.CHIN][1] - points[L.LOWER_LIP_BOTTOM][1])
    phil_h = abs(points[L.UPPER_LIP_TOP][1] - points[L.NOSE_BASE][1])
    ratio = (chin_h / phil_h) if phil_h > 0 else float("nan")
    return make_raw("chin_to_philtrum", "Chin to Philtrum Ratio", "lower", ratio,
                    module="HARM", source="frontal",
                    ideal=_CP_M if sex == "male" else _CP_F)


# ---------------------------------------------------------------------------
# Mouth to Nose Ratio = mouth width / nose width, ideal 1.38-1.53 male
# ---------------------------------------------------------------------------

_MN_M = IdealSpec(1.38, 1.53, "range")
_MN_F = IdealSpec(1.45, 1.67, "range")


def compute_mouth_to_nose(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    mouth = geo.distance(points[L.MOUTH_LEFT], points[L.MOUTH_RIGHT])
    nose = geo.distance(points[L.ALA_LEFT], points[L.ALA_RIGHT])
    ratio = (mouth / nose) if nose > 0 else float("nan")
    return make_raw("mouth_to_nose", "Mouth to Nose Ratio", "lower", ratio,
                    module="HARM", source="frontal",
                    ideal=_MN_M if sex == "male" else _MN_F)


# ---------------------------------------------------------------------------
# Nose-to-Bizygomatic Ratio = nose width / bizygomatic, ideal ~0.70
# ---------------------------------------------------------------------------

_NTB = IdealSpec(0.70, 0.70, "center")


def compute_nose_to_bizygomatic(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    nose = geo.distance(points[L.ALA_LEFT], points[L.ALA_RIGHT])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    ratio = (nose / bizyg) if bizyg > 0 else float("nan")
    return make_raw("nose_to_bizygomatic", "Nose to Bizygomatic Ratio",
                    "proportions", ratio,
                    module="HARM", source="frontal", ideal=_NTB)


# ---------------------------------------------------------------------------
# Neck Width — mask-based, ratio of neck silhouette to jaw width at lip level.
# Spec band male >90 %, female 75-85 %.
# ---------------------------------------------------------------------------

_NW_M = IdealSpec(90.0, 100.0, "range")
_NW_F = IdealSpec(75.0, 85.0, "range")


def _row_width_around(row, mid_x, max_half):
    if row[mid_x] == 0:
        return None
    left = mid_x
    lo = max(0, mid_x - max_half)
    while left > lo and row[left - 1] > 0:
        left -= 1
    right = mid_x
    hi = min(row.shape[0] - 1, mid_x + max_half)
    while right < hi and row[right + 1] > 0:
        right += 1
    return right - left + 1


def compute_neck_width(points: np.ndarray, _img=None, mask=None, sex="male") -> MetricRaw:
    ideal = _NW_M if sex == "male" else _NW_F
    if mask is None:
        return make_raw("neck_width", "Neck Width", "lower", None,
                        module="HARM", source="frontal", ideal=ideal,
                        extra={"reason": "no_mask"})
    h, w = mask.shape
    chin_y = int(points[L.CHIN][1])
    lip_y = int(points[L.LOWER_LIP_BOTTOM][1])
    bigonial = geo.distance(points[L.GONION_LEFT], points[L.GONION_RIGHT])
    if bigonial <= 0:
        return make_raw("neck_width", "Neck Width", "lower", None,
                        module="HARM", source="frontal", ideal=ideal,
                        extra={"reason": "zero_bigonial"})
    mid_x = int((points[L.ZYGION_LEFT][0] + points[L.ZYGION_RIGHT][0]) / 2.0)
    mid_x = max(0, min(w - 1, mid_x))
    max_half = int(bigonial * 1.0)
    if not (0 <= lip_y < h):
        return make_raw("neck_width", "Neck Width", "lower", None,
                        module="HARM", source="frontal", ideal=ideal,
                        extra={"reason": "lip_out_of_image"})
    jaw_at_lip = _row_width_around(mask[lip_y], mid_x, max_half)
    if not jaw_at_lip:
        for dy in (-2, -5, -10):
            yy = lip_y + dy
            if 0 <= yy < h:
                jaw_at_lip = _row_width_around(mask[yy], mid_x, max_half)
                if jaw_at_lip:
                    break
    if not jaw_at_lip:
        return make_raw("neck_width", "Neck Width", "lower", None,
                        module="HARM", source="frontal", ideal=ideal,
                        extra={"reason": "no_jaw_pixels_at_lip"})

    neck_max_half = max(1, jaw_at_lip // 2)
    offsets = np.linspace(0.10 * bigonial, 0.30 * bigonial, num=6)
    candidates: list[tuple[int, int, bool]] = []
    for off in offsets:
        y = int(chin_y + off)
        if not (0 <= y < h):
            continue
        wpx = _row_width_around(mask[y], mid_x, neck_max_half)
        if wpx and wpx > 0:
            hit_cap = wpx >= 2 * neck_max_half
            candidates.append((y, wpx, hit_cap))
    if not candidates:
        return make_raw("neck_width", "Neck Width", "lower", None,
                        module="HARM", source="frontal", ideal=ideal,
                        extra={"reason": "no_neck_pixels"})
    _y, neck_px, hit_cap = min(candidates, key=lambda t: t[1])
    pct = neck_px / jaw_at_lip * 100.0
    extra: dict = {"neck_px": neck_px, "jaw_at_lip_px": jaw_at_lip}
    if hit_cap:
        extra["hair_contamination_suspected"] = True
    return make_raw("neck_width", "Neck Width", "lower", pct,
                    module="HARM", source="frontal", ideal=ideal, extra=extra)


SPECS = [
    {"name": "jaw_width", "label": "Jaw Width", "category": "lower",
     "module": "HARM", "source": "frontal", "compute": compute_jaw_width,
     "needs_mask": False},
    {"name": "jaw_frontal_angle", "label": "Jaw Frontal Angle",
     "category": "lower", "module": "HARM", "source": "frontal",
     "compute": compute_jaw_frontal_angle},
    {"name": "chin_to_philtrum", "label": "Chin to Philtrum Ratio",
     "category": "lower", "module": "HARM", "source": "frontal",
     "compute": compute_chin_to_philtrum},
    {"name": "mouth_to_nose", "label": "Mouth to Nose Ratio",
     "category": "lower", "module": "HARM", "source": "frontal",
     "compute": compute_mouth_to_nose},
    {"name": "nose_to_bizygomatic", "label": "Nose to Bizygomatic Ratio",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_nose_to_bizygomatic},
    {"name": "neck_width", "label": "Neck Width", "category": "lower",
     "module": "HARM", "source": "frontal", "compute": compute_neck_width,
     "needs_mask": True},
]
