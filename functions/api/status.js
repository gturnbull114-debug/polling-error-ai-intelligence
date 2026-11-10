/**
 * Cloudflare Pages Function: GET /api/status
 * Program: "Polling Error" — AI Polling Intelligence Agentic System (LIAI 1001)
 */
export async function onRequestGet() {
  const payload = {
    status: "ONLINE",
    environment: "Cloudflare Pages Edge Runtime",
    program: "Polling Error — AI Polling Intelligence Agentic System",
    course: "LIAI 1001 – Strategy and Change (Georgian College)",
    student: "Graham Turnbull (200679442)",
    instructor: "Prof. Evandro Barros",
    timestamp: new Date().toISOString(),
    capabilities: {
      anthropic_connected: true,
      active_model: "claude-haiku-4-5-20251001",
      serpapi_available: true,
      reportlab_pdf_engine: true,
      deterministic_fallback: true,
      zero_pii_contact_triage: true
    },
    endpoints: [
      "GET /api/status",
      "POST /api/pipeline/run",
      "POST /api/hitl/decision",
      "POST /api/pollbot/chat",
      "POST /api/statbot/categorize",
      "POST /api/sequential/run",
      "POST /api/collaborate/run",
      "POST /api/prompter/validate",
      "POST /api/contact"
    ],
    available_pdfs: [
      "statbot_categorized_findings.pdf",
      "sequential_pipeline_report.pdf",
      "collaborative_intelligence_report.pdf"
    ],
    agents: [
      { id: 1, name: "OrchestratorAgent", role: "Workflow Manager & Pipeline Conductor", autonomy: "High", status: "READY" },
      { id: 2, name: "NormalizerAgent", role: "Data Hygiene, Schema Validation & Mode Standardization", autonomy: "High", status: "READY" },
      { id: 3, name: "ModelerAgent", role: "Bayesian Consensus Synthesis & Outlier Detection", autonomy: "Medium", status: "READY" },
      { id: 4, name: "ExplainerAgent", role: "Causal Explanation & Margin-of-Error Decomposition", autonomy: "Medium", status: "READY" },
      { id: 5, name: "HumanAuditor", role: "Human-in-the-Loop (HITL) Gatekeeper (>3.5% Divergence)", autonomy: "Supervisory", status: "STANDBY" },
      { id: 6, name: "PollBot", role: "Anthropic Claude Qualitative Analyst + SerpApi Research", autonomy: "High", status: "READY" },
      { id: 7, name: "StatBot", role: "Statistical Categorization & ReportLab PDF Specialist", autonomy: "High", status: "READY" },
      { id: 8, name: "PollingIntelligenceCollaborator", role: "Sequential & Bidirectional Multi-Agent Coordinator", autonomy: "High", status: "READY" },
      { id: 9, name: "PollingErrorPrompter", role: "Prompt Engineering, Guardrail Pre-Screener & Teleprompter", autonomy: "Interactive", status: "READY" }
    ]
  };

  return new Response(JSON.stringify(payload, null, 2), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
