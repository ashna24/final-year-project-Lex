#This file serves as the API layer.

import io
import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from models.pipeline.run_pipeline import process_document

logger = logging.getLogger("lex.api")

app = FastAPI(title="Lex API")

# Allows the local Vite dev server to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile | None = None, translate: bool = False):
    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # will verify this is actually a readable image before handing it to the pipeline
    try:
        Image.open(io.BytesIO(contents)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    suffix = Path(file.filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(contents)
        tmp.flush()

        try:
            results = process_document(tmp.name, translate=translate)
        except Exception:
            logger.exception("process_document failed for uploaded file %s", file.filename)
            raise HTTPException(status_code=500, detail="An internal error occurred while processing the document")

    return results
