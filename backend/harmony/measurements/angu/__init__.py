"""ANGU module — 9 features, all manual (subjective edge/projection ratings)."""

from __future__ import annotations

_NAMES = [
    ("mandible_visibility_front", "Mandible Visibility (Front)"),
    ("facial_3d_ness",            "Facial 3D-ness"),
    ("gonion_sharpness",          "Gonion Sharpness"),
    ("facial_depth",              "Facial Depth"),
    ("mandible_ramus_visibility", "Mandible & Ramus Visibility"),
    ("ogee_curve",                "Ogee Curve"),
    ("cheekbone_visibility",      "Cheekbone Visibility"),
    ("chin_angularity",           "Chin Angularity"),
    ("lower_midface_fat",         "Lower-Midface Fat"),
]


def specs():
    return [
        {"name": n, "label": l, "category": "angularity",
         "module": "ANGU", "source": "manual", "compute": None}
        for n, l in _NAMES
    ]
