def draft_message(business_name: str, website: str, issues: str) -> str:
    issue_text = issues or "a few opportunities to improve the website experience"
    return f"""Hi there,\n\nI came across {business_name}'s website ({website}) and noticed {issue_text}.\n\nI build modern websites for local businesses, and I think a cleaner redesign could make the site easier to use and help turn more visitors into customers.\n\nIf you'd like, I can send over a quick redesign concept for your site — no obligation.\n\nBest,\nAndrej"""
