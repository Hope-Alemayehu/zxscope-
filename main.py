import pyzx as zx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="ZXScope", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class OptimizeRequest(BaseModel):
    qasm: str


class Metrics(BaseModel):
    gate_count: int
    t_count: int
    depth: int


class OptimizeResponse(BaseModel):
    before: Metrics
    after: Metrics
    optimized_qasm: str
    before_graph: dict   # {nodes: [...], edges: [...]}
    after_graph: dict
    error: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_T_NAMES = {"T", "Tdg", "T†", "T_Conj", "Tdag"}


def _t_count(circuit) -> int:
    return sum(1 for g in circuit.gates if type(g).__name__ in _T_NAMES)


def _gate_depth(circuit) -> int:
    times: list[int] = [0] * circuit.qubits
    for g in circuit.gates:
        targets = [g.target]
        if hasattr(g, "control"):
            targets.append(g.control)
        if hasattr(g, "control2"):
            targets.append(g.control2)
        t = max(times[q] for q in targets) + 1
        for q in targets:
            times[q] = t
    return max(times) if times else 0


def _metrics(circuit) -> Metrics:
    return Metrics(
        gate_count=len(circuit.gates),
        t_count=_t_count(circuit),
        depth=_gate_depth(circuit),
    )


def _graph_to_dict(g) -> dict:
    nodes = []
    for v in g.vertices():
        try:
            row = float(g.row(v))
            qubit = float(g.qubit(v))
        except Exception:
            row, qubit = 0.0, 0.0
        nodes.append({
            "id": v,
            "type": int(g.type(v)),
            "phase": str(g.phase(v)),
            "row": row,
            "qubit": qubit,
        })
    edges = []
    for e in g.edges():
        s, t = g.edge_st(e)
        edges.append({
            "src": s,
            "tgt": t,
            "type": int(g.edge_type(e)),
        })
    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@app.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest):
    try:
        circuit = zx.Circuit.from_qasm(req.qasm)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"QASM parse error: {exc}")

    before = _metrics(circuit)

    g = circuit.to_graph()
    before_graph = _graph_to_dict(g)   # snapshot before reduction

    zx.full_reduce(g)
    after_graph = _graph_to_dict(g)    # snapshot after reduction

    try:
        c_opt = zx.extract_circuit(g).to_basic_gates()
    except Exception:
        try:
            c_opt = zx.Circuit.from_graph(g).to_basic_gates()
        except Exception:
            c_opt = circuit

    after = _metrics(c_opt)

    return OptimizeResponse(
        before=before,
        after=after,
        optimized_qasm=c_opt.to_qasm(),
        before_graph=before_graph,
        after_graph=after_graph,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
