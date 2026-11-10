"""SQLite3 Relational Database Engine for Contact & Analyst Inquiries (`src/web/contact_db.py`).

Program: "Polling Error" — AI Polling Intelligence Agentic System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Persists submitted contact form inquiries, multi-agent triage routing assignments,
and cryptographic SHA-256 receipts into `data/contact_inquiries.db`.
"""

from __future__ import annotations
import contextlib
import datetime
import hashlib
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS contact_inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id TEXT UNIQUE NOT NULL,
    signature_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    organization TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    assigned_agent TEXT NOT NULL,
    triage_summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'VERIFIED'
);

CREATE INDEX IF NOT EXISTS idx_contact_inquiries_created_at
    ON contact_inquiries (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_contact_inquiries_category
    ON contact_inquiries (category);
"""


class ContactDatabase:
    """Relational SQLite3 database manager for website contact form submissions."""

    def __init__(self, db_path: Optional[Path] = None, seed_initial: bool = True):
        """Initialize the SQLite database file and schema."""
        self.db_path = db_path or (Path.cwd() / "data" / "contact_inquiries.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        if seed_initial:
            self._seed_initial_record_if_empty()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite3 connection with Row factory enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Ensure the `contact_inquiries` table and indexes exist."""
        with contextlib.closing(self._connect()) as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def _seed_initial_record_if_empty(self) -> None:
        """Insert a default academic verification record if the table has 0 rows."""
        with contextlib.closing(self._connect()) as conn:
            cur = conn.execute("SELECT COUNT(*) AS cnt FROM contact_inquiries")
            row = cur.fetchone()
            if row and row["cnt"] == 0:
                ts = "2026-11-10T19:00:00+00:00"
                sig = hashlib.sha256(
                    f"{ts}|methodology_audit|Georgian College — LIAI 1001|Initial Database Verification".encode("utf-8")
                ).hexdigest()[:16].upper()
                conn.execute(
                    """
                    INSERT INTO contact_inquiries (
                        receipt_id, signature_sha256, created_at, sender_name,
                        contact_email, organization, category, subject, message,
                        assigned_agent, triage_summary, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"INQ-{sig[:8]}",
                        sig,
                        ts,
                        "Graham Turnbull (System Lead)",
                        "200679442@student.georgianc.on.ca",
                        "Georgian College — LIAI 1001",
                        "methodology_audit",
                        "Baseline Verification: 2021 Alberta Equalization Referendum Audit",
                        "Initial relational database record verifying SQLite3 persistence for the Polling Error Multi-Agent Inquiry Desk.",
                        "Agent 6: PollBot (Qualitative Methodology Analyst)",
                        "Queued for sampling frame, mode-effect, and likely-voter screen decomposition.",
                        "VERIFIED",
                    ),
                )
                conn.commit()

    def insert_inquiry(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a validated contact inquiry into `contact_inquiries` and return the stored row."""
        ts = str(record.get("timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat())
        sender_name = str(record.get("sender_name") or record.get("name") or "Anonymous Analyst").strip()
        contact_email = str(record.get("contact_email") or record.get("email") or "unlisted@polling-error.local").strip()
        organization = str(record.get("organization") or "Independent Evaluator").strip()
        category = str(record.get("category") or "methodology_audit").strip()
        subject = str(record.get("subject") or "").strip()
        message = str(record.get("message") or "").strip()
        assigned_agent = str(record.get("assigned_agent") or "Agent 1: OrchestratorAgent").strip()
        triage_summary = str(record.get("triage_summary") or "Registered in pipeline intake queue.").strip()
        status = str(record.get("status") or "VERIFIED").strip()

        sig_payload = f"{ts}|{sender_name}|{contact_email}|{category}|{organization}|{subject}|{len(message)}"
        signature_sha256 = str(
            record.get("signature_sha256")
            or hashlib.sha256(sig_payload.encode("utf-8")).hexdigest()[:16].upper()
        )
        receipt_id = str(record.get("receipt_id") or f"INQ-{signature_sha256[:8]}")

        with contextlib.closing(self._connect()) as conn:
            cursor = conn.execute(
                """
                INSERT INTO contact_inquiries (
                    receipt_id, signature_sha256, created_at, sender_name,
                    contact_email, organization, category, subject, message,
                    assigned_agent, triage_summary, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    signature_sha256,
                    ts,
                    sender_name,
                    contact_email,
                    organization,
                    category,
                    subject,
                    message,
                    assigned_agent,
                    triage_summary,
                    status,
                ),
            )
            conn.commit()
            row_id = cursor.lastrowid

        return {
            "id": row_id,
            "receipt_id": receipt_id,
            "signature_sha256": signature_sha256,
            "timestamp": ts,
            "created_at": ts,
            "sender_name": sender_name,
            "contact_email": contact_email,
            "organization": organization,
            "category": category,
            "subject": subject,
            "message": message,
            "assigned_agent": assigned_agent,
            "triage_summary": triage_summary,
            "status": status,
            "db_engine": "SQLite3",
            "db_file": str(self.db_path.name),
        }

    def list_inquiries(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve saved contact form inquiries ordered newest-first."""
        with contextlib.closing(self._connect()) as conn:
            if category:
                cur = conn.execute(
                    """
                    SELECT * FROM contact_inquiries
                    WHERE category = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (category, limit),
                )
            else:
                cur = conn.execute(
                    """
                    SELECT * FROM contact_inquiries
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def get_inquiry_by_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single inquiry record by its `receipt_id`."""
        with contextlib.closing(self._connect()) as conn:
            cur = conn.execute(
                "SELECT * FROM contact_inquiries WHERE receipt_id = ?",
                (receipt_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_stats(self) -> Dict[str, Any]:
        """Return summary statistics for the contact inquiries SQLite database."""
        with contextlib.closing(self._connect()) as conn:
            total_row = conn.execute("SELECT COUNT(*) AS total FROM contact_inquiries").fetchone()
            total = int(total_row["total"]) if total_row else 0

            cat_rows = conn.execute(
                "SELECT category, COUNT(*) AS cnt FROM contact_inquiries GROUP BY category"
            ).fetchall()
            by_category = {r["category"]: int(r["cnt"]) for r in cat_rows}

            latest_row = conn.execute(
                "SELECT created_at FROM contact_inquiries ORDER BY id DESC LIMIT 1"
            ).fetchone()
            latest_at = latest_row["created_at"] if latest_row else None

        return {
            "db_engine": "SQLite3",
            "db_path": str(self.db_path),
            "total_inquiries": total,
            "by_category": by_category,
            "latest_submission_at": latest_at,
        }
