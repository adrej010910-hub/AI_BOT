# AI Web Lead Agent

A focused web-audit and B2B outreach assistant for finding businesses whose public websites have clear improvement opportunities.

## Current flow

1. Enter a public business website.
2. Audit basic technical/UX signals.
3. Create a lead with an explainable score and issues.
4. Generate a short personalized English outreach draft.
5. Review it manually.
6. Approve it.
7. Send only after explicit confirmation through the dashboard.

## Vercel

The repository is structured for Vercel with a static dashboard and FastAPI in `api/index.py`. Vercel's Python runtime supports this FastAPI layout and `requirements.txt` dependency installation. The dashboard is available at `/dashboard/`.

## Environment

For sending email, configure:

- `RESEND_API_KEY`
- `OUTREACH_FROM_EMAIL`

For production persistence, configure a hosted PostgreSQL/Supabase/Neon database and wire `DATABASE_URL` into the storage layer before relying on the app for long-lived lead data. The current in-memory store is intentionally suitable for the MVP/demo only.

## Safety

The agent is designed for targeted, respectful B2B outreach rather than bulk spam. It does not send automatically, requires explicit approval, supports suppression, and should respect applicable laws, provider policies, and recipient opt-outs.

## Status

MVP is deployed-oriented. Next production hardening: persistent database, authentication, real business discovery provider, visual/Playwright audit, rate limiting, and delivery/reply tracking.
