from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from app.services.auditor import audit_url
from app.services.outreach import draft_message
from app.store import create_lead, get_lead, list_leads, update_status

app = FastAPI(title="AI Web Lead Agent", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AuditRequest(BaseModel):
    url: HttpUrl
    business_name: str = "Unknown Business"
    email: str | None = None

class StatusRequest(BaseModel):
    status: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/audit")
async def audit(request: AuditRequest):
    result = await audit_url(str(request.url))
    lead = create_lead(request.business_name, str(request.url), request.email, result.get("score", 0), "; ".join(result.get("issues", [])))
    return {"lead": lead.__dict__, "audit": result}

@app.get("/api/leads")
def leads(status: str | None = None):
    return [x.__dict__ for x in list_leads(status)]

@app.post("/api/leads/{lead_id}/draft")
def draft(lead_id: int):
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.message = draft_message(lead.business_name, lead.website, lead.audit_summary)
    lead.status = "pending_review"
    return lead.__dict__

@app.post("/api/leads/{lead_id}/status")
def status(lead_id: int, request: StatusRequest):
    if request.status not in {"new", "pending_review", "approved", "skipped", "sent"}:
        raise HTTPException(400, "Invalid status")
    lead = update_status(lead_id, request.status)
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead.__dict__

@app.get("/api/dashboard")
def dashboard():
    all_leads = list_leads()
    return {
        "total": len(all_leads),
        "new": sum(x.status == "new" for x in all_leads),
        "pending_review": sum(x.status == "pending_review" for x in all_leads),
        "approved": sum(x.status == "approved" for x in all_leads),
        "sent": sum(x.status == "sent" for x in all_leads),
    }
