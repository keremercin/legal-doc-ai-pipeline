from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from legal_doc_ai.api.auth import require_api_key
from legal_doc_ai.config import get_settings
from legal_doc_ai.core.pipeline import DocumentPipeline
from legal_doc_ai.core.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AuditEvent,
    AuditListResponse,
    ExtractRequest,
    ExtractResponse,
    HealthResponse,
    IngestResponse,
    QARequest,
    QAResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrievedChunk,
)
from legal_doc_ai.db import get_db, test_db_connection
from legal_doc_ai.services.analyzer import DocumentAnalyzer
from legal_doc_ai.services.audit import AuditService
from legal_doc_ai.services.entities import LegalEntityExtractor
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


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_ok = test_db_connection()
    return HealthResponse(
        service=settings.app_name,
        metadata={
            "retriever_backend": settings.retriever_backend,
            "db_connected": db_ok,
            "classifier_mode": settings.classifier_mode,
            "auth_enabled": bool(settings.api_key),
        },
    )


@router.post("/v1/ingest", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
async def ingest_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IngestResponse:
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
        return IngestResponse(**result)
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/v1/retrieve", response_model=RetrieveResponse, dependencies=[Depends(require_api_key)])
def retrieve(
    req: RetrieveRequest,
    db: Session = Depends(get_db),
) -> RetrieveResponse:
    store = _resolve_store(db)
    hits = store.search(query=req.query, top_k=req.top_k)
    audit.log(
        "retrieve",
        "ok",
        {"query": req.query[:120], "top_k": req.top_k, "result_count": len(hits)},
    )
    return RetrieveResponse(
        query=req.query,
        results=[
            RetrievedChunk(
                chunk_id=item.chunk_id,
                score=float(item.score),
                text=item.text,
                metadata=item.metadata,
            )
            for item in hits
        ],
    )


@router.post("/v1/extract", response_model=ExtractResponse, dependencies=[Depends(require_api_key)])
def extract_entities(req: ExtractRequest) -> ExtractResponse:
    entities = extractor.extract(req.text)
    audit.log("extract", "ok", {"text_len": len(req.text)})
    return ExtractResponse(entities=entities)


@router.post("/v1/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_api_key)])
def analyze_text(req: AnalyzeRequest) -> AnalyzeResponse:
    out = analyzer.analyze(req.text)
    audit.log(
        "analyze",
        "ok",
        {"classification": out.get("classification"), "risk_flags": len(out.get("risk_flags", []))},
    )
    return AnalyzeResponse(**out)


@router.post("/v1/qa", response_model=QAResponse, dependencies=[Depends(require_api_key)])
def answer_question(
    req: QARequest,
    db: Session = Depends(get_db),
) -> QAResponse:
    store = _resolve_store(db)
    qa = QAGenerator(store)
    out = qa.answer(req.question, top_k=req.top_k)
    audit.log("qa", "ok", {"question": req.question[:120], "citations": len(out.get("citations", []))})
    return QAResponse(**out)


@router.get("/v1/audit", response_model=AuditListResponse, dependencies=[Depends(require_api_key)])
def get_audit(limit: int = 50) -> AuditListResponse:
    events = [AuditEvent(**e) for e in audit.list_events(limit=limit)]
    return AuditListResponse(events=events)
