#This file serves as the API layer.

import io
import logging
import tempfile
from pathlib import Path

import pymupdf
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from models.pipeline.run_pipeline import process_document
from models.translation.model4_nllb import translate_to_urdu, unload_translator

logger = logging.getLogger("lex.api")

app = FastAPI(title="Lex API")

# Allows the local Vite dev server to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class TranslateRequest(BaseModel):
    text: str | None = None


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

    suffix = Path(file.filename).suffix or ".jpg"
    is_pdf = suffix.lower() == ".pdf" or file.content_type == "application/pdf"

    if is_pdf:
        # This check verifies it's a readable PDF before handing it to the pipeline.
        try:
            with pymupdf.open(stream=contents, filetype="pdf") as document:
                if document.page_count == 0:
                    raise ValueError("PDF has no pages")
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")
        # The pipeline picks its path from the file extension so force .pdf here
        suffix = ".pdf"
    else:
        # will verify this is actually a readable image before handing it to the pipeline
        try:
            Image.open(io.BytesIO(contents)).verify()
        except (UnidentifiedImageError, OSError):
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(contents)
        tmp.flush()

        try:
            results = process_document(tmp.name, translate=translate)
        except Exception:
            logger.exception("process_document failed for uploaded file %s", file.filename)
            raise HTTPException(status_code=500, detail="An internal error occurred while processing the document")

    return results


@app.post("/translate")
def translate_text(request: TranslateRequest):
    if request.text is None:
        raise HTTPException(status_code=400, detail="No text provided")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text field is empty")

    try:
        translation = translate_to_urdu(request.text)
    except Exception:
        logger.exception("translate_to_urdu failed for a /translate request")
        raise HTTPException(status_code=500, detail="An internal error occurred while translating the text")
    finally:
        # Frees NLLB after every call so it never sits in memory next to PaddleOCR
        unload_translator()

    return {"translation": translation}
