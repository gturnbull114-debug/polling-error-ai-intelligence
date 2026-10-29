# Polling Error — AI Polling Intelligence Agentic System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: Academic](https://img.shields.io/badge/license-Academic%20Use-lightgrey.svg)](LICENSE)
[![Assignment](https://img.shields.io/badge/Course-LIAI%201001%20Strategy%20%26%20Change-orange.svg)]()
[![Platform: Google Antigravity](https://img.shields.io/badge/Environment-Google%20Antigravity-green.svg)]()

> **Final Project: Designing and Prototyping an Agentic AI Solution**  
> **Program Name:** **"Polling Error"** Multi-Agent Polling Intelligence System  
> **Course:** LIAI 1001 – Strategy and Change  
> **Academic Program:** Artificial Intelligence Leadership and Management Program, Georgian College  
> **Instructor:** Prof. Evandro Barros  
> **Student:** Graham Turnbull (Student ID: `200679442`)  
> **Submission Date:** October 2026  

---

## 1. Project Overview & Business Case

### 1.1 The Business Problem
Election and public opinion polling is routinely misinterpreted by decision-makers, media, and corporate strategists. Conventional reporting treats aggregate polling as a simple numerical horse-race, ignoring critical methodological nuances:
- **Sampling frame disparities** (landline vs. mobile vs. online opt-in panels).
- **Voter screens** (Registered Voters [RV] vs. Likely Voters [LV]).
- **House effects** (systemic historical partisan leanings of individual pollsters).
- **Non-response error and sample decay** over time.

When election forecasts fail, trust in data analytics evaporates. Today, manual polling analysis is labor-intensive, slow, and prone to subjective human confirmation bias.

### 1.2 Why Agentic AI?
A simple chatbot only answers static queries. A basic script or deterministic formula cannot dynamically reason across contradictory sample designs or evaluate competing causal hypotheses. 

The **"Polling Error"** multi-agent program (AI Polling Intelligence Agentic System) uses an **autonomous multi-agent architecture** that:
1. **Decomposes margin of error:** Separates statistical variance from systematic methodological bias.
2. **Formulates causal explanations:** Explains *why* poll results moved (e.g., shifts in youth turnout screen vs. actual sentiment swing).
3. **Audits uncertainty:** Maintains a dynamic, evidence-backed ledger of plausible polling-error mechanisms.
4. **Enforces human oversight:** Integrates a mandatory Human-in-the-Loop (HITL) gatekeeper when unexpected outlier divergence is detected.

The program that **PollBot** and **StatBot** are both part of is named **"Polling Error"**. Together, they form the core qualitative analysis and statistical taxonomy layers of the system.

---

## 2. Multi-Agent System Architecture

The prototype implements an **Orchestrator-Worker Pipeline with Human Review Gate**:

```
                       ┌─────────────────────────┐
                       │   Raw Polling Feed      │
                       │   (JSON / CSV / API)    │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │   Orchestrator Agent    │
                       └────────────┬────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│ Ingestion &       │     │ Statistical       │     │ Causal Explanation│
│ Normalizer Agent  │───> │ Modeling Agent    │───> │ & Audit Agent     │
│                   │     │                   │     │                   │
│ - Schema validate │     │ - Bayesian weight │     │ - Decompose MOE   │
│ - Likely-voter adj│     │ - House effects   │     │ - Audit non-sample│
│ - Time decay      │     │ - Outlier detect  │     │ - Draft briefing  │
└───────────────────┘     └───────────────────┘     └─────────┬─────────┘
                                                              │
                                                              ▼
                                                   [ Outlier Flag > 3.5%? ]
                                                              │
                                            ┌─────────────────┴─────────────────┐
                                      YES   │                                   │  NO
                                            ▼                                   ▼
                             ┌─────────────────────────┐           ┌─────────────────────────┐
                             │ Human-in-the-Loop (HITL)│           │ Automated Verification  │
                             │ Checkpoint Review       │           │ & Log Emission          │
                             └──────────────┬──────────┘           └────────────┬────────────┘
                                            │                                   │
                                            └─────────────────┬─────────────────┘
                                                              │
                                                              ▼
                                                   ┌─────────────────────────┐
                                                   │ Executive Polling Brief │
                                                   │ & Evidence Ledger (.md) │
                                                   └─────────────────────────┘
```

### Agent Roles Summary
The architecture separates autonomous pipeline workers from two specialized, conversational and qualitative AI agents:

| Category | Agent Name | Primary Responsibility | Autonomy Level | Key Output |
| :--- | :--- | :--- | :--- | :--- |
| **Pipeline Worker** | **Orchestrator Agent** | Coordinates pipeline execution, state machine, and error recovery | Autonomous | Pipeline telemetry & status |
| **Pipeline Worker** | **Normalizer Agent** | Cleans raw poll tables, adjusts voter screens, computes recency decay | Autonomous | Standardized poll models |
| **Pipeline Worker** | **Modeler Agent** | Aggregates consensus signal, measures pollster variance & house bias | Semi-Autonomous | Weighted signal & spread |
| **Pipeline Worker** | **Explainer Agent** | Decomposes error mechanisms and drafts causal explanations | Semi-Autonomous | Plain-language brief draft |
| **Human Review** | **Human Auditor (HITL)** | Reviews flagged outliers, inspects assumptions, signs off on publication | Human Checkpoint | Signed approval certificate |
| **Specialized AI** | **PollBot (`pollbot.py`)** | Qualitative methodology audits, mode-effects, SerpApi live research | High (AI Analyst) | Narrative brief & transfer dossiers |
| **Specialized AI** | **StatBot (`statbot.py`)** | Post-processing statistical taxonomy, custom categorization, ReportLab PDF | High (AI Taxonomy) | Downloadable PDF & grouped JSON/MD |

---

### 2.2 In-Depth: The Two Specialized AI Agents (PollBot & StatBot)

Within the **"Polling Error"** program, **PollBot** and **StatBot** operate as the flagship autonomous intelligence agents. They work in tandem through an immutable handoff ledger ([`data/pollbot_to_statbot/`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot)), turning complex polling datasets into qualitative causal reasoning, structured taxonomies, and executive publication dossiers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AGENT 1: PollBot (AI Qualitative Analyst)             │
│  - Engine: Anthropic Claude (claude-haiku-4-5-20251001 / claude-sonnet)     │
│  - Real-Time Grounding: SerpApi Search Tool (track records & news)          │
│  - Ingestion: PDF (pypdf), JSON, Markdown, text files                       │
│  - Safety: Polling Domain Relevance Guardrail -> "Please provide relevant   │
│            information" / Reliability Guardrail -> "Answer Unavailable"     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ Handoff Dossier (JSON / Markdown)
┌─────────────────────────────────────────────────────────────────────────────┐
│       Inter-Agent Transfer Ledger: data/pollbot_to_statbot/                  │
│       - Immutable schema preserving sample sizes, MoE, and findings         │
│       - sample_pollbot_transfer.json & sample_pollbot_transfer.md           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ Ingests PollBot Results
┌─────────────────────────────────────────────────────────────────────────────┐
│               AGENT 2: StatBot (Statistical Taxonomy & Categorization)       │
│  - Engine: Anthropic Claude + Regex/Keyword Fallback                        │
│  - Dedicated Focus: Anchors classifications strictly in PollBot outputs     │
│  - Prompt Adherence: Dynamically groups into prompter-specified categories  │
│  - Accuracy Guardrail: Halts on inaccurate/non-existent data with:          │
│                       "I am unable to perform that task"                    │
│  - Publishing: ReportLab Platypus Engine -> statbot_categorized_findings.pdf│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 1. PollBot — AI Qualitative Analyst ([`src/agents/pollbot.py`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/agents/pollbot.py))
- **Mission & Core Responsibilities:**
  PollBot is an LLM-powered polling intelligence agent using Anthropic Claude paired with real-time web research capabilities via SerpApi. It specializes in deep forensic evaluations of pollster track records, margin-of-error decomposition, voter screen discrepancies (Likely Voters vs. Registered Voters), and mode effects (Live Phone, SMS, Online Opt-in Panel, IVR).
- **Internal Contents & Components:**
  1. **`POLLBOT_SYSTEM_PROMPT`:** System prompt encoding strict academic guardrails for the LIAI 1001 curriculum: prohibits partisan weighting alterations, forbids hallucinating numbers, mandates human escalation on outlier divergence ($>3.5\%$), and enforces objective analysis.
  2. **Anthropic Claude Engine:** Configured for `claude-haiku-4-5-20251001` (fast, cost-effective reasoning) and supports `claude-sonnet-4-5-20250929` for deep strategic reasoning, with full multi-turn conversational memory tracking (`conversation_history`).
  3. **SerpApi Search Tool ([`SerpSearchTool`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/tools/search_tool.py)):** Enables live web search (`--search`) to verify pollster transparency, cross-reference historical house biases, and inject breaking contextual news into prompt reasoning.
  4. **Multi-Format Ingestion Engine (`extract_document_text()`):** Extracts raw text from PDFs (via `pypdf` with fallback raw byte parser), JSON records, Markdown briefings, or raw text files.
  5. **Predetermined Conclusion Guardrail (`is_predetermined_conclusion_request()`):** Immediately declines any request, prompt, or document that instructs or pressures PollBot to reach a certain conclusion regardless of the truth, empirical facts, or verified data, outputting:
     `"I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All analysis must be objective and evidence-based."`
  6. **Transfer Reaffirmation Guardrail (`transfer_to_statbot()`):** Before transferring relevant polling intelligence to StatBot, PollBot requires the user to reaffirm their request in an explicit prompt (`yes`/`no`). If the user does not reaffirm the request, execution is halted immediately and no information is transferred.
  7. **Domain Relevance Guardrail (`is_polling_related()` & `analyze_document()`):** Before analyzing any document, PollBot executes an automated pre-screening check across 30+ polling terms and multi-word phrases (e.g., `margin of error`, `likely voter`, `approval rating`, `turnout`, `sample frame`). If the document is irrelevant (e.g., recipes, sports, general text), it halts execution immediately and outputs:
     `"Please provide relevant information"`
  8. **Reliability & Availability Guardrail (`is_answer_reliable()`, `get_reliable_answer()`):** If API keys are missing, network connectivity drops, or input data is unreliable or empty, PollBot safely outputs `"Answer Unavailable"`.
  9. **Deterministic Offline Fallback:** If run without API keys, PollBot falls back to an offline rule-based analysis mode without crashing.
  10. **Interactive Terminal Chat & Transfer:** Supports interactive conversational queries with built-in commands like `/search <query>` and `/transfer` (which prompts the user to reaffirm before transferring to StatBot).

#### 2. StatBot — Statistical Categorization Agent ([`src/agents/statbot.py`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/agents/statbot.py))
- **Mission & Core Responsibilities:**
  StatBot is a post-processing taxonomy and segmentation specialist. Its dedicated purpose is to take the qualitative and quantitative analytical findings produced by **PollBot** and categorize, partition, and structure them into the exact groups, taxonomies, or categories specified by the user or guiding prompt (e.g., Demographics, Geographic Factors, Methodology & Errors, Turnout Salience).
- **Internal Components & Contents:**
  1. **`STATBOT_SYSTEM_PROMPT`:** System prompt mandating four operational directives: (1) maintain dedicated focus on PollBot results; (2) strictly follow the grouping criteria and category definitions requested by the prompter; (3) ensure mutual exclusivity and statistical preservation; (4) cleanly format output in JSON or Markdown.
  2. **Claude Categorization Engine:** Dynamically interprets user grouping prompts (`--instructions` / `--prompt`) and segments findings into custom taxonomies without altering original percentages, sample sizes, or confidence intervals.
  3. **Predetermined Conclusion Guardrail (`is_predetermined_conclusion_request()`):** Immediately declines any request, guiding prompt, categorization instruction, or query that instructs or pressures StatBot to reach a certain conclusion regardless of the truth, empirical data, or verified PollBot findings, outputting:
     `"I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based."`
  4. **Transfer Reaffirmation Guardrail (`receive_transfer_from_pollbot()`):** When receiving or ingesting transferred information from PollBot, StatBot confirms or prompts the user for reaffirmation. If the transfer was not reaffirmed by the user, execution is aborted immediately.
  5. **Information Retrieval & Accuracy Guardrail (`find_information()`):** Scans PollBot outputs to locate specific metrics. If asked to find, categorize, or confirm information that is **non-existent or inaccurate**, StatBot halts execution immediately and responds:
     `"I am unable to perform that task"`
  6. **Always-On Executive PDF Publishing Engine (`ReportLab`):** Automatically formats categorized findings into a publication-grade executive PDF dossier ([`data/pollbot_to_statbot/statbot_categorized_findings.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/statbot_categorized_findings.pdf)) with styled headers, structured data tables, and metadata blocks, simultaneously syncing a copy to the project root (`statbot_categorized_findings.pdf`) for one-click downloading.
  7. **Dual Structured Output Formats:** Emits either clean hierarchical JSON (`--format json`) or formatted Markdown tables (`--format markdown`).
  8. **Deterministic Offline Engine:** Includes a robust regex and keyword-scoring engine that partitions PollBot findings across requested categories even in air-gapped or zero-API environments.
  9. **Search Tool Integration:** Includes attached [`SerpSearchTool`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/tools/search_tool.py) (`--search`) to verify domain context when taxonomy disambiguation is required.

#### 3. Agent Comparison Matrix
| Capability / Dimension | PollBot (`pollbot.py`) | StatBot (`statbot.py`) |
| :--- | :--- | :--- |
| **Primary Domain** | Qualitative analysis & methodology auditing | Statistical categorization & taxonomy structuring |
| **Input Source** | Raw polls, PDFs, JSON datasets, web queries | Intelligence briefs & findings produced by PollBot |
| **Core LLM Engine** | Anthropic Claude (`claude-haiku-4-5-20251001`) | Anthropic Claude (`claude-haiku-4-5-20251001`) |
| **Grounding Tool** | SerpApi real-time web search ([`SerpSearchTool`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/tools/search_tool.py)) | SerpApi search + ReportLab Platypus PDF engine |
| **Key Safety Guardrails** | 1. **Predetermined Conclusion Rejection**: Declines forced conclusions regardless of truth<br>2. **Transfer Reaffirmation Guardrail**: Requires user reaffirmation prompt before transfer<br>3. **Domain Relevance Check**: Rejects non-polling content with `"Please provide relevant information"`<br>4. **Non-Repetition Guardrail**: Prevents repeating StatBot metrics | 1. **Predetermined Conclusion Rejection**: Declines forced conclusions regardless of truth<br>2. **Transfer Reaffirmation Verification**: Aborts un-reaffirmed transfers<br>3. **Non-Existent/Inaccurate Data Halt**: Halts with `"I am unable to perform that task"`<br>4. **Non-Repetition Guardrail**: Deduplicates raw claims |
| **Unreliability Fallback** | Returns `"Answer Unavailable"` | Returns `"I am unable to perform that task"` |
| **Primary Artifact** | Qualitative audit briefing & transfer dossier | Downloadable PDF dossier (`statbot_categorized_findings.pdf`) |

### 2.3 Synergistic Collaboration: Zero Repetition & Building Off Each Other's Findings

To prevent the common multi-agent pitfall of informational redundancy—where agents repeat or echo each other's claims—the system introduces a **Shared Intelligence Ledger** ([`src/tools/ledger.py`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/tools/ledger.py)) and a unified **Collaborative Coordinator** ([`src/agents/collaborator.py`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/agents/collaborator.py)).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STEP 1: PollBot Primary Qualitative Groundwork            │
│  - Analyzes raw poll dataset / referendum brief                             │
│  - Decomposes collection mode, sample frames, and baseline house bias       │
│  - Registers novel facts into Shared Intelligence Ledger                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ Mandatory User Reaffirmation Gate (yes/no)
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STEP 2: StatBot Structured Categorization & Gaps          │
│  - Filters narrative fluff and deduplicates identical claims                │
│  - Partitions metrics into clean taxonomies (Demographics, Geography, etc.) │
│  - Identifies statistical gaps & cross-tabulations (e.g., Senior Salience)  │
│  - Exports findings into statbot_categorized_findings.pdf                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ Ingests Categorized Taxonomies & Gaps
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STEP 3: PollBot Advanced Strategic Synthesis              │
│  - STRICT NON-REPETITION MANDATE: Never repeats numbers or raw statements   │
│  - References StatBot's categories to derive second-order intelligence:     │
│    * Strategic & Electoral Implications (voter turnout sensitivity)         │
│    * Causal Risk & Polling Error Audit (opt-in panel non-response bias)     │
│    * Actionable Calibration Recommendations (multi-mode polling adjustments)│
│  - Registers synthesis items with builds_on="StatBot Taxonomy"              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│           UNIFIED COLLABORATIVE DOSSIER & PUBLICATION REPORT                │
│  - Markdown: data/pollbot_to_statbot/collaborative_intelligence_report.md   │
│  - PDF:      data/pollbot_to_statbot/collaborative_intelligence_report.pdf  │
│  - Root PDF: collaborative_intelligence_report.pdf                          │
│  - Deduplication Audit: 100% verified novelty (0 redundant statements)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **How Non-Repetition is Enforced:**
   - **`IntelligenceLedger`:** Maintains canonical token and numerical signatures for every finding. Calculates Jaccard similarity and metric overlap; any statement with similarity $\ge 0.55$ or duplicate core metrics is automatically suppressed.
   - **System Prompt Mandate:** Both `POLLBOT_SYSTEM_PROMPT` and `STATBOT_SYSTEM_PROMPT` explicitly mandate: *"You must never duplicate or repeat the categorized metrics, tables, or numbers already presented. Build novel qualitative depth, causal explanations, and strategic risks on top of the foundation."*
2. **How Agents Build Off Each Other:**
   - **StatBot builds on PollBot:** Strips qualitative narrative rhetoric, isolates numerical evidence, partitions figures into prompter taxonomies, and formulates analytical gaps (e.g. noticing that rural online samples lack IVR verification).
   - **PollBot builds on StatBot:** Ingests StatBot's structured taxonomy and identified gaps to project campaign risks, turnout elasticity, and methodology recalibration without restating a single percentage or bullet point.

### 2.4 Sequential Pipeline Coordination Pattern (PollBot First → StatBot Second)

In the **"Polling Error"** multi-agent program, the **Sequential Pipeline Coordination Pattern** defines a linear, stage-by-stage pipeline where agents execute in a predetermined sequence: **PollBot executes first** to conduct qualitative decomposition, passes the verified dossier across a guarded handoff gate, and **StatBot executes second** to perform statistical taxonomy segmentation and gap discovery:

```text
[ Raw Polling Data / Brief ]
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ Stage 1: PollBot Qualitative Analyst (First)          │
│ - Analyzes sampling frames (LV vs. RV) & collection mode│
│ - Audits pollster house effects & historical track rec.│
│ - Searches real-time web context via SerpApi           │
│ - Registers novel findings into IntelligenceLedger     │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼ Mandatory User Reaffirmation Checkpoint (yes/no)
┌────────────────────────────────────────────────────────┐
│ Stage 2: Guarded Hand-Off Protocol                     │
│ - Requires explicit user reaffirmation before transfer │
│ - Halts immediately if declined (zero data leakage)    │
│ - Writes immutable transfer payload to data exchange   │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼ Ingests PollBot Transfer Payload
┌────────────────────────────────────────────────────────┐
│ Stage 3: StatBot Statistical Categorization (Second)   │
│ - Non-repetition deduplication via Shared Ledger       │
│ - Systematic taxonomy partitioning into custom groups  │
│ - Identifies statistical gaps & cross-tabulations      │
│ - Automatically exports statbot_categorized_findings.pdf│
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│ Stage 4: Publication & Executive Artifact Assembly     │
│ - sequential_pipeline_report.md & .pdf                 │
│ - Synchronized root PDF for one-click downloading      │
│ - Full audit trail & ledger verification telemetry     │
└────────────────────────────────────────────────────────┘
```

- **Pipeline State Progression:** `STATE_INITIALIZED` → `STATE_POLLBOT_STAGE` → `STATE_HANDOFF_GATE` → `STATE_STATBOT_STAGE` → `STATE_COMPLETED`.
- **Coordinator Class:** [`SequentialPipelineCoordinator`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/agents/collaborator.py) handles lifecycle management, CLI commands, and automated report assembly.

---

## 3. Repository Directory Structure

```text
Assignement LIAI 1001/
├── .github/                     # GitHub workflows and collaboration templates
│   ├── ISSUE_TEMPLATE/          # Bug report & feature request templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/               # CI/CD automation pipelines
│   │   └── ci.yml               # Automated test, lint, and validation workflow
│   └── pull_request_template.md # PR checklist for agent code review
├── data/                        # Polling datasets & inter-agent handoff ledgers
│   ├── pollbot_to_statbot/      # Handoff ledger: PollBot qualitative briefs -> StatBot
│   │   ├── README.md            # Transfer protocol and schema documentation
│   │   ├── sample_pollbot_transfer.json # Immutable JSON transfer fixture
│   │   ├── sample_pollbot_transfer.md   # Markdown intelligence dossier fixture
│   │   ├── categorized_statbot_findings.md # Generated StatBot Markdown report
│   │   ├── statbot_categorized_findings.pdf # Generated publication PDF dossier
│   │   ├── sequential_pipeline_report.md # Sequential pipeline Markdown dossier
│   │   ├── sequential_pipeline_report.pdf # Sequential pipeline publication PDF
│   │   ├── collaborative_intelligence_report.md # Multi-agent non-redundant brief
│   │   └── collaborative_intelligence_report.pdf # Multi-agent collaborative PDF dossier
│   ├── raw/                     # Raw ingested poll datasets (.gitkeep)
│   └── processed/               # Normalized polling datasets (.gitkeep)
├── docs/                        # Architecture diagrams and system design documents
│   └── architecture.md
├── evidence/                    # Run outputs, execution logs, and demo screenshots
│   └── .gitkeep
├── prompts/                     # Structured agent system prompts & instructions
│   └── .gitkeep
├── src/                         # Python application source code
│   ├── agents/                  # Autonomous worker agent definitions
│   │   ├── __init__.py
│   │   ├── normalizer.py        # Ingestion & Normalizer agent logic
│   │   ├── modeler.py           # Statistical Modeling agent logic
│   │   ├── explainer.py         # Causal Explanation & Audit agent logic
│   │   ├── pollbot.py           # Anthropic Claude-powered qualitative analyst
│   │   ├── statbot.py           # Statistical taxonomy & categorization agent
│   │   └── collaborator.py      # Synergistic & sequential pipeline coordinator
│   ├── orchestrator/            # Central pipeline coordinator
│   │   ├── __init__.py
│   │   └── pipeline.py          # State machine and execution orchestrator
│   ├── tools/                   # Statistical tools and helper functions
│   │   ├── __init__.py
│   │   ├── ledger.py            # Shared Intelligence Ledger & deduplication engine
│   │   ├── math_utils.py        # Margin of error and Bayesian weighting calculations
│   │   ├── prompter.py          # Polling Error Prompter & prompt engineering engine
│   │   └── search_tool.py       # SerpApi real-time web research tool
│   └── __init__.py
├── tests/                       # Automated unit and integration test suite
│   ├── __init__.py
│   ├── sample_polls.json        # Test polling input fixtures
│   ├── test_basic.py            # End-to-end pipeline and baseline agent tests
│   ├── test_pollbot.py          # PollBot agent unit tests (18 tests)
│   ├── test_statbot.py          # StatBot agent unit tests (17 tests)
│   ├── test_collaboration.py    # Zero-repetition collaborative loop tests (9 tests)
│   ├── test_sequential_pipeline.py # Sequential pipeline coordination tests (7 tests)
│   └── test_prompter.py         # Polling Error Prompter unit tests (10 tests)
├── .env.example                 # Documented template for configuration & guardrails
├── .gitignore                   # Excludes caches, secrets, and generated files
├── AGENTS.md                    # Core agent instructions & guidelines (Required)
├── sequential_pipeline_report.pdf # Publication-ready sequential pipeline PDF
├── collaborative_intelligence_report.pdf # Publication-ready collaborative PDF
├── statbot_categorized_findings.pdf      # Publication-ready StatBot PDF
├── GITHUB.md                    # Git repository & GitHub collaboration guide
├── README.md                    # Project documentation (This file)
├── requirements.txt             # Python dependencies
└── student_info.txt             # Academic metadata and student verification
```

---

## 4. Installation & Getting Started

### 4.1 Prerequisites
- **Python 3.10+** (Tested on Python 3.14).
- **PowerShell** or standard terminal.
- **Git** for version control.

### 4.2 Setup Instructions

1. **Clone or Navigate to the Workspace:**
   ```powershell
   cd "c:\Users\gturn\OneDrive\Assignement LIAI 1001"
   ```

2. **Create and Activate a Virtual Environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```powershell
   Copy-Item .env.example .env
   ```
   *(The default `.env` is pre-configured with safe mock settings, so you can run the prototype immediately without external API keys!)*

---

## 5. How to Run the Prototype

### 5.0 Interactive Web Dashboard & PDF Ingestion Engine ("Polling Error" Tryout)
Try out the complete **"Polling Error"** multi-agent analytical system in your browser with client-side PDF reading, dynamic poll ingestion, and live agent telemetry:

```powershell
# Launch local web server (already active on port 8000)
python -m http.server 8000
```
Open your browser at: **[http://localhost:8000/](http://localhost:8000/)** (or open [`index.html`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/index.html) directly).

**Core Capabilities:**
- **Client-Side PDF Reading & Text Extraction:** Drag & drop any polling report (`.pdf`), survey memo, or academic brief. Powered by Mozilla's PDF.js with offline stream fallback.
- **Domain Relevance Guardrail:** Automatically evaluates document text against polling, survey, and election keywords. If non-polling content is uploaded, the system immediately halts processing and outputs `"Please provide relevant information"` without altering model weights.
- **Automated Metric Extraction:** Discovers pollster identity, candidate shares, undecided %, sample size $N$, margin of error, and methodology frames directly from PDF content.
- **One-Click Pre-Loaded Dossiers:** Immediately inspect and analyze the 3 publication PDFs generated by the agents:
  - [`statbot_categorized_findings.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/statbot_categorized_findings.pdf)
  - [`sequential_pipeline_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/sequential_pipeline_report.pdf)
  - [`collaborative_intelligence_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/collaborative_intelligence_report.pdf)
- **Universal File Ingestion:** Accepts `.pdf`, `.json`, `.csv`, and `.txt` datasets.
- **Zero-Unsolicited-Statistics Start:** Opens with a clean empty state ready to ingest and analyze new surveys on demand.

### 5.1 Run Standard Multi-Agent Pipeline
Execute the automated end-to-end workflow using sample polling data:
```powershell
python -m src.orchestrator.pipeline
```

### 5.2 Run with Interactive Human Checkpoint (HITL)
To simulate an outlier scenario that pauses execution and requests human verification:
```powershell
python -m src.orchestrator.pipeline --interactive
```

### 5.3 Run with Custom Poll Data
```powershell
python -m src.orchestrator.pipeline --input tests/sample_polls.json
```

### 5.4 PollBot AI Agent (Anthropic Claude + SerpApi)
Interact directly with **PollBot** for real-time polling methodology analysis, web research, and Q&A:

```powershell
# Check PollBot connection status, model, and SerpApi availability
python -m src.agents.pollbot --status

# Launch interactive terminal chat (supports live '/search <query>' and '/transfer')
python -m src.agents.pollbot --chat

# Transfer polling intelligence to StatBot (prompts user for reaffirmation)
python -m src.agents.pollbot --transfer tests/sample_polls.json

# Transfer with automated reaffirmation flag (for headless CI/CD scripts)
python -m src.agents.pollbot --transfer tests/sample_polls.json --reaffirm yes

# Conduct live web research on polling methodology via SerpApi
python -m src.agents.pollbot --search "election polling likely voter screens methodology"

# Deep-dive forensic methodology analysis on a specific poll dataset
python -m src.agents.pollbot --analyze tests/sample_polls.json

# Analyze an external polling brief with automated polling domain verification
python -m src.agents.pollbot --analyze docs/alberta_equalization_referendum_audit.md
```

### 5.5 StatBot Statistical Categorization Agent
Run **StatBot** to segment PollBot findings into customized taxonomies, search context, and generate executive PDF reports:

```powershell
# Check StatBot connection status and tool readiness
python -m src.agents.statbot --status

# Run built-in categorization demonstration with automatic PDF generation
python -m src.agents.statbot --demo

# Conduct live web research for taxonomy grounding via SerpApi
python -m src.agents.statbot --search "Alberta referendum turnout"

# Ingest and categorize PollBot transfer payload (verifies user reaffirmation)
python -m src.agents.statbot --transfer data/pollbot_to_statbot/pollbot_to_statbot_transfer.json

# Ingest and categorize a document with custom categories (JSON format)
python -m src.agents.statbot --input docs/alberta_equalization_referendum_audit.md --categories "Demographics,Methodology,Turnout" --format json

# Categorize PollBot transfer dossier with custom prompter grouping instructions
python -m src.agents.statbot --input data/pollbot_to_statbot/sample_pollbot_transfer.json --categories "Demographic Factors,Geographic Factors,Methodology & Errors,Turnout & Motivation" --prompt "Group age and gender metrics under Demographics, regional splits under Geography, and survey limitations under Methodology"

# Query specific verified information from PollBot findings (halts on inaccurate/non-existent data)
python -m src.agents.statbot --input data/pollbot_to_statbot/sample_pollbot_transfer.json --query "What was the sample size and margin of error?"
```

> [!TIP]
> **Always-On PDF Generation:** Whenever StatBot executes categorization, it compiles findings into [`data/pollbot_to_statbot/statbot_categorized_findings.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/statbot_categorized_findings.pdf) and syncs a copy to the workspace root (`statbot_categorized_findings.pdf`) for convenient one-click downloading and distribution.

### 5.6 Collaborative Synergistic Pipeline (PollBot + StatBot Zero-Repetition)
Execute the unified, bidirectional collaboration loop where PollBot and StatBot collaborate seamlessly without repeating information:

```powershell
# Run the complete synergistic collaboration demo (with automated reaffirmation)
python -m src.agents.collaborator --demo --reaffirm yes

# Run collaboration on a custom PollBot dossier with specific taxonomy rules
python -m src.agents.collaborator --input data/pollbot_to_statbot/sample_pollbot_transfer.json --categories "Demographics,Geography,Methodology,Turnout" --prompt "Focus on age divides under Demographics and rural splits under Geography" --reaffirm yes

# Trigger collaboration directly through PollBot
python -m src.agents.pollbot --collaborate

# Trigger collaboration directly through StatBot
python -m src.agents.statbot --collaborate
```

> [!NOTE]
> **Collaborative Artifacts:** The collaboration loop generates both a Markdown intelligence dossier ([`data/pollbot_to_statbot/collaborative_intelligence_report.md`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/collaborative_intelligence_report.md)) and an executive PDF dossier ([`data/pollbot_to_statbot/collaborative_intelligence_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/collaborative_intelligence_report.pdf)), also synced directly to root workspace as [`collaborative_intelligence_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/collaborative_intelligence_report.pdf).

### 5.7 Sequential Pipeline Coordination Pattern (PollBot First → StatBot Second)
Execute PollBot and StatBot using the sequential pipeline coordination pattern where PollBot runs first, performs qualitative reasoning, hands off across the user reaffirmation gate, and StatBot runs second to categorize findings and compile publication PDFs:

```powershell
# Run the sequential pipeline via orchestrator
python -m src.orchestrator.pipeline --sequential --reaffirm yes

# Run the sequential pipeline directly via collaborator
python -m src.agents.collaborator --sequential --demo --reaffirm yes

# Run sequential pipeline directly via PollBot
python -m src.agents.pollbot --sequential tests/sample_polls.json --reaffirm yes

# Run sequential pipeline directly via StatBot
python -m src.agents.statbot --sequential tests/sample_polls.json --reaffirm yes
```

> [!NOTE]
> **Sequential Artifacts:** The sequential pipeline compiles findings into a sequential Markdown dossier ([`data/pollbot_to_statbot/sequential_pipeline_report.md`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/sequential_pipeline_report.md)), an executive PDF dossier ([`data/pollbot_to_statbot/sequential_pipeline_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/data/pollbot_to_statbot/sequential_pipeline_report.pdf)), and synchronizes a copy directly to root workspace as [`sequential_pipeline_report.pdf`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/sequential_pipeline_report.pdf) for one-click downloading.

### 5.8 The Prompter on "Polling Error" (AI Prompt Studio & Teleprompter)
Use the dedicated Prompter tool to design, pre-screen, and inject precision instructions into PollBot, StatBot, or the Sequential Pipeline:

```powershell
# List all verified prompter templates
python -m src.tools.prompter --list

# Load a specific prompter recipe
python -m src.tools.prompter --template statbot_taxonomy

# Validate a custom prompt against agentic guardrails
python -m src.tools.prompter --validate "Analyze Likely Voter screens vs Registered Voters within MOE"

# Format a structured prompter directive for StatBot
python -m src.tools.prompter --agent statbot --categories "Age,Region,Turnout" --prompt "Focus on youth voter gap"

# Launch interactive prompter terminal console
python -m src.tools.prompter --interactive

# Launch prompter directly through pipeline orchestrator
python -m src.orchestrator.pipeline --prompter
```

> [!TIP]
> **Interactive Prompter on the Web:** Navigate to **[http://localhost:8000/#prompterStudio](http://localhost:8000/#prompterStudio)** to use the visual Prompter Studio with real-time Guardrail Pre-Flight badges, one-click recipe cards, and a broadcast teleprompter mode.

---

## 6. Sample Inputs & Output Demonstration

### Sample Input Format (`tests/sample_polls.json`)
```json
[
  {
    "poll_id": "POLL-001",
    "pollster": "National Metric Research",
    "field_date_end": "2026-10-20",
    "sample_size": 1200,
    "sample_frame": "Likely Voters (LV)",
    "mode": "Live Phone + SMS",
    "candidate_a_share": 49.2,
    "candidate_b_share": 47.8,
    "undecided_share": 3.0,
    "margin_of_error": 2.8
  },
  {
    "poll_id": "POLL-002",
    "pollster": "Civic Pulse Online",
    "field_date_end": "2026-10-22",
    "sample_size": 850,
    "sample_frame": "Registered Voters (RV)",
    "mode": "Online Panel",
    "candidate_a_share": 46.5,
    "candidate_b_share": 51.0,
    "undecided_share": 2.5,
    "margin_of_error": 3.4
  }
]
```

### Sample Intelligence Output Brief
When executed, the system produces:
1. **Normalized Signal:** Weighted Candidate A ($48.7\%$) vs. Candidate B ($48.2\%$).
2. **Margin of Error Decomposition:**
   - Sampling Variance: $\pm 2.4\%$
   - Likely-Voter Adjustment Impact: $+1.6\%$ toward Candidate A.
   - Mode Bias (Online Panel vs. Live Phone): $2.1\%$ divergence noted.
3. **Audit Ledger:** Flags `POLL-002` as an outlier due to Registered Voter screen and lack of non-response weighting.
4. **Human Review Gate:** If divergence threshold ($>3.5\%$) is triggered, human analyst approves or overrides before output finalization.

---

## 7. Running Tests & Quality Verification

Run the automated test suite to verify agent contracts, mathematical calculations, guardrails, non-repetition ledgers, and pipeline coordination:

```powershell
# Run the entire test suite (83 automated unit and integration tests)
python -m unittest discover tests -v

# Run Prompter unit tests (10 tests)
python -m unittest tests/test_prompter.py -v

# Run Sequential Pipeline Coordination Pattern tests (7 tests)
python -m unittest tests/test_sequential_pipeline.py -v

# Run Collaborative Synergistic Loop tests (9 tests)
python -m unittest tests/test_collaboration.py -v

# Run PollBot-specific tests (initialization, guardrails, relevance check, SerpApi)
python -m unittest tests/test_pollbot.py -v

# Run StatBot-specific tests (taxonomy grouping, PDF generation, accuracy guardrail)
python -m unittest tests/test_statbot.py -v

# Run code style and lint validation
flake8 src tests
```

---

## 8. Evidence & Artifacts

All prototype run artifacts, execution logs, and demo screenshots should be stored in the [`evidence/`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/evidence) folder:
- **`evidence/demo_run_log.txt`**: Complete pipeline console log with agent hand-offs.
- **`evidence/human_checkpoint_screenshot.png`**: Visual proof of the Human-in-the-Loop review prompt.
- **`evidence/output_brief.md`**: Generated intelligence brief artifact.

---

## 9. Academic Integrity & AI Tools Declaration

- **Individual Work Statement:** This project, architecture, code, and documentation represent the original work of **Graham Turnbull (200679442)** for **LIAI 1001 – Strategy and Change**.
- **Use of AI Tools:** Built and prototyped in **Google Antigravity**. In accordance with Section 8 of the assignment guidelines, AI agent capabilities were leveraged for code pairing, refactoring, and test generation. All design decisions, mathematical models, and code validation were reviewed and verified by the student.
- **No Secrets Policy:** In accordance with the course rubric, all sensitive keys are omitted; only safe `.env.example` templates are provided.
