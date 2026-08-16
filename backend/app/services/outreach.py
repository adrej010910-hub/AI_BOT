SYSTEM_PROMPT = """
You write concise, respectful B2B website-redesign outreach for a real business.
Use only supplied audit facts. Never invent a person's name, relationship, revenue, or results.
Do not use deceptive urgency. Offer an optional free redesign preview and make it easy to decline.
""".strip()


def build_outreach(business_name: str, audit: dict) -> str:
    issues = audit.get("issues", [])
    issue_text = " ".join(issues[:3]) or "a few UX and presentation opportunities"
    return (
        f"Hi {business_name} team,\n\n"
        f"I came across your website and noticed {issue_text.lower()} that may be worth improving.\n\n"
        "I build modern website redesigns for businesses and can put together a free visual concept "
        "so you can see a possible direction before deciding on anything.\n\n"
        "Would you like me to send it over? If not, no worries."
    )


def draft_message(business_name: str, website: str, issues: str) -> str:
    return build_outreach(business_name, {"issues": [x.strip() for x in issues.split(";") if x.strip()], "website": website})
