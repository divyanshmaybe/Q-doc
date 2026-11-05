"""
Database management for Q-Doc MVP.
Manages sessions, turns, images, predictions, policy_decisions, and briefs tables.
Uses connection context manager ensuring WAL mode and clean resource disposal.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "qdoc.db"))

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

@contextmanager
def db_session():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'hi-IN',
            mode TEXT NOT NULL DEFAULT 'autonomous',
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            turn_index INTEGER NOT NULL,
            speaker TEXT NOT NULL,
            transcript TEXT NOT NULL,
            slots_json TEXT NOT NULL DEFAULT '{}',
            timestamp TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            quality_score REAL NOT NULL,
            blur_score REAL NOT NULL,
            brightness_score REAL NOT NULL,
            quality_passed INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            image_id TEXT NOT NULL,
            top_condition TEXT NOT NULL,
            confidence REAL NOT NULL,
            differential_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            action TEXT NOT NULL,
            abstain INTEGER NOT NULL,
            urgency TEXT NOT NULL,
            spoken_patient_message TEXT NOT NULL,
            applied_rules_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS briefs (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL UNIQUE,
            brief_json TEXT NOT NULL,
            doctor_approved INTEGER DEFAULT NULL,
            doctor_notes TEXT DEFAULT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)
        conn.commit()

init_db()

class DatabaseRepo:
    get_connection = staticmethod(get_connection)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def create_session(cls, session_id: str, language: str = "hi-IN", mode: str = "autonomous") -> Dict[str, Any]:
        now = cls.now_iso()
        with db_session() as conn:
            with conn:
                conn.execute(
                    "INSERT INTO sessions (id, language, mode, status, created_at, updated_at) VALUES (?, ?, ?, 'active', ?, ?)",
                    (session_id, language, mode, now, now)
                )
        return {"id": session_id, "language": language, "mode": mode, "status": "active", "created_at": now}

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        with db_session() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            return dict(row) if row else None

    @classmethod
    def update_session_mode(cls, session_id: str, mode: str) -> None:
        with db_session() as conn:
            with conn:
                conn.execute("UPDATE sessions SET mode = ?, updated_at = ? WHERE id = ?", (mode, cls.now_iso(), session_id))

    @classmethod
    def update_session_language(cls, session_id: str, language: str) -> None:
        with db_session() as conn:
            with conn:
                conn.execute("UPDATE sessions SET language = ?, updated_at = ? WHERE id = ?", (language, cls.now_iso(), session_id))

    @classmethod
    def log_turn(cls, session_id: str, turn_index: int, speaker: str, transcript: str, slots_json: str) -> None:
        with db_session() as conn:
            with conn:
                conn.execute(
                    "INSERT INTO turns (session_id, turn_index, speaker, transcript, slots_json, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, turn_index, speaker, transcript, slots_json, cls.now_iso())
                )

    @classmethod
    def get_session_turns(cls, session_id: str) -> List[Dict[str, Any]]:
        with db_session() as conn:
            rows = conn.execute("SELECT * FROM turns WHERE session_id = ? ORDER BY turn_index ASC", (session_id,)).fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d["slots"] = json.loads(d["slots_json"])
                res.append(d)
            return res

    @classmethod
    def save_image_record(
        cls,
        image_id: str,
        session_id: str,
        file_path: str,
        quality_score: float,
        blur_score: float,
        brightness_score: float,
        quality_passed: bool
    ) -> None:
        with db_session() as conn:
            with conn:
                conn.execute(
                    """INSERT INTO images (
                        id, session_id, file_path, quality_score, blur_score, brightness_score, quality_passed, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        image_id, session_id, file_path, quality_score,
                        blur_score, brightness_score, 1 if quality_passed else 0, cls.now_iso()
                    )
                )

    @classmethod
    def log_prediction(cls, session_id: str, image_id: str, top_cond: str, conf: float, differential: List[Dict[str, Any]]) -> None:
        with db_session() as conn:
            with conn:
                conn.execute(
                    "INSERT INTO predictions (session_id, image_id, top_condition, confidence, differential_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, image_id, top_cond, conf, json.dumps(differential), cls.now_iso())
                )

    @classmethod
    def log_policy_decision(
        cls,
        session_id: str,
        mode: str,
        action: str,
        abstain: bool,
        urgency: str,
        spoken_msg: str,
        applied_rules: List[str]
    ) -> None:
        with db_session() as conn:
            with conn:
                conn.execute(
                    """INSERT INTO policy_decisions (
                        session_id, mode, action, abstain, urgency, spoken_patient_message, applied_rules_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        session_id, mode, action, 1 if abstain else 0, urgency,
                        spoken_msg, json.dumps(applied_rules), cls.now_iso()
                    )
                )

    @classmethod
    def save_brief(cls, session_id: str, brief_data: Dict[str, Any]) -> str:
        brief_id = f"brief_{session_id}"
        with db_session() as conn:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO briefs (id, session_id, brief_json, created_at) VALUES (?, ?, ?, ?)",
                    (brief_id, session_id, json.dumps(brief_data), cls.now_iso())
                )
        return brief_id

    @classmethod
    def get_brief(cls, brief_id: str) -> Optional[Dict[str, Any]]:
        with db_session() as conn:
            row = conn.execute("SELECT * FROM briefs WHERE id = ?", (brief_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["brief_data"] = json.loads(d["brief_json"])
            return d

    @classmethod
    def list_briefs(cls) -> List[Dict[str, Any]]:
        with db_session() as conn:
            rows = conn.execute("SELECT b.*, s.language, s.mode FROM briefs b JOIN sessions s ON b.session_id = s.id ORDER BY b.created_at DESC").fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d["brief_data"] = json.loads(d["brief_json"])
                res.append(d)
            return res

    @classmethod
    def update_brief_review(cls, brief_id: str, approved: bool, notes: str) -> None:
        with db_session() as conn:
            with conn:
                conn.execute(
                    "UPDATE briefs SET doctor_approved = ?, doctor_notes = ? WHERE id = ?",
                    (1 if approved else 0, notes, brief_id)
                )
