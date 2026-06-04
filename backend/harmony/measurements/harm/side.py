"""HARM side-profile features.

These consume ``side_annotations``: a ``dict[str, (x, y)]`` of 16 manually
clicked points (see ``harmony/cv/profile_landmarks.py``).
"""

from __future__ import annotations

import math
from typing import Mapping

from ..base import IdealSpec, MetricRaw, geo, make_raw


SidePoints = Mapping[str, tuple[float, float]]


def _need(pts: SidePoints, *names) -> bool:
    return all(n in pts for n in names)


def _missing(name: str, label: str) -> MetricRaw:
    return make_raw(name, label, "side", None,
                    module="HARM", source="side", ideal=None,
                    extra={"reason": "side_profile_missing"})


# ---------------------------------------------------------------------------
# Nasofrontal Angle — angle at nasion between glabella and nose tip.
# Ideal 125-135° strict / 106-129° loose; pick mid range 115-135 as accepting.
# ---------------------------------------------------------------------------

_NFA = IdealSpec(125.0, 135.0, "range")


def compute_nasofrontal_angle(pts: SidePoints, sex="male") -> MetricRaw:
    if not _need(pts, "glabella", "nasion", "nose_tip"):
        return _missing("nasofrontal_angle", "Nasofrontal Angle")
    deg = geo.angle_between(pts["glabella"], pts["nasion"], pts["nose_tip"])
    return make_raw("nasofrontal_angle", "Nasofrontal Angle", "side", deg,
                    module="HARM", source="side", ideal=_NFA)


# ---------------------------------------------------------------------------
# Brow Ridge Inclination — supraorbital margin angle vs Frankfurt plane.
# Frankfurt plane approximated by the horizontal axis (we assume a level head
# in the side photo). Ideal 5-15°.
# ---------------------------------------------------------------------------

_BRI = IdealSpec(5.0, 15.0, "range")


def compute_brow_ridge_inclination(pts: SidePoints, sex="male") -> MetricRaw:
    if not _need(pts, "brow_ridge_tip", "nasion"):
        return _missing("brow_ridge_inclination", "Brow Ridge Inclination")
    # Angle of the line nasion → brow_ridge_tip vs the horizontal.
    # If brow_ridge_tip projects forward and slightly upward from nasion, the
    # angle is positive (typical for masculine brows).
    deg = geo.signed_angle_from_horizontal(pts["nasion"], pts["brow_ridge_tip"])
    return make_raw("brow_ridge_inclination", "Brow Ridge Inclination",
                    "side", abs(deg), module="HARM", source="side", ideal=_BRI)


# ---------------------------------------------------------------------------
# Gonial Angle — angle at gonion between tragion and gnathion.
# Ideal 112-123°.
# ---------------------------------------------------------------------------

_GONIAL = IdealSpec(112.0, 123.0, "range")


def compute_gonial_angle(pts: SidePoints, sex="male") -> MetricRaw:
    if not _need(pts, "tragion", "gonion", "gnathion"):
        return _missing("gonial_angle", "Gonial Angle")
    deg = geo.angle_between(pts["tragion"], pts["gonion"], pts["gnathion"])
    return make_raw("gonial_angle", "Gonial Angle", "side", deg,
                    module="HARM", source="side", ideal=_GONIAL)


# ---------------------------------------------------------------------------
# Ramus Length = ramus height / mandible body length, ideal 0.59-0.78.
# Ramus = tragion → gonion. Mandible body = gonion → pogonion.
# ---------------------------------------------------------------------------

_RAMUS = IdealSpec(0.59, 0.78, "range")


def compute_ramus_length(pts: SidePoints, sex="male") -> MetricRaw:
    if not _need(pts, "tragion", "gonion", "pogonion"):
        return _missing("ramus_length", "Ramus Length")
    ramus = geo.distance(pts["tragion"], pts["gonion"])
    body = geo.distance(pts["gonion"], pts["pogonion"])
    if body <= 0:
        return _missing("ramus_length", "Ramus Length")
    return make_raw("ramus_length", "Ramus Length", "side", ramus / body,
                    module="HARM", source="side", ideal=_RAMUS)


# ---------------------------------------------------------------------------
# Thirds of Jaw — vertical proportions of upper/mid/lower jaw on the side
# profile. We measure the deviation from even (33-33-33).
# Use nasion-stomion-pogonion-gnathion as three segments (rough proxy).
# Ideal: max deviation ≤3.5 percentage points.
# ---------------------------------------------------------------------------

_TOJ = IdealSpec(0.0, 3.5, "range")


def compute_thirds_of_jaw(pts: SidePoints, sex="male") -> MetricRaw:
    if not _need(pts, "subnasale", "stomion", "labrale_inferius", "gnathion"):
        return _missing("thirds_of_jaw", "Thirds of Jaw")
    sn = pts["subnasale"][1]
    st = pts["stomion"][1]
    li = pts["labrale_inferius"][1]
    gn = pts["gnathion"][1]
    total = gn - sn
    if total <= 0:
        return _missing("thirds_of_jaw", "Thirds of Jaw")
    thirds = [
        (st - sn) / total,
        (li - st) / total,
        (gn - li) / total,
    ]
    devs = [abs(t - 1 / 3.0) * 100.0 for t in thirds]
    return make_raw("thirds_of_jaw", "Thirds of Jaw", "side", max(devs),
                    module="HARM", source="side", ideal=_TOJ,
                    extra={"thirds": thirds})


SPECS = [
    {"name": "nasofrontal_angle", "label": "Nasofrontal Angle",
     "category": "side", "module": "HARM", "source": "side",
     "compute": compute_nasofrontal_angle},
    {"name": "brow_ridge_inclination", "label": "Brow Ridge Inclination",
     "category": "side", "module": "HARM", "source": "side",
     "compute": compute_brow_ridge_inclination},
    {"name": "gonial_angle", "label": "Gonial Angle",
     "category": "side", "module": "HARM", "source": "side",
     "compute": compute_gonial_angle},
    {"name": "ramus_length", "label": "Ramus Length",
     "category": "side", "module": "HARM", "source": "side",
     "compute": compute_ramus_length},
    {"name": "thirds_of_jaw", "label": "Thirds of Jaw",
     "category": "side", "module": "HARM", "source": "side",
     "compute": compute_thirds_of_jaw},
]
