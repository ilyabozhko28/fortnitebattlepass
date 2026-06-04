"""Per-feature point tables for all 96 spec features across 4 modules.

Each entry: ``feature_name -> {tier_int: points_float}``. Tiers without a
defined value in the spec (em-dash in the source table) are simply omitted.

The values are encoded verbatim from the v2 spec the user provided. Some
entries have ``None`` for a tier slot — those mean "tier exists but adds 0
points" and are kept as ``0.0`` here for simpler aggregation.
"""

from __future__ import annotations

# Universal denominator for the legacy single-module score. Retained for
# back-compat only; the new ``aggregate`` module uses per-module normalization.
MAX_POINTS: float = 275.0


# ----------------------------------------------------------------------------
# HARM — 26 features
# ----------------------------------------------------------------------------
_HARM: dict[str, dict[int, float]] = {
    "eye_separation_ratio":       {1: 12.20, 2: 10.98, 3: 6.59, 4: 3.66, 5: -10.98, 6: -65.88, 7: -97.5},
    "facial_thirds":              {1: 19.83, 2: 17.84, 3: 9.91, 4: 5.95, 5: -5.95, 6: -11.90},
    "lateral_canthal_tilt":       {1: 12.35, 2: 11.12, 3: 6.18, 4: 3.71, 5: -3.71, 6: -7.40},
    "fwhr":                       {1: 18.30, 2: 16.47, 3: 9.15, 4: 5.49, 5: -16.47, 6: -49.41, 7: -85.0},
    "jaw_frontal_angle":          {1: 9.15,  2: 8.24,  3: 4.58, 4: 2.75, 5: -4.58, 6: -9.15, 7: -15.0},
    "cheekbone_setness":          {1: 20.0,  2: 10.0,  3: 5.0,  4: 2.5,  5: 0.0,   6: -2.5,  7: -5.0},
    "face_length":                {1: 20.0,  2: 10.0,  3: 5.0,  4: 2.5,  5: 0.0,   6: -2.5,  7: -5.0},
    "jaw_width":                  {1: 20.59, 2: 18.53, 3: 10.29, 4: 6.18, 5: -18.53, 6: -46.32, 7: -65.0},
    "chin_to_philtrum":           {1: 12.96, 2: 11.67, 3: 6.48, 4: 3.89, 5: -1.95, 6: -3.89},
    "neck_width":                 {1: 19.06, 2: 17.16, 3: 9.53, 4: 5.72, 5: -17.16, 6: -34.31},
    "mouth_to_nose":              {1: 12.35, 2: 11.12, 3: 6.18, 4: 3.71, 5: -3.71, 6: -7.40},
    "midface_ratio":              {1: 11.90, 2: 10.71, 3: 5.95, 4: 3.57, 5: -3.57, 6: -7.14},
    "eye_to_brow_distance":       {1: 19.83, 2: 17.84, 3: 9.91, 4: 5.95, 5: -5.95, 6: -11.90},
    "eye_spacing":                {1: 12.20, 2: 10.98, 3: 6.59, 4: 3.66, 5: -10.98, 6: -65.88},
    "eye_aspect_ratio":           {1: 18.30, 2: 16.47, 3: 9.15, 4: 5.49, 5: -5.49, 6: -10.98},
    "lower_lip_to_upper_lip_ratio": {1: 5.0, 2: 2.5, 3: 1.25, 4: 0.0, 5: -1.25, 6: -2.5},
    "iaa_to_jfa_deviation":       {1: 7.5, 2: 3.75, 3: 1.88, 4: 0.0, 5: -1.88, 6: -3.75},
    "eyebrow_tilt":               {1: 10.0,  2: 5.0,  3: 2.5,  4: 0.0, 5: -2.5, 6: -5.0},
    "bitemporal_width":           {1: 7.5,   2: 3.75, 3: 1.88, 4: 0.0, 5: -1.88, 6: -3.75},
    "lower_third_proportion":     {1: 5.0,   2: 2.5,  3: 1.25, 4: 0.0, 5: -1.25, 6: -2.5},
}


# ----------------------------------------------------------------------------
# DIMORPHISM — 11 features
# ----------------------------------------------------------------------------
_DIMO: dict[str, dict[int, float]] = {
    "eye_depth":              {1: 22.32, 2: 16.74, 3: 11.16, 4: 0.0,  5: -33.48},
    "brow_ridge_shape":       {1: 13.44, 2: 10.08, 3: 6.72,  4: 3.36, 5: -3.36},
    "chin_shape":             {1: 12.72, 2: 9.54,  3: 6.36,  4: 3.36, 5: -12.72},
    "buccal_fat_size":        {1: 11.70, 2: 8.78,  3: 5.85,  4: 2.93, 5: -2.93},
    "ramus_length_front":     {1: 11.53, 2: 8.65,  3: 5.77,  4: 2.88, 5: -2.88},
    "gonion_outward_growth":  {1: 11.04, 2: 8.28,  3: 5.52,  4: 2.76, 5: -2.76},
    "narrowing_upper_third":  {1: 9.00,  2: 6.75,  3: 4.50,  4: 2.25, 5: -2.25},
    "facial_hair_development":{1: 7.80,  2: 5.85,  3: 3.90,  4: 1.95, 5: -1.95},
    "rough_skin_texture":     {1: 7.20,  2: 5.40,  3: 3.60,  4: 1.80, 5: -1.80},
    "cheekbone_size":         {1: 6.91,  2: 5.18,  3: 3.46,  4: 1.73, 5: -1.73},
    "lip_fullness_dimo":      {1: 6.34,  2: 4.75,  3: 3.17,  4: 1.58, 5: -1.58},
}


# ----------------------------------------------------------------------------
# ANGULARITY — 9 features (mostly subjective)
# ----------------------------------------------------------------------------
_ANGU: dict[str, dict[int, float]] = {
    "mandible_visibility_front": {1: 24.75, 2: 21.04, 3: 17.33, 4: 13.61, 5: 9.90, 6: 6.19, 7: 3.09},
    "facial_3d_ness":            {1: 18.75, 2: 15.94, 3: 13.13, 4: 10.33, 5: 7.52, 6: 4.71, 7: 2.36},
    "gonion_sharpness":          {1: 18.75, 2: 15.94, 3: 13.13, 4: 10.33, 5: 7.52, 6: 4.71, 7: 2.36},
    "facial_depth":              {1: 17.25, 2: 14.66, 3: 12.08, 4: 9.49,  5: 6.91, 6: 4.33, 7: 2.17},
    "mandible_ramus_visibility": {1: 16.74, 2: 14.23, 3: 11.71, 4: 9.19,  5: 6.68, 6: 4.17, 7: 2.09},
    "ogee_curve":                {1: 15.75, 2: 13.39, 3: 11.03, 4: 8.67,  5: 6.30, 6: 3.94, 7: 1.97},
    "cheekbone_visibility":      {1: 15.11, 2: 12.85, 3: 10.58, 4: 8.32,  5: 6.05, 6: 3.79, 7: 1.89},
    "chin_angularity":           {1: 12.30, 2: 10.46, 3: 8.61,  4: 6.77,  5: 4.92, 6: 3.08, 7: 1.54},
    "lower_midface_fat":         {1: 10.43, 2: 8.86,  3: 7.30,  4: 5.73,  5: 4.17, 6: 3.13, 7: 1.56},
}


# ----------------------------------------------------------------------------
# MISC — 50 features across 7 categories. All subjective (user-rated).
# ----------------------------------------------------------------------------
_MISC_SKIN: dict[str, dict[int, float]] = {
    "skin_clearness":          {1: 50, 2: 25, 3: 10, 4: 5, 5: 0, 6: -10, 7: -20, 8: -30},
    "hyperpigmentation":       {1: 30, 2: 10, 3: 5,  4: 2, 5: 0, 6: -5,  7: -10, 8: -30},
    "moles":                   {1: 10, 2: 7,  3: 5,  4: 3, 5: 1, 6: 0,   7: -5,  8: -10},
    "skin_texture":            {1: 15, 2: 10, 3: 5,  4: 3, 5: 1, 6: 0,   7: -2,  8: -5},
    "acne_scarring":           {1: 15, 2: 10, 3: 5,  4: 3, 5: 1, 6: 0,   7: -2,  8: -5},
    "facial_folds_wrinkles":   {1: 40, 2: 20, 3: 10, 4: 5, 5: 2, 6: 0,   7: -5,  8: -15},
}

_MISC_EYE: dict[str, dict[int, float]] = {
    "upper_eyelid":           {1: 35, 2: 20, 3: 10, 4: 5, 5: 3,  6: 0,   7: -5,  8: -15},
    "lower_eyelid_shape":     {1: 20, 2: 10, 3: 5,  4: 3, 5: 1,  6: 0,   7: -3,  8: -8},
    "sclera_show":            {1: 15, 2: 5,  3: 3,  4: 1, 5: 0,  6: -5,  7: -10, 8: -15},
    "eyelashes":              {1: 15, 2: 8,  3: 4,  4: 2, 5: 0,  6: -2,  7: -4},
    "eyebrows":               {1: 30, 2: 18, 3: 9,  4: 5, 5: 2,  6: 0,   7: -5,  8: -15},
    "periorbital_darkening":  {1: 25, 2: 10, 3: 5,  4: 0, 5: -5, 6: -10, 7: -30, 8: -50},
    "under_eye_circles":      {1: 15, 2: 8,  3: 4,  4: 2, 5: 0,  6: -3,  7: -5,  8: -15},
    "lee":                    {1: 15, 2: 10, 3: 5,  4: 2, 5: 0,  6: -5,  7: -8},
    "eye_colour_eye":         {1: 10, 2: 7,  3: 5},
    "scleral_triangles":      {1: 8,  2: 4,  3: 2,  4: 1, 5: 0,  6: -5,  7: -10, 8: -15},
    "medial_canthus":         {1: 10, 2: 5,  3: 2,  4: 0, 5: -1},
    "pfl":                    {1: 20, 2: 10, 3: 5,  4: 3, 5: 0,  6: -5,  7: -10, 8: -15},
    "sclera_colour_eye":      {1: 8,  2: 4,  3: 2,  4: 0},
    "unibrow":                {1: 5,  2: 3,  3: 1,  4: -2,5: -5, 6: -10, 7: -15, 8: -30},
}

_MISC_COLOURING: dict[str, dict[int, float]] = {
    "skin_colour":          {1: 30, 2: 10, 3: 5, 4: 3, 5: 0},
    "lip_colour":           {1: 15, 2: 10, 3: 5, 4: 3, 5: 0, 6: -3},
    "eyelash_visibility":   {1: 15, 2: 8,  3: 4, 4: 2, 5: 0},
    "eye_colour_col":       {1: 20, 2: 10, 3: 5},
    "hair_colour":          {1: 25, 2: 10, 3: 5, 4: 0},
    "eyebrow_colour":       {1: 20, 2: 10, 3: 5, 4: 0},
    "sclera_whiteness":     {1: 10, 2: 5,  3: 0},
}

_MISC_LOWER_THIRD: dict[str, dict[int, float]] = {
    "gonions":          {1: 40, 2: 20, 3: 10, 4: 5, 5: 3, 6: 0, 7: -5},
    "chin_shape_misc":  {1: 30, 2: 15, 3: 8,  4: 4, 5: 2, 6: 0, 7: -5},
    "chin_width":       {1: 25, 2: 13, 3: 7,  4: 3, 5: 0, 6: -5},
    "ramus_length_misc":{1: 35, 2: 20, 3: 10, 4: 5, 5: 3, 6: 0, 7: -5},
    "mandible_length":  {1: 30, 2: 15, 3: 8,  4: 4, 5: 2, 6: 0, 7: -5},
    "mandible_shape":   {1: 10, 2: 5,  3: 3,  4: 1, 5: 0, 6: -3},
}

_MISC_LIPS: dict[str, dict[int, float]] = {
    "lip_width":         {1: 25, 2: 12, 3: 6, 4: 3, 5: 1, 6: 0, 7: -5},
    "philtrum_length":   {1: 20, 2: 10, 3: 5, 4: 3, 5: 1, 6: 0, 7: -5},
    "philtrum_ridges":   {1: 10, 2: 5,  3: 2, 4: 0, 5: -3},
    "lip_fullness_lips": {1: 15, 2: 8,  3: 4, 4: 2, 5: 1, 6: 0, 7: -5},
    "lip_health":        {1: 15, 2: 8,  3: 4, 4: 2, 5: 1, 6: 0, 7: -5},
    "commissures":       {1: 10, 2: 5,  3: 2, 4: 0, 5: -3},
    "cupids_bow":        {1: 10, 2: 5,  3: 2, 4: 0, 5: -3},
    "lip_seal":          {1: 5,  2: 3,  3: 1, 4: 0, 5: -3},
}

_MISC_NOSE: dict[str, dict[int, float]] = {
    "alar_width":       {1: 15, 2: 8,  3: 4, 4: 2, 5: 1, 6: 0, 7: -5},
    "nose_bulbosity":   {1: 20, 2: 10, 3: 5, 4: 3, 5: 1, 6: 0, 7: -5},
    "nasal_tip":        {1: 25, 2: 12, 3: 6, 4: 3, 5: 1, 6: 0, 7: -5},
    "nostril_show":     {1: 20, 2: 10, 3: 5, 4: 3, 5: 1, 6: 0, 7: -5},
    "nostril_flare":    {1: 10, 2: 5,  3: 2, 4: 0, 5: -3},
    "dorsum":           {1: 5,  2: 3,  3: 1, 4: 0, 5: -3},
    "radix_projection": {1: 15, 2: 8,  3: 4, 4: 2, 5: 1, 6: 0, 7: -5},
}

_MISC_OTHER: dict[str, dict[int, float]] = {
    "ears":     {1: 15,  2: 8,  3: 4,  4: 0,  5: -5, 6: -10, 7: -20, 8: -40},
    "symmetry": {1: 100, 2: 70, 3: 50, 4: 30, 5: 10, 6: 0,   7: -10, 8: -50},
}

_MISC: dict[str, dict[int, float]] = {
    **_MISC_SKIN,
    **_MISC_EYE,
    **_MISC_COLOURING,
    **_MISC_LOWER_THIRD,
    **_MISC_LIPS,
    **_MISC_NOSE,
    **_MISC_OTHER,
}


# ----------------------------------------------------------------------------
# Public lookup
# ----------------------------------------------------------------------------
POINTS: dict[str, dict[int, float]] = {**_HARM, **_DIMO, **_ANGU, **_MISC}


# Module assignment lookup (canonical owner of each feature name).
MODULE_OF: dict[str, str] = (
    {name: "HARM" for name in _HARM}
    | {name: "DIMO" for name in _DIMO}
    | {name: "ANGU" for name in _ANGU}
    | {name: "MISC" for name in _MISC}
)


def points_for(feature: str, tier: int | None) -> float:
    if tier is None:
        return 0.0
    table = POINTS.get(feature)
    if not table:
        return 0.0
    val = table.get(tier)
    return float(val) if val is not None else 0.0


def max_tier_for(feature: str) -> int:
    table = POINTS.get(feature)
    if not table:
        return 7
    return max(table.keys())


def all_features() -> list[str]:
    return list(POINTS.keys())


def features_in(module: str) -> list[str]:
    return [name for name, m in MODULE_OF.items() if m == module]


__all__ = [
    "POINTS",
    "MODULE_OF",
    "MAX_POINTS",
    "points_for",
    "max_tier_for",
    "all_features",
    "features_in",
]
