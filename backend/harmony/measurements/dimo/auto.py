"""DIMORPHISM automatic metrics (frontal + side)."""

from __future__ import annotations

from typing import Mapping

from ..base import IdealSpec, L, MetricRaw, geo, make_raw, np


SidePoints = Mapping[str, tuple[float, float]]


# ---------------------------------------------------------------------------
# Eye Depth (side) — orbital vector. Positive = deep-set. Approximated as
# horizontal offset of upper_eyelid_mid behind brow_ridge_tip, in % of head depth.
# ---------------------------------------------------------------------------

_EYE_DEPTH = IdealSpec(3.0, 8.0, "range")  # 3-8% inset is deep-set ideal


def compute_eye_depth(pts: SidePoints, sex="male") -> MetricRaw:
    if not all(k in pts for k in ("brow_ridge_tip", "upper_eyelid_mid", "tragion")):
        return make_raw("eye_depth", "Eye Depth", "side", None,
                        module="DIMO", source="side",
                        ideal=_EYE_DEPTH, extra={"reason": "side_profile_missing"})
    head_depth = abs(pts["tragion"][0] - pts["brow_ridge_tip"][0])
    if head_depth <= 0:
        return make_raw("eye_depth", "Eye Depth", "side", None,
                        module="DIMO", source="side",
                        ideal=_EYE_DEPTH, extra={"reason": "zero_head_depth"})
    # Eyelid behind brow ridge: positive = inset. Assume right-facing profile
    # so x increases toward the back of the head; we use absolute offset.
    inset = abs(pts["brow_ridge_tip"][0] - pts["upper_eyelid_mid"][0])
    return make_raw("eye_depth", "Eye Depth", "side",
                    inset / head_depth * 100.0,
                    module="DIMO", source="side", ideal=_EYE_DEPTH)


# ---------------------------------------------------------------------------
# Brow Ridge Shape (side) — supraorbital projection in mm, ideal > 8 mm.
# Approximated as horizontal distance from nasion to brow_ridge_tip,
# calibrated via frontal IPD (carried in the request side-effect param).
# Here we just produce the raw pixel projection — calibration done in pipeline
# if frontal IPD is available; otherwise we surface "pixels" as raw.
# ---------------------------------------------------------------------------

_BROW_PROJ = IdealSpec(8.0, 8.0, "lower_bound")  # ≥ 8 mm


def compute_brow_ridge_shape(pts: SidePoints, sex="male",
                              pixels_per_mm: float | None = None) -> MetricRaw:
    if not all(k in pts for k in ("nasion", "brow_ridge_tip")):
        return make_raw("brow_ridge_shape", "Brow Ridge Shape", "side", None,
                        module="DIMO", source="side", ideal=_BROW_PROJ,
                        extra={"reason": "side_profile_missing"})
    px = abs(pts["brow_ridge_tip"][0] - pts["nasion"][0])
    if pixels_per_mm and pixels_per_mm > 0:
        mm = px / pixels_per_mm
        return make_raw("brow_ridge_shape", "Brow Ridge Shape", "side", mm,
                        module="DIMO", source="side", ideal=_BROW_PROJ,
                        extra={"projection_mm": mm})
    return make_raw("brow_ridge_shape", "Brow Ridge Shape", "side", None,
                    module="DIMO", source="side", ideal=_BROW_PROJ,
                    extra={"reason": "no_mm_calibration", "projection_px": px})


# ---------------------------------------------------------------------------
# Chin Shape — combine frontal chin width + side projection
# Ideal: high projection. Approximated as the horizontal projection of pogonion
# beyond gnathion's x, as % of head depth.
# ---------------------------------------------------------------------------

_CHIN_SHAPE = IdealSpec(0.0, 5.0, "range")  # well-projected; small offset = strong


def compute_chin_shape(pts: SidePoints, sex="male") -> MetricRaw:
    if not all(k in pts for k in ("pogonion", "gnathion", "tragion")):
        return make_raw("chin_shape", "Chin Shape", "side", None,
                        module="DIMO", source="side", ideal=_CHIN_SHAPE,
                        extra={"reason": "side_profile_missing"})
    head_depth = abs(pts["tragion"][0] - pts["pogonion"][0])
    if head_depth <= 0:
        return make_raw("chin_shape", "Chin Shape", "side", None,
                        module="DIMO", source="side", ideal=_CHIN_SHAPE,
                        extra={"reason": "zero_head_depth"})
    # Pogonion should project forward of gnathion (or roughly at same x for
    # square chin). Measure horizontal offset relative to head depth.
    offset = abs(pts["pogonion"][0] - pts["gnathion"][0]) / head_depth * 100.0
    return make_raw("chin_shape", "Chin Shape", "side", offset,
                    module="DIMO", source="side", ideal=_CHIN_SHAPE)


# ---------------------------------------------------------------------------
# Ramus Length Front — visible ramus / lower face height, ideal 35-45 %
# Frontal proxy: distance from gonion y to top-of-ear y (estimated via temple)
# divided by lower face height (nose_base → chin).
# ---------------------------------------------------------------------------

_RLF = IdealSpec(35.0, 45.0, "range")


def compute_ramus_length_front(points, _img=None, _mask=None, sex="male") -> MetricRaw:
    gonion_y = (float(points[L.GONION_LEFT][1]) + float(points[L.GONION_RIGHT][1])) / 2.0
    temple_y = (float(points[L.TEMPLE_LEFT][1]) + float(points[L.TEMPLE_RIGHT][1])) / 2.0
    lower_face = float(points[L.CHIN][1]) - float(points[L.NOSE_BASE][1])
    if lower_face <= 0:
        return make_raw("ramus_length_front", "Ramus Length (Front)", "lower",
                        None, module="DIMO", source="frontal", ideal=_RLF,
                        extra={"reason": "bad_geometry"})
    visible = abs(gonion_y - temple_y)
    return make_raw("ramus_length_front", "Ramus Length (Front)", "lower",
                    visible / lower_face * 100.0,
                    module="DIMO", source="frontal", ideal=_RLF)


# ---------------------------------------------------------------------------
# Gonion Outward Growth = gonion width / bizygomatic, ideal 86-92 %
# ---------------------------------------------------------------------------

_GOG = IdealSpec(86.0, 92.0, "range")


def compute_gonion_outward(points, _img=None, _mask=None, sex="male") -> MetricRaw:
    gonia = geo.distance(points[L.GONION_LEFT], points[L.GONION_RIGHT])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (gonia / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw("gonion_outward_growth", "Gonion Outward Growth", "lower",
                    pct, module="DIMO", source="frontal", ideal=_GOG)


# ---------------------------------------------------------------------------
# Narrowing Upper Third = bitemporal / bizygomatic, ideal 80-90 % (same as HARM
# bitemporal but rated under DIMO with stricter narrowing semantic).
# ---------------------------------------------------------------------------

_NUT = IdealSpec(80.0, 90.0, "range")


def compute_narrowing_upper_third(points, _img=None, _mask=None, sex="male") -> MetricRaw:
    bitemp = geo.distance(points[L.TEMPLE_LEFT], points[L.TEMPLE_RIGHT])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (bitemp / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw("narrowing_upper_third", "Narrowing Upper Third",
                    "proportions", pct, module="DIMO", source="frontal",
                    ideal=_NUT)


# ---------------------------------------------------------------------------
# Cheekbone Size — zygomatic arch projection / face width, ideal high.
# Frontal proxy: ratio of cheekbone-apex horizontal spread to bizygomatic.
# ---------------------------------------------------------------------------

_CBS = IdealSpec(75.0, 95.0, "range")


def compute_cheekbone_size(points, _img=None, _mask=None, sex="male") -> MetricRaw:
    apex_l = points[L.CHEEKBONE_APEX_LEFT]
    apex_r = points[L.CHEEKBONE_APEX_RIGHT]
    spread = abs(apex_l[0] - apex_r[0])
    bizyg = geo.distance(points[L.ZYGION_LEFT], points[L.ZYGION_RIGHT])
    pct = (spread / bizyg * 100.0) if bizyg > 0 else float("nan")
    return make_raw("cheekbone_size", "Cheekbone Size", "midface", pct,
                    module="DIMO", source="frontal", ideal=_CBS)


SPECS = [
    {"name": "eye_depth", "label": "Eye Depth", "category": "side",
     "module": "DIMO", "source": "side", "compute": compute_eye_depth},
    {"name": "brow_ridge_shape", "label": "Brow Ridge Shape",
     "category": "side", "module": "DIMO", "source": "side",
     "compute": compute_brow_ridge_shape},
    {"name": "chin_shape", "label": "Chin Shape", "category": "side",
     "module": "DIMO", "source": "side", "compute": compute_chin_shape},
    {"name": "ramus_length_front", "label": "Ramus Length (Front)",
     "category": "lower", "module": "DIMO", "source": "frontal",
     "compute": compute_ramus_length_front},
    {"name": "gonion_outward_growth", "label": "Gonion Outward Growth",
     "category": "lower", "module": "DIMO", "source": "frontal",
     "compute": compute_gonion_outward},
    {"name": "narrowing_upper_third", "label": "Narrowing Upper Third",
     "category": "proportions", "module": "DIMO", "source": "frontal",
     "compute": compute_narrowing_upper_third},
    {"name": "cheekbone_size", "label": "Cheekbone Size", "category": "midface",
     "module": "DIMO", "source": "frontal", "compute": compute_cheekbone_size},
]
