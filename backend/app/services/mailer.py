import os

import httpx

from .suppression import SUPPRESSION


async def send_email(to: str, subject: str, text: str) -> dict:
    if SUPPRESSION.contains(to):
        raise ValueError("Recipient is on the suppression list")

    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("OUTREACH_FROM_EMAIL")
    if not api_key or not from_email:
        raise RuntimeError("RESEND_API_KEY and OUTREACH_FROM_EMAIL are required to send email")

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"from": from_email, "to": [to], "subject": subject, "text": text},
        )
        response.raise_for_status()
        return response.json()
