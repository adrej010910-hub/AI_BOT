from typing import Dict, List
from .models import Lead

_leads: Dict[int, Lead] = {}
_next_id = 1


def create_lead(business_name: str, website: str, email: str | None = None, score: int = 0, audit_summary: str = "") -> Lead:
    global _next_id
    normalized = website.lower().rstrip("/")
    for existing in _leads.values():
        if existing.website.lower().rstrip("/") == normalized:
            if email and not existing.email:
                existing.email = email
            if audit_summary:
                existing.audit_summary = audit_summary
            existing.score = score
            return existing
    lead = Lead(id=_next_id, business_name=business_name, website=website, email=email, score=score, audit_summary=audit_summary)
    _leads[_next_id] = lead
    _next_id += 1
    return lead


def list_leads(status: str | None = None) -> List[Lead]:
    values = list(_leads.values())
    return [x for x in values if status is None or x.status == status]


def get_lead(lead_id: int) -> Lead | None:
    return _leads.get(lead_id)


def update_status(lead_id: int, status: str) -> Lead | None:
    lead = get_lead(lead_id)
    if lead:
        lead.status = status
    return lead
