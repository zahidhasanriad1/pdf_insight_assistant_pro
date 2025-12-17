from __future__ import annotations
from app.postprocess import clean_repetition
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import load_config
from app.logging_conf import setup_logging
from app.utils import new_doc_id, safe_filename, ensure_dir
from app.ingestion import load_and_split_pdf
from app.vectorstore import build_faiss_index, load_faiss_index
from app.rag_chain import build_rag_chain, format_context, docs_to_sources, RAGSettings
from app.schemas import UploadResponse, AskRequest, AskResponse
from app.storage import write_manifest, read_manifest

cfg = load_config()
logger = setup_logging()

ensure_dir(cfg.upload_dir)
ensure_dir(cfg.index_dir)

app = FastAPI(title="PDF Insight Assistant Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = build_rag_chain(
    RAGSettings(
        model=cfg.default_model,
        fallback_model=cfg.fallback_model,
        prompt_version="v2",
        temperature=0.0,
    )
)

@app.get("/")
def root():
    return {"message": "PDF Insight Assistant Pro running. Open /docs for Swagger UI."}

@app.get("/health")
def health():
    return {"status": "ok", "env": cfg.app_env}

@app.get("/documents")
def list_documents():
    docs = []
    for p in cfg.index_dir.glob("*"):
        if p.is_dir():
            m = read_manifest(p)
            if m:
                docs.append(m)

    docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"docs": docs}

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    max_bytes = cfg.max_upload_mb * 1024 * 1024
    raw = await file.read()
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {cfg.max_upload_mb} MB"
        )

    doc_id = new_doc_id()
    clean_name = safe_filename(file.filename)
    pdf_path = cfg.upload_dir / f"{doc_id}_{clean_name}"

    with open(pdf_path, "wb") as f:
        f.write(raw)

    t0 = time.time()
    docs = load_and_split_pdf(pdf_path)
    index_path = cfg.index_dir / doc_id
    build_faiss_index(docs, index_path)

    manifest = {
        "doc_id": doc_id,
        "filename": clean_name,
        "stored_path": str(pdf_path),
        "chunks": len(docs),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "index_path": str(index_path),
        "ingest_seconds": round(time.time() - t0, 3),
    }
    write_manifest(index_path, manifest)

    logger.info(f"Upload indexed | doc_id={doc_id} chunks={len(docs)}")
    return UploadResponse(status="ok", doc_id=doc_id, filename=clean_name, chunks=len(docs))

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    index_path = cfg.index_dir / req.doc_id
    if not index_path.exists():
        raise HTTPException(status_code=400, detail="Unknown doc_id. Upload a PDF first.")

    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    if req.top_k < 1 or req.top_k > 12:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 12")

    lang = (getattr(req, "language", "bn") or "bn").strip().lower()
    if lang not in {"bn", "en"}:
        raise HTTPException(status_code=400, detail="language must be bn or en")

    reply_language_instruction = "Bengali using Bengali script" if lang == "bn" else "English"

    vs = load_faiss_index(index_path)
    retriever = vs.as_retriever(search_kwargs={"k": req.top_k})

    docs = await retriever.ainvoke(req.question.strip())
    context = format_context(docs)
    session_key = f"{req.doc_id}::{req.session_id}"

    answer = rag.invoke(
        {
            "context": context,
            "question": req.question.strip(),
            "reply_language_instruction": reply_language_instruction,
        },
        config={"configurable": {"session_id": session_key}},
    )
    answer = clean_repetition(answer)


    sources = docs_to_sources(docs)
    return AskResponse(answer=answer, sources=sources)
