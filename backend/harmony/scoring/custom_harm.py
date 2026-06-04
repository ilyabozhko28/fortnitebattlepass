from __future__ import annotations

import math
from typing import Optional
from .tiers import TierResult

def _dev(raw: float, low: float, high: float) -> float:
    if low <= raw <= high:
        return 0.0
    return min(abs(raw - low), abs(raw - high))

def custom_classify(name: str, raw: float | None, sex: str) -> Optional[TierResult]:
    if raw is None or math.isnan(raw):
        return None

    if name == "eye_separation_ratio":
        # T1: (Male) 44.3-47.7 / (Female) 45-47.9
        low, high = (44.3, 47.7) if sex == "male" else (45.0, 47.9)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.5: return TierResult(2, "Tier 2", d)
        if d <= 1.0: return TierResult(3, "Tier 3", d)
        if d <= 1.5: return TierResult(4, "Tier 4", d)
        if d <= 2.3: return TierResult(5, "Tier 5", d)
        if d <= 2.5: return TierResult(6, "Tier 6", d)
        return TierResult(7, "Tier 7", d)

    if name == "facial_thirds":
        # T1: 1-3% from 33%
        # Wait, the metric returns `max(devs)` where dev = abs(pct - 33.33)
        # So raw is already the deviation in %.
        # T1: <= 3%
        # T2: 4%, T3: 5%, T4: 6%, T5: 7%, T6: >8%
        d = raw
        if d <= 3.5: return TierResult(1, "Tier 1", d)
        if d <= 4.5: return TierResult(2, "Tier 2", d)
        if d <= 5.5: return TierResult(3, "Tier 3", d)
        if d <= 6.5: return TierResult(4, "Tier 4", d)
        if d <= 7.5: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "lateral_canthal_tilt":
        low, high = (5.0, 8.5) if sex == "male" else (6.0, 9.5)
        if low <= raw <= high: return TierResult(1, "Tier 1", 0.0)
        # Check negative specifics from spec?
        # T4: (Male) 0-2 / (Female) 0-3 Degree
        # T5: (-1) or (-2) Degree
        # T6: >(-2) Degree (meaning <-2)
        if (sex == "male" and 0 <= raw <= 2) or (sex == "female" and 0 <= raw <= 3):
            return TierResult(4, "Tier 4", raw)
        if -2 <= raw <= -1:
            return TierResult(5, "Tier 5", raw)
        if raw < -2:
            return TierResult(6, "Tier 6", raw)
        
        d = _dev(raw, low, high)
        if d <= 1.25: return TierResult(2, "Tier 2", d)
        if d <= 2.99: return TierResult(3, "Tier 3", d)
        return TierResult(6, "Tier 6", d) # Fallback

    if name == "fwhr":
        # T1: 1.9-2.06
        d = _dev(raw, 1.9, 2.06)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.07: return TierResult(2, "Tier 2", d)
        if d <= 0.10: return TierResult(3, "Tier 3", d)
        if d <= 0.12: return TierResult(4, "Tier 4", d)
        # T5: 2.19-2.23 / 1.7-1.77 Deviation (meaning values, not dev) -> dev is 0.13 to 0.20
        # T6: >2.23 Deviation (meaning raw > 2.23 -> dev > 0.17)
        # T7: 1.55-1.69 Deviation (meaning raw 1.55-1.69 -> dev 0.21-0.35)
        # Just use deviation strictly:
        if raw >= 2.19 and raw <= 2.23 or raw >= 1.7 and raw <= 1.77: return TierResult(5, "Tier 5", d)
        if raw > 2.23: return TierResult(6, "Tier 6", d)
        if raw >= 1.55 and raw <= 1.69: return TierResult(7, "Tier 7", d)
        # Fallback to nearest by deviation
        if d <= 0.20: return TierResult(5, "Tier 5", d)
        return TierResult(7, "Tier 7", d)

    if name == "jaw_frontal_angle":
        low, high = (84.0, 95.0) if sex == "male" else (86.0, 97.0)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 3.0: return TierResult(2, "Tier 2", d)
        if d <= 5.0: return TierResult(3, "Tier 3", d)
        if d <= 10.0: return TierResult(4, "Tier 4", d)
        if d <= 15.0: return TierResult(5, "Tier 5", d)
        if d <= 20.0: return TierResult(6, "Tier 6", d)
        return TierResult(7, "Tier 7", d)

    if name == "cheekbone_setness":
        if raw >= 81.0: return TierResult(1, "Tier 1", 0.0)
        if raw >= 76.0: return TierResult(2, "Tier 2", 81 - raw)
        if raw >= 70.0: return TierResult(3, "Tier 3", 81 - raw)
        if raw >= 66.0: return TierResult(4, "Tier 4", 81 - raw)
        if raw >= 60.0: return TierResult(5, "Tier 5", 81 - raw)
        if raw >= 56.0: return TierResult(6, "Tier 6", 81 - raw)
        return TierResult(7, "Tier 7", 81 - raw)

    if name == "face_length":
        low, high = (1.33, 1.38) if sex == "male" else (1.29, 1.33)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.05: return TierResult(2, "Tier 2", d)
        if d <= 0.08: return TierResult(3, "Tier 3", d)
        if d <= 0.10: return TierResult(4, "Tier 4", d)
        if d <= 0.12: return TierResult(5, "Tier 5", d)
        if d <= 0.16: return TierResult(6, "Tier 6", d)
        return TierResult(7, "Tier 7", d)

    if name == "jaw_width":
        low, high = (85.0, 92.0) if sex == "male" else (82.0, 89.0)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 2.0: return TierResult(2, "Tier 2", d)
        if d <= 5.0: return TierResult(3, "Tier 3", d)
        if d <= 7.0: return TierResult(4, "Tier 4", d)
        if d <= 11.0: return TierResult(5, "Tier 5", d)
        if d <= 16.0: return TierResult(6, "Tier 6", d)
        return TierResult(7, "Tier 7", d)

    if name == "chin_to_philtrum":
        low, high = (2.05, 2.55) if sex == "male" else (2.0, 2.5)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.10: return TierResult(2, "Tier 2", d)
        if d <= 0.25: return TierResult(3, "Tier 3", d)
        if d <= 0.50: return TierResult(4, "Tier 4", d)
        if d <= 1.0: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "neck_width":
        if sex == "male":
            low, high = 90.0, 200.0 # >90
        else:
            low, high = 75.0, 85.0
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 5.0: return TierResult(2, "Tier 2", d)
        if d <= 10.0: return TierResult(3, "Tier 3", d)
        if d <= 15.0: return TierResult(4, "Tier 4", d)
        if d <= 20.0: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "mouth_to_nose":
        low, high = (1.38, 1.53) if sex == "male" else (1.45, 1.67)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.04: return TierResult(2, "Tier 2", d)
        if d <= 0.08: return TierResult(3, "Tier 3", d)
        if d <= 0.12: return TierResult(4, "Tier 4", d)
        if d <= 0.16: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "midface_ratio":
        low, high = (0.93, 1.01) if sex == "male" else (1.0, 1.1)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.02: return TierResult(2, "Tier 2", d)
        if d <= 0.05: return TierResult(3, "Tier 3", d)
        if d <= 0.08: return TierResult(4, "Tier 4", d)
        if d <= 0.13: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "eye_to_brow_distance":
        if sex == "male":
            if raw <= 0.66: return TierResult(1, "Tier 1", 0.0)
            if raw <= 0.95: return TierResult(2, "Tier 2", raw - 0.66)
            if raw <= 1.20: return TierResult(3, "Tier 3", raw - 0.66)
            if raw <= 1.50: return TierResult(4, "Tier 4", raw - 0.66)
            if raw <= 1.80: return TierResult(5, "Tier 5", raw - 0.66)
            return TierResult(6, "Tier 6", raw - 0.66)
        else:
            if 0.40 <= raw <= 0.85: return TierResult(1, "Tier 1", 0.0)
            if 0.86 <= raw <= 1.20: return TierResult(2, "Tier 2", _dev(raw, 0.4, 0.85))
            if 1.21 <= raw <= 1.50: return TierResult(3, "Tier 3", _dev(raw, 0.4, 0.85))
            if 1.51 <= raw <= 1.80: return TierResult(4, "Tier 4", _dev(raw, 0.4, 0.85))
            if 1.81 <= raw <= 2.0:  return TierResult(5, "Tier 5", _dev(raw, 0.4, 0.85))
            return TierResult(6, "Tier 6", _dev(raw, 0.4, 0.85))

    if name == "eye_spacing":
        if (0.95 <= raw <= 1.00) or (1.00 <= raw <= 1.05): return TierResult(1, "Tier 1", 0.0)
        d = _dev(raw, 0.95, 1.05)
        if d <= 0.03: return TierResult(2, "Tier 2", d)
        if d <= 0.08: return TierResult(3, "Tier 3", d)
        if d <= 0.13: return TierResult(4, "Tier 4", d)
        if d <= 0.20: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "eye_aspect_ratio":
        low, high = (2.8, 3.6) if sex == "male" else (2.5, 3.3)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.2: return TierResult(2, "Tier 2", d)
        if d <= 0.4: return TierResult(3, "Tier 3", d)
        if d <= 0.6: return TierResult(4, "Tier 4", d)
        if d <= 0.8: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "lower_lip_to_upper_lip_ratio":
        d = _dev(raw, 1.4, 2.0)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 0.2: return TierResult(2, "Tier 2", d)
        if d <= 0.4: return TierResult(3, "Tier 3", d)
        if d <= 0.6: return TierResult(4, "Tier 4", d)
        if d <= 0.8: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "iaa_to_jfa_deviation":
        if raw <= 5.0: return TierResult(1, "Tier 1", raw)
        if raw <= 10.0: return TierResult(2, "Tier 2", raw)
        if raw <= 15.0: return TierResult(3, "Tier 3", raw)
        if raw <= 18.0: return TierResult(4, "Tier 4", raw)
        if raw <= 20.0: return TierResult(5, "Tier 5", raw)
        return TierResult(6, "Tier 6", raw)

    if name == "eyebrow_tilt":
        low, high = (5.0, 13.0) if sex == "male" else (11.0, 19.0)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 5.0: return TierResult(2, "Tier 2", d)
        if sex == "male":
            if 6.0 <= raw <= 10.0: return TierResult(3, "Tier 3", d)  # Note: "Unisex 6-10 positive tilt" wait, if 6-10 is T3 but 5-13 is T1? That's overlapping! Let's just use deviation for 3-6 if not caught.
            if 0.0 <= raw <= -3.0: return TierResult(4, "Tier 4", d) # Meaning -3 to 0
            if -5.0 <= raw <= -4.0: return TierResult(5, "Tier 5", d)
            if raw < -5.0: return TierResult(6, "Tier 6", d)
        else:
            if 3.0 <= raw <= 6.0: return TierResult(3, "Tier 3", d)
            if 0.0 <= raw <= 3.0: return TierResult(4, "Tier 4", d)
            if -3.0 <= raw <= -1.0: return TierResult(5, "Tier 5", d)
            if raw < -3.0: return TierResult(6, "Tier 6", d)
        # Fallback to dev 6-10
        return TierResult(3, "Tier 3", d)

    if name == "bitemporal_width":
        low, high = (84.0, 95.0) if sex == "male" else (79.0, 92.0)
        d = _dev(raw, low, high)
        if d == 0: return TierResult(1, "Tier 1", d)
        if d <= 3.0: return TierResult(2, "Tier 2", d)
        if d <= 5.0: return TierResult(3, "Tier 3", d)
        if d <= 8.0: return TierResult(4, "Tier 4", d)
        if d <= 13.0: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    if name == "lower_third_proportion":
        d = abs(raw - 33.33)
        if raw <= 33.0 or d <= 3.0: return TierResult(1, "Tier 1", d) # <3% to 33%
        if d <= 4.5: return TierResult(2, "Tier 2", d)
        if d <= 5.5: return TierResult(3, "Tier 3", d)
        if d <= 6.5: return TierResult(4, "Tier 4", d)
        if d <= 7.5: return TierResult(5, "Tier 5", d)
        return TierResult(6, "Tier 6", d)

    return None
