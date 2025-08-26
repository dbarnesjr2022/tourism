# TODOs: Tourism Intelligence SaaS Platform

## 1. Project setup & structure

- [x] Create backend and frontend directory scaffolding
- [x] Set up Python virtual environment and install dependencies
- [x] Initialize Next.js frontend app
- [x] Set up PostgreSQL database (local/dev)

## 2. Backend API (FastAPI)

- [x] Implement `/forecast` endpoint (mock/integrated tests)
- [x] Implement `/pricing`, `/personas`, `/campaigns`, `/chatbot` (mock)

- [x] Stripe billing integration (webhook handlers, subscription lifecycle, invoice failures)
  - [x] CRM sync endpoints (HubSpot/Salesforce Lite)
  - [x] Cross-promotion endpoint for bundled offers
  - [x] Error handling and input validation

- [x] Unit tests for billing endpoints and webhooks (see `backend/tests/test_billing_webhooks.py`)

## 3. Data pipelines & ETL

- [x] Event calendar fetcher (Orlando/Kissimmee) — `backend/scripts/fetch_event_calendars.py`
- [x] Weather data fetcher — `backend/scripts/fetch_weather_data.py`
- [x] Competitor price fetcher (mock-first) — `backend/scripts/fetch_competitor_prices.py`
  - [x] Added mock fixtures under `data/raw/rapidapi/` and unit tests
  - [x] Implemented conservative live-mode helpers: httpx GET wrapper, per-provider header helper, jittered exponential backoff, and simple per-provider rate limiter
  - [x] Provider-specific fetch functions call live helper only when explicit `--live`/env keys are provided
  - [x] Added SQLAlchemy `CompetitorPrice` model and `backend/scripts/store_competitor_prices.py` writer (persistence prototype)
  - [x] Unit + integration tests added for fetcher and writer; tests pass locally
  - [ ] Robust live fetcher hardening (provider pagination, retries per-status, request batching)
  - [ ] Add Alembic migration and production-ready `competitor_prices` table
  - [ ] ETL scheduling, snapshot retention, and raw response archival (S3)

- [x] Ingest historical bookings — `backend/scripts/ingest_historical_bookings.py`
- [x] Store raw/processed data in PostgreSQL — `backend/scripts/store_data_postgres.py`
- [x] ETL scheduler script exists — `backend/scripts/schedule_etl_jobs.py`
  - [ ] Add Alembic migration and finalize `competitor_prices` schema (in progress — see `backend/migrations/0001_create_competitor_prices.py`)

## 4. ML models & services

- [x] MVP demand forecasting — `backend/scripts/forecast_demand.py`
- [x] Dynamic pricing scripts — `backend/scripts/dynamic_pricing.py`
- [x] Persona clustering — `backend/scripts/persona_clustering.py`
- [x] LLM integrations (persona descriptions & campaign generation) — prototype scripts exist
- [x] Model evaluation & retraining scripts

## 5. Frontend dashboard (Next.js)

_Work in progress — frontend repo and tests exist; dashboard pages and components remain to be completed._

## 6. Integrations

- [x] Frontend unit/integration tests (some coverage under `frontend/__tests__`)
- [x] Stripe billing and webhook handlers — `backend/app/api/billing.py`
- [x] Chatbot widget integration (component scaffolded)
- [x] Email/SMS/postcard delivery integrated at prototype level

## 7. Deployment & DevOps

- [x] CI workflow added: `.github/workflows/ci.yml` runs ruff + pytest for backend
- [x] Ruff config present in `pyproject.toml`
- [x] `backend/.env.example` and `.gitignore` guidance added to avoid committing secrets
- [ ] Add Vercel for frontend (pending)
- [ ] AWS RDS/Postgres production deployment (pending)
- [ ] Harden CI/CD (deploy steps, secret handling, and verifications)
- [ ] Logging & monitoring (Sentry/CloudWatch)

## 8. Documentation

- [ ] Architecture overview
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Data pipeline docs
- [ ] ML model docs
- [ ] Onboarding guide for pilot businesses
- [ ] User help docs and FAQ

## 9. Pilot & iteration

- [ ] Onboard pilot customers
- [ ] Collect feedback and iterate on models and UX

## Recent changes (delta)

- Implemented mock-first competitor ingestion in Python and TypeScript prototypes.
- Added live-mode httpx helper, jittered backoff, and a per-provider rate limiter.
- Added SQLAlchemy `CompetitorPrice` model and a writer script.
- Added unit and integration tests for fetcher + persistence; local test run: `15 passed`.
- Added CI workflow (`.github/workflows/ci.yml`) to run ruff + pytest.
- Added `.env.example` and `.gitignore` entries to avoid committing secrets.

## Current blocker

- GitHub push-protection flagged historical commits that include an OpenAI API key. Remote pushes are rejected until the leaked secret is revoked/rotated and the repository history is sanitized or a clean branch is created from `origin/main` and pushed.

Action required: revoke/rotate the exposed key in the provider dashboard (OpenAI) immediately, then either:

- create a sanitized branch from `origin/main` and reapply changes (recommended), or
- rewrite history to remove secrets (git-filter-repo / BFG) and force-push cleaned branches (requires coordination with collaborators).

## Next actions (priority ordered)

1. Revoke/rotate the leaked OpenAI key (user action, critical).
2. Create a sanitized branch from `origin/main`, copy only the cleaned files, and push — open a draft PR to run CI on GitHub.
3. Add missing repository secrets in GitHub (DATABASE_URL, VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID) and fix `ci.yml` if needed.
4. Add Alembic migration and finalize `competitor_prices` schema.
5. Harden live fetcher: provider-specific pagination, robust error handling, and higher-quality normalization.
6. Implement ETL schedule + snapshot retention + raw response archival (S3).

## Requirements coverage checklist

- Competitor ingestion implemented (mock + live helpers): Done (partial live hardening required)
- Persistence prototype (model + writer + tests): Done
- Tests & CI: Done locally; CI added but remote runs blocked until push-protection issue resolved
- Secrets handling: `.env.example` added; historical secret must be revoked to proceed with remote PRs

If you want, I can create the sanitized branch locally and prepare a commit that excludes the offending files, then attempt the push once you confirm the leaked key is rotated or you give permission to proceed with history rewrite.
    - Added `.env.example` and `.gitignore` entries to avoid committing secrets.

    ## Current blocker
    - GitHub push-protection flagged historical commits that include an OpenAI API key. Remote pushes are rejected until the leaked secret is revoked/rotated and the repository history is sanitized or a clean branch is created from `origin/main` and pushed.

    Action required: revoke/rotate the exposed key in the provider dashboard (OpenAI) immediately, then either:
    - create a sanitized branch from `origin/main` and reapply changes (recommended), or
    - rewrite history to remove secrets (git-filter-repo / BFG) and force-push cleaned branches (requires coordination with collaborators).

    ## Next actions (priority ordered)
    1. Revoke/rotate the leaked OpenAI key (user action, critical).
    2. Create a sanitized branch from `origin/main`, copy only the cleaned files, and push — open a draft PR to run CI on GitHub.
    3. Add missing repository secrets in GitHub (DATABASE_URL, VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID) and fix `ci.yml` if needed.
    4. Add Alembic migration and finalize `competitor_prices` schema.
    5. Harden live fetcher: provider-specific pagination, robust error handling, and higher-quality normalization.
    6. Implement ETL schedule + snapshot retention + raw response archival (S3).

    ## Requirements coverage checklist
    - Competitor ingestion implemented (mock + live helpers): Done (partial live hardening required)
    - Persistence prototype (model + writer + tests): Done
    - Tests & CI: Done locally; CI added but remote runs blocked until push-protection issue resolved
    - Secrets handling: `.env.example` added; historical secret must be revoked to proceed with remote PRs

    If you want, I can create the sanitized branch locally and prepare a commit that excludes the offending files, then attempt the push once you confirm the leaked key is rotated or you give permission to proceed with history rewrite.
