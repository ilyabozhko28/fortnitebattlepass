"""Universal tier-deviation classifier.

Per the v2 spec, every metric uses the same deviation-from-ideal table:

    percent_deviation = |measured - ideal_center| / ideal_center * 100

    T1: 0-3%         Near-perfect
    T2: 3-8%         Excellent
    T3: 8-15%        Good
    T4: 15-25%       Average
    T5: 25-40%       Below average
    T6: 40-60%       Poor
    T7: > 60%        Very poor (or inverted/absent for one-sided metrics)

Each metric supplies an :class:`IdealSpec` with one of four ``kind`` values:

- ``range``        T1 if ``low <= raw <= high``, else deviation from the
                   nearest band edge as percent of the band center.
- ``center``       T1 if within ±3 % of ``low``; otherwise relative deviation
                   from ``low``.
- ``lower_bound``  T1 if ``raw >= low``; otherwise deviation = ``(low-raw)/low*100``.
- ``upper_bound``  T1 if ``raw <= low``; otherwise deviation = ``(raw-low)/low*100``.

The classifier is sex-agnostic — sex-aware ideal ranges are picked by the
measurement modules before calling :func:`classify`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..schemas import IdealSpec

_EPS = 1e-9

# (max_inclusive_pct, tier, label)
_BANDS: list[tuple[float, int, str]] = [
    (3.0,   1, "≤3% deviation (near-perfect)"),
    (8.0,   2, "3-8% deviation (excellent)"),
    (15.0,  3, "8-15% deviation (good)"),
    (25.0,  4, "15-25% deviation (average)"),
    (40.0,  5, "25-40% deviation (below average)"),
    (60.0,  6, "40-60% deviation (poor)"),
    (math.inf, 7, ">60% deviation (very poor)"),
]


@dataclass(slots=True)
class TierResult:
    tier: int | None
    label: str | None
    deviation_pct: float | None


def deviation_pct(raw: float, ideal: IdealSpec) -> float:
    """Return the absolute deviation percentage from the ideal center, per the
    rules above. 0.0 means 'inside the ideal range or at the bound'."""
    if ideal.kind == "range":
        if ideal.low - _EPS <= raw <= ideal.high + _EPS:
            return 0.0
        nearest = ideal.low if raw < ideal.low else ideal.high
        center = (ideal.low + ideal.high) / 2.0
        if center == 0:
            return float("inf")
        return abs(raw - nearest) / abs(center) * 100.0

    if ideal.kind == "center":
        if ideal.low == 0:
            return float("inf")
        return abs(raw - ideal.low) / abs(ideal.low) * 100.0

    if ideal.kind == "lower_bound":
        if raw + _EPS >= ideal.low:
            return 0.0
        if ideal.low == 0:
            return float("inf")
        return abs(ideal.low - raw) / abs(ideal.low) * 100.0

    if ideal.kind == "upper_bound":
        if raw - _EPS <= ideal.low:
            return 0.0
        if ideal.low == 0:
            return float("inf")
        return abs(raw - ideal.low) / abs(ideal.low) * 100.0

    raise ValueError(f"unsupported IdealSpec.kind: {ideal.kind!r}")


def classify(raw: float | None, ideal: IdealSpec | None, max_tier: int = 7) -> TierResult:
    """Map ``raw`` to a tier (1..max_tier). Returns ``TierResult(None, ...)``
    if ``raw`` is missing or ``ideal`` not supplied.

    ``max_tier`` caps the returned tier — features with only 5 or 6 defined
    tiers should pass their own cap so the universal T7/T8 don't overshoot.
    """
    if raw is None or (isinstance(raw, float) and math.isnan(raw)) or ideal is None:
        return TierResult(tier=None, label=None, deviation_pct=None)

    dev = deviation_pct(float(raw), ideal)
    if math.isinf(dev):
        return TierResult(tier=min(7, max_tier), label=_BANDS[-1][2], deviation_pct=dev)

    for cutoff, tier, label in _BANDS:
        if dev <= cutoff + _EPS:
            capped = min(tier, max_tier)
            return TierResult(tier=capped, label=label, deviation_pct=round(dev, 2))

    capped = min(7, max_tier)
    return TierResult(tier=capped, label=_BANDS[-1][2], deviation_pct=round(dev, 2))


# Back-compat helper used by the legacy aggregator. New code should use
# ``classify`` directly via metric specs.
def assign(metric, sex, ideal: IdealSpec | None = None, max_tier: int = 7):  # type: ignore[no-untyped-def]
    raw = getattr(metric, "raw_value", None)
    if isinstance(raw, float) and math.isnan(raw):
        raw = None
    result = classify(raw, ideal, max_tier=max_tier)
    return result.tier, result.label


__all__ = ["TierResult", "classify", "deviation_pct", "assign"]
