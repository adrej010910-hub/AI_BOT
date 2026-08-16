from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

from app.services.auditor import audit_url

app = FastAPI(title="AI Web Lead Agent", version="0.1.0")


class AuditRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/audit")
async def audit(request: AuditRequest):
    return await audit_url(str(request.url))
