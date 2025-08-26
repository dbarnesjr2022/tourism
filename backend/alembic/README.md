# Alembic (local dev)

Local alembic environment for development.

Usage (WSL with existing venv):

```bash
# from repo root
cd backend
. .venv/bin/activate
alembic upgrade head
# or create a revision:
alembic revision --autogenerate -m "create competitor_prices"
```

Notes:

- This environment uses `backend.app.db.DATABASE_URL` if no `DATABASE_URL` env var is set.
- For production, use a proper centralized alembic config and CI-safe secrets handling.
