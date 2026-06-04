"""Side-profile landmark catalog.

User-clicked named points for the side view (no automatic detection — see
``SideAnnotator.tsx``). The frontend mirrors this list, and a parametrized
test verifies parity between client and server lists.
"""

from __future__ import annotations

# (name, human_label, description)
SIDE_POINTS: list[tuple[str, str, str]] = [
    ("trichion",         "Trichion",         "Hairline at the top of the forehead"),
    ("glabella",         "Glabella",         "Most prominent forward point between the brows"),
    ("brow_ridge_tip",   "Brow ridge tip",   "Most forward point of the supraorbital ridge"),
    ("nasion",           "Nasion",           "Deepest point of the bridge of the nose"),
    ("nose_tip",         "Nose tip",         "Pronasale"),
    ("subnasale",        "Subnasale",        "Junction of columella and upper lip"),
    ("labrale_superius", "Upper lip top",    "Vermillion border of the upper lip"),
    ("stomion",          "Stomion",          "Midline of the labial fissure"),
    ("labrale_inferius", "Lower lip bottom", "Vermillion border of the lower lip"),
    ("pogonion",         "Pogonion",         "Most prominent forward point of the chin"),
    ("gnathion",         "Gnathion",         "Lowest midline point of the chin"),
    ("gonion",           "Gonion",           "Jaw angle where ramus meets mandible body"),
    ("tragion",          "Tragion",          "Notch above the tragus of the ear"),
    ("eye_outer_corner", "Eye outer corner", "Lateral canthus visible on the profile"),
    ("upper_eyelid_mid", "Upper eyelid mid", "Midpoint of upper eyelid (for eye depth)"),
    ("brow_lower_mid",   "Brow lower mid",   "Lower edge of the brow at its midpoint"),
]

NAMES = [name for name, _, _ in SIDE_POINTS]
LABELS = {name: label for name, label, _ in SIDE_POINTS}
DESCRIPTIONS = {name: desc for name, _, desc in SIDE_POINTS}


def validate_annotations(annotations: dict | None) -> dict[str, tuple[float, float]] | None:
    """Coerce JSON ``{name: [x,y]}`` (or ``{name: {x,y}}``) into a dict of
    tuples. Unknown names are dropped silently. Returns ``None`` for empty
    input."""
    if not annotations:
        return None
    out: dict[str, tuple[float, float]] = {}
    for name in NAMES:
        v = annotations.get(name)
        if v is None:
            continue
        if isinstance(v, dict):
            try:
                out[name] = (float(v["x"]), float(v["y"]))
            except (KeyError, TypeError, ValueError):
                continue
        elif isinstance(v, (list, tuple)) and len(v) >= 2:
            try:
                out[name] = (float(v[0]), float(v[1]))
            except (TypeError, ValueError):
                continue
    return out or None
