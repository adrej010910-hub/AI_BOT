from dataclasses import dataclass
from urllib.parse import quote_plus

@dataclass
class DiscoveryConfig:
    niche: str
    location: str
    limit: int = 20
    max_score: int = 60


def build_search_queries(config: DiscoveryConfig) -> list[str]:
    # Search-provider adapters can consume these queries. We intentionally do not
    # scrape private data or bypass access controls.
    base = f"{config.niche} {config.location} website"
    return [base, f"{config.niche} in {config.location} official website"]


def normalize_candidate(name: str, website: str) -> dict:
    return {"business_name": name.strip(), "website": website.strip(), "source": "public_search"}
