"""End-to-end ``run(...)`` entrypoint for the v2 4-module pipeline.

Inputs:
- ``frontal_bytes``: required JPEG/PNG bytes of the frontal photo
- ``sex``: "male" or "female" (drives sex-aware ideal ranges)
- ``side_bytes`` and ``side_annotations``: optional second photo and its
  manually-clicked named landmarks (dict[name, (x, y)])
- ``misc_ratings``: optional ``dict[feature_name, tier_int]`` for subjective
  features (MISC + manual ANGU + manual DIMO)

Everything is in-memory: bytes are decoded once, scored, then dropped.
"""

from __future__ import annotations

import base64
import io
import math
from typing import Any, Iterable, Mapping

import numpy as np

from .cv import alignment, profile_landmarks, segmentation
from .measurements import all_measurements
from .schemas import (
    AnalysisResult,
    FinalScore,
    ImageSize,
    MetricRaw,
    MetricResult,
    ModuleScore,
    Sex,
)
from .scoring import score as scoring_score


# ---------------------------------------------------------------------------
# Mask base64 helpers
# ---------------------------------------------------------------------------

def _encode_mask_b64(mask: np.ndarray | None) -> str | None:
    if mask is None:
        return None
    try:
        import cv2

        ok, buf = cv2.imencode(".png", mask)
        if not ok:
            return None
        return base64.b64encode(buf.tobytes()).decode("ascii")
    except Exception:
        return None


def _decode_mask_b64(mask_b64: str | None) -> np.ndarray | None:
    if not mask_b64:
        return None
    try:
        import cv2

        raw = base64.b64decode(mask_b64)
        arr = np.frombuffer(raw, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Image decode + frontal pipeline
# ---------------------------------------------------------------------------

class PipelineError(RuntimeError):
    pass


def _decode(image_bytes: bytes) -> np.ndarray:
    import cv2

    if not image_bytes:
        raise PipelineError("empty image payload")
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        try:
            from PIL import Image

            pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            arr_rgb = np.array(pil)
            image = arr_rgb[:, :, ::-1].copy()
        except Exception as exc:
            raise PipelineError(f"could not decode image: {exc}") from exc
    return image


# ---------------------------------------------------------------------------
# Measurement runner
# ---------------------------------------------------------------------------

def _safe_call(spec: dict, *args, **kwargs) -> MetricRaw:
    """Invoke ``spec['compute']``; on exception, return a placeholder MetricRaw."""
    try:
        result = spec["compute"](*args, **kwargs)
        if not isinstance(result, MetricRaw):
            raise TypeError(f"compute returned {type(result).__name__}, expected MetricRaw")
        return result
    except Exception as exc:
        return MetricRaw(
            name=spec["name"], label=spec["label"], category=spec["category"],
            raw_value=None,
            debug={"reason": f"exception: {exc}", "module": spec["module"], "source": spec["source"]},
        )


def _manual_raw(spec: dict, tier: int | None) -> MetricRaw:
    return MetricRaw(
        name=spec["name"], label=spec["label"], category=spec["category"],
        raw_value=float(tier) if tier is not None else None,
        debug={
            "module": spec["module"], "source": "manual",
            "manual_tier": tier,
        },
    )


def _run_measurements(
    frontal_pts: np.ndarray | None,
    frontal_image: np.ndarray | None,
    mask: np.ndarray | None,
    side_pts: Mapping[str, tuple[float, float]] | None,
    misc_ratings: Mapping[str, int] | None,
    sex: Sex,
) -> tuple[list[MetricRaw], list[str]]:
    raws: list[MetricRaw] = []
    warnings: list[str] = []
    misc_ratings = misc_ratings or {}
    missing_side = side_pts is None

    for spec in all_measurements():
        src = spec["source"]
        if src == "frontal":
            if frontal_pts is None:
                raws.append(MetricRaw(
                    name=spec["name"], label=spec["label"], category=spec["category"],
                    raw_value=None,
                    debug={"reason": "no_frontal", "module": spec["module"], "source": "frontal"}
                ))
                continue
            needs_mask = spec.get("needs_mask", False)
            args: list[Any] = [frontal_pts, None, mask if needs_mask else None]
            raws.append(_safe_call(spec, *args, sex=sex))
        elif src == "side":
            if missing_side:
                raws.append(MetricRaw(
                    name=spec["name"], label=spec["label"], category=spec["category"],
                    raw_value=None,
                    debug={"reason": "side_profile_missing", "module": spec["module"], "source": "side"}
                ))
                continue
            raws.append(_safe_call(spec, side_pts, sex=sex))
        elif src == "manual":
            raws.append(_manual_raw(spec, misc_ratings.get(spec["name"])))
        else:
            raws.append(MetricRaw(
                name=spec["name"], label=spec["label"], category=spec["category"],
                raw_value=None, debug={"reason": f"unknown_source: {src}", "module": spec["module"], "source": src}
            ))

    if missing_side and any(s["source"] == "side" for s in all_measurements()):
        warnings.append("No side profile uploaded — side-derived metrics skipped.")
    if not misc_ratings:
        warnings.append("No subjective ratings provided — MISC/ANGU/DIMO manual features default to 0.")
    return raws, warnings


def _landmarks_for_response(points: np.ndarray) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in points]


def _empty_modules() -> dict[str, ModuleScore]:
    from .scoring.aggregate import MODULE_NORMS

    out: dict[str, ModuleScore] = {}
    for name, (offset, span, weight) in MODULE_NORMS.items():
        if name == "HARM":
            pct = 0.0
        else:
            pct = ((0.0 + offset) / span) * 100.0
        out[name] = ModuleScore(
            module=name,  # type: ignore[arg-type]
            raw=0.0, max_raw=0.0, pct=round(pct, 2),
            weight=weight, weighted_tens=round((pct / 10.0) * weight, 3),
            measured_count=0, total_count=0,
        )
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run(
    frontal_bytes: bytes,
    sex: Sex,
    *,
    side_bytes: bytes | None = None,
    side_annotations: Mapping[str, tuple[float, float]] | None = None,
    misc_ratings: Mapping[str, int] | None = None,
) -> AnalysisResult:
    if sex not in ("male", "female"):
        raise PipelineError(f"unsupported sex: {sex!r}")

    image = _decode(frontal_bytes)
    try:
        aligned = alignment.normalize(image)
    except Exception as exc:
        raise PipelineError(f"could not align face: {exc}") from exc
    points = aligned.landmarks.points

    try:
        mask = segmentation.person_mask(aligned.image)
    except Exception:
        mask = None

    side_pts = profile_landmarks.validate_annotations(dict(side_annotations) if side_annotations else None)

    side_size: ImageSize | None = None
    if side_bytes:
        try:
            side_img = _decode(side_bytes)
            h, w = side_img.shape[:2]
            side_size = ImageSize(width=int(w), height=int(h))
        except Exception:
            pass

    raws, warnings = _run_measurements(
        points, aligned.image, mask, side_pts, misc_ratings, sex
    )

    metric_results, modules, final = scoring_score.full_score(raws, sex=sex)

    h, w = aligned.image.shape[:2]
    return AnalysisResult(
        sex=sex,
        metrics=metric_results,
        modules=modules,
        final=final,
        landmarks=_landmarks_for_response(points),
        image_size=ImageSize(width=int(w), height=int(h)),
        warnings=warnings,
        mask_b64=_encode_mask_b64(mask),
        side_annotations={k: list(v) for k, v in side_pts.items()} if side_pts else None,
        side_image_size=side_size,
    )


def score_from_landmarks(
    landmarks: list[tuple[float, float]] | np.ndarray,
    sex: Sex,
    image_size: tuple[int, int] | None = None,
    mask_b64: str | None = None,
    *,
    side_annotations: Mapping[str, tuple[float, float]] | None = None,
    misc_ratings: Mapping[str, int] | None = None,
    side_image_size: tuple[int, int] | None = None,
) -> AnalysisResult:
    """Recompute the full 4-module score from edited inputs (no image needed)."""
    if sex not in ("male", "female"):
        raise PipelineError(f"unsupported sex: {sex!r}")

    pts = np.asarray(landmarks, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise PipelineError(f"expected landmarks of shape (N, 2), got {pts.shape}")
    if pts.shape[0] < 468:
        raise PipelineError(f"expected at least 468 landmarks, got {pts.shape[0]}")

    mask = _decode_mask_b64(mask_b64)
    side_pts = profile_landmarks.validate_annotations(dict(side_annotations) if side_annotations else None)

    raws, warnings = _run_measurements(pts, None, mask, side_pts, misc_ratings, sex)
    if mask is None:
        warnings.append("Recomputed without segmentation mask — neck width skipped.")

    metric_results, modules, final = scoring_score.full_score(raws, sex=sex)

    if image_size is None:
        xs = pts[:, 0]; ys = pts[:, 1]
        w = int(xs.max() + 1); h = int(ys.max() + 1)
    else:
        w, h = image_size

    side_size = None
    if side_image_size:
        side_size = ImageSize(width=int(side_image_size[0]), height=int(side_image_size[1]))

    return AnalysisResult(
        sex=sex,
        metrics=metric_results,
        modules=modules,
        final=final,
        landmarks=_landmarks_for_response(pts),
        image_size=ImageSize(width=int(w), height=int(h)),
        warnings=warnings,
        mask_b64=mask_b64,
        side_annotations={k: list(v) for k, v in side_pts.items()} if side_pts else None,
        side_image_size=side_size,
    )


__all__ = ["run", "score_from_landmarks", "PipelineError"]
