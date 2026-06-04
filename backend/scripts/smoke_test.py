"""Smoke test: run the pipeline on a path provided via CLI.

Usage::

    python -m scripts.smoke_test path/to/face.jpg [male|female]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from harmony.pipeline import run


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: smoke_test <image_path> [male|female]", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    sex = sys.argv[2] if len(sys.argv) > 2 else "male"
    if sex not in ("male", "female"):
        print(f"invalid sex: {sex!r} (expected 'male' or 'female')", file=sys.stderr)
        return 2

    data = path.read_bytes()
    result = run(data, sex)
    out = result.to_dict()
    # Trim landmark list for readability.
    out["landmarks"] = f"<{len(out['landmarks'])} points>"
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
