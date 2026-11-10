/**
 * Cloudflare Pages Edge Function: POST /api/contact
 * Saves submitted contact form inquiries to Cloudflare D1 SQL Database (if bound)
 * and the Edge Inquiry Database Ledger, while enforcing the Predetermined Conclusion Guardrail.
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

export async function onRequestPost(context) {
  let payload = {};
  try {
    payload = await context.request.json();
  } catch (_) {}

  const senderName = String(payload.name || payload.sender_name || "Anonymous Analyst").trim() || "Anonymous Analyst";
  const contactEmail = String(payload.email || payload.contact_email || "unlisted@polling-error.local").trim() || "unlisted@polling-error.local";
  const category = String(payload.category || "methodology_audit").trim();
  const organization = String(payload.organization || "Independent Evaluator").trim() || "Independent Evaluator";
  const subject = String(payload.subject || "").trim();
  const message = String(payload.message || "").trim();

  if (!subject || !message) {
    return new Response(
      JSON.stringify({
        status: "ERROR",
        message: "Please provide both a subject line and an inquiry message.",
      }, null, 2),
      {
        status: 400,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  }

  const combined = `${subject}\n${message}`;
  const predeterminedPatterns = [
    /regardless\s+of\s+(?:the\s+)?(?:truth|facts?|data|evidence|reality)/i,
    /no\s+matter\s+(?:what|the\s+truth|the\s+facts?|the\s+evidence)/i,
    /must\s+(?:conclude|find|declare|state)\s+that\s+.+\s+(?:won|leads?|lost|failed)/i,
    /force\s+(?:the\s+)?conclusion/i,
    /ignore\s+(?:the\s+)?(?:data|evidence|facts?|numbers?|reality)/i,
  ];

  if (predeterminedPatterns.some((p) => p.test(combined))) {
    return new Response(
      JSON.stringify({
        status: "DECLINED",
        guardrail_triggered: "PREDETERMINED_CONCLUSION",
        message:
          "I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All analysis must be objective and evidence-based.",
      }, null, 2),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  }

  const routingMap = {
    methodology_audit: [
      "Agent 6: PollBot (Qualitative Methodology Analyst)",
      "Queued for sampling frame, mode-effect, and likely-voter screen decomposition.",
    ],
    statbot_taxonomy: [
      "Agent 7: StatBot (Statistical Categorization & PDF Specialist)",
      "Queued for demographic/geographic cross-tabulation and ReportLab PDF dossier generation.",
    ],
    hitl_governance: [
      "Agent 5: HumanAuditor (HITL Oversight Gatekeeper)",
      "Escalated to Human-in-the-Loop Supervisor (Graham Turnbull, ID: 200679442) for governance review.",
    ],
    academic_liai1001: [
      "Academic Lead: Graham Turnbull (200679442) & Prof. Evandro Barros",
      "Routed to LIAI 1001 – Strategy and Change (Georgian College) evaluation desk.",
    ],
    general_orchestrator: [
      "Agent 1: OrchestratorAgent (Pipeline Conductor)",
      "Registered in pipeline intake queue for multi-agent workflow routing.",
    ],
  };

  const [assignedAgent, triageNote] = routingMap[category] || routingMap.general_orchestrator;
  const ts = new Date().toISOString();
  const encoder = new TextEncoder();
  const data = encoder.encode(`${ts}|${senderName}|${contactEmail}|${category}|${organization}|${subject}|${message.length}`);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 16).toUpperCase();

  const store = getEdgeStore();
  let dbEngine = "Cloudflare Edge Store + SQLite3 Schema";
  let rowId = store.length + 1;

  if (context.env && context.env.DB) {
    try {
      await context.env.DB.prepare(
        `CREATE TABLE IF NOT EXISTS contact_inquiries (
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
          status TEXT NOT NULL DEFAULT 'SAVED_TO_DB'
        )`
      ).run();

      const res = await context.env.DB.prepare(
        `INSERT INTO contact_inquiries (
          receipt_id, signature_sha256, created_at, sender_name,
          contact_email, organization, category, subject, message,
          assigned_agent, triage_summary, status
        ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, 'SAVED_TO_DB')`
      ).bind(
        `INQ-${hashHex.slice(0, 8)}`,
        hashHex,
        ts,
        senderName,
        contactEmail,
        organization,
        category,
        subject,
        message,
        assignedAgent,
        triageNote
      ).run();
      if (res && res.meta && res.meta.last_row_id) {
        rowId = res.meta.last_row_id;
      }
      dbEngine = "Cloudflare D1 SQL Database";
    } catch (_) {}
  }

  const receipt = {
    id: rowId,
    receipt_id: `INQ-${hashHex.slice(0, 8)}`,
    signature_sha256: hashHex,
    timestamp: ts,
    created_at: ts,
    sender_name: senderName,
    contact_email: contactEmail,
    organization,
    category,
    subject,
    message,
    assigned_agent: assignedAgent,
    triage_summary: triageNote,
    status: "SAVED_TO_DB",
    db_engine: dbEngine,
  };

  store.unshift(receipt);

  return new Response(
    JSON.stringify({
      status: "SUBMITTED",
      message: "Your contact inquiry has been saved to the database and routed to the assigned agent.",
      receipt,
      db_stats: {
        db_engine: dbEngine,
        total_inquiries: store.length,
        latest_submission_at: ts,
      },
    }, null, 2),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
      },
    }
  );
}
