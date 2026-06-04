"""Run the pipeline from the terminal — proves the package works without a web shim.

Usage::

    python -m harmony.cli --image path/to/face.jpg --sex male
    python -m harmony.cli -i face.jpg -s female --indent 2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import PipelineError, run


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="harmony",
        description="Frontal Harmony — run the CV + AI pipeline on a single image.",
    )
    p.add_argument("-i", "--image", required=True, type=Path, help="Path to a frontal photo.")
    p.add_argument(
        "-s",
        "--sex",
        required=True,
        choices=["male", "female"],
        help="Sex (drives tier ranges).",
    )
    p.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default: 2). Use 0 for compact.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        data = args.image.read_bytes()
    except OSError as exc:
        print(f"error: could not read image: {exc}", file=sys.stderr)
        return 2

    try:
        result = run(data, args.sex)
    except PipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    indent = args.indent if args.indent > 0 else None
    json.dump(result.to_dict(), sys.stdout, indent=indent, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
