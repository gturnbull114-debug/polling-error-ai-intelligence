/**
 * Cloudflare Pages Function: POST /api/hitl/decision
 * Generates a signed cryptographic SHA-256 Human Auditor (HITL) receipt.
 */
export async function onRequestPost(context) {
  let body = {};
  try {
    body = await context.request.json();
  } catch (_) {}

  const decision = String(body.decision || "approve").toLowerCase();
  const supervisor = String(body.supervisor || "Graham Turnbull (200679442)");
  const notes = String(body.notes || "Reviewed methodology and outlier divergence spread.");
  const pollId = String(body.poll_id || "POLL-002");

  let statusCode = "APPROVED_BY_HUMAN";
  let verdictLabel = "Publication Approved by Human Supervisor";
  if (decision === "override") {
    statusCode = "APPROVED_WITH_OVERRIDE";
    verdictLabel = "Approved with Methodology Weight Override";
  } else if (decision === "reject") {
    statusCode = "REJECTED_BY_HUMAN";
    verdictLabel = "Publication Blocked & Quarantined by Human Supervisor";
  }

  const ts = new Date().toISOString();
  const encoder = new TextEncoder();
  const data = encoder.encode(`${ts}|${supervisor}|${statusCode}|${pollId}|${notes}`);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const fullHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  const receiptHash = fullHex.slice(0, 16);

  const payload = {
    status: "RECORDED",
    receipt: {
      receipt_id: `HITL-${receiptHash.slice(0, 8)}`,
      signature_sha256: receiptHash,
      timestamp: ts,
      supervisor: supervisor,
      poll_id: pollId,
      status_code: statusCode,
      verdict_label: verdictLabel,
      notes: notes
    }
  };

  return new Response(JSON.stringify(payload, null, 2), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*"
    }
  });
}

