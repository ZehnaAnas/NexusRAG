"""
db.py - The single place in the app that talks to the database

Why this file exists:

Every other file (main.py, rag_chain.py, etc.) should NEVER write raw SQL directly. 
They should just call functions like set_status(...) or get_status(...) from here. 
That way, if you ever swap SQLite for Postgres later, you only rewrite THIS file - nothing else changes.
"""
import sqlite3
from contextlib import contextmanager
from utils.config import DATA_DIR

#This is the single file on disk that holds all our persistent data
#It lives next to your uploads/vectorstores folders.

DB_PATH = DATA_DIR/"app.db"

@contextmanager
def get_connection():
    """
    Opens a connection to the database file, hands it to whoever asked
    for it (the 'with' block), then automatically closes afterwards - even
    if an error happens in between.

    This pattern (a "context manager") is worth learning on its own: it's how
    python guarantees cleanup happens, similar to how you'd always want to close a file you opened.

    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # lets us read results by column name
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    """
    Creates the table if it doesn't already exist. 
    Safe to call everytime the app starts - it won't wipe existing data.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_uploads(
                file_name   TEXT PRIMARY KEY,
                status      TEXT NOT NULL,
                error       TEXT,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

def set_status(file_name:str, status:str, error:str | None = None):
    """
    Writes (or overwrites) the status for a file.
    This directly replaces: file_status[file_name] = status

    Notice the "?" placeholders below instead of an f-string. 
    This is parameterized-query habit from the lesson - sqlite3 safely
    inserts the values for us, so user-supplied text can never be 
    interpreted as part of the SQL command itself.

    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO file_uploads (file_name, status, error, updated_at)
            VALUES (?,?,?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_name) DO UPDATE SET
                status = excluded.status,
                error = excluded.error,
                updated_at = CURRENT_TIMESTAMP
            """,
            (file_name,status,error),
        )

def get_status(file_name:str) -> dict:
    """
    Reads the status for a file.
    This directly replaces: file_status.get(file_name,"unknown")
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT file_name, status, error, updated_at FROM file_uploads WHERE file_name = ?",
            (file_name,),
        ).fetchone()

    if row is None:
        return {"file_name":file_name,"status":"unknown","error":None}

    return {
        "file_name": row["file_name"],
        "status" : row["status"],
        "error" : row["error"],
        "updated_at" : row["updated_at"],
    }