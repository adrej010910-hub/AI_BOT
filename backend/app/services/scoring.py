from dataclasses import dataclass

@dataclass
class ScoreInput:
    https: bool
    mobile: bool
    has_title: bool
    has_h1: bool
    has_cta: bool
    image_alt_ratio: float
    load_time_ms: int | None = None


def score_site(x: ScoreInput) -> tuple[int, list[str]]:
    score = 100
    issues: list[str] = []
    if not x.https:
        score -= 20; issues.append("No HTTPS")
    if not x.mobile:
        score -= 20; issues.append("Poor mobile viewport support")
    if not x.has_title:
        score -= 8; issues.append("Missing page title")
    if not x.has_h1:
        score -= 8; issues.append("Missing primary H1")
    if not x.has_cta:
        score -= 12; issues.append("No clear call-to-action")
    if x.image_alt_ratio < 0.7:
        score -= 8; issues.append("Many images lack alt text")
    if x.load_time_ms is not None and x.load_time_ms > 4000:
        score -= 12; issues.append("Slow initial load")
    return max(0, min(100, score)), issues
