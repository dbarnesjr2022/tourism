# API key handling — safe local setup

Do NOT paste secrets into chat or commit them to git. Follow these local steps to store RapidAPI keys and use them in the code.

1. Create a local `.env`

   - Copy `backend/.env.example` to `backend/.env` and fill in `RAPIDAPI_KEY` and any provider hostnames.

2. Keep `.env` out of git

   - `backend/.gitignore` already ignores `.env` and the RapidAPI cache at `data/raw/rapidapi/`.

3. Load env in WSL / bash before running scripts

   - Lightweight:

     ```bash
     export $(grep -v '^#' backend/.env | xargs)
     ```

   - Or use `direnv`, `python-dotenv`, or `source backend/.env` (be cautious when sourcing directly).

4. Running the fetch script (example)

   - Default is MOCK mode; to run live explicitly:

     ```bash
     # Run in live mode (ensure backend/.env has RAPIDAPI_KEY and MOCK=false)
     cd backend
     python -m backend.scripts.fetch_competitor_prices --live
     ```

5. Rotate keys if accidentally exposed

   - In the RapidAPI dashboard, revoke/regenerate the key immediately.

6. CI / GitHub Actions

   - Add the real key to repository secrets (Settings → Secrets) and reference it as `${{ secrets.RAPIDAPI_KEY }}` in workflows.

If you want, I can scaffold the adapter to read these env values and run in MOCK mode by default.
