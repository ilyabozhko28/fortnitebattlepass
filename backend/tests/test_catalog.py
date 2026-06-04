"""Catalog integrity tests.

Verify that the subjective feature catalog, points table, and measurement
specs all stay in sync.
"""

import pytest

from harmony.cv.profile_landmarks import NAMES as SIDE_NAMES
from harmony.measurements import all_measurements
from harmony.measurements.subjective import (
    _SUBJECTIVE_FEATURES,
    subjective_feature_catalog,
)
from harmony.scoring.points import MODULE_OF, POINTS, features_in


def test_total_feature_count():
    assert len(POINTS) == 96


def test_module_counts_in_points():
    assert len(features_in("HARM")) == 26
    assert len(features_in("DIMO")) == 11
    assert len(features_in("ANGU")) == 9
    assert len(features_in("MISC")) == 50


def test_specs_match_points_table():
    specs = all_measurements()
    spec_names = {s["name"] for s in specs}
    assert spec_names == set(POINTS.keys())


def test_subjective_catalog_size():
    # MISC 50 + ANGU 9 + DIMO manual 4 = 63 subjective features
    assert len(_SUBJECTIVE_FEATURES) == 63


def test_subjective_catalog_modules_correct():
    by_module = {}
    for name, _label, mod, _cat, _desc in _SUBJECTIVE_FEATURES:
        by_module[mod] = by_module.get(mod, 0) + 1
    assert by_module == {"MISC": 50, "ANGU": 9, "DIMO": 4}


def test_subjective_features_have_tiers():
    catalog = subjective_feature_catalog()
    for entry in catalog:
        assert entry["tiers"], f"{entry['name']} has no tiers"
        # tiers are (tier_int, points_float, label_str)
        for t in entry["tiers"]:
            assert len(t) == 3
            assert isinstance(t[0], int)


def test_side_landmark_count():
    assert len(SIDE_NAMES) == 16


def test_no_orphan_points_keys():
    """Every key in POINTS table must have a corresponding spec."""
    specs = all_measurements()
    spec_names = {s["name"] for s in specs}
    orphans = set(POINTS.keys()) - spec_names
    assert not orphans, f"points table has orphan keys: {sorted(orphans)}"


def test_modules_of_assignment_consistency():
    specs = all_measurements()
    for s in specs:
        assert MODULE_OF.get(s["name"]) == s["module"], (
            f"{s['name']} module mismatch: spec={s['module']} table={MODULE_OF.get(s['name'])}"
        )


def test_manual_specs_have_no_compute():
    for s in all_measurements():
        if s["source"] == "manual":
            assert s["compute"] is None
        else:
            assert callable(s["compute"])
