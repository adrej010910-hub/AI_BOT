import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from app.services.auditor import audit_url
from app.services.contact_finder import find_public_email
from app.services.outreach import draft_message
from app.services.gemini import discover_businesses, ai_redesign_analysis
from app.services.mailer import send_email
from app.services.suppression import SUPPRESSION
from app.store import create_lead, get_lead, list_leads, update_status

app = FastAPI(title="AI Web Lead Agent", version="0.5.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AuditRequest(BaseModel):
    url: HttpUrl
    business_name: str = Field(default="Unknown Business", min_length=1, max_length=200)
    email: EmailStr | None = None
class StatusRequest(BaseModel):
    status: str
class DiscoverRequest(BaseModel):
    niche: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=5, ge=1, le=8)
    max_score: int = Field(default=65, ge=0, le=100)
class SendRequest(BaseModel):
    confirm: bool = False

@app.get("/api/health")
def health(): return {"status": "ok", "version": "0.5.2"}

async def qualify_candidate(name: str, website: str, email: str | None = None):
    audit_result = await audit_url(website)
    if not audit_result.get("signals", {}).get("reachable", False): return None, audit_result, None
    ai = await ai_redesign_analysis(name, website, audit_result)
    score = int(ai.get("redesign_score", max(0, 100 - audit_result.get("score", 100))))
    public_email = email or await find_public_email(website)
    summary = "; ".join(ai.get("top_problems", audit_result.get("issues", [])))
    return create_lead(name, website, public_email, score, summary), audit_result, ai

@app.post("/api/audit")
async def audit(request: AuditRequest):
    lead, result, ai = await qualify_candidate(request.business_name.strip(), str(request.url), str(request.email) if request.email else None)
    return {"lead": lead.__dict__ if lead else None, "audit": result, "ai": ai, "message": None if lead else "Website could not be audited."}

async def qualify_one(candidate: dict, min_score: int):
    try:
        name = str(candidate.get("business_name") or "").strip()
        website = str(candidate.get("website") or "").strip()
        if not name or not website: return None
        lead, audit_result, ai = await qualify_candidate(name, website)
        if lead and lead.score >= min_score:
            return {"lead": lead.__dict__, "ai": ai, "audit": audit_result, "source": candidate.get("source_url")}
        return None
    except Exception as exc:
        return {"business_name": str(candidate.get("business_name") or "Candidate"), "website": str(candidate.get("website") or ""), "error": str(exc)}

@app.post("/api/discover")
async def discover(request: DiscoverRequest):
    niche = request.niche.strip()
    location = request.location.strip()
    if not niche or not location: raise HTTPException(422, "Niche and location are required")
    try:
        candidates = await discover_businesses(niche, location, request.limit)
    except Exception as exc:
        raise HTTPException(502, f"AI search failed: {exc}") from exc
    results = await asyncio.gather(*(qualify_one(c, request.max_score) for c in candidates))
    results = [r for r in results if r is not None]
    return {"found": len(candidates), "qualified": len([r for r in results if "lead" in r]), "results": results}

@app.get("/api/leads")
def leads(status: str | None = None): return [x.__dict__ for x in list_leads(status)]

@app.post("/api/leads/{lead_id}/draft")
def draft(lead_id: int):
    lead = get_lead(lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    lead.message = draft_message(lead.business_name, lead.website, lead.audit_summary)
    lead.status = "pending_review"
    return lead.__dict__

@app.post("/api/leads/{lead_id}/status")
def status(lead_id: int, request: StatusRequest):
    if request.status not in {"new", "pending_review", "approved", "skipped", "sent"}: raise HTTPException(400, "Invalid status")
    lead = update_status(lead_id, request.status)
    if not lead: raise HTTPException(404, "Lead not found")
    return lead.__dict__

@app.post("/api/leads/{lead_id}/send")
async def send(lead_id: int, request: SendRequest):
    lead = get_lead(lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    if lead.status != "approved": raise HTTPException(409, "Lead must be approved before sending")
    if not lead.email: raise HTTPException(400, "No public email found for this lead")
    if not lead.message: raise HTTPException(400, "Generate the message before sending")
    if SUPPRESSION.contains(lead.email): raise HTTPException(409, "Recipient is suppressed")
    if not request.confirm: raise HTTPException(428, "Explicit send confirmation required")
    result = await send_email(lead.email, f"Website redesign idea for {lead.business_name}", lead.message)
    lead.status = "sent"
    return {"lead": lead.__dict__, "provider": result}

@app.get("/api/dashboard")
def dashboard():
    all_leads = list_leads()
    return {"total": len(all_leads), "new": sum(x.status == "new" for x in all_leads), "pending_review": sum(x.status == "pending_review" for x in all_leads), "approved": sum(x.status == "approved" for x in all_leads), "sent": sum(x.status == "sent" for x in all_leads)}
