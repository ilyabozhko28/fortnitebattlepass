"""MediaPipe FaceLandmarker wrapper (Tasks API).

Lazy-instantiates the detector on first use so importing this module is cheap.
Exposes named landmark indices that downstream measurement modules reference
by meaning rather than magic numbers.

The Tasks API needs a ``face_landmarker.task`` asset; we auto-download it on
first use into ``harmony/models/weights/``.
"""

from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# --- Named indices ----------------------------------------------------------
# MediaPipe FaceMesh — canonical 468-point model.
NOSE_TIP = 1
NOSE_BASE = 2  # subnasale
BROW_MID = 9   # glabella-ish
UPPER_LIP_TOP = 0
UPPER_LIP_BOTTOM = 13
LOWER_LIP_TOP = 14
LOWER_LIP_BOTTOM = 17
CHIN = 152

LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374

# Brow tips — the **outermost** points along the eyebrow's upper edge
# (MediaPipe FaceMesh canonical curve: 70-63-105-66-107 left, 300-293-334-296-336
# right). Use the tips (70/300 outer, 107/336 inner) so tilt is measured along
# the full span of the brow, not an interior chord.
LEFT_BROW_INNER = 107
LEFT_BROW_OUTER = 70
RIGHT_BROW_INNER = 336
RIGHT_BROW_OUTER = 300

MOUTH_LEFT = 61
MOUTH_RIGHT = 291

ALA_LEFT = 49
ALA_RIGHT = 279

# Malar / zygomatic prominence apex (mid-cheek bump). MediaPipe 50/280 sit on
# the surface of the cheekbone, roughly at its highest point.
CHEEKBONE_APEX_LEFT = 50
CHEEKBONE_APEX_RIGHT = 280

# Face boundary points
TEMPLE_LEFT = 54
TEMPLE_RIGHT = 284
ZYGION_LEFT = 234
ZYGION_RIGHT = 454

# True mandibular angle (gonion): the point where the ramus meets the body of
# the mandible. On MediaPipe FaceMesh this lives on the jaw curve closest to
# the ear, indices 132/361. Empirically this gives a Jaw Frontal Angle of
# ~86° for a normal male face (spec target band 84-95°), and a bigonial /
# bizygomatic ratio in the spec's 85-92% band.
GONION_LEFT = 132
GONION_RIGHT = 361

# Kept for reference (intermediate jaw-curve points). Not used by any metric
# any more — JFA + bigonial both use the true gonions above.
JAW_MID_LEFT = 172
JAW_MID_RIGHT = 397

FOREHEAD_TOP = 10  # top of FaceMesh hairline approximation (not actual hairline)


@dataclass(slots=True)
class LandmarkResult:
    """All landmark coordinates in image pixel space, plus face bbox."""

    points: np.ndarray  # shape (468, 2), dtype float64
    bbox: tuple[int, int, int, int]  # x, y, w, h


_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)
_MODEL_PATH = (
    Path(__file__).resolve().parents[1] / "models" / "weights" / "face_landmarker.task"
)

_detector: Any | None = None


def _ensure_asset() -> Path:
    if _MODEL_PATH.exists():
        return _MODEL_PATH
    override = os.environ.get("HARMONY_FACE_LANDMARKER_PATH")
    if override and Path(override).exists():
        return Path(override)
    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    url = os.environ.get("HARMONY_FACE_LANDMARKER_URL", _MODEL_URL)
    with urllib.request.urlopen(url) as resp, _MODEL_PATH.open("wb") as out:
        out.write(resp.read())
    return _MODEL_PATH


def _get_detector() -> Any:
    global _detector
    if _detector is None:
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        asset = _ensure_asset()
        options = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(asset)),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        _detector = mp_vision.FaceLandmarker.create_from_options(options)
    return _detector


class NoFaceFoundError(RuntimeError):
    pass


def detect(image_bgr: np.ndarray) -> LandmarkResult:
    """Run FaceLandmarker on a BGR uint8 image and return pixel-space landmarks."""
    import cv2  # local import to keep top-level import light
    import mediapipe as mp

    det = _get_detector()
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    result = det.detect(mp_image)
    if not result.face_landmarks:
        raise NoFaceFoundError("FaceLandmarker did not detect any face")

    h, w = image_bgr.shape[:2]
    face = result.face_landmarks[0]
    # FaceLandmarker returns 478 landmarks (468 mesh + 10 iris); first 468 indices
    # match the legacy FaceMesh model exactly.
    points = np.array(
        [[lm.x * w, lm.y * h] for lm in face[:468]],
        dtype=np.float64,
    )
    xs = points[:, 0]
    ys = points[:, 1]
    x0, y0 = float(xs.min()), float(ys.min())
    x1, y1 = float(xs.max()), float(ys.max())
    bbox = (
        max(0, int(x0)),
        max(0, int(y0)),
        min(w, int(x1) + 1) - max(0, int(x0)),
        min(h, int(y1) + 1) - max(0, int(y0)),
    )
    return LandmarkResult(points=points, bbox=bbox)
