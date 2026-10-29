# AGENTS.md — Polling Error: AI Polling Intelligence Agentic System Guidelines

**Program Name:** "Polling Error" Multi-Agent Polling Intelligence System  
**Course:** LIAI 1001 – Strategy and Change: Agentic AI Solution Assignment  
**Academic Program:** Artificial Intelligence Leadership and Management Program, Georgian College  
**Instructor:** Prof. Evandro Barros  
**Student:** Graham Turnbull (Student ID: 200679442)  
**Workspace:** `Assignement LIAI 1001`

---

## 1. Project Purpose & Scope

### 1.1 Mission & Value Proposition
The **"Polling Error"** multi-agent program (AI Polling Intelligence Agentic System) provides an automated, multi-agent analytical layer that synthesizes election and opinion polling data. Beyond simply reporting a horse-race consensus, the system decomposes the underlying causal reasons why polls agree or disagree—analyzing sampling methodology, likely-voter screens, house effects, and timing—while maintaining an evidence-backed ledger of plausible polling-error mechanisms. Both **PollBot** and **StatBot** are core, specialized autonomous intelligence agents within the **"Polling Error"** program.

### 1.2 System Scope
- **What the Solution Does:**
  1. **Collect & Ingest:** Parses raw poll datasets (field dates, sample frames, methodology, sample size, question wording).
  2. **Normalize & Screen:** Adjusts sample weights based on population definitions, likely-voter screening criteria, and collection mode (live phone, IVR, online panel).
  3. **Statistical Modeling:** Computes consensus signals accounting for pollster correlations, time decay, and historical house bias.
  4. **Causal Explanation & Audit:** Formulates clear, plain-language causal hypotheses on movement versus statistical noise and audits non-sampling errors.
  5. **Human Oversight & Approval:** Integrates mandatory human checkpoints before publishing sensitive polling forecasts or outlier divergence reports.

- **What the Solution MUST NOT Do:**
  - **No Partisan Manipulation:** The system must never alter weights to favor any candidate, party, or ballot measure.
  - **No Fabricated Data:** Agents are strictly prohibited from generating synthetic or hallucinated poll results.
  - **No Autonomous High-Impact Publishing:** No polling analysis or alert exceeding divergence thresholds may be exported or published without explicit human approval.
  - **No Storage of PII:** Raw individual-level respondent identifying information must never be logged or stored.
  - **No Uncontrolled External API Calls:** Agents must only query whitelisted statistical APIs or validated local data sources.

---

## 2. Agent Roster (Agent Cards)

The multi-agent system comprises four specialized autonomous agents plus one mandatory Human-in-the-Loop checkpoint:

```
[ Raw Polling Data ]
        │
        ▼
┌────────────────────────────────────────┐
│      1. Orchestrator Agent             │
└───────┬────────────────────────┬───────┘
        │                        ▲
        ▼                        │ Status & Logs
┌────────────────────────┐       │
│  2. Ingestion &        │       │
│     Normalizer Agent   ├───────┤
└───────┬────────────────┘       │
        ▼                        │
┌────────────────────────┐       │
│  3. Statistical        │       │
│     Modeling Agent     ├───────┤
└───────┬────────────────┘       │
        ▼                        │
┌────────────────────────┐       │
│  4. Causal Explanation │       │
│     & Audit Agent      ├───────┘
└───────┬────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│  5. Human Oversight Checkpoint (HITL)  │  <--- [Approve / Reject / Override]
└───────┬────────────────────────────────┘
        │
        ▼
[ Verified Polling Intelligence Brief ]
```

### Agent Card 1: Orchestrator Agent (`OrchestratorAgent`)
- **Role:** Workflow manager and pipeline conductor.
- **Goal:** Direct execution flow, validate phase outputs, monitor agent execution timeouts, and enforce guardrails.
- **Inputs / Trigger:** CLI command, scheduled batch cron, or new raw poll JSON/CSV upload.
- **Tools & Data:** Pipeline state engine, error logger, configuration manager, execution timer.
- **Outputs:** Coordinated pipeline execution state, telemetry logs, and final assembled intelligence dossier.
- **Autonomy Level:** High (Acts alone within configured operational constraints).
- **Failure Handling:** If any downstream worker agent errors or exceeds timeout (60s), the orchestrator triggers graceful rollback, records error telemetry, and alerts human supervisor.

### Agent Card 2: Ingestion & Normalizer Agent (`NormalizerAgent`)
- **Role:** Data hygiene, schema validation, and methodology standardization.
- **Goal:** Transform heterogeneous pollster data into a unified, comparable statistical schema.
- **Inputs / Trigger:** Raw polling records (candidate shares, sample size, field dates, pollster name, methodology).
- **Tools & Data:** Schema validator (`pydantic`), date parsing utilities, methodology classification dictionary.
- **Outputs:** Normalized polling objects containing weighted sample sizes, date decay factors, and mode classifications.
- **Autonomy Level:** High (Autonomous data validation and normalization).
- **Failure Handling:** Flags malformed records or missing methodology metadata; isolates invalid rows into `quarantine_data/` without crashing the pipeline.

### Agent Card 3: Statistical Modeling Agent (`ModelerAgent`)
- **Role:** Bayesian consensus synthesis and house effect estimation.
- **Goal:** Calculate aggregate candidate standings, variance bands, and identify statistical outliers.
- **Inputs / Trigger:** Normalized poll records from `NormalizerAgent`.
- **Tools & Data:** Weighted moving average calculator, margin-of-error estimator, historical pollster house-effect matrix.
- **Outputs:** Polling signal metrics (consensus shares, margin-of-error spread, pollster divergence index).
- **Autonomy Level:** Medium (Proposes calculated consensus model for audit review).
- **Failure Handling:** If sample size is insufficient ($n < 3$ independent polls within window), flags low-confidence state and prevents over-interpretation.

### Agent Card 4: Causal Explanation & Audit Agent (`ExplainerAgent`)
- **Role:** Qualitative analysis, non-sampling error auditing, and briefing generator.
- **Goal:** Decompose why polls diverge (sample frame differences, likely-voter vs. registered-voter screens, weighting changes) and compile the evidence ledger.
- **Inputs / Trigger:** Statistical output and outlier indicators from `ModelerAgent`.
- **Tools & Data:** Causal template generator, margin-of-error decomposition matrix, error ledger recorder.
- **Outputs:** Executive Intelligence Brief (Markdown/JSON) highlighting consensus signal, plausible error mechanisms, and confidence audit.
- **Autonomy Level:** Medium (Drafts briefing for human verification).
- **Failure Handling:** If divergence cannot be attributed to known methodology factors, marks reasoning as "Unexplained Variance" for human investigation.

### Agent Card 5: Human Oversight Checkpoint (`HumanAuditor`)
- **Role:** Human-in-the-Loop (HITL) gatekeeper.
- **Goal:** Review flagged outlier divergence, inspect methodology assumptions, and approve or reject publication.
- **Inputs / Trigger:** Triggered automatically whenever outlier divergence $> 3.5\%$ or low confidence score is detected.
- **Tools & Data:** Interactive CLI prompt, approval dashboard, audit override log.
- **Outputs:** Cryptographically signed approval receipt or rejection notice with mandatory feedback notes.
- **Autonomy Level:** Advisory/Supervisory (Absolute authority over final report release).
- **Failure Handling:** Timeout or lack of human input defaults to "PENDING_APPROVAL" state; publication remains strictly blocked.

### Agent Card 6: PollBot AI Qualitative Analyst (`PollBot`)
- **Program Affiliation:** Core Qualitative Analyst in the **"Polling Error"** program.
- **Role:** LLM-powered polling intelligence agent using Anthropic Claude with real-time web research capabilities via SerpApi.
- **Goal:** Perform deep qualitative audits on methodology, assess mode effects, research pollster credibility in real-time, answer interactive analyst queries, and synthesize narrative reasoning within the "Polling Error" system.
- **Inputs / Trigger:** Outlier records from `ModelerAgent`, individual poll records, PDF reports, text/Markdown dossiers, live research queries (`--search`), or direct user chat prompt.
- **Tools & Data:** Anthropic Claude API (`claude-haiku-4-5-20251001` / `claude-sonnet-4-5-20250929`), SerpApi search tool (`src.tools.search_tool.SerpSearchTool`), PDF text extractor (`pypdf`), methodology decomposition prompts, conversation memory.
- **Outputs:** Detailed methodological audits, causal divergence narratives, real-time pollster research summaries, and executive markdown briefs.
- **Autonomy Level:** High (Acts under strict system prompt guardrails; strictly prohibited from modifying numbers, publishing unapproved alerts, or hallucinating unverified data).
- **Non-Repetition & Synergistic Collaboration Directive:** When collaborating with StatBot or building on StatBot's categorized findings, PollBot must never duplicate or repeat the categorized metrics, tables, or numbers already presented. It generates novel qualitative depth, causal explanations, strategic voter mobilization risks, and forward-looking implications on top of StatBot's foundation.
- **Predetermined Conclusion Guardrail:** Must immediately decline any request, prompt, or document that instructs or pressures it to reach a certain conclusion regardless of the truth, empirical facts, or verified data, outputting: `"I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All analysis must be objective and evidence-based."`
- **Transfer Reaffirmation Guardrail:** Before transferring any relevant polling intelligence from PollBot to StatBot, PollBot must require the user to reaffirm their request in an explicit prompt (`yes`/`no`). If the user does not reaffirm the request, execution halts and the transfer is cancelled immediately.
- **Domain Relevance Guardrail:** Before analyzing any document (PDF, text, JSON, or briefing), PollBot performs an automated pre-screening check to detect if the information relates to polling, surveys, or election voting data. If the document does not relate to polling, it terminates the prompt immediately and outputs `"Please provide relevant information"`.
- **Failure Handling:** If API keys (Anthropic or SerpApi) are unavailable, network errors occur, or data credibility criteria are not met, falls back gracefully to deterministic rule-based analysis and outputs "Answer Unavailable".

### Agent Card 7: StatBot Statistical Categorization Agent (`StatBot`)
- **Program Affiliation:** Core Taxonomy & Categorization Specialist in the **"Polling Error"** program.
- **Role:** Post-processing taxonomy and segmentation specialist.
- **Goal:** Maintain dedicated focus on the analytical results delivered by `PollBot` within the "Polling Error" program and systematically categorize and partition those results into the exact groups, taxonomies, or categories requested by the guiding prompt or user instructions (e.g. demographics, methodology, geographic zones, turnout salience, or custom prompter schemas).
- **Core Directives:**
  1. **Direct Focus on PollBot Results:** Anchor all classified points, figures, and insights directly in the outputs delivered by PollBot.
  2. **Adherence to Guiding Prompt / Instructions:** Strictly follow grouping rules, criteria, and category structures provided by the prompter.
  3. **Preservation of Statistical Rigor:** Maintain original percentages, sample sizes, and margins of error without alteration.
  4. **Non-Repetition & Synergistic Foundation:** Filter out redundant claims, partition statistical metrics cleanly into structured taxonomies, and isolate cross-cutting statistical gaps that PollBot builds upon in subsequent analysis.
  5. **Always-On PDF Report Placement:** Always compile categorized findings into an executive, publication-grade PDF dossier (`data/pollbot_to_statbot/statbot_categorized_findings.pdf`) and sync to workspace root for one-click downloading.
- **Inputs / Trigger:** PollBot analytical reports, qualitative briefings, transfer dossiers (`data/pollbot_to_statbot/`), live research queries (`--search`), or user categorization requests (`--input`, `--categories`, `--prompt`).
- **Tools & Data:** Anthropic Claude API (`claude-haiku-4-5-20251001`), SerpApi search tool (`src.tools.search_tool.SerpSearchTool`), ReportLab PDF engine (`reportlab.platypus`), regex taxonomy parser, JSON/Markdown schema formatters.
- **Outputs:** Downloadable Executive PDF Dossier (`statbot_categorized_findings.pdf`), segmented JSON taxonomy objects, and formatted Markdown category tables.
- **Autonomy Level:** High (Operates under strict preservation guardrails; never alters underlying statistics; defaults to "I am unable to perform that task" if inputs cannot be reliably classified or are non-existent/inaccurate).
- **Predetermined Conclusion Guardrail:** Must immediately decline any request, guiding prompt, categorization instruction, or query that instructs or pressures it to reach a certain conclusion regardless of the truth, empirical data, or verified PollBot findings, outputting: `"I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based."`
- **Transfer Reaffirmation Guardrail:** When ingesting or processing information transferred from PollBot, StatBot must confirm or require that the user reaffirmed their request in an explicit prompt. If the transfer was not reaffirmed by the user, StatBot immediately halts execution and outputs `"I am unable to perform that task"`.
- **Failure Handling:** If asked to find, categorize, or confirm information that is either non-existent or inaccurate, StatBot immediately halts execution and outputs `"I am unable to perform that task"`. If API calls fail or data is missing, it safely falls back to deterministic rule-based keyword sorting or outputs `"I am unable to perform that task"`.

### Agent Card 8: Collaborative Intelligence Coordinator (`PollingIntelligenceCollaborator`)
- **Program Affiliation:** Multi-Agent Pipeline Coordinator in the **"Polling Error"** program.
- **Role:** Synergistic workflow orchestrator connecting PollBot and StatBot.
- **Goal:** Coordinate PollBot and StatBot working together in the "Polling Error" program via sequential and bidirectional loops that guarantee zero redundant information and ensure each agent builds directly upon the other's findings.
- **Inputs / Trigger:** Input datasets, referendum audits, `--collaborate` CLI command, or `/collaborate` chat instruction.
- **Tools & Data:** Shared Finding Ledger (`IntelligenceLedger`), ReportLab PDF compiler (`SimpleDocTemplate`), Markdown synthesizer.
- **Autonomy Level:** High (Autonomous workflow orchestration enforcing non-repetition and mandatory user reaffirmation gates).

### Agent Card 9: Polling Error Prompter (`PollingErrorPrompter`)
- **Program Affiliation:** Core Prompt Engineering & Guiding Interface in the **"Polling Error"** program.
- **Role:** Prompt architect, guardrail pre-screener, and teleprompter director.
- **Goal:** Provide analysts and decision-makers with structured guiding templates, real-time guardrail pre-screening, and broadcast-style teleprompter views to inject verified, bias-free instructions into PollBot, StatBot, and the Sequential Pipeline.
- **Core Directives:**
  1. **Guiding Instruction Formulation:** Structure prompter directives with clear taxonomy boundaries, analytical focus areas, and tone constraints.
  2. **Real-Time Guardrail Pre-Screening:** Detect and flag predetermined conclusion bias or non-polling queries before agents are dispatched.
  3. **Multi-Agent Routing:** Format tailored directives matching the specific schema contracts of PollBot (qualitative inquiry), StatBot (taxonomic partitioning), and the Sequential Pipeline (coordinated end-to-end handoff).
  4. **Broadcast Teleprompter Delivery:** Provide high-visibility scrolling teleprompter scripts for live analyst briefings and interactive presentations.
- **Inputs / Trigger:** CLI commands (`python -m src.tools.prompter`), interactive terminal console (`--interactive`), web studio (`#prompterStudio`), or pipeline flags (`--prompter`).
- **Tools & Data:** Prompter Recipe Library (`src.tools.prompter`), regex guardrail validator, teleprompter viewport engine.
- **Outputs:** Validated prompter directives, JSON sequential payloads, and live teleprompter script feeds.
- **Autonomy Level:** Interactive / Advisory.

---

## 3. Coordination Pattern & Hand-offs

1. **Coordination Style:** **Orchestrator-Worker Pipeline with Reviewer, Human Checkpoint Loop, and Sequential Pipeline Coordination Pattern**.
2. **State Management:** A centralized `PipelineState` dictionary tracks phase progress:
   `IDLE` $\rightarrow$ `COLLECTING` $\rightarrow$ `NORMALIZING` $\rightarrow$ `MODELING` $\rightarrow$ `AUDITING` $\rightarrow$ `HUMAN_REVIEW` $\rightarrow$ `PUBLISHED`.
3. **Sequential Pipeline Coordination Pattern (PollBot First $\rightarrow$ StatBot Second):**
   The primary coordination pattern between PollBot and StatBot follows a strict, step-by-step linear pipeline where PollBot runs first and StatBot runs second:
   ```text
   [ Raw Polling Data ]
           │
           ▼
   ┌────────────────────────────────────────────────────────┐
   │ Stage 1: PollBot Qualitative Analyst (First)          │
   │ - Decomposes sampling frame, collection mode, & bias   │
   │ - Conducts real-time web research via SerpApi          │
   │ - Registers novel findings into IntelligenceLedger     │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼ Mandatory User Reaffirmation Gate (yes/no)
   ┌────────────────────────────────────────────────────────┐
   │ Stage 2: Guarded Hand-Off Protocol                     │
   │ - Validates user reaffirmation before transfer         │
   │ - Records immutable transfer JSON to handoff ledger    │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼ Ingests PollBot Transfer Payload
   ┌────────────────────────────────────────────────────────┐
   │ Stage 3: StatBot Statistical Categorization (Second)   │
   │ - Filters redundant claims using Shared Ledger         │
   │ - Partitions findings into requested category taxonomy │
   │ - Discovers cross-tabulation blindspots & gaps         │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │ Stage 4: Publication & Executive Artifact Assembly     │
   │ - sequential_pipeline_report.md & .pdf                 │
   │ - statbot_categorized_findings.pdf                     │
   │ - Root synchronization for one-click downloading       │
   └────────────────────────────────────────────────────────┘
   ```
4. **PollBot & StatBot Synergistic Synthesis Loop (Advanced Bidirectional):**
   - For bidirectional second-order strategic analysis, PollBot can optionally consume StatBot's categories to project campaign risks and turnout elasticity with zero repetition of underlying metrics.
5. **Hand-Off Protocol & User Reaffirmation Requirement:**
   - **Mandatory User Reaffirmation Prompt:** The system requires the user to reaffirm their request in an explicit prompt (`yes`/`no`) before transferring relevant information from PollBot to StatBot. If the user does not reaffirm the request, the transfer is aborted immediately and no data is transferred.
   - Every hand-off package is immutable upon writing and recorded in `data/pollbot_to_statbot/` with `"user_reaffirmed": true`.
   - Hand-offs occur through typed models to avoid data leakage or hallucinated contract assumptions.
6. **Human Checkpoint Rule:**
   - If `outlier_flag == True` or `confidence_score < 0.70`, the Orchestrator pauses autonomous execution and routes control to the `HumanAuditor`.

---

## 4. Tech Stack & Coding Conventions

- **Language:** Python 3.10+ (Current runtime: Python 3.14 compatible).
- **Core Libraries:**
  - `anthropic`: Anthropic Claude API client for PollBot reasoning.
  - `pydantic`: Strict data validation and typed schema contracts.
  - `python-dotenv`: Safe environment configuration management.
  - `pytest`: Automated test suite for agent logic and pipeline integrity.
  - `rich`: Formatted CLI output, tables, and progress indicators.
- **Repository Structure:**
  ```text
  Assignement LIAI 1001/
  ├── .github/                     # GitHub workflows and issue/PR templates
  │   └── workflows/
  │       └── ci.yml
  ├── data/                        # Polling datasets & inter-agent handoff ledgers
  │   ├── pollbot_to_statbot/      # Handoff ledger: PollBot qualitative briefs -> StatBot
  │   ├── raw/                     # Raw ingested poll datasets (.gitkeep)
  │   └── processed/               # Normalized polling datasets (.gitkeep)
  ├── docs/                        # Architecture diagrams and design specifications
  │   └── architecture.md
  ├── evidence/                    # Prototype run logs, screenshots, and demo assets
  │   └── .gitkeep
  ├── prompts/                     # Structured agent prompts and system instructions
  │   └── .gitkeep
  ├── src/                         # Core codebase
  │   ├── agents/                  # Autonomous worker agent modules
  │   │   ├── __init__.py
  │   │   ├── normalizer.py
  │   │   ├── modeler.py
  │   │   ├── explainer.py
  │   │   ├── pollbot.py           # Anthropic Claude-powered analyst
  │   │   ├── statbot.py           # Statistical categorization & taxonomy agent
  │   │   └── collaborator.py      # Synergistic workflow orchestrator (PollBot & StatBot)
  │   ├── orchestrator/            # Central coordinator & pipeline state machine
  │   │   ├── __init__.py
  │   │   └── pipeline.py
  │   ├── tools/                   # Shared utility tools & statistical formulas
  │   │   ├── __init__.py
  │   │   ├── math_utils.py
  │   │   ├── search_tool.py       # SerpApi real-time web research tool
  │   │   └── ledger.py            # IntelligenceLedger (non-repetition & novelty tracking)
  │   └── __init__.py
  ├── tests/                       # Unit and integration tests
  │   ├── __init__.py
  │   ├── sample_polls.json        # Test polling input fixtures
  │   ├── test_basic.py            # End-to-end pipeline and baseline agent tests
  │   ├── test_pollbot.py          # PollBot agent tests (18 tests)
  │   ├── test_statbot.py          # StatBot agent tests (17 tests)
  │   ├── test_collaboration.py    # Non-repetition & collaborative loop tests (9 tests)
  │   └── test_sequential_pipeline.py # Sequential pipeline coordination tests (7 tests)
  ├── .env.example                 # Documented template for configuration
  ├── .gitignore                   # Exclusions for virtualenvs, secrets, caches
  ├── AGENTS.md                    # Agent instructions and system specifications
  ├── sequential_pipeline_report.pdf # Publication-ready sequential pipeline PDF
  ├── collaborative_intelligence_report.pdf # Publication-ready collaborative PDF
  ├── statbot_categorized_findings.pdf # Publication-ready StatBot PDF
  ├── GITHUB.md                    # Git & GitHub version control guide
  ├── README.md                    # Setup, execution guide, and prototype overview
  ├── requirements.txt             # Project dependencies
  └── student_info.txt             # Academic submission metadata
  ```
- **Conventions & Style:**
  - **PEP 8 Compliance:** 4 spaces indentation, 88-100 character line limit.
  - **Type Hints:** All function and method signatures must include Python type annotations.
  - **Docstrings:** Use Google-style docstrings for public functions and classes.
  - **Pure Functions:** Business logic and mathematical formulas in `tools/` must be pure and free of side-effects.

---

## 5. Commands Reference

### 5.1 Environment Setup
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
Copy-Item .env.example .env
```

### 5.2 Running the Prototype
```powershell
# Run the pipeline with default sample polling dataset
python -m src.orchestrator.pipeline

# Run in interactive mode with Human-in-the-Loop review
python -m src.orchestrator.pipeline --interactive

# Run with custom sample input file
python -m src.orchestrator.pipeline --input tests/sample_polls.json

# Run Sequential Pipeline Coordination Pattern via orchestrator (PollBot first -> StatBot second)
python -m src.orchestrator.pipeline --sequential --reaffirm yes

# Run Sequential Pipeline directly via collaborator
python -m src.agents.collaborator --sequential --demo --reaffirm yes

# Run Sequential Pipeline directly via PollBot
python -m src.agents.pollbot --sequential tests/sample_polls.json --reaffirm yes

# Run Sequential Pipeline directly via StatBot
python -m src.agents.statbot --sequential tests/sample_polls.json --reaffirm yes

# Check PollBot & SerpApi status and active model
python -m src.agents.pollbot --status

# Launch live web research on polling news / methodology via SerpApi
python -m src.agents.pollbot --search "election polling likely voter screens methodology"

# Launch interactive Q&A session with PollBot (supports '/sequential', '/search <term>', '/transfer', '/collaborate')
python -m src.agents.pollbot --chat

# Transfer polling intelligence from PollBot to StatBot (requires user reaffirmation)
python -m src.agents.pollbot --transfer tests/sample_polls.json

# Transfer with automated reaffirmation in batch pipelines
python -m src.agents.pollbot --transfer tests/sample_polls.json --reaffirm yes

# Run non-redundant collaborative workflow directly from PollBot
python -m src.agents.pollbot --collaborate tests/sample_polls.json --reaffirm yes

# Check StatBot status and active SerpApi / Claude tools
python -m src.agents.statbot --status

# Ingest and categorize PollBot transfer payload (verifies user reaffirmation)
python -m src.agents.statbot --transfer data/pollbot_to_statbot/pollbot_to_statbot_transfer.json

# Run non-redundant collaborative workflow directly from StatBot
python -m src.agents.statbot --collaborate tests/sample_polls.json --reaffirm yes

# Run dedicated PollBot & StatBot collaborative workflow (zero repetition, builds off each other)
python -m src.agents.collaborator --demo --reaffirm yes

# Run collaboration on specific document with custom categories
python -m src.agents.collaborator --input docs/alberta_equalization_referendum_audit.md --categories "Demographic Factors,Geographic Factors,Methodology & Errors,Turnout & Motivation" --reaffirm yes
```

### 5.3 Testing & Quality Verification
```powershell
# Run the complete test suite across all 73 automated tests
python -m unittest discover tests -v

# Run Sequential Pipeline Coordination Pattern tests (7 tests)
python -m unittest tests/test_sequential_pipeline.py -v

# Run Collaborative Synergistic Loop tests (9 tests)
python -m unittest tests/test_collaboration.py -v

# Run PollBot tests (18 tests)
python -m unittest tests/test_pollbot.py -v

# Run StatBot tests (17 tests)
python -m unittest tests/test_statbot.py -v

# Run pipeline baseline tests (7 tests)
python -m unittest tests/test_basic.py -v

# Run lint checks
flake8 src tests
```

---

## 6. Rules, Safety Guardrails & Academic Integrity

1. **Zero Secrets in Git:**
   - Real API keys, passwords, or personal credentials must **never** be committed. Always verify `.gitignore` excludes `.env`.
2. **Deterministic Fallbacks:**
   - The system includes a deterministic mock data provider so that the prototype can run and demonstrate complete agentic functionality without external paid API dependencies.
3. **Academic Integrity:**
   - Developed by **Graham Turnbull (200679442)** for Georgian College course **LIAI 1001**.
   - Conforms with Georgian College Academic Integrity Policy and Course Guidelines for Prof. Evandro Barros.
