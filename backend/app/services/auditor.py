from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


async def audit_url(url: str) -> dict:
    """Collect conservative, explainable signals from a public website."""
    headers = {"User-Agent": "AI-Web-Lead-Agent/0.2 (+website-audit)"}
    timeout = httpx.Timeout(15.0)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {
            "url": url,
            "score": 0,
            "signals": {"reachable": False, "error": str(exc)},
            "issues": ["Website could not be fetched reliably."],
            "recommendation": "Manual review required",
        }

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    viewport = soup.find("meta", attrs={"name": "viewport"})
    h1_count = len(soup.find_all("h1"))
    body_text = soup.get_text(" ", strip=True).lower()
    cta_present = any(word in body_text for word in ("contact", "book", "quote", "call", "get started"))
    images = soup.find_all("img")
    images_without_alt = sum(1 for img in images if not img.get("alt"))

    signals = {
        "reachable": True,
        "https": urlparse(str(response.url)).scheme == "https",
        "mobile_viewport": viewport is not None,
        "has_title": bool(title),
        "h1_count": h1_count,
        "cta_signal": cta_present,
        "images_without_alt": images_without_alt,
        "status_code": response.status_code,
        "final_url": str(response.url),
    }

    score = 100
    issues: list[str] = []
    if not signals["https"]:
        score -= 15; issues.append("Site is not using HTTPS.")
    if not signals["mobile_viewport"]:
        score -= 20; issues.append("No mobile viewport meta tag was detected.")
    if not signals["has_title"]:
        score -= 10; issues.append("Page title is missing.")
    if h1_count == 0:
        score -= 10; issues.append("No H1 heading was detected.")
    elif h1_count > 1:
        score -= 5; issues.append("Multiple H1 headings were detected.")
    if not cta_present:
        score -= 10; issues.append("No obvious conversion CTA wording was detected.")
    if images_without_alt:
        issues.append(f"{images_without_alt} image(s) are missing alt text.")

    return {
        "url": url,
        "score": max(score, 0),
        "signals": signals,
        "issues": issues,
        "recommendation": "Strong redesign candidate" if score < 65 else "Review further before outreach",
    }
