-- ============================================================================
-- "Polling Error" Multi-Agent System — Contact Inquiries SQL Schema
-- Compatible with SQLite3 (`data/contact_inquiries.db`) and Cloudflare D1
-- Course: LIAI 1001 – Strategy and Change (Georgian College)
-- Student: Graham Turnbull (200679442)
-- ============================================================================

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

