from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    classification: str
    chunk_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrieveResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)


class ExtractResponse(BaseModel):
    entities: dict[str, Any] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalyzeResponse(BaseModel):
    classification: str
    summary: str
    entities: dict[str, Any] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)


class QARequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def meaningful_question(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Question must contain at least three non-whitespace characters")
        return value


class QAResponse(BaseModel):
    question: str
    answer: str
    citations: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    timestamp: str
    action: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditListResponse(BaseModel):
    events: list[AuditEvent] = Field(default_factory=list)
