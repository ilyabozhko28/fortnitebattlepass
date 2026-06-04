"""DIMORPHISM manual specs (user-rated). These have no compute callable; the
pipeline reads ``misc_ratings[feature_name]`` and synthesises a MetricRaw."""

from __future__ import annotations

_NAMES = [
    ("buccal_fat_size",        "Buccal Fat Size"),
    ("facial_hair_development","Facial Hair Development"),
    ("rough_skin_texture",     "Rough Skin Texture"),
    ("lip_fullness_dimo",      "Lip Fullness (Dimorphism)"),
]

SPECS = [
    {"name": n, "label": l, "category": "dimorphism",
     "module": "DIMO", "source": "manual", "compute": None}
    for n, l in _NAMES
]
