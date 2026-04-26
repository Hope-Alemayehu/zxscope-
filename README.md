 # ZXScope — QASM Circuit Optimizer

Paste or upload an OpenQASM 2.0 circuit. The backend runs **pyzx** `full_reduce` (ZX-calculus graph rewriting) and returns:

- Before/after gate count, T-count, and depth with animated metric cards
- The optimized QASM string (copyable)
- A base64-encoded PNG of the reduced ZX graph

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `index.html` in your browser (works over `file://` — CORS is fully open).

## Quick start

1. Click one of the **preset** buttons (Toffoli gate, 3-qubit QFT, Clifford+T adder)
2. Click **⚡ Optimize Circuit** (or press `Ctrl+Enter`)
3. View metric cards, the ZX graph diagram, and the optimized QASM

You can also drag-and-drop or upload any `.qasm` file.

## API

`POST http://localhost:8000/optimize`

```json
{ "qasm": "OPENQASM 2.0;\n..." }
```

Response:

```json
{
  "before": { "gate_count": 15, "t_count": 7, "depth": 10 },
  "after":  { "gate_count":  9, "t_count": 4, "depth":  7 },
  "optimized_qasm": "OPENQASM 2.0;\n...",
  "zx_graph_png": "<base64 PNG or empty string>"
}
```

## Stack

| Layer    | Tech                          |
|----------|-------------------------------|
| Backend  | Python 3.11+, FastAPI, pyzx, matplotlib |
| Frontend | Single `index.html`, vanilla JS, no build step |
| Protocol | JSON over HTTP, CORS open     |
