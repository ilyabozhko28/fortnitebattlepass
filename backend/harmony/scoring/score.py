"""Score a list of raw measurements into MetricResults and run the 4-module
aggregation.

Compared to the v1 single-module ``aggregate``, this module:

- Looks up tiers via the universal ``tiers.classify`` (per-feature ``IdealSpec``).
- Looks up points via ``points.points_for``.
- Routes each metric into its module via ``points.MODULE_OF``.
- Returns ``(per_metric_results, module_scores, final_score)``.

Measurement modules now annotate the ``IdealSpec`` directly on the
``MetricRaw.debug["ideal"]`` slot so this code doesn't need to know per-metric
specifics. ``debug["source"]`` ("frontal" | "side" | "manual") similarly
travels along.
"""

from __future__ import annotations

import math
from typing import Iterable

from ..schemas import (
    FinalScore,
    IdealSpec,
    MetricRaw,
    MetricResult,
    Module,
    ModuleScore,
    SourceKind,
)
from . import aggregate as agg_mod
from . import tiers as tier_mod
from .points import MODULE_OF, max_tier_for, points_for
from .custom_harm import custom_classify


def _note_from_debug(debug: dict) -> str | None:
    if debug.get("hair_contamination_suspected"):
        return "Hair likely touches the neck silhouette — value capped at jaw width."
    if debug.get("used_model") is False:
        return "Helper model not loaded — heuristic fallback used."
    if "reason" in debug:
        return f"Skipped: {debug['reason']}"
    return None


def _module_of(name: str, debug: dict) -> Module:
    # Allow measurement modules to override the canonical module.
    if "module" in debug:
        return debug["module"]
    return MODULE_OF.get(name, "HARM")  # type: ignore[return-value]


def _source_of(debug: dict) -> SourceKind:
    return debug.get("source", "frontal")  # type: ignore[return-value]


def score_metrics(raws: Iterable[MetricRaw], sex: str = "male") -> list[MetricResult]:
    """Tier-classify each raw measurement and look up points."""
    out: list[MetricResult] = []
    for m in raws:
        ideal: IdealSpec | None = m.debug.get("ideal")  # type: ignore[assignment]
        explicit_tier: int | None = m.debug.get("manual_tier")
        max_tier = max_tier_for(m.name)
        if explicit_tier is not None:
            tier_int: int | None = max(1, min(int(explicit_tier), max_tier))
            label = f"T{tier_int} (user-rated)"
        else:
            # First try custom classification for the new HARM rules
            tr = custom_classify(m.name, m.raw_value, sex)
            if tr is None:
                tr = tier_mod.classify(m.raw_value, ideal, max_tier=max_tier)
            tier_int = tr.tier
            label = tr.label
            if label and tr.deviation_pct is not None and tier_int is not None:
                label = f"{label} ({tr.deviation_pct:g}% from ideal)"
        pts = points_for(m.name, tier_int)
        out.append(
            MetricResult(
                name=m.name,
                label=m.label,
                category=m.category,
                module=_module_of(m.name, m.debug),
                source=_source_of(m.debug),
                raw=m.raw_value,
                tier=tier_int,
                points=pts,
                tier_label=label,
                note=_note_from_debug(m.debug),
            )
        )
    return out


def aggregate(
    raws: Iterable[MetricRaw],
    _sex: str | None = None,
) -> tuple[float, float, list[MetricResult]]:
    """Back-compat wrapper retained for the few callers that still expect the
    v1 ``(score, total_points, results)`` shape.

    New callers should use :func:`score_metrics` + :func:`agg_mod.aggregate`.
    """
    results = score_metrics(raws, sex=_sex or "male")
    _modules, final = agg_mod.aggregate(results)
    total_points = sum(r.points for r in results)
    score_val = final.final / 10.0
    if math.isnan(score_val):
        score_val = 0.0
    return score_val, total_points, results


def full_score(
    raws: Iterable[MetricRaw],
    sex: str = "male",
) -> tuple[list[MetricResult], dict[str, ModuleScore], FinalScore]:
    """The new v2 entrypoint."""
    results = score_metrics(raws, sex=sex)
    modules, final = agg_mod.aggregate(results)
    return results, modules, final


__all__ = ["score_metrics", "full_score", "aggregate"]
