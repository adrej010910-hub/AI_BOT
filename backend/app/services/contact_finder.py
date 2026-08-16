import re
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)

async def find_public_email(url: str) -> str | None:
    headers={"User-Agent":"AI-Web-Lead-Agent/0.4 (+public-contact-discovery)"}
    async with httpx.AsyncClient(follow_redirects=True,timeout=10,headers=headers) as client:
        urls=[url]
        try:
            r=await client.get(url); soup=BeautifulSoup(r.text,"html.parser")
            for a in soup.find_all("a",href=True):
                text=(a.get_text(" ",strip=True)+" "+a["href"]).lower()
                if any(k in text for k in ("contact","about","email")):
                    urls.append(urljoin(str(r.url),a["href"]))
            for page in list(dict.fromkeys(urls))[:4]:
                rr=await client.get(page)
                matches=EMAIL_RE.findall(rr.text)
                for email in matches:
                    low=email.lower()
                    if not any(x in low for x in ("example.com","sentry.io","wixpress.com","wordpress.com")):
                        return low
        except Exception:
            return None
    return None
