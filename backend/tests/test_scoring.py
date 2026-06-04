"""Unit tests for the universal tier-deviation classifier, points lookup,
and 4-module aggregation."""

import pytest

from harmony.schemas import IdealSpec, MetricRaw, MetricResult
from harmony.scoring import aggregate as agg_mod
from harmony.scoring import score as scoring_score
from harmony.scoring import tiers
from harmony.scoring.points import POINTS, MODULE_OF, points_for, features_in


# --- IdealSpec / deviation -------------------------------------------------

def test_dev_zero_when_inside_range():
    spec = IdealSpec(85.5, 92.0, "range")
    assert tiers.deviation_pct(88.0, spec) == 0.0


def test_dev_positive_outside_range_above():
    spec = IdealSpec(85.5, 92.0, "range")
    # 100 → dev from 92 / center 88.75 = 8/88.75 * 100 ≈ 9.01
    assert tiers.deviation_pct(100.0, spec) == pytest.approx(9.014, abs=1e-3)


def test_dev_center_kind():
    spec = IdealSpec(20.42, 20.42, "center")
    # 22 → (22-20.42)/20.42 * 100 ≈ 7.74
    assert tiers.deviation_pct(22.0, spec) == pytest.approx(7.7375, abs=1e-3)


def test_dev_lower_bound():
    spec = IdealSpec(90.0, 90.0, "lower_bound")
    assert tiers.deviation_pct(95.0, spec) == 0.0
    assert tiers.deviation_pct(85.0, spec) == pytest.approx(5.555, abs=1e-3)


def test_dev_upper_bound():
    spec = IdealSpec(50.0, 50.0, "upper_bound")
    assert tiers.deviation_pct(40.0, spec) == 0.0
    assert tiers.deviation_pct(60.0, spec) == pytest.approx(20.0, abs=1e-6)


# --- Universal tier bands ---------------------------------------------------

@pytest.mark.parametrize(
    ("dev_pct", "expected_tier"),
    [(0.0, 1), (3.0, 1), (4.0, 2), (8.0, 2), (9.0, 3),
     (15.0, 3), (16.0, 4), (25.0, 4), (26.0, 5), (40.0, 5),
     (41.0, 6), (60.0, 6), (61.0, 7), (200.0, 7)],
)
def test_universal_bands_centered_spec(dev_pct, expected_tier):
    spec = IdealSpec(100.0, 100.0, "center")
    raw = 100.0 + dev_pct  # so deviation_pct = dev_pct
    res = tiers.classify(raw, spec, max_tier=7)
    assert res.tier == expected_tier


def test_max_tier_caps_universal_band():
    spec = IdealSpec(100.0, 100.0, "center")
    # huge deviation that would be T7 normally
    res = tiers.classify(500.0, spec, max_tier=6)
    assert res.tier == 6


def test_none_raw_returns_none_tier():
    res = tiers.classify(None, IdealSpec(1.0, 1.0, "center"))
    assert res.tier is None and res.label is None


# --- Points lookup ----------------------------------------------------------

def test_points_for_known_tier():
    assert points_for("eye_separation_ratio", 1) == 12.20
    assert points_for("eye_separation_ratio", 6) == -65.88


def test_points_for_undefined_tier():
    # chin_to_philtrum has no T7 in spec → 0
    assert points_for("chin_to_philtrum", 7) == 0.0


def test_points_for_unknown_feature():
    assert points_for("does_not_exist", 1) == 0.0


# --- Catalog parity ---------------------------------------------------------

def test_modules_have_expected_counts():
    assert len(features_in("HARM")) == 26
    assert len(features_in("DIMO")) == 11
    assert len(features_in("ANGU")) == 9
    assert len(features_in("MISC")) == 50


def test_module_of_covers_all_points():
    assert set(MODULE_OF.keys()) == set(POINTS.keys())


# --- score_metrics + aggregate ---------------------------------------------

def _raw(name, value, *, ideal=None, manual_tier=None, source="frontal"):
    debug = {"module": MODULE_OF.get(name, "HARM"), "source": source}
    if ideal is not None:
        debug["ideal"] = ideal
    if manual_tier is not None:
        debug["manual_tier"] = manual_tier
    return MetricRaw(name=name, label=name, category="x", raw_value=value, debug=debug)


def test_score_metrics_assigns_tier_and_points():
    esr_ideal = IdealSpec(44.3, 47.7, "range")
    results = scoring_score.score_metrics([_raw("eye_separation_ratio", 46.0, ideal=esr_ideal)])
    assert len(results) == 1
    r = results[0]
    assert r.tier == 1
    assert r.points == 12.20
    assert r.module == "HARM"
    assert r.source == "frontal"


def test_score_metrics_manual_tier():
    results = scoring_score.score_metrics(
        [_raw("skin_clearness", None, manual_tier=2, source="manual")]
    )
    r = results[0]
    assert r.tier == 2
    assert r.points == 25  # MISC SKIN T2
    assert r.module == "MISC"


def test_aggregate_4_modules():
    esr_ideal = IdealSpec(44.3, 47.7, "range")
    fwhr_ideal = IdealSpec(1.9, 2.06, "range")
    raws = [
        _raw("eye_separation_ratio", 46.0, ideal=esr_ideal),
        _raw("fwhr", 2.0, ideal=fwhr_ideal),
        _raw("skin_clearness", None, manual_tier=1, source="manual"),
        _raw("symmetry", None, manual_tier=1, source="manual"),
    ]
    results, modules, final = scoring_score.full_score(raws)
    # HARM raw = 12.20 + 18.30 = 30.50
    assert modules["HARM"].raw == pytest.approx(30.50, abs=1e-6)
    # MISC raw = 50 + 100 = 150
    assert modules["MISC"].raw == pytest.approx(150.0, abs=1e-6)
    # ANGU has no contributors → raw 0
    assert modules["ANGU"].raw == 0.0
    # DIMO has no contributors → raw 0
    assert modules["DIMO"].raw == 0.0
    # Final score = weighted - deduction; verify it ran without nan
    assert isinstance(final.final, float)


def test_aggregate_normalization_matches_spec():
    # HARM% = ((raw + 409.92) / 799.66) * 100
    # For raw=0: pct ≈ 51.26
    mods, _ = agg_mod.aggregate([])
    assert mods["HARM"].pct == pytest.approx(51.26, abs=0.05)


def test_imbalance_deduction_applied():
    # Construct results so that one module pct = 100, another = 0
    # HARM raw needs to produce 100% pct: ((raw + 409.92) / 799.66) * 100 = 100 → raw = 389.74
    # MISC raw for 0%: (raw + 460) / 1491 * 100 = 0 → raw = -460
    high = MetricResult(name="x", label="x", category="x", module="HARM",
                        source="frontal", raw=None, tier=1, points=389.74,
                        tier_label=None)
    low = MetricResult(name="y", label="y", category="y", module="MISC",
                       source="manual", raw=None, tier=1, points=-460,
                       tier_label=None)
    _mods, final = agg_mod.aggregate([high, low])
    # H tens = 10, M tens = 0, A tens ≈ -1.45, D tens ≈ -3.6
    # max - min = 10 - min(...). deduction > 0
    assert final.deduction > 0
