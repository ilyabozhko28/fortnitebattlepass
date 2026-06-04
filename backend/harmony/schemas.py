"""Result types shared by pipeline, CLI, and FastAPI shim.

These are plain dataclasses with ``to_dict`` helpers so the shim can return
them as JSON without coupling to Pydantic models.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Sex = Literal["male", "female"]
SourceKind = Literal["frontal", "side", "manual"]
Module = Literal["HARM", "DIMO", "ANGU", "MISC"]


@dataclass(slots=True)
class IdealSpec:
    """Declares the ideal value/range and the tier-classification kind for a
    metric. Consumed by ``scoring.tiers.classify``."""

    low: float
    high: float
    kind: Literal["range", "center", "lower_bound", "upper_bound"] = "range"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MetricRaw:
    """Raw output of one measurement module."""

    name: str
    label: str
    category: str
    raw_value: float | None
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MetricResult:
    """A measurement after tier + points assignment."""

    name: str
    label: str
    category: str
    module: Module
    source: SourceKind
    raw: float | None
    tier: int | None
    points: float
    tier_label: str | None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ModuleScore:
    """Per-module raw points + normalized percentages and weighted contribution."""

    module: Module
    raw: float          # sum of points across the module's measurements
    max_raw: float      # theoretical max for the module (offset+span minus offset)
    pct: float          # 0-100 normalized
    weight: float       # contribution weight (0-1)
    weighted_tens: float  # (pct/10) * weight
    measured_count: int   # how many of the module's metrics actually produced points
    total_count: int      # total metric count in this module

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FinalScore:
    """The /10 score with imbalance deduction."""

    modules: dict[str, float]   # module -> tens (pct/10)
    weighted: float             # weighted sum of tens (already on /10 scale)
    deduction: float            # imbalance penalty
    final: float                # weighted - deduction

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ImageSize:
    width: int
    height: int

    def to_dict(self) -> dict[str, int]:
        return {"width": self.width, "height": self.height}


@dataclass(slots=True)
class AnalysisResult:
    """The full response shape. Always returns 4-module + final + per-metric
    breakdown. Modules with no contributing measurements report ``raw=0`` and
    the floor pct that the normalization yields for raw=0."""

    sex: Sex
    metrics: list[MetricResult]
    modules: dict[str, ModuleScore]
    final: FinalScore
    # Frontal-specific
    landmarks: list[tuple[float, float]]
    image_size: ImageSize
    warnings: list[str] = field(default_factory=list)
    mask_b64: str | None = None
    # Side-specific
    side_annotations: dict[str, list[float]] | None = None
    side_image_size: ImageSize | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sex": self.sex,
            "metrics": [m.to_dict() for m in self.metrics],
            "modules": {k: v.to_dict() for k, v in self.modules.items()},
            "final": self.final.to_dict(),
            "landmarks": [list(p) for p in self.landmarks],
            "image_size": self.image_size.to_dict(),
            "warnings": list(self.warnings),
            "mask_b64": self.mask_b64,
            "side_annotations": self.side_annotations,
            "side_image_size": self.side_image_size.to_dict() if self.side_image_size else None,
        }
