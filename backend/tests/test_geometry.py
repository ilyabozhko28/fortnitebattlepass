import math

import pytest

from harmony.cv import geometry as geo


def test_distance_basic():
    assert geo.distance((0.0, 0.0), (3.0, 4.0)) == pytest.approx(5.0)


def test_midpoint():
    assert geo.midpoint((0.0, 0.0), (4.0, 2.0)) == (2.0, 1.0)


def test_signed_angle_image_coords():
    # In image coords (y grows downward), a line from (0,1) to (1,0) is "up to the right".
    # Our helper negates dy so positive angle == up-to-the-right.
    deg = geo.signed_angle_from_horizontal((0.0, 1.0), (1.0, 0.0))
    assert deg == pytest.approx(45.0)


def test_angle_between():
    deg = geo.angle_between((1.0, 0.0), (0.0, 0.0), (0.0, 1.0))
    assert deg == pytest.approx(90.0)


def test_safe_div_zero():
    assert geo.safe_div(1.0, 0.0) is None
    assert geo.safe_div(2.0, 4.0) == 0.5


def test_distance_nan_safety():
    # We don't pass NaNs in production but make sure the function doesn't raise.
    d = geo.distance((float("inf"), 0.0), (0.0, 0.0))
    assert math.isinf(d)
