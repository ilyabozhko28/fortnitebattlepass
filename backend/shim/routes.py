"""Two endpoints (both stateless, no auth, no storage):

- POST /api/analyze — frontal image + optional side + optional ratings → full v2 JSON
- POST /api/score   — JSON of edited frontal landmarks + optional side annotations
                       + optional ratings → recomputed JSON
- GET  /api/subjective-features — catalog of MISC/ANGU/DIMO manual features for the UI

Multipart form for /api/analyze because it carries up to two image files plus
two JSON blobs in form fields.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from harmony.cv import profile_landmarks
from harmony.measurements.subjective import subjective_feature_catalog
from harmony.pipeline import PipelineError, run, score_from_landmarks

router = APIRouter(prefix="/api")

MAX_BYTES = 12 * 1024 * 1024  # 12 MiB per image


def _parse_json(name: str, value: str | None) -> dict | None:
    if not value:
        return None
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"{name}: invalid JSON ({exc})") from exc
    if not isinstance(loaded, dict):
        raise HTTPException(status_code=400, detail=f"{name}: must be a JSON object")
    return loaded


@router.get("/subjective-features")
def subjective_features() -> dict:
    """Catalog used by the React form to render tier pickers."""
    return {"features": subjective_feature_catalog()}


@router.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    sex: Literal["male", "female"] = Form(...),
    side_image: UploadFile | None = File(default=None),
    side_annotations: str | None = Form(default=None),
    misc_ratings: str | None = Form(default=None),
) -> dict:
    data = await image.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="empty image upload")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="image too large (max 12 MiB)")

    side_bytes: bytes | None = None
    if side_image is not None:
        side_bytes = await side_image.read()
        if len(side_bytes) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="side image too large (max 12 MiB)")
        if len(side_bytes) == 0:
            side_bytes = None

    side_anno_dict = _parse_json("side_annotations", side_annotations) or {}
    misc_dict = _parse_json("misc_ratings", misc_ratings) or {}

    try:
        result = run(
            data, sex,
            side_bytes=side_bytes,
            side_annotations=side_anno_dict or None,
            misc_ratings=misc_dict or None,
        )
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.to_dict()


class ImageSizeIn(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class ScoreRequest(BaseModel):
    landmarks: list[list[float]]
    sex: Literal["male", "female"]
    image_size: ImageSizeIn | None = None
    mask_b64: str | None = None
    side_annotations: dict[str, list[float]] | None = None
    side_image_size: ImageSizeIn | None = None
    misc_ratings: dict[str, int] | None = None


@router.post("/score")
async def score(req: ScoreRequest) -> dict:
    if len(req.landmarks) < 468:
        raise HTTPException(status_code=400,
                            detail=f"need at least 468 landmarks, got {len(req.landmarks)}")
    img_size = (req.image_size.width, req.image_size.height) if req.image_size else None
    side_size = (req.side_image_size.width, req.side_image_size.height) if req.side_image_size else None
    try:
        result = score_from_landmarks(
            req.landmarks, req.sex,
            image_size=img_size, mask_b64=req.mask_b64,
            side_annotations=req.side_annotations,
            misc_ratings=req.misc_ratings,
            side_image_size=side_size,
        )
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.to_dict()
