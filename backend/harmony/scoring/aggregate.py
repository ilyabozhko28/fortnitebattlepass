"""4-module aggregation + final weighted-with-deduction score.

Per v2 spec:

    HARM% = ((HARM_raw + 409.92) / 799.66) * 100
    MISC% = ((MISC_raw + 460)    / 1491)   * 100
    ANGU% = ((ANGU_raw - 19.03)  / 130.80) * 100
    DIMO% = ((DIMO_raw + 67.44)  / 187.44) * 100

    H, M, A, D    = each_pct / 10                 # to /10 scale
    Weighted      = H*0.32 + M*0.26 + A*0.22 + D*0.20
    TS            = max(H,M,A,D) - min(H,M,A,D)
    Deduction     = TS * 0.1
    FINAL         = Weighted - Deduction

The ANGU offset is *subtracted*: ((raw - 19.03) / 130.80) * 100. The other
three modules' offsets are added. This is encoded as a signed offset so
``(raw + offset) / span`` works uniformly.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from ..schemas import FinalScore, MetricResult, Module, ModuleScore

# (offset_added_to_raw, span, weight)
# For ANGU the spec subtracts 19.03 → encode as offset = -19.03.
MODULE_NORMS: dict[str, tuple[float, float, float]] = {
    "HARM": (+409.92, 799.66, 0.32),
    "MISC": (+460.00, 1491.0, 0.26),
    "ANGU": (-19.03,  130.80, 0.22),
    "DIMO": (+67.44,  187.44, 0.20),
}


def module_raws(metrics: Iterable[MetricResult]) -> dict[str, float]:
    """Sum the awarded points per module."""
    totals: dict[str, float] = {m: 0.0 for m in MODULE_NORMS}
    for m in metrics:
        if m.module in totals:
            totals[m.module] += float(m.points)
    return totals


def module_counts(metrics: Iterable[MetricResult]) -> dict[str, tuple[int, int]]:
    """Return ``module -> (measured_count, total_count)``.

    ``measured_count`` is metrics whose tier is not None.
    """
    out: dict[str, list[int]] = {m: [0, 0] for m in MODULE_NORMS}
    for m in metrics:
        if m.module not in out:
            continue
        out[m.module][1] += 1
        if m.tier is not None:
            out[m.module][0] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


def aggregate(
    metrics: list[MetricResult],
) -> tuple[dict[str, ModuleScore], FinalScore]:
    raws = module_raws(metrics)
    counts = module_counts(metrics)

    modules: dict[str, ModuleScore] = {}
    tens: dict[str, float] = {}
    for name, (offset, span, weight) in MODULE_NORMS.items():
        raw = raws[name]
        if name == "HARM":
            pct = (raw / 275.0) * 100.0
        else:
            pct = ((raw + offset) / span) * 100.0
        ten = pct / 10.0
        weighted_tens = ten * weight
        measured, total = counts[name]
        modules[name] = ModuleScore(
            module=name,  # type: ignore[arg-type]
            raw=round(raw, 3),
            max_raw=275.0 if name == "HARM" else (round(span - offset if offset < 0 else span + (-offset), 3) if False else 0.0),
            pct=round(pct, 2),
            weight=weight,
            weighted_tens=round(weighted_tens, 3),
            measured_count=measured,
            total_count=total,
        )
        tens[name] = ten

    if tens:
        ts = max(tens.values()) - min(tens.values())
    else:
        ts = 0.0
    weighted_total = sum(modules[m].weighted_tens for m in MODULE_NORMS)
    deduction = ts * 0.1
    final_val = weighted_total - deduction

    final = FinalScore(
        modules={k: round(v, 3) for k, v in tens.items()},
        weighted=round(weighted_total, 3),
        deduction=round(deduction, 3),
        final=round(final_val, 3),
    )
    return modules, final


__all__ = ["aggregate", "module_raws", "module_counts", "MODULE_NORMS"]
