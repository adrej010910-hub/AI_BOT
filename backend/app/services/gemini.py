import json
import os
import httpx

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

async def gemini_generate(prompt: str, use_search: bool = False) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if use_search:
        payload["tools"] = [{"google_search": {}}]
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(GEMINI_URL, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        data = response.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts)

async def discover_businesses(niche: str, location: str, limit: int = 10) -> list[dict]:
    prompt = f'''Search the public web for {limit} real businesses in {location} in the {niche} niche that have an official website. Prefer small/local businesses whose websites look dated, confusing, poorly mobile-optimized, slow, or otherwise likely to benefit from a professional redesign. Do not invent businesses or URLs. Exclude major global brands, web agencies, directories, social profiles, and businesses without a public website.
Return ONLY valid JSON array with objects containing: business_name, website, reason, source_url. Use the official business website as website. Keep reason under 180 characters.'''
    text = await gemini_generate(prompt, use_search=True)
    try:
        parsed = json.loads(text[text.find("["):text.rfind("]") + 1])
        return [x for x in parsed if x.get("business_name") and x.get("website")][:limit]
    except Exception:
        return []

async def ai_redesign_analysis(business_name: str, website: str, audit: dict) -> dict:
    prompt = f'''Act as a senior web designer doing a sales-qualified website audit. Business: {business_name}. Website: {website}. Technical audit: {json.dumps(audit)}. Based only on supplied facts, return concise JSON with keys redesign_score (0-100), top_problems (array of 3), redesign_pitch (string), and outreach_angle (string). Do not claim visual issues that were not observed.'''
    text = await gemini_generate(prompt)
    try:
        return json.loads(text[text.find("{"):text.rfind("}") + 1])
    except Exception:
        return {"redesign_score": audit.get("score", 0), "top_problems": audit.get("issues", [])[:3], "redesign_pitch": "Modernize the website experience.", "outreach_angle": "Offer a short redesign concept."}
