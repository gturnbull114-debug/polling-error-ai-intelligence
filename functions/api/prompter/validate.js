/**
 * Cloudflare Pages Edge Function: POST /api/prompter/validate
 * Agent 9: PollingErrorPrompter Guardrail Pre-Screener & Directive Builder.
 */
export async function onRequestPost(context) {
  let payload = {};
  try {
    payload = await context.request.json();
  } catch (_) {}

  const promptText = String(payload.prompt || "").trim();
  const agent = String(payload.agent || "statbot").trim().toLowerCase();
  const categories = payload.categories || "Demographic Factors, Geographic Factors, Methodology & Errors, Turnout Salience";

  const predeterminedPatterns = [
    /regardless\s+of\s+(?:the\s+)?(?:truth|facts?|data|evidence|reality)/i,
    /no\s+matter\s+(?:what|the\s+truth|the\s+facts?|the\s+evidence)/i,
    /must\s+(?:conclude|find|declare|state)\s+that\s+.+\s+(?:won|leads?|lost|failed)/i,
    /force\s+(?:the\s+)?conclusion/i,
    /ignore\s+(?:the\s+)?(?:data|evidence|facts?|numbers?|reality)/i
  ];

  const hasPredetermined = predeterminedPatterns.some((p) => p.test(promptText));
  const validation = {
    is_valid: !hasPredetermined && promptText.length > 0,
    predetermined_conclusion_detected: hasPredetermined,
    status: hasPredetermined ? "DECLINED_PREDETERMINED_CONCLUSION" : "APPROVED"
  };

  const composed = [
    "======================================================================",
    "[POLLING ERROR PROMPTER DIRECTIVE — AGENT 9]",
    "======================================================================",
    `Target Agent: ${agent.toUpperCase()}`,
    `Categories:   ${Array.isArray(categories) ? categories.join(", ") : categories}`,
    `Guardrail:    ${validation.status}`,
    "Guiding Instructions:",
    promptText,
    "======================================================================"
  ].join("\n");

  return new Response(
    JSON.stringify({
      status: "SUCCESS",
      validation,
      agent,
      composed_directive: composed
    }, null, 2),
    { status: 200, headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" } }
  );
}

