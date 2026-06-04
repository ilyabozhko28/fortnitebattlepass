"""Tiny CNN regressing the cheekbone-apex vertical position.

Input: 64x64 grayscale midface crop. Output: a single scalar in [0, 1]
representing the vertical position of the cheekbone apex within the crop
(0 = top of crop, 1 = bottom).

Architecture intentionally small (<200K params) so it runs on CPU instantly.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class CheekboneNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x)).squeeze(-1)
