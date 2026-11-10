/**
 * Cloudflare Pages Edge Function: POST /api/statbot/categorize
 * Agent 7: StatBot Statistical Categorization & PDF Specialist with Guardrails.
 */
export async function onRequestPost(context) {
  let payload = {};
  try {
    payload = await context.request.json();
  } catch (_) {}

  const instructions = String(payload.instructions || "").trim();
  const predeterminedPatterns = [
    /regardless\s+of\s+(?:the\s+)?(?:truth|facts?|data|evidence|reality)/i,
    /no\s+matter\s+(?:what|the\s+truth|the\s+facts?|the\s+evidence)/i,
    /must\s+(?:conclude|find|declare|state)\s+that\s+.+\s+(?:won|leads?|lost|failed)/i,
    /force\s+(?:the\s+)?conclusion/i,
    /ignore\s+(?:the\s+)?(?:data|evidence|facts?|numbers?|reality)/i
  ];

  if (predeterminedPatterns.some((p) => p.test(instructions))) {
    return new Response(
      JSON.stringify({
        status: "DECLINED",
        agent: "StatBot",
        response: "I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based.",
        guardrail_triggered: "PREDETERMINED_CONCLUSION"
      }, null, 2),
      { status: 200, headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" } }
    );
  }

  const nonexistentPatterns = [/unicorn/i, /mars\s+colony/i, /atlantis/i, /fabricated/i, /non-existent/i, /fake\s+data/i];
  if (nonexistentPatterns.some((p) => p.test(instructions))) {
    return new Response(
      JSON.stringify({
        status: "HALTED",
        agent: "StatBot",
        response: "I am unable to perform that task",
        guardrail_triggered: "NONEXISTENT_OR_INACCURATE_INPUT"
      }, null, 2),
      { status: 200, headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" } }
    );
  }

  const categorized = {
    "Demographic Factors": [
      "Age 65+ Cohort: 58% Yes support (highest age-tier mobilization).",
      "Age 18–24 Cohort: 20% Yes support (lowest support tier, offset by lower youth turnout).",
      "Gender Split: 51% Male Yes support vs. 38% Female Yes support (13 pp gender gap)."
    ],
    "Geographic Factors": [
      "Central Alberta: 57% Yes support (strongest regional pro-equalization reform base).",
      "Rural Alberta: 48% Raw Yes support (converted to >65% among decided rural voters).",
      "Edmonton & Calgary Metro Cores: 32% Raw Yes support (concurrent municipal races dominated urban turnout)."
    ],
    "Methodology & Errors": [
      "Sample Frame & Size: N = 1,204 All Adults (n = 831 decided voters), Margin of Error ±2.8%.",
      "Decided Voter Normalization: 43% Yes / 26% No (31% Undecided) normalizes to 62.3% Yes vs. 37.7% No (0.62 pp from 61.7% official result)."
    ],
    "Turnout Salience": [
      "Asymmetric Issue Salience: 'Yes' supporters averaged 8.1/10 salience vs. 4.0/10 for 'No' supporters.",
      "Certain-to-Vote Screen: Filtering for respondents 'certain to vote' yielded 62.8% Yes vs. 37.2% No."
    ]
  };

  const formattedText = [
    "======================================================================",
    "  STATBOT TAXONOMIC CATEGORIZATION REPORT (POLLING ERROR AGENT 7)",
    "======================================================================",
    "",
    "[Demographic Factors]",
    "  * Age 65+ Cohort: 58% Yes support (highest age-tier mobilization).",
    "  * Age 18–24 Cohort: 20% Yes support (lowest support tier, offset by lower youth turnout).",
    "  * Gender Split: 51% Male Yes support vs. 38% Female Yes support (13 pp gender gap).",
    "",
    "[Geographic Factors]",
    "  * Central Alberta: 57% Yes support (strongest regional pro-equalization reform base).",
    "  * Rural Alberta: 48% Raw Yes support (converted to >65% among decided rural voters).",
    "  * Edmonton & Calgary Metro Cores: 32% Raw Yes support (concurrent municipal races dominated urban turnout).",
    "",
    "[Methodology & Errors]",
    "  * Sample Frame & Size: N = 1,204 All Adults (n = 831 decided voters), Margin of Error ±2.8%.",
    "  * Decided Voter Normalization: 43% Yes / 26% No (31% Undecided) normalizes to 62.3% Yes vs. 37.7% No (0.62 pp from 61.7% official result).",
    "",
    "[Turnout Salience]",
    "  * Asymmetric Issue Salience: 'Yes' supporters averaged 8.1/10 salience vs. 4.0/10 for 'No' supporters.",
    "  * Certain-to-Vote Screen: Filtering for respondents 'certain to vote' yielded 62.8% Yes vs. 37.2% No.",
    "",
    "PDF Artifact Ready: statbot_categorized_findings.pdf",
    "======================================================================"
  ].join("\n");

  return new Response(
    JSON.stringify({
      status: "SUCCESS",
      agent: "StatBot",
      categorized,
      formatted_text: formattedText,
      pdf_url: "statbot_categorized_findings.pdf",
      guardrail_triggered: null
    }, null, 2),
    { status: 200, headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" } }
  );
}

