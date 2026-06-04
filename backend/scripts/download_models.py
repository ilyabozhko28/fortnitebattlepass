"""Download or place helper-model weights.

By default this is a no-op because the project does not bundle pretrained
weights. The pipeline transparently falls back to OpenCV heuristics when
weights are missing.

To plug in your own weights, set ``HARMONY_CHEEKBONE_URL`` and / or
``HARMONY_HAIRLINE_URL`` environment variables pointing to ``.pt`` state-dict
files and run::

    python -m scripts.download_models
"""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

WEIGHTS_DIR = Path(__file__).resolve().parents[1] / "harmony" / "models" / "weights"


def _fetch(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"  -> {url}  →  {target}")
    with urllib.request.urlopen(url) as resp, target.open("wb") as out:
        out.write(resp.read())


def main() -> int:
    cheekbone_url = os.environ.get("HARMONY_CHEEKBONE_URL")
    hairline_url = os.environ.get("HARMONY_HAIRLINE_URL")

    if not cheekbone_url and not hairline_url:
        print(
            "no HARMONY_CHEEKBONE_URL / HARMONY_HAIRLINE_URL set — nothing to download.",
            file=sys.stderr,
        )
        print(
            "the pipeline will use OpenCV heuristics for cheekbone/hairline.",
            file=sys.stderr,
        )
        return 0

    if cheekbone_url:
        _fetch(cheekbone_url, WEIGHTS_DIR / "cheekbone_net.pt")
    if hairline_url:
        _fetch(hairline_url, WEIGHTS_DIR / "hairline_net.pt")
    print("done.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
