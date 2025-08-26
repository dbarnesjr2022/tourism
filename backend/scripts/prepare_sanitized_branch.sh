#!/usr/bin/env bash
# Prepare a sanitized branch from origin/main containing only selected cleaned files.
# Run locally from the repo root. This script does not push by default.

set -euo pipefail

if [ -z "${1-}" ]; then
  echo "Usage: $0 <sanitized-branch-name>"
  exit 2
fi
BRANCH_NAME="$1"

# 1. Fetch and create branch from remote main
git fetch origin main
git checkout --detach origin/main

git checkout -b "$BRANCH_NAME"

# 2. Remove everything (we'll re-add only desired files)
git rm -rf .

# 3. Recreate minimal project tree you want to push
mkdir -p backend app frontend .github

# Example: copy only backend code, alembic, tests, and CI
cp -R backend/app backend/alembic backend/alembic.ini backend/requirements.txt backend/pytest.ini .github || true
cp -R backend/tests backend/scripts || true

# 4. Create .gitignore and .env.example if missing
cat > .gitignore <<'GITIGNORE'
.env
backend/.venv
*.pyc
__pycache__/
GITIGNORE

cat > backend/.env.example <<'ENV'
# Put required secrets locally; do NOT commit real secrets
DATABASE_URL=sqlite:///./dev.db
ENV=development
ENV_SECRET=
ENV_API_KEY=
ENV_OPENAI_KEY=
ENV_OTHER=
ENV

# 5. Commit
git add -A
git commit -m "chore: sanitized branch prepared (no secrets)"

echo "Sanitized branch '$BRANCH_NAME' prepared locally. Review the tree, then push with: git push origin $BRANCH_NAME"
