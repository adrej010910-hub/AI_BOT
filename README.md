# AI Web Lead Agent

AI-powered assistant for finding businesses with outdated websites, auditing their web presence, and preparing personalized redesign outreach.

## MVP

- Discover candidate businesses from approved/public sources
- Analyze public websites for basic UX, mobile, performance, and technical signals
- Generate an explainable lead score
- Draft personalized outreach messages in English
- Store leads and audit results
- Require human approval before any outreach is sent

## Safety / outreach

This project is designed for targeted, compliant business outreach rather than bulk spam. It includes deduplication, rate limits, an opt-out/suppression list, and a manual approval step before sending.

## Planned stack

- Python + FastAPI
- Playwright
- SQLite/PostgreSQL
- OpenAI-compatible LLM provider
- React/Next.js dashboard

## Status

Initial repository scaffold. The next commits will add the crawler/auditor, scoring engine, lead storage, and dashboard.
