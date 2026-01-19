"""
Lightweight SQLite migration script for adding auth/feedback tables/columns.
Run: python scripts/migrate_sqlite.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.core.config import settings


def _db_path() -> Path:
    url = settings.database_url
    if url.startswith("sqlite+aiosqlite:///"):
        url = url.replace("sqlite+aiosqlite:///", "sqlite:///")
    if not url.startswith("sqlite:///"):
        raise RuntimeError("Only SQLite is supported by this migration script.")
    return Path(url.replace("sqlite:///", ""))


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def main():
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            session_id TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    if not _column_exists(cursor, "users", "email"):
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if not _column_exists(cursor, "users", "password_hash"):
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if not _column_exists(cursor, "users", "full_name"):
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    if not _column_exists(cursor, "users", "role"):
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT,
            message_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT UNIQUE,
            title TEXT,
            summary TEXT,
            last_message TEXT,
            last_role TEXT,
            pinned INTEGER DEFAULT 0,
            deleted_at TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    for column, ddl in [
        ("title", "ALTER TABLE chat_sessions ADD COLUMN title TEXT"),
        ("summary", "ALTER TABLE chat_sessions ADD COLUMN summary TEXT"),
        ("last_message", "ALTER TABLE chat_sessions ADD COLUMN last_message TEXT"),
        ("last_role", "ALTER TABLE chat_sessions ADD COLUMN last_role TEXT"),
        ("pinned", "ALTER TABLE chat_sessions ADD COLUMN pinned INTEGER DEFAULT 0"),
        ("deleted_at", "ALTER TABLE chat_sessions ADD COLUMN deleted_at TIMESTAMP"),
        ("last_updated", "ALTER TABLE chat_sessions ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("created_at", "ALTER TABLE chat_sessions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]:
        if not _column_exists(cursor, "chat_sessions", column):
            cursor.execute(ddl)

    conn.commit()
    conn.close()
    print("✅ Migration complete.")


if __name__ == "__main__":
    main()
