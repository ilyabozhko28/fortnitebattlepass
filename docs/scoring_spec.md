# Frontal Harmony — scoring specification

Verbatim spec used by the implementation. Source of truth for tier ranges and
points. The aggregator divides the summed points by **275**.

## Points per tier

| Metric                                  | T1     | T2     | T3    | T4   | T5     | T6      | T7     |
| --------------------------------------- | ------ | ------ | ----- | ---- | ------ | ------- | ------ |
| Eye Separation Ratio (ESR)              | 12.20  | 10.98  | 6.59  | 3.66 | -10.98 | -65.88  | -97.5  |
| Facial Thirds                           | 19.83  | 17.84  | 9.91  | 5.95 | -5.95  | -11.90  | —      |
| Canthal Tilt                            | 12.35  | 11.12  | 6.18  | 3.71 | -3.71  | -7.40   | —      |
| FWHR                                    | 18.30  | 16.47  | 9.15  | 5.49 | -16.47 | -49.41  | -85    |
| Jaw Frontal Angle                       | 9.15   | 8.24   | 4.58  | 2.75 | -4.58  | -9.15   | -15    |
| Cheekbone Setness                       | 20     | 10     | 5     | 2.5  | 0      | -2.5    | -5     |
| Face Length (Total width/height)        | 20     | 10     | 5     | 2.5  | 0      | -2.5    | -5     |
| Bigonial Width (Jaw Width)              | 20.59  | 18.53  | 10.29 | 6.18 | -18.53 | -46.32  | -65    |
| Chin to Philtrum Ratio                  | 12.96  | 11.67  | 6.48  | 3.89 | -1.95  | -3.89   | —      |
| Neck Width                              | 19.06  | 17.16  | 9.53  | 5.72 | -17.16 | -34.31  | —      |
| Mouth to Nose Ratio                     | 12.35  | 11.12  | 6.18  | 3.71 | -3.71  | -7.40   | —      |
| Midface Ratio                           | 11.90  | 10.71  | 5.95  | 3.57 | -3.57  | -7.14   | —      |
| Eyebrow Setedness                       | 19.83  | 17.84  | 9.91  | 5.95 | -5.95  | -11.90  | —      |
| Eye Spacing (One Eye Test)              | 12.20  | 10.98  | 6.59  | 3.66 | -10.98 | -65.88  | —      |
| Eye Aspect Ratio                        | 18.30  | 16.47  | 9.15  | 5.49 | -5.49  | -10.98  | —      |
| Lower Lip to Upper Lip Ratio            | 5      | 2.5    | 1.25  | 0    | -1.25  | -2.5    | —      |
| Deviation IAA to JFA                    | 7.5    | 3.75   | 1.88  | 0    | -1.88  | -3.75   | —      |
| Eyebrow Tilt                            | 10     | 5      | 2.5   | 0    | -2.5   | -5      | —      |
| Bitemporal Width                        | 7.5    | 3.75   | 1.88  | 0    | -1.88  | -3.75   | —      |
| Lower Third Proportion                  | 5      | 2.5    | 1.25  | 0    | -1.25  | -2.5    | —      |

`Frontal Harmony Score = (sum of awarded points) / 275`.

## Tier ranges

### Eye Separation Ratio

- Tier 1 — Male 44.3%–47.7% / Female 45%–47.9%
- Tier 2 — 0.1–0.5 deviation
- Tier 3 — 0.6–1 deviation
- Tier 4 — 1.1–1.5 deviation
- Tier 5 — 1.6–2.3 deviation
- Tier 6 — 2.4–2.5 deviation
- Tier 7 — > 2.5 deviation

### Facial Thirds

- Tier 1 — Unisex 1–3% from 33%
- Tier 2 — 4% deviation
- Tier 3 — 5% deviation
- Tier 4 — 6% deviation
- Tier 5 — 7% deviation
- Tier 6 — > 8% deviation

### Canthal Tilt

- Tier 1 — Male 5°–8.5° / Female 6°–9.5°
- Tier 2 — 0.1°–1.25° deviation
- Tier 3 — 1.26°–2.99° deviation
- Tier 4 — Male 0°–2° / Female 0°–3°
- Tier 5 — −1° or −2°
- Tier 6 — > −2°

### Facial Width to Height Ratio (FWHR)

- Tier 1 — 1.9–2.06
- Tier 2 — 0.01–0.07 deviation
- Tier 3 — 0.08–0.10 deviation
- Tier 4 — 0.11–0.12 deviation
- Tier 5 — 2.19–2.23 or 1.7–1.77
- Tier 6 — > 2.23
- Tier 7 — 1.55–1.69

### Jaw Frontal Angle

- Tier 1 — Male 84°–95° / Female 86°–97°
- Tier 2 — 0.1°–3° deviation
- Tier 3 — 4°–5° deviation
- Tier 4 — 6°–10° deviation
- Tier 5 — 11°–15° deviation
- Tier 6 — 16°–20° deviation
- Tier 7 — > 20° deviation

### Cheekbones High Setedness

- Tier 1 — ≥ 81%
- Tier 2 — 80%–76%
- Tier 3 — 75%–70%
- Tier 4 — 69%–66%
- Tier 5 — 65%–60%
- Tier 6 — 59%–56%
- Tier 7 — < 56%

### Total Facial Height to Width (Face Length)

- Tier 1 — Male 1.33–1.38 / Female 1.29–1.33
- Tier 2 — 0.01–0.05 deviation
- Tier 3 — 0.06–0.08 deviation
- Tier 4 — 0.09–0.10 deviation
- Tier 5 — 0.11–0.12 deviation
- Tier 6 — 0.13–0.16 deviation
- Tier 7 — > 0.16 deviation

### Bigonial Width

- Tier 1 — Male 85%–92% / Female 82%–89%
- Tier 2 — 0.1%–2% deviation
- Tier 3 — 3%–5% deviation
- Tier 4 — 6%–7% deviation
- Tier 5 — 8%–11% deviation
- Tier 6 — 12%–16% deviation
- Tier 7 — > 16% deviation

### Chin to Philtrum

- Tier 1 — Male 2.05–2.55 / Female 2.0–2.5
- Tier 2 — 0.01–0.10 deviation
- Tier 3 — 0.11–0.25 deviation
- Tier 4 — 0.26–0.5 deviation
- Tier 5 — 0.51–1 deviation
- Tier 6 — > 1 deviation

### Neck Width

- Tier 1 — Male > 90% / Female 75%–85%
- Tier 2 — 1%–5% deviation
- Tier 3 — 6%–10% deviation
- Tier 4 — 11%–15% deviation
- Tier 5 — 16%–20% deviation
- Tier 6 — > 20% deviation

### Mouth to Nose Width

- Tier 1 — Male 1.38–1.53 / Female 1.45–1.67
- Tier 2 — 0.01–0.04 deviation
- Tier 3 — 0.05–0.08 deviation
- Tier 4 — 0.09–0.12 deviation
- Tier 5 — 0.13–0.16 deviation
- Tier 6 — > 0.16 deviation

### Midface Ratio

- Tier 1 — Male 0.93–1.01 / Female 1.0–1.1
- Tier 2 — 0.01–0.02 deviation
- Tier 3 — 0.03–0.05 deviation
- Tier 4 — 0.06–0.08 deviation
- Tier 5 — 0.09–0.13 deviation
- Tier 6 — > 0.13 deviation

### Eyebrow Setedness

- Tier 1 — Male < 0.66 / Female 0.40–0.85
- Tier 2 — Male 0.66–0.95 / Female 0.86–1.20
- Tier 3 — Male 0.96–1.20 / Female 1.21–1.50
- Tier 4 — Male 1.21–1.50 / Female 1.51–1.80
- Tier 5 — Male 1.51–1.80 / Female 1.81–2.0
- Tier 6 — Male > 1.80 / Female > 2.0

### Eye Spacing (One Eye Test)

- Tier 1 — 0.95–1.05
- Tier 2 — 0.01–0.03 deviation
- Tier 3 — 0.04–0.08 deviation
- Tier 4 — 0.09–0.13 deviation
- Tier 5 — 0.14–0.20 deviation
- Tier 6 — > 0.20 deviation

### Eye Aspect Ratio

- Tier 1 — Male 2.8–3.6 / Female 2.5–3.3
- Tier 2 — 0.01–0.2 deviation
- Tier 3 — 0.3–0.4 deviation
- Tier 4 — 0.5–0.6 deviation
- Tier 5 — 0.7–0.8 deviation
- Tier 6 — > 0.8 deviation

### Lower Lip to Upper Lip Ratio

- Tier 1 — 1.4–2.0
- Tier 2 — 0.01–0.2 deviation
- Tier 3 — 0.3–0.4 deviation
- Tier 4 — 0.5–0.6 deviation
- Tier 5 — 0.7–0.8 deviation
- Tier 6 — > 0.8 deviation

### Deviation IAA to JFA

- Tier 1 — 0°–5°
- Tier 2 — 6°–10°
- Tier 3 — 11°–15°
- Tier 4 — 16°–18°
- Tier 5 — 19°–20°
- Tier 6 — > 20°

### Eyebrow Tilt

- Tier 1 — Male 5°–13° / Female 11°–19°
- Tier 2 — 0.1°–5° deviation
- Tier 3 — Unisex 6°–10° positive tilt / Female 6°–3°
- Tier 4 — Men 0°–(−3°) / Female 3°–0°
- Tier 5 — Men −4° to −5° / Female −1° to −3°
- Tier 6 — Men > −5° / Female > −3°

### Bitemporal Width

- Tier 1 — Male 84%–95% / Female 79%–92%
- Tier 2 — 0.1%–3% deviation
- Tier 3 — 4%–5% deviation
- Tier 4 — 6%–8% deviation
- Tier 5 — 9%–13% deviation
- Tier 6 — > 13% deviation

### Lower Third Proportion

- Tier 1 — < 3% from 33%
- Tier 2 — 4% deviation
- Tier 3 — 5% deviation
- Tier 4 — 6% deviation
- Tier 5 — 7% deviation
- Tier 6 — > 8% deviation

### Ipsilateral Alar Angle (not scored — input to Deviation IAA to JFA)

- Tier 1 — Male 84%–95% / Female 86%–97%
- Tier 2 — 0.1–2 deviation
- Tier 3 — 3–5 deviation
- Tier 4 — > 5 deviation
