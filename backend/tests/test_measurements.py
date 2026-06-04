"""Tests for v2 measurement modules.

We build a synthetic (468, 2) landmarks array and a 16-name side-annotations
dict, then call each measurement's compute and check the raw value.
"""

import numpy as np
import pytest

from harmony.cv import landmarks as L
from harmony.measurements.harm import eyes, face, jaw, side as side_mod


# ---------------------------------------------------------------------------
# Frontal landmark fixture (symmetric idealized face)
# ---------------------------------------------------------------------------

@pytest.fixture
def points() -> np.ndarray:
    p = np.zeros((468, 2), dtype=np.float64)
    p[L.FOREHEAD_TOP] = (200.0, 60.0)
    p[L.CHIN] = (200.0, 340.0)
    p[L.ZYGION_LEFT] = (100.0, 200.0)
    p[L.ZYGION_RIGHT] = (300.0, 200.0)
    p[L.TEMPLE_LEFT] = (110.0, 130.0)
    p[L.TEMPLE_RIGHT] = (290.0, 130.0)
    p[L.GONION_LEFT] = (120.0, 260.0)
    p[L.GONION_RIGHT] = (280.0, 260.0)
    p[L.BROW_MID] = (200.0, 150.0)
    # Eyes
    p[L.LEFT_EYE_OUTER] = (130.0, 175.0)
    p[L.LEFT_EYE_INNER] = (180.0, 175.0)
    p[L.LEFT_EYE_TOP] = (155.0, 170.0)
    p[L.LEFT_EYE_BOTTOM] = (155.0, 185.0)
    p[L.RIGHT_EYE_INNER] = (220.0, 175.0)
    p[L.RIGHT_EYE_OUTER] = (270.0, 175.0)
    p[L.RIGHT_EYE_TOP] = (245.0, 170.0)
    p[L.RIGHT_EYE_BOTTOM] = (245.0, 185.0)
    # Brows (using true tip indices)
    p[L.LEFT_BROW_INNER] = (180.0, 160.0)
    p[L.LEFT_BROW_OUTER] = (130.0, 160.0)
    p[L.RIGHT_BROW_INNER] = (220.0, 160.0)
    p[L.RIGHT_BROW_OUTER] = (270.0, 160.0)
    # Nose
    p[L.NOSE_TIP] = (200.0, 230.0)
    p[L.NOSE_BASE] = (200.0, 245.0)
    p[L.ALA_LEFT] = (185.0, 245.0)
    p[L.ALA_RIGHT] = (215.0, 245.0)
    p[L.CHEEKBONE_APEX_LEFT] = (140.0, 220.0)
    p[L.CHEEKBONE_APEX_RIGHT] = (260.0, 220.0)
    # Mouth
    p[L.MOUTH_LEFT] = (170.0, 290.0)
    p[L.MOUTH_RIGHT] = (230.0, 290.0)
    p[L.UPPER_LIP_TOP] = (200.0, 280.0)
    p[L.UPPER_LIP_BOTTOM] = (200.0, 290.0)
    p[L.LOWER_LIP_TOP] = (200.0, 295.0)
    p[L.LOWER_LIP_BOTTOM] = (200.0, 310.0)
    return p


# ---------------------------------------------------------------------------
# Eyes
# ---------------------------------------------------------------------------

def test_eye_separation_ipd_over_bizyg(points):
    m = eyes.compute_eye_separation(points, sex="male")
    # left_pupil_x = (130+180)/2 = 155, right_pupil_x = (220+270)/2 = 245
    # IPD = 90, bizyg = 200 → 45%
    assert m.raw_value == pytest.approx(45.0)
    assert m.debug["module"] == "HARM"
    assert m.debug["source"] == "frontal"


def test_eye_aspect_ratio(points):
    m = eyes.compute_eye_aspect_ratio(points, sex="male")
    # eye width 50, height 15 → 50/15 ≈ 3.33
    assert m.raw_value == pytest.approx(50.0 / 15.0)


def test_lateral_canthal_tilt_zero_for_symmetric(points):
    m = eyes.compute_lateral_canthal_tilt(points, sex="male")
    assert m.raw_value == pytest.approx(0.0, abs=1e-6)


def test_eye_to_brow_distance(points):
    m = eyes.compute_eye_to_brow_distance(points, sex="male")
    # brow_y 160, eye top 170, eye width 50 → gap/width = 10/50 = 0.2
    assert m.raw_value == pytest.approx(0.2)


def test_eyebrow_tilt_zero(points):
    m = eyes.compute_eyebrow_tilt(points, sex="male")
    assert m.raw_value == pytest.approx(0.0, abs=1e-6)


def test_medial_canthal_angle_nonzero(points):
    m = eyes.compute_medial_canthal_angle(points, sex="male")
    # Should be a positive angle (brow_mid at (200,150) above canthi at (180,175)/(220,175))
    assert m.raw_value > 0


# ---------------------------------------------------------------------------
# Face frame
# ---------------------------------------------------------------------------

def test_fwhr(points):
    m = face.compute_fwhr(points, sex="male")
    # width 200, brow→upper_lip 130 → 200/130
    assert m.raw_value == pytest.approx(200.0 / 130.0)


def test_face_length(points):
    m = face.compute_face_length(points, sex="male")
    assert m.raw_value == pytest.approx(280.0 / 200.0)


def test_bizygomatic_mm_uses_ipd_calibration(points):
    m = face.compute_bizygomatic_mm(points, sex="male")
    # IPD = 90 px = 63 mm → px_per_mm = 90/63 = 1.4286
    # bizyg = 200 px → 200 / 1.4286 ≈ 140 mm
    assert m.raw_value == pytest.approx(140.0, abs=0.1)


def test_bitemporal_width(points):
    m = face.compute_bitemporal_width(points, sex="male")
    assert m.raw_value == pytest.approx(180.0 / 200.0 * 100.0)


def test_midface_ratio(points):
    m = face.compute_midface_ratio(points, sex="male")
    # IPD 90 / (UPPER_LIP_TOP 280 - BROW_MID 150) = 90/130
    assert m.raw_value == pytest.approx(90.0 / 130.0)


def test_facial_thirds_deviation_in_pp(points):
    m = face.compute_facial_thirds(points, sex="male")
    # forehead 60, brow 150, nose_base 245, chin 340. Total 280.
    # thirds: 90/280, 95/280, 95/280 → max dev from 33.33% is ~6.3%
    assert m.raw_value > 0
    assert m.raw_value < 10  # plausible


def test_lower_third_proportion(points):
    m = face.compute_lower_third_proportion(points, sex="male")
    # nose 245, chin 340, stomion (290+295)/2 = 292.5
    # pct = (292.5 - 245) / (340 - 245) * 100 = 47.5/95 * 100 = 50
    # dev from 33.33 ≈ 16.67
    assert m.raw_value == pytest.approx(50.0 - 100.0/3.0, abs=0.5)


def test_cheekbone_setness_uses_lip_pupil(points):
    m = face.compute_cheekbone_setness(points, sex="male")
    # lip_y 280, pupil_y 175, apex_y 220
    # (280-220)/(280-175)*100 = 60/105*100 ≈ 57.14
    assert m.raw_value == pytest.approx(60.0 / 105.0 * 100.0, abs=0.01)


# ---------------------------------------------------------------------------
# Jaw
# ---------------------------------------------------------------------------

def test_jaw_width(points):
    m = jaw.compute_jaw_width(points, sex="male")
    # gonia 280-120 = 160, bizyg 200 → 80%
    assert m.raw_value == pytest.approx(80.0)


def test_jaw_frontal_angle_is_a_valid_angle(points):
    m = jaw.compute_jaw_frontal_angle(points, sex="male")
    assert 30.0 < m.raw_value < 180.0


def test_chin_to_philtrum(points):
    m = jaw.compute_chin_to_philtrum(points, sex="male")
    # chin_h = |340-310| = 30, phil_h = |280-245| = 35 → 30/35 ≈ 0.857
    assert m.raw_value == pytest.approx(30.0 / 35.0)


def test_mouth_to_nose(points):
    m = jaw.compute_mouth_to_nose(points, sex="male")
    # mouth 60, nose 30 → 2.0
    assert m.raw_value == pytest.approx(2.0)


def test_nose_to_bizygomatic(points):
    m = jaw.compute_nose_to_bizygomatic(points, sex="male")
    # nose 30, bizyg 200 → 0.15
    assert m.raw_value == pytest.approx(0.15)


def test_neck_width_no_mask_returns_none(points):
    m = jaw.compute_neck_width(points, None, None, sex="male")
    assert m.raw_value is None


# ---------------------------------------------------------------------------
# Side profile measurements
# ---------------------------------------------------------------------------

def _side():
    """A plausible right-facing side profile (x increases toward the back)."""
    return {
        "trichion":         (40, 0),
        "glabella":         (40, 80),
        "brow_ridge_tip":   (30, 85),
        "nasion":           (50, 95),
        "nose_tip":         (10, 130),
        "subnasale":        (45, 160),
        "labrale_superius": (50, 175),
        "stomion":          (55, 185),
        "labrale_inferius": (55, 195),
        "pogonion":         (50, 250),
        "gnathion":         (60, 260),
        "gonion":           (160, 220),
        "tragion":          (200, 130),
        "eye_outer_corner": (80, 110),
        "upper_eyelid_mid": (60, 108),
        "brow_lower_mid":   (50, 95),
    }


def test_nasofrontal_angle_computed():
    m = side_mod.compute_nasofrontal_angle(_side(), sex="male")
    # glabella -> nasion -> nose_tip, angle at nasion. Should be a valid angle.
    assert 90.0 < m.raw_value < 180.0


def test_brow_ridge_inclination_computed():
    m = side_mod.compute_brow_ridge_inclination(_side(), sex="male")
    assert m.raw_value is not None and m.raw_value >= 0


def test_gonial_angle_computed():
    m = side_mod.compute_gonial_angle(_side(), sex="male")
    assert 60.0 < m.raw_value < 180.0


def test_ramus_length_computed():
    m = side_mod.compute_ramus_length(_side(), sex="male")
    assert m.raw_value is not None and m.raw_value > 0


def test_thirds_of_jaw_computed():
    m = side_mod.compute_thirds_of_jaw(_side(), sex="male")
    assert m.raw_value is not None and m.raw_value >= 0


def test_side_metrics_skip_when_missing_points():
    m = side_mod.compute_nasofrontal_angle({}, sex="male")
    assert m.raw_value is None
    assert "reason" in m.debug
