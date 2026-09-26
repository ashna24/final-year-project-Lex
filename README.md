# Lex — AI Legal Document Analyser

Lex is a legal document analyser that reads a photo or scan of a contract, breaks it into individual clauses, and
explains each one in plain English — flagging which clauses carry High, Medium, or
Low risk, and why. Explanations can also be shown in Urdu. It's aimed at people
without legal training who need to understand what they're about to sign.

Upload a document → Lex runs OCR, splits it into clauses, classifies each one with a
local LLM, and returns a plain-English (and optionally Urdu) explanation with a risk
rating for every clause.

## How it works

1. Extraction — [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) reads the
   text out of an uploaded image or PDF (PDFs are rendered page by page with
   [PyMuPDF](https://pymupdf.readthedocs.io/) before OCR).
2. Splitting — a rule-based splitter breaks the extracted text into clauses,
   using numbered markers ("1.", "2.") or Article-style headers where present,
   falling back to sentence-boundary splitting otherwise.
3. Classification — each clause is sent to a local [Ollama](https://ollama.com)
   instance running 'llama3.2', which returns a risk level (High/Medium/Low), a
   confidence score, and a plain-English explanation.
4. Translation (optional) — [NLLB-200]
   (https://huggingface.co/facebooknllb-200-distilled-600M) translates explanations into Urdu, either upfront for the whole document or per clause.

Everything runs locally — no document content is sent to any external API.

## Tech stack

| Layer | Stack |
|---|---|
| Backend | Python, FastAPI, PaddleOCR, PyMuPDF, Hugging Face Transformers (NLLB-200), Ollama (llama3.2) |
| Frontend | React 19, TypeScript, Vite |
| Testing | pytest (backend), Vitest + React Testing Library (frontend) |

## Project structure

```
api/                FastAPI app (main.py)
models/
  extraction/       OCR (PaddleOCR + PDF rendering)
  clause_splitter/  Rule-based clause splitting
  analysis/         LLM classification (Ollama)
  translation/      Urdu translation (NLLB-200)
  pipeline/         Wires the above into one pipeline
frontend/           React + Vite app
tests/              Backend test suite (pytest)
archive/            Rejected models kept for comparison (EasyOCR, BART, DeBERTa, Ollama (for translation))
```

## Prerequisites

- Python 3.13
- Node.js 18+
- [Ollama](https://ollama.com), running locally with llama3.2 pulled:
  ```bash
  ollama pull llama3.2
  ollama serve
  ```
  Classification requires Ollama to be reachable at "localhost:11434". /analyze
  will still respond without it, but every clause comes back with
  risk_level: "Error".

PaddleOCR and NLLB-200 download their own model weights automatically on first use
(a few GB total) — the first real request will be slower than subsequent ones.

## Setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run the API server:

```bash
python3 -m uvicorn api.main:app --reload
```

This starts the server at "http://127.0.0.1:8000". "--reload" restarts it
automatically on code changes.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

This starts the dev server at "http://localhost:5173". The backend must also be
running — the frontend calls it directly.

## API reference

- GET /health — returns {"status": "ok"}.
- POST /analyze — multipart upload (file: an image or PDF, up to 20 MB) with an
  optional translate query parameter (true/false, default false). Runs the
  full pipeline and returns a list of per-clause results as JSON.
- POST /translate — JSON body {"text": "..."}. Translates a single string to
  Urdu without touching OCR or classification — used for on-demand, per-clause
  translation in the UI.

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F "file=@models/test_docs/numbered_clean.jpg"

curl -X POST "http://127.0.0.1:8000/analyze?translate=true" \
  -F "file=@models/test_docs/numbered_clean.jpg"

curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "The tenant must pay rent on the first day of each month."}'
```

## Testing

```bash
# Backend (from the project root)
python3 -m pytest

# Frontend (from frontend/)
npm test
```

Some backend tests make real calls to Ollama, PaddleOCR, and NLLB-200 rather than
mocking them, so a full run is slow (several minutes) and requires Ollama to be
running. The frontend suite is fully mocked and runs in a couple of seconds.

## Known limitations

- Performance is memory-dependent. PaddleOCR, NLLB-200, and Ollama's llama3.2 are
  all loaded at different stages of a request rather than held in memory
  simultaneously, and each model is explicitly unloaded after use — but on a
  memory-constrained machine (eg 8 GB RAM), a full analysis can still range from
  roughly 60-90 seconds under normal conditions to considerably longer under memory
  pressure. This is a hardware constraint.
- OCR accuracy depends on scan quality. Blurry, low-resolution, or heavily degraded
  scans can produce incomplete or inaccurate extracted text — the UI surfaces a
  warning about this while a document is being read, and results should be checked
  against the original document.
- This is not legal advice. Lex is an AI-generated analysis tool, not a substitute
  for a qualified lawyer — this is stated directly in the app.
