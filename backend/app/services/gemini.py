import json
import os
import httpx

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _json_object(text: str, fallback: dict):
    try:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start:end + 1]) if start >= 0 and end > start else fallback
    except Exception:
        return fallback


def _json_array(text: str):
    try:
        start, end = text.find("["), text.rfind("]")
        return json.loads(text[start:end + 1]) if start >= 0 and end > start else []
    except Exception:
        return []


async def gemini_generate(prompt: str, use_search: bool = False) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    if use_search:
        payload["tools"] = [{"google_search": {}}]
    async with httpx.AsyncClient(timeout=50) as client:
        response = await client.post(
            GEMINI_URL,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts)


async def discover_businesses(niche: str, location: str, limit: int = 10) -> list[dict]:
    prompt = f'''Use Google Search grounding to find {limit} REAL small/local businesses in {location} in the {niche} niche that have an official public website.
Prioritize independent businesses whose website has clear, observable signs of being outdated or weak: missing mobile viewport, poor information architecture, weak conversion CTA, old-looking structure, missing essential pages, or other concrete web problems.
Exclude franchises/global brands, agencies, directories, social profiles, marketplaces, and businesses without an official website.
Never invent a business, URL, email, or person. Use only URLs supported by search results.
Return ONLY a JSON array. Each item must contain: business_name, website, source_url, reason.
The website must be the business's own canonical website. Keep reason under 220 characters.'''
    text = await gemini_generate(prompt, use_search=True)
    items = _json_array(text)
    output = []
    seen = set()
    for x in items:
        name, website = str(x.get("business_name", "")).strip(), str(x.get("website", "")).strip()
        key = website.lower().rstrip("/")
        if name and website.startswith(("http://", "https://")) and key not in seen:
            seen.add(key)
            output.append({"business_name": name, "website": website, "reason": str(x.get("reason", ""))[:220], "source_url": x.get("source_url")})
    return output[:limit]


async def ai_redesign_analysis(business_name: str, website: str, audit: dict) -> dict:
    prompt = f'''You are a senior web designer qualifying a redesign lead.
Business: {business_name}
Website: {website}
Observed technical audit: {json.dumps(audit, ensure_ascii=False)}

Use ONLY the observed facts. Do not pretend you saw visual problems that were not supplied.
Define redesign_score as NEED FOR REDESIGN: 100 = strong opportunity, 0 = no clear opportunity.
Return ONLY JSON with:
redesign_score (integer 0-100),
top_problems (exactly up to 4 concrete observed problems),
redesign_pitch (one sentence),
outreach_angle (one sentence).
A score above 65 should require multiple meaningful issues; otherwise keep it below 65.'''
    text = await gemini_generate(prompt)
    fallback = {
        "redesign_score": max(0, min(100, 100 - int(audit.get("score", 100)))),
        "top_problems": audit.get("issues", [])[:4],
        "redesign_pitch": "A cleaner, more modern website could improve the customer experience.",
        "outreach_angle": "Offer a free visual redesign concept based on the observed issues.",
    }
    result = _json_object(text, fallback)
    try:
        result["redesign_score"] = max(0, min(100, int(result.get("redesign_score", fallback["redesign_score"]))))
    except (TypeError, ValueError):
        result["redesign_score"] = fallback["redesign_score"]
    result["top_problems"] = [str(x) for x in result.get("top_problems", [])][:4]
    return result
