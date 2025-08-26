"""Store data in Postgres with clear type hints so Pylance is happy.

- Works with psycopg2 (no extra stubs needed) using Protocol types.
- If you use psycopg v3 instead, see the note at the bottom.
"""
from __future__ import annotations

import os
from typing import Any, Protocol, TypedDict, runtime_checkable, Tuple

# psycopg2 import is not needed directly; pg_connect is imported below
from psycopg2 import connect as pg_connect  # type: ignore[attr-defined]

# --- Types --------------------------------------------------------------------

class DBConfig(TypedDict):
    host: str
    port: int
    dbname: str
    user: str
    password: str

@runtime_checkable
class CursorLike(Protocol):
    def execute(self, sql: str, params: Tuple[Any, ...] | None = ...) -> Any: ...
    def close(self) -> None: ...

@runtime_checkable
class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...

# --- Config -------------------------------------------------------------------

DB_CONFIG: DBConfig = {
    "host": os.getenv("PGHOST", "127.0.0.1"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "postgres"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}

# Prefer DATABASE_URL/DSN if provided; otherwise build from pieces above.
dsn: str = os.getenv(
    "DATABASE_URL",
    f"dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} "
    f"password={DB_CONFIG['password']} host={DB_CONFIG['host']} port={DB_CONFIG['port']}"
)

# --- Main logic ---------------------------------------------------------------

def main() -> None:
    # Pylance knows 'dsn' is a str and 'conn'/'cur' implement the Protocols.
    conn: ConnectionLike = pg_connect(dsn)  # type: ignore[call-arg]
    try:
        cur: CursorLike = conn.cursor()
        try:
            # Example statement; replace with your real INSERT/UPSERT etc.
            cur.execute("SELECT 1;")
            conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
