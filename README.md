 # ZXScope — QASM Circuit Optimizer

Paste or upload an OpenQASM 2.0 circuit. The backend runs **pyzx** `full_reduce` (ZX-calculus graph rewriting) and returns:

- Before/after gate count, T-count, and depth with animated metric cards
- The optimized QASM string (copyable)
- Node/edge data for the ZX graph before and after reduction

## Setup (local)

```bash
pip install -r requirements.txt uvicorn
uvicorn main:app --reload
```

Then open <http://localhost:8000>. The root `main.py` is for local development only: it serves `index.html` at `/` and mounts the same API routes that Vercel runs, so the page and backend share one origin.

## Deployment

Everything runs on a single Vercel project:

- `index.html` is served as a static file.
- `api/index.py` (the FastAPI app) is deployed as a Python serverless function. `vercel.json` rewrites `/api/*` to it and allows up to 60 s per request.
- `requirements.txt` holds the function's dependencies (FastAPI, pyzx). Keep it small so the function stays under Vercel's 250 MB limit.

Push to `main` and Vercel redeploys. No separate backend host is needed.

## Quick start

1. Click one of the **preset** buttons (Toffoli gate, 3-qubit QFT, Clifford+T adder)
2. Click **⚡ Optimize Circuit** (or press `Ctrl+Enter`)
3. View metric cards, the ZX graph diagram, and the optimized QASM

You can also drag-and-drop or upload any `.qasm` file.

## API

`POST /api/optimize`

```json
{ "qasm": "OPENQASM 2.0;
..." }
```

Response:

```json
{
  "before": { "gate_count": 15, "t_count": 7, "depth": 10 },
  "after":  { "gate_count":  9, "t_count": 4, "depth":  7 },
  "optimized_qasm": "OPENQASM 2.0;
...",
  "before_graph": { "nodes": [...], "edges": [...] },
  "after_graph":  { "nodes": [...], "edges": [...] }
}
```

Invalid QASM returns `400` with a `detail` message.

`GET /api/health` returns `{ "status": "ok" }`.

## Stack

| Layer    | Tech                          |
|----------|-------------------------------|
| Backend  | Python 3.11+, FastAPI, pyzx (Vercel serverless function) |
| Frontend | Single `index.html`, vanilla JS, no build step |
| Protocol | JSON over HTTP, same origin (`/api`) |
