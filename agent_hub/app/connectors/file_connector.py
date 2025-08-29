import os, io, csv, filetype
from typing import Dict, Any, List

# Env limits
FILE_MAX_BYTES = int(os.getenv("FILE_MAX_BYTES", str(25*1024*1024)))
PDF_MAX_PAGES  = int(os.getenv("PDF_MAX_PAGES", "300"))
CSV_MAX_ROWS   = int(os.getenv("CSV_MAX_ROWS", "100000"))
CHUNK_MAX_BYTES = int(os.getenv("CHUNK_MAX_BYTES", "8192"))
CHUNK_OVERLAP   = int(os.getenv("CHUNK_OVERLAP", "768"))
BOUNDARY_WINDOW = int(os.getenv("CHUNK_BOUNDARY_WINDOW", "200"))
MAX_CHUNKS      = int(os.getenv("MAX_CHUNKS", "500"))

SENT_END = {'.','?','!'}  # naive sentence enders

def _boundary_cut(buf: str) -> int:
    """Find a good cut point <= CHUNK_MAX_BYTES using sentence/whitespace near the end.
    Returns index (exclusive)."""
    n = len(buf)
    if n <= CHUNK_MAX_BYTES:
        return n
    j = CHUNK_MAX_BYTES
    # look backward within boundary window for sentence end
    start = max(0, j-BOUNDARY_WINDOW)
    segment = buf[start:j]
    for k in range(len(segment)-1, -1, -1):
        if segment[k] in SENT_END:
            return start + k + 1
    # fallback: last whitespace
    for k in range(len(segment)-1, -1, -1):
        if segment[k].isspace():
            return start + k + 1
    # fallback: hard cut
    return j

def _append_and_flush_chunks(acc: List[str], buf: str) -> str:
    """Append as many chunks as possible from buf; return remaining tail."""
    while len(buf) > CHUNK_MAX_BYTES and len(acc) < MAX_CHUNKS:
        cut = _boundary_cut(buf[:CHUNK_MAX_BYTES+BOUNDARY_WINDOW])
        acc.append(buf[:cut])
        # ensure overlap
        tail_start = max(cut - CHUNK_OVERLAP, 0)
        buf = buf[tail_start:]
    return buf

def _finalize(acc: List[str], buf: str):
    if buf and len(acc) < MAX_CHUNKS:
        acc.append(buf)

def _chunk_stream_text(text_iter, meta: Dict[str, Any]) -> Dict[str, Any]:
    chunks: List[str] = []
    buf = ""
    for piece in text_iter:
        if not piece:
            continue
        buf += piece
        buf = _append_and_flush_chunks(chunks, buf)
        if len(chunks) >= MAX_CHUNKS:
            return {"status":"partial","chunks":chunks,"meta":meta | {"max_chunks":MAX_CHUNKS}}
    _finalize(chunks, buf)
    return {"status":"ok","chunks":chunks,"meta":meta}

def _iter_pdf_text(path: str, max_pages: int):
    from PyPDF2 import PdfReader
    reader = PdfReader(path)
    for i, page in enumerate(reader.pages):
        if i >= max_pages: break
        try:
            yield (page.extract_text() or "") + "\n"
        except Exception:
            yield "\n"

def _read_pdf(path: str, opts: dict) -> Dict[str, Any]:
    max_pages = min(int(opts.get("max_pages", PDF_MAX_PAGES)), PDF_MAX_PAGES)
    meta = {"type":"pdf","max_pages":max_pages}
    return _chunk_stream_text(_iter_pdf_text(path, max_pages), meta)

def _read_txt(path: str, opts: dict) -> Dict[str, Any]:
    meta = {"type":"text"}
    def _iter():
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            while True:
                piece = f.read(8192)
                if not piece: break
                yield piece
    return _chunk_stream_text(_iter(), meta)

def _read_csv(path: str, opts: dict) -> Dict[str, Any]:
    max_rows = min(int(opts.get("max_rows", CSV_MAX_ROWS)), CSV_MAX_ROWS)
    meta = {"type":"csv","max_rows":max_rows}
    def _iter():
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= max_rows: break
                # turn row into delimited text line
                yield ",".join(str(c) for c in row) + "\n"
    return _chunk_stream_text(_iter(), meta)

def mcp_file(payload: dict) -> dict:
    path = payload.get("path")
    if not path or not os.path.exists(path):
        return {"status":"error","error":"MISSING_OR_BAD_PATH"}
    size = os.path.getsize(path)
    if size > FILE_MAX_BYTES:
        return {"status":"error","error":"FILE_TOO_LARGE","detail":{"size":size,"limit":FILE_MAX_BYTES}}

    kind = filetype.guess(path)
    ext = ("." + kind.extension) if kind else os.path.splitext(path)[1].lower()

    opts = payload.get("options", {})
    if ext in [".txt",".md"]:
        return _read_txt(path, opts)
    if ext in [".csv",".tsv"]:
        return _read_csv(path, opts)
    if ext == ".pdf":
        return _read_pdf(path, opts)
    return {"status":"error","error":f"UNSUPPORTED_TYPE:{ext}"}
