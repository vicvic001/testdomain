from __future__ import annotations

import sqlite3
from pathlib import Path


class DomainStore:
    def __init__(self, sqlite_path: str) -> None:
        self._path = Path(sqlite_path)
        self._connection = sqlite3.connect(self._path)
        self._init_schema()

    def _init_schema(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS domains (
                domain TEXT PRIMARY KEY,
                first_seen_url TEXT,
                first_seen_at TEXT,
                available INTEGER,
                checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notified INTEGER DEFAULT 0
            )
            """
        )
        self._connection.commit()

    def domain_seen(self, domain: str) -> bool:
        cursor = self._connection.execute(
            "SELECT 1 FROM domains WHERE domain = ? LIMIT 1", (domain,)
        )
        return cursor.fetchone() is not None

    def record_domain(self, domain: str, url: str, found_at: str, available: bool) -> None:
        self._connection.execute(
            """
            INSERT OR REPLACE INTO domains (domain, first_seen_url, first_seen_at, available)
            VALUES (?, ?, ?, ?)
            """,
            (domain, url, found_at, int(available)),
        )
        self._connection.commit()

    def mark_notified(self, domain: str) -> None:
        self._connection.execute(
            "UPDATE domains SET notified = 1 WHERE domain = ?", (domain,)
        )
        self._connection.commit()
