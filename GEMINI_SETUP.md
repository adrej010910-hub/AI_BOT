# Gemini setup

1. Create a Gemini API key in Google AI Studio.
2. In Vercel, open Project Settings → Environment Variables.
3. Add `GEMINI_API_KEY` with the key. Never commit it to GitHub.
4. Add `GEMINI_MODEL=gemini-2.5-flash`.
5. Redeploy.

The app uses Gemini's Google Search grounding to find real public businesses and official websites. Google currently lists free-tier access for eligible Gemini API models and publishes quotas on its pricing/rate-limit pages. The application intentionally uses a conservative daily search cap.

Useful endpoints after deployment:
- `/api/health`
- `/api/discover`
- `/api/leads`
- `/dashboard/discover.html`
