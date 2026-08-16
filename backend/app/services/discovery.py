from dataclasses import dataclass

@dataclass
class DiscoveryConfig:
    niche: str
    location: str
    limit: int = 20
    max_score: int = 60


def build_search_queries(config: DiscoveryConfig) -> list[str]:
    niche = str(config.niche or "").strip()
    location = str(config.location or "").strip()
    if not niche or not location:
        return []
    base = f"{niche} {location} website"
    return [base, f"{niche} in {location} official website"]


def normalize_candidate(name: str | None, website: str | None) -> dict | None:
    business_name = str(name or "").strip()
    site = str(website or "").strip()
    if not business_name or not site:
        return None
    return {"business_name": business_name, "website": site, "source": "public_search"}
