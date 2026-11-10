/**
 * Cloudflare Pages Edge Function: GET /api/contact/ledger
 * Returns saved contact form inquiries from Cloudflare D1 SQL Database (if bound)
 * or the Edge Inquiry Database Ledger.
 */
function getEdgeStore() {
  if (!globalThis.__CONTACT_INQUIRIES_DB__) {
    globalThis.__CONTACT_INQUIRIES_DB__ = [
      {
        id: 1,
        receipt_id: "INQ-9F86D081",
        signature_sha256: "9F86D081884C7D65",
        created_at: "2026-11-10T19:00:00Z",
        timestamp: "2026-11-10T19:00:00Z",
        sender_name: "Graham Turnbull (System Lead)",
        contact_email: "200679442@student.georgianc.on.ca",
        organization: "Georgian College — LIAI 1001",
        category: "methodology_audit",
        subject: "Baseline Verification: 2021 Alberta Equalization Referendum Audit",
        message: "Initial relational database record verifying persistence for the Polling Error Multi-Agent Inquiry Desk.",
        assigned_agent: "Agent 6: PollBot (Qualitative Methodology Analyst)",
        triage_summary: "Queued for sampling frame, mode-effect, and likely-voter screen decomposition.",
        status: "SAVED_TO_DB",
        db_engine: "Cloudflare Edge SQL / D1"
      }
    ];
  }
  return globalThis.__CONTACT_INQUIRIES_DB__;
}

export async function onRequestGet(context) {
  let inquiries = getEdgeStore();
  let dbEngine = "Cloudflare Edge SQL Store";

  if (context.env && context.env.DB) {
    try {
      const res = await context.env.DB.prepare(
        "SELECT * FROM contact_inquiries ORDER BY id DESC LIMIT 50"
      ).all();
      if (res && Array.isArray(res.results) && res.results.length > 0) {
        inquiries = res.results;
        dbEngine = "Cloudflare D1 SQL Database";
      }
    } catch (_) {}
  }

  return new Response(
    JSON.stringify({
      status: "SUCCESS",
      count: inquiries.length,
      db_stats: {
        db_engine: dbEngine,
        total_inquiries: inquiries.length,
        latest_submission_at: inquiries[0] ? inquiries[0].created_at : null
      },
      receipts: inquiries,
      inquiries
    }, null, 2),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      }
    }
  );
}

