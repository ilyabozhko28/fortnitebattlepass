# harmony-backend

Two parts:

- **`harmony/`** — the CV + AI script package. No web concerns. The single
  entrypoint is `harmony.pipeline.run(image_bytes, sex)`.
- **`shim/`** — a tiny FastAPI transport (~50 LOC) with a single endpoint,
  `POST /api/analyze`, that calls `pipeline.run` and returns JSON. Stateless,
  no DB, no auth.

## Install

```bash
python -m venv .venv
. .venv/bin/activate            # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the web shim

```bash
uvicorn shim.main:app --reload --port 8000
```

## Run the CLI (no web)

```bash
python -m harmony.cli --image path/to/face.jpg --sex male
```

## Tests

```bash
pytest -q
```

## PyTorch helper models

`harmony/models/cheekbone_net.py` and `harmony/models/hairline_net.py` define
small PyTorch architectures. The pipeline tries to load weights from
`harmony/models/weights/*.pt`; if they're missing, it falls back to OpenCV
heuristics and adds a warning to the response. Run
`python scripts/download_models.py` to attempt to fetch shipped weights (the
script is a no-op by default since weights aren't bundled — see the README in
that script for how to plug in your own).
