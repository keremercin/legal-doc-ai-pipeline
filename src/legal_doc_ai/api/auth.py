from fastapi import Header, HTTPException

from legal_doc_ai.config import get_settings

settings = get_settings()


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Optional API key auth.

    If API_KEY is set in env, all protected endpoints require `X-API-Key`.
    If unset, auth is bypassed for local dev convenience.
    """
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
