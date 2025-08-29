# Echo Agent Hub v0.4 — File Connector (alpha1)

**What's new**
- Streaming file ingestion with sentence-boundary chunking
- Size validation and env-tunable limits
- CSV/TSV and PDF (text-based) supported; TXT/MD supported
- No OCR (planned v0.5)

## Limits (env)
- FILE_MAX_BYTES=26214400 (25MB)
- PDF_MAX_PAGES=300
- CSV_MAX_ROWS=100000
- CHUNK_MAX_BYTES=8192
- CHUNK_OVERLAP=768
- CHUNK_BOUNDARY_WINDOW=200
- MAX_CHUNKS=500

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8014
```
