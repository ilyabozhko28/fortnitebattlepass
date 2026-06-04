"""End-to-end pipeline test.

Most of the pipeline depends on MediaPipe + OpenCV which can't run on a
no-face fixture, so the actual ``run`` call is exercised in the smoke test
script. Here we just verify the import surface and that decoding fails
gracefully on empty bytes.
"""

import pytest

from harmony.pipeline import PipelineError, run


def test_run_empty_bytes_raises():
    with pytest.raises(PipelineError):
        run(b"", "male")


def test_run_invalid_sex_raises():
    with pytest.raises(PipelineError):
        run(b"garbage", "alien")  # type: ignore[arg-type]


def test_run_invalid_image_raises():
    with pytest.raises(PipelineError):
        run(b"this is not an image", "male")
