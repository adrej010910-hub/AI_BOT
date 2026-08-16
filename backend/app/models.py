from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Lead:
    id: int
    business_name: str
    website: str
    email: Optional[str] = None
    score: int = 0
    status: str = "new"
    audit_summary: str = ""
    message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditResult:
    url: str
    score: int
    issues: list[str]
    positives: list[str]
    mobile: bool
    https: bool
