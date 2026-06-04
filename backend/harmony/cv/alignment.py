"""Roll-correct and crop a face image based on FaceMesh landmarks.

Strategy:
1. Run FaceMesh on the original BGR image.
2. Compute the inter-pupil midpoint line angle and rotate the whole image so
   the eyes lie horizontal. The full image is used as input to downstream
   measurements so that segmentation (neck) still has shoulders/neck visible.
3. Re-run FaceMesh on the rotated image to get aligned landmarks.

The function returns the aligned image plus its fresh landmarks. If the face
is already close to level, the rotation step is skipped.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import landmarks as lm_mod
from .landmarks import LandmarkResult


@dataclass(slots=True)
class AlignedFace:
    image: np.ndarray  # BGR
    landmarks: LandmarkResult
    rotation_deg: float


def _eye_angle(points: np.ndarray) -> float:
    left = points[lm_mod.LEFT_EYE_OUTER]
    right = points[lm_mod.RIGHT_EYE_OUTER]
    dx = right[0] - left[0]
    dy = right[1] - left[1]
    import math

    return math.degrees(math.atan2(dy, dx))


def _rotate_image(image: np.ndarray, angle_deg: float) -> np.ndarray:
    import cv2

    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def normalize(image_bgr: np.ndarray) -> AlignedFace:
    """Detect face, roll-correct so eyes are horizontal, and return aligned data."""
    initial = lm_mod.detect(image_bgr)
    angle = _eye_angle(initial.points)
    if abs(angle) < 0.6:
        return AlignedFace(image=image_bgr, landmarks=initial, rotation_deg=0.0)

    rotated = _rotate_image(image_bgr, angle)
    aligned_lms = lm_mod.detect(rotated)
    return AlignedFace(image=rotated, landmarks=aligned_lms, rotation_deg=angle)
