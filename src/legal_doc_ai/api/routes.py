from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from legal_doc_ai.api.auth import require_api_key
from legal_doc_ai.api.response import APP_VERSION, api_response
from legal_doc_ai.config import get_settings
from legal_doc_ai.core.pipeline import DocumentPipeline
from legal_doc_ai.core.schemas import (
    AnalyzeRequest,
    AuditEvent,
    ExtractRequest,
    QARequest,
    RetrievedChunk,
    RetrieveRequest,
)
from legal_doc_ai.db import get_db, test_db_connection
from legal_doc_ai.services.analyzer import DocumentAnalyzer
from legal_doc_ai.services.audit import AuditService
from legal_doc_ai.services.entities import LegalEntityExtractor
from legal_doc_ai.services.ocr import ExtractionError
from legal_doc_ai.services.qa import QAGenerator
from legal_doc_ai.services.vector_store import InMemoryVectorStore, PGVectorStore

router = APIRouter()
settings = get_settings()
memory_store = InMemoryVectorStore()
extractor = LegalEntityExtractor()
analyzer = DocumentAnalyzer()
audit = AuditService(max_items=1000)


def _resolve_store(db: Session):
    if settings.retriever_backend == "pgvector" and test_db_connection():
        return PGVectorStore(db)
    return memory_store


@router.get("/health")
def health() -> dict:
    db_ok = test_db_connection() if settings.retriever_backend == "pgvector" else False
    return api_response(
        data={
            "service": settings.app_name,
            "retriever_backend": settings.retriever_backend,
            "db_connected": db_ok,
            "classifier_mode": settings.classifier_mode,
            "auth_enabled": bool(settings.api_key),
        }
    )


@router.get("/version")
def version() -> dict:
    return api_response(data={"service": settings.app_name, "version": APP_VERSION})


@router.post("/v1/ingest", dependencies=[Depends(require_api_key)])
async def ingest_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    suffix = Path(file.filename).suffix if file.filename else ".bin"

    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        if not content:
            audit.log("ingest", "error", {"reason": "empty_file"})
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        tmp.write(content)
        temp_path = Path(tmp.name)

    try:
        store = _resolve_store(db)
        pipeline = DocumentPipeline(store=store)
        result = pipeline.ingest(temp_path)
        audit.log(
            "ingest",
            "ok",
            {
                "filename": file.filename or temp_path.name,
                "classification": result.get("classification"),
                "chunk_count": result.get("chunk_count"),
            },
        )
        return api_response(data=result)
    except ExtractionError as exc:
        audit.log("ingest", "error", {"reason": "extraction_failed"})
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/v1/retrieve", dependencies=[Depends(require_api_key)])
def retrieve(
    req: RetrieveRequest,
    db: Session = Depends(get_db),
) -> dict:
    store = _resolve_store(db)
    hits = store.search(query=req.query, top_k=req.top_k)
    audit.log(
        "retrieve",
        "ok",
        {"query": req.query[:120], "top_k": req.top_k, "result_count": len(hits)},
    )
    result = {
        "query": req.query,
        "results": [
            RetrievedChunk(
                chunk_id=item.chunk_id,
                score=float(item.score),
                text=item.text,
                metadata=item.metadata,
            ).model_dump()
            for item in hits
        ],
    }
    return api_response(data=result)


@router.post("/v1/extract", dependencies=[Depends(require_api_key)])
def extract_entities(req: ExtractRequest) -> dict:
    entities = extractor.extract(req.text)
    audit.log("extract", "ok", {"text_len": len(req.text)})
    return api_response(data={"entities": entities})


@router.post("/v1/analyze", dependencies=[Depends(require_api_key)])
def analyze_text(req: AnalyzeRequest) -> dict:
    out = analyzer.analyze(req.text)
    audit.log(
        "analyze",
        "ok",
        {"classification": out.get("classification"), "risk_flags": len(out.get("risk_flags", []))},
    )
    return api_response(data=out)


@router.post("/v1/qa", dependencies=[Depends(require_api_key)])
def answer_question(
    req: QARequest,
    db: Session = Depends(get_db),
) -> dict:
    store = _resolve_store(db)
    qa = QAGenerator(store)
    out = qa.answer(req.question, top_k=req.top_k)
    audit.log("qa", "ok", {"question": req.question[:120], "citations": len(out.get("citations", []))})
    return api_response(data=out)


@router.get("/v1/audit", dependencies=[Depends(require_api_key)])
def get_audit(limit: int = 50) -> dict:
    events = [AuditEvent(**e).model_dump() for e in audit.list_events(limit=limit)]
    return api_response(data={"events": events})
