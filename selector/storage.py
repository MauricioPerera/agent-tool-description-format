from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


class CatalogStorage:
    """SQLite-backed persistence for ATDF tool catalogs."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._initialize_schema()

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------
    def _initialize_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT,
                cache_timestamp TEXT,
                etag TEXT,
                last_sync TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                tool_id TEXT NOT NULL,
                version_hash TEXT NOT NULL,
                descriptor TEXT NOT NULL,
                description TEXT,
                when_to_use TEXT,
                languages TEXT,
                tags TEXT,
                active INTEGER DEFAULT 1,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES servers(id) ON DELETE CASCADE,
                UNIQUE(server_id, tool_id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                tool_id TEXT NOT NULL,
                outcome TEXT NOT NULL CHECK(outcome IN ('success','error')),
                detail TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES servers(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                tool_id TEXT NOT NULL,
                outcome TEXT NOT NULL CHECK(outcome IN ('success','error')),
                detail TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES servers(id) ON DELETE CASCADE
            );
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Server helpers
    # ------------------------------------------------------------------
    def register_server(self, url: str, name: Optional[str] = None) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT id, name FROM servers WHERE url = ?", (url,))
        row = cur.fetchone()
        if row:
            if name and (row["name"] or "") != name:
                cur.execute(
                    "UPDATE servers SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (name, row["id"]),
                )
                self._conn.commit()
            return int(row["id"])

        cur.execute(
            "INSERT INTO servers (url, name) VALUES (?, ?)",
            (url, name),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def update_server_metadata(
        self,
        server_id: int,
        *,
        cache_timestamp: Optional[str] = None,
        etag: Optional[str] = None,
        last_sync: Optional[datetime] = None,
    ) -> None:
        fields: Dict[str, object] = {"updated_at": datetime.utcnow().isoformat()}
        if cache_timestamp is not None:
            fields["cache_timestamp"] = cache_timestamp
        if etag is not None:
            fields["etag"] = etag
        if last_sync is not None:
            fields["last_sync"] = last_sync.isoformat()

        assignments = ", ".join(f"{key} = ?" for key in fields.keys())
        values = list(fields.values()) + [server_id]
        query = f"UPDATE servers SET {assignments} WHERE id = ?"
        self._conn.execute(query, values)
        self._conn.commit()

    def list_servers(self) -> List[Dict[str, object]]:
        cur = self._conn.execute(
            "SELECT id, url, name, cache_timestamp, last_sync FROM servers ORDER BY url"
        )
        return [dict(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Tool persistence
    # ------------------------------------------------------------------
    def upsert_tool(
        self,
        server_id: int,
        tool_id: str,
        descriptor: Dict[str, object],
        *,
        description: str,
        when_to_use: Optional[str],
        languages: Sequence[str],
        tags: Sequence[str],
    ) -> str:
        descriptor_json = json.dumps(descriptor, sort_keys=True, ensure_ascii=False)
        version_hash = hashlib.sha256(descriptor_json.encode("utf-8")).hexdigest()

        self._conn.execute(
            """
            INSERT INTO tools (
                server_id, tool_id, version_hash, descriptor,
                description, when_to_use, languages, tags, active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(server_id, tool_id) DO UPDATE SET
                version_hash = excluded.version_hash,
                descriptor = excluded.descriptor,
                description = excluded.description,
                when_to_use = excluded.when_to_use,
                languages = excluded.languages,
                tags = excluded.tags,
                active = 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                server_id,
                tool_id,
                version_hash,
                descriptor_json,
                description,
                when_to_use,
                json.dumps(list(languages), ensure_ascii=False),
                json.dumps(list(tags), ensure_ascii=False),
            ),
        )
        self._conn.commit()
        return version_hash

    def mark_inactive(self, server_id: int, active_tool_ids: Iterable[str]) -> None:
        active_set = set(active_tool_ids)
        placeholders = ",".join("?" for _ in active_set)
        params: List[object] = [server_id]
        query = "UPDATE tools SET active = 0 WHERE server_id = ? AND active = 1"
        if active_set:
            query += f" AND tool_id NOT IN ({placeholders})"
            params.extend(active_set)
        self._conn.execute(query, params)
        self._conn.commit()

    def fetch_records(
        self,
        *,
        server_urls: Optional[Sequence[str]] = None,
        tool_ids: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, object]]:
        query = (
            "SELECT t.tool_id, t.descriptor, t.description, t.when_to_use, "
            "t.languages, t.tags, s.url AS source "
            "FROM tools t JOIN servers s ON s.id = t.server_id "
            "WHERE t.active = 1"
        )
        params: List[object] = []
        if server_urls:
            placeholders = ",".join("?" for _ in server_urls)
            query += f" AND s.url IN ({placeholders})"
            params.extend(server_urls)
        if tool_ids:
            placeholders = ",".join("?" for _ in tool_ids)
            query += f" AND t.tool_id IN ({placeholders})"
            params.extend(tool_ids)
        query += " ORDER BY s.url, t.tool_id"

        cursor = self._conn.execute(query, params)
        records: List[Dict[str, object]] = []
        for row in cursor.fetchall():
            descriptor = json.loads(row["descriptor"])
            languages = json.loads(row["languages"]) if row["languages"] else []
            tags = json.loads(row["tags"]) if row["tags"] else []
            records.append(
                {
                    "tool_id": row["tool_id"],
                    "descriptor": descriptor,
                    "description": row["description"],
                    "when_to_use": row["when_to_use"],
                    "languages": languages,
                    "tags": tags,
                    "source": row["source"],
                    "schema_version": str(descriptor.get("schema_version") or "1.0.0"),
                }
            )
        return records
    def record_feedback(
        self,
        *,
        server_url: str,
        tool_id: str,
        outcome: str,
        detail: Optional[str] = None,
    ) -> None:
        if outcome not in {'success', 'error'}:
            raise ValueError("outcome must be 'success' or 'error'")
        server_id = self.register_server(server_url)
        self._conn.execute("INSERT INTO feedback (server_id, tool_id, outcome, detail) VALUES (?, ?, ?, ?)", (server_id, tool_id, outcome, detail))
        self._conn.commit()

    def feedback_summary(self) -> Dict[str, Dict[str, int]]:
        query = (
            "SELECT s.url AS server_url, f.tool_id, "
            "       SUM(CASE WHEN f.outcome = 'success' THEN 1 ELSE 0 END) AS success_count, "
            "       SUM(CASE WHEN f.outcome = 'error' THEN 1 ELSE 0 END) AS error_count "
            "FROM feedback f JOIN servers s ON s.id = f.server_id "
            "GROUP BY s.url, f.tool_id"
        )
        cur = self._conn.execute(query)
        summary: Dict[str, Dict[str, int]] = {}
        for row in cur.fetchall():
            key = f"{row['server_url']}::{row['tool_id']}"
            summary[key] = {
                'success': int(row['success_count'] or 0),
                'error': int(row['error_count'] or 0),
            }
        return summary

    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def bootstrap_records(self) -> List[Dict[str, object]]:
        return self.fetch_records()
