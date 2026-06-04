"""Lazy loader for small PyTorch helpers with graceful OpenCV fallbacks.

The pipeline does not crash if weights are missing — instead it uses
deterministic heuristic estimators and surfaces a warning in the response.

Public API:

- :func:`estimate_cheekbone_apex` -> ``(y_pixel: float, used_model: bool)``
- :func:`estimate_hairline_y`     -> ``(y_pixel: float, used_model: bool)``
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

WEIGHTS_DIR = Path(__file__).resolve().parent / "weights"


@dataclass(slots=True)
class _Cache:
    cheekbone: Any | None = None
    hairline: Any | None = None
    cheekbone_loaded: bool = False
    hairline_loaded: bool = False


_cache = _Cache()


def _try_load(name: str, ctor) -> Any | None:
    """Try to load a state_dict from ``WEIGHTS_DIR / name`` into ``ctor()``."""
    path = WEIGHTS_DIR / name
    if not path.exists():
        return None
    try:
        import torch  # noqa: WPS433 — local import is intentional

        net = ctor()
        state = torch.load(path, map_location="cpu")
        net.load_state_dict(state)
        net.eval()
        return net
    except Exception:
        return None


def _get_cheekbone():
    if not _cache.cheekbone_loaded:
        from .cheekbone_net import CheekboneNet

        _cache.cheekbone = _try_load("cheekbone_net.pt", CheekboneNet)
        _cache.cheekbone_loaded = True
    return _cache.cheekbone


def _get_hairline():
    if not _cache.hairline_loaded:
        from .hairline_net import HairlineNet

        _cache.hairline = _try_load("hairline_net.pt", HairlineNet)
        _cache.hairline_loaded = True
    return _cache.hairline


# --- Cheekbone apex --------------------------------------------------------

def estimate_cheekbone_apex(
    image_bgr: np.ndarray,
    *,
    face_top: float,
    face_bottom: float,
    zygion_left: tuple[float, float],
    zygion_right: tuple[float, float],
) -> tuple[float, bool]:
    """Return (y in pixel space, used_pytorch_model)."""
    model = _get_cheekbone()
    crop_y0 = int(max(0, face_top))
    crop_y1 = int(min(image_bgr.shape[0], face_bottom))
    crop_x0 = int(max(0, min(zygion_left[0], zygion_right[0])))
    crop_x1 = int(min(image_bgr.shape[1], max(zygion_left[0], zygion_right[0])))

    if crop_y1 <= crop_y0 or crop_x1 <= crop_x0:
        return (face_top + 0.4 * (face_bottom - face_top), False)

    crop = image_bgr[crop_y0:crop_y1, crop_x0:crop_x1]

    if model is not None:
        try:
            import cv2
            import torch

            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
            tensor = torch.from_numpy(resized).float().unsqueeze(0).unsqueeze(0) / 255.0
            with torch.no_grad():
                rel = float(model(tensor).item())
            y_pixel = crop_y0 + rel * (crop_y1 - crop_y0)
            return (y_pixel, True)
        except Exception:
            pass

    # Heuristic fallback: cheekbone apex sits roughly at 38% from face top to chin,
    # which is a commonly cited canon for the inferior-orbital / zygomatic apex line.
    y_pixel = face_top + 0.38 * (face_bottom - face_top)
    return (y_pixel, False)


# --- Hairline --------------------------------------------------------------

def estimate_hairline_y(
    image_bgr: np.ndarray,
    *,
    forehead_top: float,
    brow_y: float,
    face_left: float,
    face_right: float,
) -> tuple[float, bool]:
    """Return (hairline y, used_pytorch_model).

    ``forehead_top`` is the y coordinate of the topmost FaceMesh point (which
    sits roughly at the hairline already); we treat it as an upper bound. The
    heuristic falls back to ``forehead_top`` itself, which is the best
    available approximation when no hair-segmentation model is loaded.
    """
    model = _get_hairline()
    crop_y0 = int(max(0, forehead_top - 0.3 * (brow_y - forehead_top)))
    crop_y1 = int(min(image_bgr.shape[0], brow_y))
    crop_x0 = int(max(0, face_left))
    crop_x1 = int(min(image_bgr.shape[1], face_right))

    if crop_y1 <= crop_y0 or crop_x1 <= crop_x0:
        return (forehead_top, False)

    crop = image_bgr[crop_y0:crop_y1, crop_x0:crop_x1]

    if model is not None:
        try:
            import cv2
            import torch

            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
            tensor = torch.from_numpy(resized).float().unsqueeze(0).unsqueeze(0) / 255.0
            with torch.no_grad():
                rel = float(model(tensor).item())
            y_pixel = crop_y0 + rel * (crop_y1 - crop_y0)
            return (y_pixel, True)
        except Exception:
            pass

    return (float(forehead_top), False)
