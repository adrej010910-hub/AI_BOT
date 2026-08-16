import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from app.services.auditor import audit_url
from app.services.outreach import draft_message
from app.services.gemini import discover_businesses, ai_redesign_analysis
from app.store import create_lead, get_lead, list_leads, update_status

app = FastAPI(title="AI Web Lead Agent", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AuditRequest(BaseModel):
    url: HttpUrl
    business_name: str = "Unknown Business"
    email: str | None = None
class StatusRequest(BaseModel):
    status: str
class DiscoverRequest(BaseModel):
    niche: str
    location: str
    limit: int = 10
    max_score: int = 65

@app.get("/api/health")
def health(): return {"status":"ok","version":"0.4.0"}

@app.post("/api/audit")
async def audit(request: AuditRequest):
    result = await audit_url(str(request.url))
    ai = await ai_redesign_analysis(request.business_name, str(request.url), result)
    score = int(ai.get("redesign_score", result.get("score", 0)))
    summary = "; ".join(ai.get("top_problems", result.get("issues", [])))
    lead = create_lead(request.business_name, str(request.url), request.email, score, summary)
    return {"lead": lead.__dict__, "audit": result, "ai": ai}

@app.post("/api/discover")
async def discover(request: DiscoverRequest):
    limit = max(1, min(request.limit, 25))
    candidates = await discover_businesses(request.niche, request.location, limit)
    results = []
    for candidate in candidates:
        try:
            audit_result = await audit_url(candidate["website"])
            ai = await ai_redesign_analysis(candidate["business_name"], candidate["website"], audit_result)
            score = int(ai.get("redesign_score", audit_result.get("score", 0)))
            if score <= request.max_score:
                lead = create_lead(candidate["business_name"], candidate["website"], None, score, "; ".join(ai.get("top_problems", audit_result.get("issues", []))))
                results.append({"lead": lead.__dict__, "ai": ai, "source": candidate.get("source_url")})
        except Exception as exc:
            results.append({"business_name": candidate.get("business_name"), "website": candidate.get("website"), "error": str(exc)})
        await asyncio.sleep(0.2)
    return {"found": len(candidates), "qualified": len([r for r in results if "lead" in r]), "results": results}

@app.get("/api/leads")
def leads(status: str | None = None): return [x.__dict__ for x in list_leads(status)]
@app.post("/api/leads/{lead_id}/draft")
def draft(lead_id: int):
    lead=get_lead(lead_id)
    if not lead: raise HTTPException(404,"Lead not found")
    lead.message=draft_message(lead.business_name,lead.website,lead.audit_summary); lead.status="pending_review"
    return lead.__dict__
@app.post("/api/leads/{lead_id}/status")
def status(lead_id: int, request: StatusRequest):
    if request.status not in {"new","pending_review","approved","skipped","sent"}: raise HTTPException(400,"Invalid status")
    lead=update_status(lead_id,request.status)
    if not lead: raise HTTPException(404,"Lead not found")
    return lead.__dict__
@app.get("/api/dashboard")
def dashboard():
    all_leads=list_leads()
    return {"total":len(all_leads),"new":sum(x.status=="new" for x in all_leads),"pending_review":sum(x.status=="pending_review" for x in all_leads),"approved":sum(x.status=="approved" for x in all_leads),"sent":sum(x.status=="sent" for x in all_leads)}
