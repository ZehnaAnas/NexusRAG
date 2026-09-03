"""
db.py — the single place in the app that talks to the database.

Why this file exists:
Every other file (main.py, rag_chain.py, etc.) should NEVER write raw SQL
directly. They should just call functions like set_status(...) or
get_status(...) from here. That way, if you ever swap SQLite for
Postgres later, you only rewrite THIS file — nothing else changes.
"""

import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from utils.config import DATA_DIR

# This is the single file on disk that holds all our persistent data.
# It lives next to your uploads/vectorstores folders.
DB_PATH = DATA_DIR / "app.db"

# Defensive: SQLite can create the database FILE, but not the folder
# containing it — a missing parent directory surfaces as the fairly
# unhelpful "unable to open database file". Making sure it exists at
# import time removes that whole failure mode.
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection():
    """
    Opens a connection to the database file, hands it to whoever asked
    for it (the 'with' block), then automatically closes it afterwards
    — even if an error happens in between.

    This pattern (a "context manager") is worth learning on its own:
    it's how Python guarantees cleanup happens, similar to how you'd
    always want to close a file you opened.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read results by column name
    try:
        yield conn
        conn.commit()  # save changes to disk
    finally:
        conn.close()


def init_db():
    """
    Creates the tables if they don't already exist. Safe to call every
    time the app starts — it won't wipe existing data.

    NOTE: if you already have an old app.db from before this change,
    delete it once (utils/data/app.db) so the new "owner" column can
    be created fresh. In a real production app you'd use a migration
    tool (e.g. Alembic) to upgrade an existing table's schema without
    losing data — deleting and recreating is a fine shortcut while
    you're the only user and there's nothing real to lose yet.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_uploads (
                owner       TEXT NOT NULL,
                file_name   TEXT NOT NULL,
                status      TEXT NOT NULL,
                error       TEXT,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (owner, file_name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                key_hash    TEXT PRIMARY KEY,
                owner       TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def set_status(owner: str, file_name: str, status: str, error: str | None = None):
    """
    Writes (or overwrites) the status for a file, scoped to its owner.
    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO file_uploads (owner, file_name, status, error, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(owner, file_name) DO UPDATE SET
                status = excluded.status,
                error = excluded.error,
                updated_at = CURRENT_TIMESTAMP
            """,
            (owner, file_name, status, error),
        )


def get_status(owner: str, file_name: str) -> dict:
    """
    Reads the status for a file, scoped to its owner. If a DIFFERENT
    owner's file_name is requested, the WHERE clause simply finds no
    matching row — the caller gets "unknown" back, the exact same
    response as if the file never existed at all. This is the
    authorization check happening naturally, as a side effect of
    always filtering by owner, not as a special extra "if" statement.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT owner, file_name, status, error, updated_at FROM file_uploads WHERE owner = ? AND file_name = ?",
            (owner, file_name),
        ).fetchone()

    if row is None:
        return {"file_name": file_name, "status": "unknown", "error": None}

    return {
        "file_name": row["file_name"],
        "status": row["status"],
        "error": row["error"],
        "updated_at": row["updated_at"],
    }  


def _hash_key(raw_key: str) -> str:
    """
    One-way transform: turns a raw API key into a fixed-length hash
    that's stored instead of the key itself. Same raw key always
    produces the same hash (so we can look it up later), but you
    cannot go backwards from the hash to the original key.
    """
    return hashlib.sha256(raw_key.encode()).hexdigest()


def create_api_key(owner: str) -> str:
    """
    Mints a brand-new API key for an owner. The RAW key is returned
    ONCE, here, and never stored anywhere — only its hash goes in the
    database. This mirrors exactly how GitHub, Stripe, and Anthropic
    show you a new key exactly once and say "copy this now."
    """
    raw_key = secrets.token_urlsafe(32)  # a long, random, unguessable string
    key_hash = _hash_key(raw_key)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO api_keys (key_hash, owner) VALUES (?, ?)",
            (key_hash, owner),
        )
    return raw_key


def verify_api_key(raw_key: str) -> str | None:
    """
    Given a raw key a client sent, hash it the same way and look for
    a match. Returns the owner name if valid, or None if not — the
    caller (our FastAPI dependency) turns None into a 401 response.
    """
    if not raw_key:
        return None
    key_hash = _hash_key(raw_key)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT owner FROM api_keys WHERE key_hash = ?", (key_hash,)
        ).fetchone()
    return row["owner"] if row else None