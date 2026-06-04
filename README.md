# Frontal Harmony

Web product that measures the **Frontal Harmony Score** of a face from a frontal photo.

The backend is a pure CV + AI script package (PyTorch + MediaPipe + OpenCV) plus a
minimal FastAPI shim whose only job is to transport bytes between the React /
TypeScript / Tailwind frontend and the scripts.

Everything is **stateless and ephemeral**:

- no database, no Redis, no message queue,
- no filesystem writes for user data — image bytes live only in the request
  handler's local scope,
- no authentication, no user accounts, no sessions,
- no history endpoint — there is no way to retrieve a previous analysis.

## Repository layout

```
ishakkkk/
├── frontend/    React + TS + Vite + Tailwind SPA
├── backend/     CV + AI script package (`harmony/`) + thin FastAPI shim (`shim/`)
├── docs/        Scoring spec and pipeline architecture
└── docker-compose.yml
```

## Quick start

### Option A — Docker (one command)

```bash
docker compose up --build
```

- Frontend → http://localhost:5173
- Shim API → http://localhost:8000/api/analyze

### Option B — Local

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn shim.main:app --reload --port 8000

# Frontend (in another shell)
cd frontend
npm install
npm run dev
```

### Option C — CLI (no web)

```bash
cd backend
python -m harmony.cli --image path/to/face.jpg --sex male
```

Prints the analysis JSON to stdout.

## How the score works

Each of 20 metrics is measured from the photo, classified into a tier
(sex-aware), and mapped to points via the table in
[`docs/scoring_spec.md`](docs/scoring_spec.md). Final score is

```
score = sum(points across all metrics) / 275
```

See [`docs/pipeline.md`](docs/pipeline.md) for the full CV pipeline.
