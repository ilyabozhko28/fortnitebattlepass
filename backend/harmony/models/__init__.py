"""Small PyTorch helper models with heuristic OpenCV fallbacks.

Pipeline asks :mod:`harmony.models.registry` for an estimator. If pretrained
weights are present in ``weights/``, a PyTorch model is loaded; otherwise the
registry returns a callable that performs a deterministic OpenCV heuristic and
sets ``warning`` on the response.
"""
