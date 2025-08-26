# TODOs: Tourism Intelligence SaaS Platform

## 1. Project Setup & Structure

- [x] Create backend and frontend directory scaffolding
- [x] Set up Python virtual environment and install dependencies
- [x] Initialize Next.js frontend app
- [x] Set up PostgreSQL database (local/dev)

## 2. Backend API (FastAPI)

- [x] Implement `/forecast` endpoint (done, mock)
- [x] Implement `/pricing` endpoint (mock)
- [x] Implement `/personas` endpoint (mock)
- [x] Implement `/campaigns` endpoint (mock)
- [x] Implement `/chatbot` endpoint (mock)

- [x] Add Stripe billing integration (webhook handlers, subscription lifecycle, invoice failures)
  - [x] Add CRM sync endpoints (HubSpot/Salesforce Lite)
  - [x] Add cross-promotion endpoint for bundled offers
  - [x] Add error handling and input validation

- [x] Write unit tests for billing endpoints and webhooks
  - Billing logic is robust, type/lint clean, and all tests pass (see `backend/tests/test_billing_webhooks.py`).
  - Next: Expand test coverage for all endpoints and edge cases.

## 3. Data Pipelines & ETL

- [x] Script to fetch Orlando/Kissimmee event calendars
  - Implemented: see `backend/scripts/fetch_event_calendars.py`
- [x] Script to fetch weather data (API)
  - Implemented: see `backend/scripts/fetch_weather_data.py`
- [x] Script to scrape OTA competitor prices (Booking, Expedia, Airbnb)
  - Implemented: see `backend/scripts/fetch_competitor_prices.py`
  - [ ] Implement robust live fetcher
    - Add per-provider RapidAPI header wiring, secure key usage, and explicit host env vars
    - Add retries/backoff and respectful rate-limiting (httpx or tenacity)
    - Add unit tests that mock httpx responses
  - [ ] Persist normalized competitor rows to PostgreSQL
    - Define `competitor_prices` table and migration
    - Implement writer function and idempotent/dedup ingestion
    - Add tests for persistence and replayability
  - [ ] Wire ETL scheduling and snapshots
    - Ensure `schedule_etl_jobs.py` can run hourly/daily snapshots
    - Add snapshot retention and S3/archive strategy for raw responses
- [x] Script to ingest historical bookings (CSV/API)
  - Implemented: see `backend/scripts/ingest_historical_bookings.py`
- [x] Store raw and processed data in PostgreSQL
  - Implemented: see `backend/scripts/store_data_postgres.py`
- [x] Schedule ETL jobs (cron or serverless)
  - Implemented: see `backend/scripts/schedule_etl_jobs.py`

## 4. ML Models & Services

- [x] Implement MVP demand forecasting (Prophet)
  - Implemented: see `backend/scripts/forecast_demand.py`
- [x] Implement dynamic pricing model (regression/Bayesian optimization)
  - Implemented: see `backend/scripts/dynamic_pricing.py`
- [x] Implement persona clustering (K-Means/DBSCAN)
  - Implemented: see `backend/scripts/persona_clustering.py`
- [x] Integrate LLM for persona descriptions (OpenAI/Claude API)
- [x] Integrate LLM for campaign generation (email/social/postcard copy)
- [x] Add model evaluation and retraining scripts

## 5. Frontend Dashboard (Next.js)

## 6. Integrations

[x] Write frontend unit/integration tests

[x] Stripe billing setup and test
Webhook handlers for subscription events and invoice.payment_failed implemented in `backend/app/api/billing.py`.

[ ] Write frontend unit/integration tests
Tests pass: `backend/tests/test_billing.py` and `backend/tests/test_billing_webhooks.py`.
Billing code is robust and type/lint clean.
[ ] HubSpot/Salesforce Lite CRM sync
[x] Chatbot widget integration (custom or third-party)
[x] Email/SMS/postcard campaign delivery (SendGrid/Twilio/Lob)

## 7. Deployment & DevOps

- [ ] Set up Vercel for frontend hosting
- [x] Set up AWS Lambda for backend ML inference
- [ ] Set up AWS RDS/PostgreSQL for production DB
- [ ] Set up CI/CD pipelines (GitHub Actions)
- [ ] Set up environment variables and secrets management
- [ ] Set up logging and monitoring (Sentry/CloudWatch)

Notes:

- CI workflow added: `.github/workflows/ci.yml` runs ruff + pytest for `backend`.

- Ruff config added to root `pyproject.toml`.

- README and Makefile additions for local dev in `backend/README.md`.

## 8. Documentation

- [ ] Write architecture overview
- [ ] Write API documentation (OpenAPI/Swagger)
- [ ] Write data pipeline documentation
- [ ] Write ML model documentation
- [ ] Write onboarding guide for pilot businesses
- [ ] Write user help docs and FAQ

## 9. Pilot & Iteration

- [ ] Onboard 3–5 pilot businesses
- [ ] Collect feedback and usage data
- [ ] Refine models, personas, and UX based on feedback
- [ ] Prepare for public launch
