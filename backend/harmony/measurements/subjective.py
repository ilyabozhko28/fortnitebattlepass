"""Subjective feature catalog — used by manual tier-pickers in the UI.

This module is the **single source of truth** for the subjective feature
definitions on the backend. The frontend mirrors it in
``frontend/src/lib/subjective_features.ts``. A parametrized test asserts the
two stay in sync.

Each entry is a dict with: ``name``, ``label``, ``category``, ``module``,
``description`` (UI hint), ``tiers`` (ordered list of (tier_int, points_float,
short_label) tuples).
"""

from __future__ import annotations

from .. import scoring


def _tiers_for(name: str) -> list[tuple[int, float, str]]:
    """Build the tier list for a feature from the points table.
    Default labels are 'T<n>'; UI replaces them with hand-written ones via
    the tier_label override map below.
    """
    table = scoring.points.POINTS.get(name, {})
    return [(t, float(p), TIER_LABELS.get(name, {}).get(t, f"T{t}"))
            for t, p in sorted(table.items())]


# Human-readable tier labels per feature. Only spec-required hints; UI shows
# tier numbers + points if no label is set.
TIER_LABELS: dict[str, dict[int, str]] = {
    # MISC SKIN
    "skin_clearness":          {1: "Clear, no acne", 2: "1-3 spots", 3: "Mild scattered",
                                4: "Moderate", 5: "Notable", 6: "Heavy", 7: "Severe", 8: "Cystic"},
    "hyperpigmentation":       {1: "None", 2: "Faint", 3: "Mild", 4: "Localized",
                                5: "Patchy", 6: "Pronounced", 7: "Heavy", 8: "Severe melasma"},
    "moles":                   {1: "None visible", 2: "1-2 small", 3: "Few small",
                                4: "Few moderate", 5: "Many", 6: "Many noticeable",
                                7: "Heavy", 8: "Disfiguring"},
    "skin_texture":            {1: "Smooth, glassy", 2: "Smooth", 3: "Slight texture",
                                4: "Mild texture", 5: "Visible pores", 6: "Rough",
                                7: "Very rough", 8: "Very poor"},
    "acne_scarring":           {1: "None", 2: "Very faint", 3: "Mild few scars",
                                4: "Mild", 5: "Moderate", 6: "Notable", 7: "Heavy", 8: "Severe"},
    "facial_folds_wrinkles":   {1: "None", 2: "Very faint", 3: "Mild", 4: "Moderate",
                                5: "Notable", 6: "Heavy", 7: "Deep", 8: "Severe"},
    # MISC EYE
    "upper_eyelid":           {1: "No UEE", 2: "Faint", 3: "Mild", 4: "Moderate",
                               5: "Visible", 6: "Pronounced", 7: "Heavy", 8: "Severe"},
    "lower_eyelid_shape":     {1: "Straight", 2: "Slight tilt", 3: "Mild rounded",
                               4: "Rounded", 5: "Downturned", 6: "Heavy", 7: "Sagging", 8: "Severe"},
    "sclera_show":            {1: "None", 2: "Very faint", 3: "Mild", 4: "Moderate",
                               5: "Visible", 6: "Pronounced", 7: "Heavy", 8: "Severe scleral show"},
    "eyelashes":              {1: "Thick, dark, long", 2: "Thick", 3: "Average",
                               4: "Sparse", 5: "Very sparse", 6: "Almost none", 7: "Absent"},
    "eyebrows":               {1: "Thick, dark, well-shaped", 2: "Thick", 3: "Average",
                               4: "Thin", 5: "Patchy", 6: "Sparse", 7: "Very sparse", 8: "Absent"},
    "periorbital_darkening":  {1: "None", 2: "Faint", 3: "Mild", 4: "Moderate",
                               5: "Noticeable", 6: "Pronounced", 7: "Severe", 8: "Very severe"},
    "under_eye_circles":      {1: "None", 2: "Faint", 3: "Mild", 4: "Moderate",
                               5: "Notable", 6: "Pronounced", 7: "Severe", 8: "Very severe"},
    "lee":                    {1: "None", 2: "Faint", 3: "Mild", 4: "Moderate",
                               5: "Notable", 6: "Heavy", 7: "Severe"},
    "eye_colour_eye":         {1: "Light/striking", 2: "Medium", 3: "Dark"},
    "scleral_triangles":      {1: "Even", 2: "Slight asym", 3: "Mild",
                               4: "Asymmetric", 5: "Moderate", 6: "Pronounced",
                               7: "Heavy", 8: "Severe"},
    "medial_canthus":         {1: "Downturned long", 2: "Slight", 3: "Average",
                               4: "Upturned short", 5: "Heavily upturned"},
    "pfl":                    {1: "27 mm+", 2: "26 mm", 3: "25 mm", 4: "24 mm",
                               5: "22-23 mm", 6: "20-21 mm", 7: "Below 20 mm", 8: "Very short"},
    "sclera_colour_eye":      {1: "White", 2: "Slightly off", 3: "Yellow tint", 4: "Heavy yellow"},
    "unibrow":                {1: "None", 2: "Very faint", 3: "Mild",
                               4: "Visible", 5: "Pronounced", 6: "Heavy",
                               7: "Joined", 8: "Very heavy"},
    # MISC COLOURING
    "skin_colour":            {1: "Tanned", 2: "Olive", 3: "Fair", 4: "Pale", 5: "Very pale"},
    "lip_colour":             {1: "Reddish pink", 2: "Pink", 3: "Pale pink",
                               4: "Pale", 5: "Bluish", 6: "Very pale"},
    "eyelash_visibility":     {1: "Contrasting", 2: "Visible", 3: "Average",
                               4: "Pale", 5: "Invisible"},
    "eye_colour_col":         {1: "Light (blue/green)", 2: "Hazel/light brown", 3: "Dark"},
    "hair_colour":            {1: "Dark", 2: "Medium", 3: "Light", 4: "Very light"},
    "eyebrow_colour":         {1: "Dark", 2: "Medium", 3: "Light", 4: "Very light"},
    "sclera_whiteness":       {1: "Bright white", 2: "White", 3: "Off-white"},
    # MISC LOWER THIRD
    "gonions":                {1: "Flared", 2: "Strong", 3: "Average", 4: "Weak",
                               5: "Very weak", 6: "Recessed", 7: "Sloped"},
    "chin_shape_misc":        {1: "Square", 2: "Strong", 3: "Average", 4: "Soft",
                               5: "Round", 6: "Pointed", 7: "Weak"},
    "chin_width":             {1: "Wide", 2: "Average-wide", 3: "Average",
                               4: "Narrow", 5: "Very narrow", 6: "Tapered"},
    "ramus_length_misc":      {1: "Tall", 2: "Long", 3: "Average", 4: "Short",
                               5: "Very short", 6: "Stubby", 7: "Hidden"},
    "mandible_length":        {1: "Long & straight", 2: "Long", 3: "Average",
                               4: "Short", 5: "Very short", 6: "Curved", 7: "Sloped"},
    "mandible_shape":         {1: "Straight", 2: "Slight curve", 3: "Mild curve",
                               4: "Curved", 5: "Sloped", 6: "Very sloped"},
    # MISC LIPS
    "lip_width":              {1: "Wide", 2: "Above avg", 3: "Average",
                               4: "Narrow", 5: "Very narrow", 6: "Tiny", 7: "Almost absent"},
    "philtrum_length":        {1: "Short", 2: "Slightly short", 3: "Average",
                               4: "Long", 5: "Very long", 6: "Excessive", 7: "Disfiguring"},
    "philtrum_ridges":        {1: "Defined", 2: "Visible", 3: "Faint", 4: "Absent", 5: "Inverted"},
    "lip_fullness_lips":      {1: "Full", 2: "Above avg", 3: "Average",
                               4: "Thin", 5: "Very thin", 6: "Disappearing", 7: "Absent"},
    "lip_health":             {1: "No cracking", 2: "Slight dryness", 3: "Mild cracking",
                               4: "Notable", 5: "Chapped", 6: "Bleeding", 7: "Severe"},
    "commissures":            {1: "Slight upturn", 2: "Neutral", 3: "Faint downturn",
                               4: "Downturned", 5: "Heavy downturn"},
    "cupids_bow":             {1: "Prominent", 2: "Defined", 3: "Faint",
                               4: "Absent", 5: "Flat"},
    "lip_seal":               {1: "Straight", 2: "Slight gap", 3: "Mild gap",
                               4: "Open", 5: "Very open"},
    # MISC NOSE
    "alar_width":             {1: "Narrow", 2: "Slightly wide", 3: "Average",
                               4: "Wide", 5: "Very wide", 6: "Bulbous", 7: "Very bulbous"},
    "nose_bulbosity":         {1: "Low", 2: "Slight", 3: "Mild", 4: "Moderate",
                               5: "Pronounced", 6: "Heavy", 7: "Severe"},
    "nasal_tip":              {1: "Defined", 2: "Slightly defined", 3: "Average",
                               4: "Soft", 5: "Bulbous", 6: "Drooping", 7: "Sagging"},
    "nostril_show":           {1: "Minimal", 2: "Slight", 3: "Mild", 4: "Moderate",
                               5: "Visible", 6: "Heavy", 7: "Excessive"},
    "nostril_flare":          {1: "None", 2: "Slight", 3: "Mild", 4: "Visible", 5: "Heavy"},
    "dorsum":                 {1: "Straight", 2: "Slight hump", 3: "Mild hump",
                               4: "Saddle", 5: "Severe"},
    "radix_projection":       {1: "Projected", 2: "Slight", 3: "Average",
                               4: "Low", 5: "Very low", 6: "Recessed", 7: "Saddle"},
    # MISC OTHER
    "ears":                   {1: "Pinned back", 2: "Slightly out", 3: "Mild",
                               4: "Average", 5: "Sticking out", 6: "Heavy", 7: "Very heavy",
                               8: "Extreme"},
    "symmetry":               {1: "Minimal asymmetry", 2: "Slight", 3: "Mild",
                               4: "Notable", 5: "Asymmetric", 6: "Heavy",
                               7: "Very asymmetric", 8: "Severe"},
    # ANGU
    "mandible_visibility_front": {1: "Sharp, broad flare", 2: "Sharp",
                                  3: "Clear", 4: "Average", 5: "Soft",
                                  6: "Buried", 7: "Hidden"},
    "facial_3d_ness":            {1: "Strong projection", 2: "Strong", 3: "Average",
                                  4: "Mild", 5: "Flat", 6: "Very flat", 7: "Concave"},
    "gonion_sharpness":          {1: "Sharp 120-130°", 2: "Sharp", 3: "Clear",
                                  4: "Average", 5: "Soft", 6: "Rounded", 7: "Hidden"},
    "facial_depth":              {1: "Strong forward", 2: "Strong", 3: "Average",
                                  4: "Mild", 5: "Flat", 6: "Recessed", 7: "Very recessed"},
    "mandible_ramus_visibility": {1: "Tall, sharp", 2: "Tall", 3: "Clear",
                                  4: "Average", 5: "Short", 6: "Hidden", 7: "Absent"},
    "ogee_curve":                {1: "Defined S-curve", 2: "Strong", 3: "Average",
                                  4: "Mild", 5: "Flat", 6: "Inverted", 7: "Absent"},
    "cheekbone_visibility":      {1: "High & wide", 2: "Strong", 3: "Average",
                                  4: "Soft", 5: "Flat", 6: "Hidden", 7: "Absent"},
    "chin_angularity":           {1: "Squared sharp", 2: "Strong", 3: "Clear",
                                  4: "Average", 5: "Soft", 6: "Round", 7: "Pointed"},
    "lower_midface_fat":         {1: "Minimal", 2: "Low", 3: "Average",
                                  4: "Notable", 5: "High", 6: "Pronounced", 7: "Heavy"},
    # DIMO manual
    "buccal_fat_size":           {1: "Very low, hollow", 2: "Low", 3: "Average",
                                  4: "Full", 5: "Heavy"},
    "facial_hair_development":   {1: "Dense, full beard", 2: "Full", 3: "Average",
                                  4: "Patchy", 5: "Sparse"},
    "rough_skin_texture":        {1: "Thick, visible pores", 2: "Slightly textured",
                                  3: "Average", 4: "Smooth", 5: "Very smooth"},
    "lip_fullness_dimo":         {1: "Thin to average, tight", 2: "Slightly thin",
                                  3: "Average", 4: "Full", 5: "Very full"},
}


# --- Manual feature catalog --------------------------------------------------
# (name, label, module, description). MISC categories surface via the "category"
# annotation in the entry below; ANGU and DIMO manual features get "side"/
# "frontal"/"manual" but always source="manual" since they're user-rated.

_SUBJECTIVE_FEATURES: list[tuple[str, str, str, str, str]] = [
    # MISC SKIN
    ("skin_clearness",          "Skin Clearness",            "MISC", "skin",         "Acne, breakouts"),
    ("hyperpigmentation",       "Hyperpigmentation",         "MISC", "skin",         "Sun spots, melasma"),
    ("moles",                   "Moles",                     "MISC", "skin",         "Visible facial moles"),
    ("skin_texture",            "Skin Texture",              "MISC", "skin",         "Smoothness / pore visibility"),
    ("acne_scarring",           "Acne Scarring",             "MISC", "skin",         "Pitted or raised scars"),
    ("facial_folds_wrinkles",   "Facial Folds + Wrinkles",   "MISC", "skin",         "Dynamic + static lines"),
    # MISC EYE
    ("upper_eyelid",            "Upper Eyelid Exposure",     "MISC", "eyes",         "Hooded / UEE"),
    ("lower_eyelid_shape",      "Lower Eyelid Shape",        "MISC", "eyes",         "Straight vs rounded"),
    ("sclera_show",             "Sclera Show",               "MISC", "eyes",         "Visible white below iris"),
    ("eyelashes",               "Eyelashes",                 "MISC", "eyes",         "Thickness / darkness"),
    ("eyebrows",                "Eyebrows Quality",          "MISC", "eyes",         "Density / shape"),
    ("periorbital_darkening",   "Periorbital Darkening",     "MISC", "eyes",         "Hyperpigmentation around eyes"),
    ("under_eye_circles",       "Under-Eye Circles",         "MISC", "eyes",         "Shadows under eyes"),
    ("lee",                     "Lower Eyelid Exposure",     "MISC", "eyes",         "LEE / fat pad show"),
    ("eye_colour_eye",          "Eye Colour (overall)",      "MISC", "eyes",         "Striking vs neutral"),
    ("scleral_triangles",       "Scleral Triangles",         "MISC", "eyes",         "Triangle evenness"),
    ("medial_canthus",          "Medial Canthus Shape",      "MISC", "eyes",         "Downturned / long"),
    ("pfl",                     "Palpebral Fissure Length",  "MISC", "eyes",         "Eye length in mm"),
    ("sclera_colour_eye",       "Sclera Colour",             "MISC", "eyes",         "Whiteness"),
    ("unibrow",                 "Unibrow",                   "MISC", "eyes",         "Joined brows"),
    # MISC COLOURING
    ("skin_colour",             "Skin Tone",                 "MISC", "colouring",    "Tanned vs pale"),
    ("lip_colour",              "Lip Colour",                "MISC", "colouring",    "Reddish-pink ideal"),
    ("eyelash_visibility",      "Eyelash Visibility",        "MISC", "colouring",    "Contrast vs skin"),
    ("eye_colour_col",          "Eye Colour Intensity",      "MISC", "colouring",    "Light vs dark"),
    ("hair_colour",             "Hair Colour",               "MISC", "colouring",    "Dark ideal"),
    ("eyebrow_colour",          "Eyebrow Colour",            "MISC", "colouring",    "Dark ideal"),
    ("sclera_whiteness",        "Sclera Whiteness",          "MISC", "colouring",    "Bright white ideal"),
    # MISC LOWER THIRD
    ("gonions",                 "Gonion Flare",              "MISC", "lower",        "Visible jaw corners"),
    ("chin_shape_misc",         "Chin Shape",                "MISC", "lower",        "Square ideal"),
    ("chin_width",              "Chin Width",                "MISC", "lower",        "Wide ideal"),
    ("ramus_length_misc",       "Ramus Length",              "MISC", "lower",        "Tall ideal"),
    ("mandible_length",         "Mandible Length",           "MISC", "lower",        "Long & straight"),
    ("mandible_shape",          "Mandible Shape",            "MISC", "lower",        "Straight ideal"),
    # MISC LIPS
    ("lip_width",               "Lip Width",                 "MISC", "lips",         "Wide ideal"),
    ("philtrum_length",         "Philtrum Length",           "MISC", "lips",         "Short ideal"),
    ("philtrum_ridges",         "Philtrum Ridges",           "MISC", "lips",         "Defined ideal"),
    ("lip_fullness_lips",       "Lip Fullness",              "MISC", "lips",         "Full ideal"),
    ("lip_health",              "Lip Health",                "MISC", "lips",         "No cracking ideal"),
    ("commissures",             "Mouth Commissures",         "MISC", "lips",         "Slight upturn ideal"),
    ("cupids_bow",              "Cupid's Bow",               "MISC", "lips",         "Prominent ideal"),
    ("lip_seal",                "Lip Seal",                  "MISC", "lips",         "Straight ideal"),
    # MISC NOSE
    ("alar_width",              "Alar Width",                "MISC", "nose",         "Not wide ideal"),
    ("nose_bulbosity",          "Nose Bulbosity",            "MISC", "nose",         "Low ideal"),
    ("nasal_tip",               "Nasal Tip",                 "MISC", "nose",         "Defined ideal"),
    ("nostril_show",            "Nostril Show",              "MISC", "nose",         "Minimal ideal"),
    ("nostril_flare",           "Nostril Flare",             "MISC", "nose",         "None ideal"),
    ("dorsum",                  "Nasal Dorsum",              "MISC", "nose",         "Straight ideal"),
    ("radix_projection",        "Radix Projection",          "MISC", "nose",         "Projected ideal"),
    # MISC OTHER
    ("ears",                    "Ears",                      "MISC", "other",        "Pinned back ideal"),
    ("symmetry",                "Symmetry",                  "MISC", "other",        "Minimal asymmetry"),
    # ANGU (all manual)
    ("mandible_visibility_front", "Mandible Visibility (Front)", "ANGU", "angularity", "Edge clarity"),
    ("facial_3d_ness",            "Facial 3D-ness",              "ANGU", "angularity", "Midface projection"),
    ("gonion_sharpness",          "Gonion Sharpness",            "ANGU", "angularity", "120-130° + edge"),
    ("facial_depth",              "Facial Depth",                "ANGU", "angularity", "Forward-projected"),
    ("mandible_ramus_visibility", "Mandible & Ramus Visibility", "ANGU", "angularity", "Tall, sharp"),
    ("ogee_curve",                "Ogee Curve",                  "ANGU", "angularity", "Defined S-curve"),
    ("cheekbone_visibility",      "Cheekbone Visibility",        "ANGU", "angularity", "High wide shadow"),
    ("chin_angularity",           "Chin Angularity",             "ANGU", "angularity", "Squared sharp"),
    ("lower_midface_fat",         "Lower-Midface Fat",           "ANGU", "angularity", "Minimal buccal fat"),
    # DIMO manual
    ("buccal_fat_size",         "Buccal Fat Size",           "DIMO", "dimorphism",   "Very low, hollow ideal"),
    ("facial_hair_development", "Facial Hair Development",   "DIMO", "dimorphism",   "Dense beard ideal"),
    ("rough_skin_texture",      "Rough Skin Texture",        "DIMO", "dimorphism",   "Thick pores ideal"),
    ("lip_fullness_dimo",       "Lip Fullness (Dimorphism)", "DIMO", "dimorphism",   "Thin to avg, tight"),
]


def subjective_feature_catalog() -> list[dict]:
    out: list[dict] = []
    for name, label, module, category, description in _SUBJECTIVE_FEATURES:
        out.append({
            "name": name,
            "label": label,
            "module": module,
            "category": category,
            "description": description,
            "tiers": _tiers_for(name),
        })
    return out


def is_subjective(name: str) -> bool:
    return any(t[0] == name for t in _SUBJECTIVE_FEATURES)
