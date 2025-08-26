# Backend (FastAPI) — quick dev commands

## Prerequisites

- Python 3.10
- A virtualenv (created as `.venv` in this repo root)

## Activate venv

```bash
cd backend
. .venv/bin/activate
```

## Run tests

```bash
python -m pytest -q
```

## Run linter (ruff)

```bash
python -m ruff check .
```

## Start dev server

```bash
uvicorn main:app --reload
```
