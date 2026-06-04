"""HARM face-frame & midface features (frontal landmarks)."""

from __future__ import annotations

from ..base import IdealSpec, L, MetricRaw, geo, left_pupil, make_raw, np, right_pupil

# ---------------------------------------------------------------------------
# FWHR = bizygomatic / (brow midline to upper-lip top), ideal 1.9-2.06
# ---------------------------------------------------------------------------

_FWHR = IdealSpec(1.9, 2.06, "range")


def compute_fwhr(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    width = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    height = abs(points[L.UPPER_LIP_TOP][1] - points[L.BROW_MID][1])
    ratio = (width / height) if height > 0 else float("nan")
    return make_raw("fwhr", "FWHR", "proportions", ratio,
                    module="HARM", source="frontal", ideal=_FWHR,
                    extra={"width_px": width, "height_px": height})


# ---------------------------------------------------------------------------
# Face Length = total face height / bizygomatic, ideal 1.33-1.38
# ---------------------------------------------------------------------------

_FL_M = IdealSpec(1.33, 1.38, "range")
_FL_F = IdealSpec(1.29, 1.33, "range")


def compute_face_length(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    height = abs(points[L.CHIN][1] - points[L.FOREHEAD_TOP][1])
    width = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    ratio = (height / width) if width > 0 else float("nan")
    return make_raw("face_length", "Face Length", "proportions", ratio,
                    module="HARM", source="frontal",
                    ideal=_FL_M if sex == "male" else _FL_F)


# ---------------------------------------------------------------------------
# Bizygomatic Width in mm — calibrated via assumed IPD = 63 mm
# Ideal 140-150 mm (adult male)
# ---------------------------------------------------------------------------

_IPD_MM = 63.0
_BIZYG_M = IdealSpec(140.0, 150.0, "range")
_BIZYG_F = IdealSpec(128.0, 138.0, "range")  # adult female estimate


def compute_bizygomatic_mm(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    ipd_px = geo.distance(left_pupil(points), right_pupil(points))
    bizyg_px = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    if ipd_px <= 0:
        return make_raw("bizygomatic_mm", "Bizygomatic Width (mm)", "proportions",
                        None, module="HARM", source="frontal",
                        ideal=_BIZYG_M, extra={"reason": "zero_ipd"})
    px_per_mm = ipd_px / _IPD_MM
    mm = bizyg_px / px_per_mm
    return make_raw("bizygomatic_mm", "Bizygomatic Width (mm)", "proportions", mm,
                    module="HARM", source="frontal",
                    ideal=_BIZYG_M if sex == "male" else _BIZYG_F,
                    extra={"ipd_px": ipd_px, "px_per_mm": px_per_mm,
                           "assumed_ipd_mm": _IPD_MM})


# ---------------------------------------------------------------------------
# Bitemporal Width as % of bizygomatic, ideal ~80-90 % per v2 spec
# ---------------------------------------------------------------------------

_BITEMP = IdealSpec(80.0, 90.0, "range")


def compute_bitemporal_width(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    bitemp = geo.distance(points[L.TEMPLE_LEFT], points[L.TEMPLE_RIGHT])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (bitemp / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw("bitemporal_width", "Bitemporal Width", "proportions", pct,
                    module="HARM", source="frontal", ideal=_BITEMP)


# ---------------------------------------------------------------------------
# Midface Ratio = IPD / (upper-lip top → glabella), ideal 0.95-1.05
# ---------------------------------------------------------------------------

_MIDFACE = IdealSpec(0.95, 1.05, "range")


def compute_midface_ratio(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    ipd = geo.distance(left_pupil(points), right_pupil(points))
    height = abs(points[L.UPPER_LIP_TOP][1] - points[L.BROW_MID][1])
    ratio = (ipd / height) if height > 0 else float("nan")
    return make_raw("midface_ratio", "Midface Ratio", "midface", ratio,
                    module="HARM", source="frontal", ideal=_MIDFACE)


# ---------------------------------------------------------------------------
# Facial Thirds = max % deviation of any third from 33.33 %, ideal ≤3
# (kept as the spec's "29.5-36.5% each" maps to a max 3.5pp deviation).
# We expose the *deviation* itself with ideal=range(0, 3.5).
# ---------------------------------------------------------------------------

_THIRDS = IdealSpec(0.0, 3.5, "range")


def compute_facial_thirds(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    brow_y = float(points[L.BROW_MID][1])
    nose_y = float(points[L.NOSE_BASE][1])
    chin_y = float(points[L.CHIN][1])
    forehead_y = float(points[L.FOREHEAD_TOP][1])
    total = chin_y - forehead_y
    if total <= 0:
        return make_raw("facial_thirds", "Facial Thirds", "proportions", None,
                        module="HARM", source="frontal", ideal=_THIRDS,
                        extra={"reason": "zero_total"})
    thirds = [
        (brow_y - forehead_y) / total,
        (nose_y - brow_y) / total,
        (chin_y - nose_y) / total,
    ]
    devs = [abs(t - 1 / 3.0) * 100.0 for t in thirds]
    return make_raw("facial_thirds", "Facial Thirds", "proportions", max(devs),
                    module="HARM", source="frontal", ideal=_THIRDS,
                    extra={"thirds": thirds, "devs_pct": devs})


# ---------------------------------------------------------------------------
# Lower Third Proportion = (nose_base → stomion) / (nose_base → chin) × 100,
# ideal 33-34 % (deviation from 33 % ≤3 → tier 1).
# ---------------------------------------------------------------------------

_LT = IdealSpec(0.0, 3.5, "range")


def compute_lower_third_proportion(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    nose_y = float(points[L.NOSE_BASE][1])
    chin_y = float(points[L.CHIN][1])
    stomion_y = (float(points[L.UPPER_LIP_BOTTOM][1]) + float(points[L.LOWER_LIP_TOP][1])) / 2.0
    denom = chin_y - nose_y
    if denom <= 0:
        return make_raw("lower_third_proportion", "Lower Third Proportion", "proportions",
                        None, module="HARM", source="frontal", ideal=_LT,
                        extra={"reason": "zero_denominator"})
    pct = (stomion_y - nose_y) / denom * 100.0
    dev = abs(pct - 100.0 / 3.0)
    return make_raw("lower_third_proportion", "Lower Third Proportion",
                    "proportions", dev, module="HARM", source="frontal", ideal=_LT,
                    extra={"ratio_pct": pct})


# ---------------------------------------------------------------------------
# Lower Third Subproportion — sub-thirds within the lower third (alt). Use
# the simpler stomion-position check as the alt metric. Ideal ≤3 % deviation.
# ---------------------------------------------------------------------------

_LT_ALT = IdealSpec(0.0, 5.0, "range")


def compute_lower_third_subproportion(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    """Stomion should sit ~33 % of the way from nose_base to chin (even
    33-33-33 within the lower third). Smaller deviation = more even."""
    nose_y = float(points[L.NOSE_BASE][1])
    chin_y = float(points[L.CHIN][1])
    stomion_y = (float(points[L.UPPER_LIP_BOTTOM][1]) + float(points[L.LOWER_LIP_TOP][1])) / 2.0
    denom = chin_y - nose_y
    if denom <= 0:
        return make_raw("lower_third_subproportion", "Lower Third Sub-proportion",
                        "proportions", None, module="HARM", source="frontal", ideal=_LT_ALT,
                        extra={"reason": "zero_denominator"})
    pct = (stomion_y - nose_y) / denom * 100.0
    return make_raw("lower_third_subproportion", "Lower Third Sub-proportion",
                    "proportions", abs(pct - 100.0 / 3.0),
                    module="HARM", source="frontal", ideal=_LT_ALT)


# ---------------------------------------------------------------------------
# Cheekbone Setness = (lip_y - apex_y) / (lip_y - pupil_y) × 100, ideal ≥81 %
# ---------------------------------------------------------------------------

_CHEEK = IdealSpec(81.0, 81.0, "lower_bound")


def compute_cheekbone_setness(points: np.ndarray, _img=None, _mask=None, sex="male") -> MetricRaw:
    lip_y = float(points[L.UPPER_LIP_TOP][1])
    pupil_y = (left_pupil(points)[1] + right_pupil(points)[1]) / 2.0
    apex_y = (float(points[L.CHEEKBONE_APEX_LEFT][1])
              + float(points[L.CHEEKBONE_APEX_RIGHT][1])) / 2.0
    denom = lip_y - pupil_y
    if denom <= 0:
        return make_raw("cheekbone_setness", "Cheekbone Setness", "midface", None,
                        module="HARM", source="frontal", ideal=_CHEEK,
                        extra={"reason": "bad_geometry"})
    pct = (lip_y - apex_y) / denom * 100.0
    return make_raw("cheekbone_setness", "Cheekbone Setness", "midface", pct,
                    module="HARM", source="frontal", ideal=_CHEEK,
                    extra={"lip_y": lip_y, "pupil_y": pupil_y, "apex_y": apex_y})


SPECS = [
    {"name": "fwhr", "label": "FWHR", "category": "proportions",
     "module": "HARM", "source": "frontal", "compute": compute_fwhr},
    {"name": "face_length", "label": "Face Length", "category": "proportions",
     "module": "HARM", "source": "frontal", "compute": compute_face_length},
    {"name": "bizygomatic_mm", "label": "Bizygomatic Width (mm)",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_bizygomatic_mm},
    {"name": "bitemporal_width", "label": "Bitemporal Width",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_bitemporal_width},
    {"name": "midface_ratio", "label": "Midface Ratio",
     "category": "midface", "module": "HARM", "source": "frontal",
     "compute": compute_midface_ratio},
    {"name": "facial_thirds", "label": "Facial Thirds",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_facial_thirds},
    {"name": "lower_third_proportion", "label": "Lower Third Proportion",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_lower_third_proportion},
    {"name": "lower_third_subproportion", "label": "Lower Third Sub-proportion",
     "category": "proportions", "module": "HARM", "source": "frontal",
     "compute": compute_lower_third_subproportion},
    {"name": "cheekbone_setness", "label": "Cheekbone Setness",
     "category": "midface", "module": "HARM", "source": "frontal",
     "compute": compute_cheekbone_setness},
]
