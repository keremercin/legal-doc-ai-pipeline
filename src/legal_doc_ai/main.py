from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request

from legal_doc_ai.api.routes import router
from legal_doc_ai.config import get_settings
from legal_doc_ai.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.retriever_backend == "pgvector":
        init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.4.0", lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response
