SYSTEM_PROMPT = """
You write concise, respectful B2B website-redesign outreach for a real business.
Use only the supplied audit facts. Never invent a person's name, relationship, revenue,
or performance results. Do not use deceptive urgency. Keep the message under 120 words.
Offer a free, optional redesign preview and make it easy to decline future contact.
""".strip()


def build_outreach(business_name: str, audit: dict) -> str:
    issues = audit.get("issues", [])
    issue_text = " ".join(issues[:3]) or "a few UX and presentation opportunities"
    return (
        f"Hi {business_name} team,\n\n"
        f"I came across your website and noticed {issue_text.lower()} "
        "that may be worth improving, especially for visitors on mobile.\n\n"
        "I build modern website redesigns for businesses and can put together a free "
        "visual concept for your site so you can see the direction before deciding on anything.\n\n"
        "Would you like me to send it over? If not, no worries."
    )
