"""Local development entry point.

Serves index.html at "/" alongside the API routes so `uvicorn main:app`
runs the full app. On Vercel, api/index.py is deployed as the function
and index.html is served as a static file.
"""
from pathlib import Path

from fastapi.responses import FileResponse

from api.index import app

_INDEX = Path(__file__).parent / "index.html"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(_INDEX)
