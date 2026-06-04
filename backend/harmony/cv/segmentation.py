"""MediaPipe ImageSegmenter wrapper (Tasks API) for selfie segmentation.

Used to estimate neck width below the chin. The asset ``selfie_segmenter.tflite``
is auto-downloaded on first use into ``harmony/models/weights/``.

Returns a ``uint8`` mask of shape ``(H, W)`` with values 0 or 255.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
    "selfie_segmenter/float16/latest/selfie_segmenter.tflite"
)
_MODEL_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "weights" / "selfie_segmenter.tflite"
)

_segmenter: Any | None = None


def _ensure_asset() -> Path:
    if _MODEL_PATH.exists():
        return _MODEL_PATH
    override = os.environ.get("HARMONY_SELFIE_SEGMENTER_PATH")
    if override and Path(override).exists():
        return Path(override)
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    url = os.environ.get("HARMONY_SELFIE_SEGMENTER_URL", _MODEL_URL)
    with urllib.request.urlopen(url) as resp, _MODEL_PATH.open("wb") as out:
        out.write(resp.read())
    return _MODEL_PATH


def _get_segmenter() -> Any:
    global _segmenter
    if _segmenter is None:
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        asset = _ensure_asset()
        options = mp_vision.ImageSegmenterOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(asset)),
            running_mode=mp_vision.RunningMode.IMAGE,
            output_category_mask=True,
            output_confidence_masks=False,
        )
        _segmenter = mp_vision.ImageSegmenter.create_from_options(options)
    return _segmenter


def person_mask(image_bgr: np.ndarray) -> np.ndarray:
    import cv2
    import mediapipe as mp

    seg = _get_segmenter()
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    result = seg.segment(mp_image)
    if result.category_mask is None:
        return np.zeros(image_bgr.shape[:2], dtype=np.uint8)
    cat = np.asarray(result.category_mask.numpy_view())
    if cat.ndim == 3:
        cat = cat[..., 0]
    # SelfieSegmenter's category_mask uses 0 = background, 255 = person on Windows
    # builds (the model's internal category IDs are 0/1 but get scaled by 255).
    # Defensive: if more than half of the central face region looks like 0 we may
    # have the inverted convention — detect by majority vote inside the central
    # region and invert if necessary.
    h, w = cat.shape
    cy0, cy1 = int(h * 0.35), int(h * 0.65)
    cx0, cx1 = int(w * 0.35), int(w * 0.65)
    center = cat[cy0:cy1, cx0:cx1]
    if center.size > 0 and (center > 0).mean() < 0.5:
        # Center of frame is mostly "0" — selfie segmenter outputs background=255 here
        # (some MP builds invert the mask), so flip.
        binary = (cat == 0).astype(np.uint8) * 255
    else:
        binary = (cat > 0).astype(np.uint8) * 255
    return binary
