"""SQLite local persistence; replace with managed PostgreSQL + migrations for multi-user deployment."""
from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB = str(Path(__file__).resolve().parent.parent / 'frameforge.db')

def db_path():
    return os.environ.get('FRAMEFORGE_DB_PATH', DEFAULT_DB)

@contextmanager
def connect():
    conn = sqlite3.connect(db_path(), timeout=10.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA busy_timeout = 10000')
        yield conn
    finally:
        conn.close()

def initialize():
    with connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript("""
            CREATE TABLE IF NOT EXISTS projects(
                id TEXT PRIMARY KEY, title TEXT NOT NULL, created_at TEXT NOT NULL,
                settings TEXT NOT NULL, storyboard TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed','cancelled')),
                provider TEXT NOT NULL, estimated_cents INTEGER NOT NULL,
                result_json TEXT, error TEXT, idem_key TEXT UNIQUE,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS graphs(
                id TEXT PRIMARY KEY, title TEXT NOT NULL, graph TEXT NOT NULL, created_at TEXT NOT NULL
            );
        """)
