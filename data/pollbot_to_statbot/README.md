# PollBot-to-StatBot Handoff & Transfer Directory (`data/pollbot_to_statbot/`)

**Program Name:** "Polling Error" Multi-Agent Polling Intelligence System  
**Course:** LIAI 1001 – Strategy and Change: Agentic AI Solution Assignment  
**Academic Program:** Artificial Intelligence Leadership and Management Program, Georgian College  
**Student:** Graham Turnbull (Student ID: 200679442)  

---

## 1. Directory Purpose

This directory serves as the dedicated data exchange and audit ledger for information transferred between **PollBot** (Qualitative Analyst & Narrative Reasoning Agent) and **StatBot** (Statistical Categorization & Taxonomy Agent), both operating as specialized agents within the **"Polling Error"** program.

```
┌──────────────────────────────┐
│           PollBot            │
│  (Qualitative Analysis &     │
│   Methodology Auditing)      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   data/pollbot_to_statbot/   │  <── Transfer & Handoff Ledger
│   (Immutable JSON & Markdown)│
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│           StatBot            │
│   (Statistical Taxonomy &    │
│    Category Segmentation)    │
└──────────────────────────────┘
```

---

## 2. Transfer Protocol & Schema

In alignment with the **Agent Hand-off Protocol** specified in `AGENTS.md`:
- **Mandatory User Reaffirmation:** A user must reaffirm their request in an explicit prompt (`yes`/`no`) before any relevant intelligence is transferred from PollBot to StatBot. If the user does not reaffirm, the transfer is immediately halted and no data is transferred.
- Every hand-off package is immutable upon writing.
- Payloads maintain source attribution, timestamp, reaffirmation confirmation, and audit metadata.
- Preserves raw statistical metrics to prevent hallucination or numerical drift.

### 2.1 JSON Transfer Schema
```json
{
  "transfer_id": "TRANS-YYYYMMDD-###",
  "source_agent": "PollBot",
  "target_agent": "StatBot",
  "timestamp": "ISO-8601 UTC timestamp",
  "status": "READY_FOR_CATEGORIZATION",
  "user_reaffirmed": true,
  "dataset_reference": "Name of polling dataset or event",
  "metadata": {
    "model": "claude-haiku-4-5-20251001",
    "serpapi_grounding": true,
    "confidence_score": 0.90,
    "reaffirmation_confirmed_at": "ISO-8601 UTC timestamp"
  },
  "content": {
    "summary": "High-level analytical summary",
    "key_findings": [
      "Finding 1 with explicit metrics...",
      "Finding 2..."
    ],
    "suggested_categories": [
      "Demographic Factors",
      "Geographic Factors",
      "Methodology & Errors",
      "Turnout & Motivation"
    ]
  }
}
```

### 2.2 Markdown Transfer Format
For human-readable audit trails and CLI pipeline outputs, transfer dossiers are also saved as `.md` files containing structured headings and bulleted data points.

---

## 3. Usage & CLI Workflow

### 3.1 Initiating Transfer from PollBot (with User Reaffirmation)
```powershell
# Transfer polling intelligence to StatBot (prompts user for reaffirmation)
python -m src.agents.pollbot --transfer tests/sample_polls.json

# Non-interactive automated pipeline transfer (with explicit reaffirmation)
python -m src.agents.pollbot --transfer tests/sample_polls.json --reaffirm yes

# Interactive chat transfer
# Launch chat: python -m src.agents.pollbot --chat
# Type: /transfer
# Prompt: "Do you reaffirm your request to transfer this information from PollBot to StatBot? (yes/no): "
```

### 3.2 StatBot Ingesting & Categorizing Transfer File
StatBot can ingest and categorize any payload from this directory via CLI:

```powershell
# Ingest and categorize transfer payload (confirms user reaffirmation)
python -m src.agents.statbot --transfer data/pollbot_to_statbot/sample_pollbot_transfer.json

# Categorize JSON transfer file into custom taxonomies
python -m src.agents.statbot --input data/pollbot_to_statbot/sample_pollbot_transfer.json --categories "Demographic Factors,Geographic Factors,Methodology & Errors,Turnout & Motivation"

# Categorize Markdown transfer file into custom categories with JSON output
python -m src.agents.statbot --input data/pollbot_to_statbot/sample_pollbot_transfer.md --categories "Demographics,Geography,Methodology,Turnout" --format json

# Categorize PollBot results emphasizing custom grouping prompt
python -m src.agents.statbot --input data/pollbot_to_statbot/sample_pollbot_transfer.json --categories "Demographic Factors,Geographic Factors,Methodology & Errors,Turnout & Motivation" --prompt "Emphasize age and gender divides under Demographics, regional geography under Geographic Factors, and turnout salience under Turnout"
```

### 3.3 Synergistic Multi-Agent Collaboration (Zero Repetition)
Execute the unified, bidirectional loop where PollBot and StatBot collaborate through the `IntelligenceLedger` ([`src/tools/ledger.py`](file:///c:/Users/gturn/OneDrive/Assignement%20LIAI%201001/src/tools/ledger.py)):

```powershell
# Run the complete synergistic collaboration demo (with automated reaffirmation)
python -m src.agents.collaborator --demo --reaffirm yes

# Run collaboration on an existing transfer dossier with custom taxonomy rules
python -m src.agents.collaborator --input data/pollbot_to_statbot/sample_pollbot_transfer.json --categories "Demographics,Geography,Methodology,Turnout" --prompt "Focus on age divides under Demographics and rural splits under Geography" --reaffirm yes
```

### 3.4 Sequential Pipeline Coordination Pattern (PollBot First → StatBot Second)
Execute PollBot and StatBot using the sequential pipeline coordination pattern where PollBot runs first, passes verified intelligence across the user reaffirmation gate, and StatBot runs second to categorize findings:

```powershell
# Run sequential pipeline via orchestrator
python -m src.orchestrator.pipeline --sequential --reaffirm yes

# Run sequential pipeline directly via collaborator
python -m src.agents.collaborator --sequential --demo --reaffirm yes

# Run sequential pipeline directly via PollBot
python -m src.agents.pollbot --sequential tests/sample_polls.json --reaffirm yes

# Run sequential pipeline directly via StatBot
python -m src.agents.statbot --sequential tests/sample_polls.json --reaffirm yes
```

---

## 4. File Inventory
- `.gitkeep`: Retains directory tracking in Git.
- `README.md`: Specification and protocol guidelines (this document).
- `sample_pollbot_transfer.json`: Verified JSON test fixture for automated testing and handoff demos.
- `sample_pollbot_transfer.md`: Verified Markdown intelligence dossier fixture.
- `pollbot_to_statbot_transfer.json`: Ingestion payload generated during live agent transfers.
- `categorized_statbot_findings.md`: Markdown taxonomy breakdown generated by StatBot.
- `statbot_categorized_findings.pdf`: Publication-grade categorized PDF dossier generated by StatBot.
- `sequential_pipeline_report.md`: Sequential pipeline Markdown dossier (PollBot first -> StatBot second).
- `sequential_pipeline_report.pdf`: Executive publication-grade sequential PDF dossier syncing to root workspace.
- `collaborative_intelligence_report.md`: Joint intelligence dossier compiled with zero duplicated statements.
- `collaborative_intelligence_report.pdf`: Executive publication-grade collaborative PDF dossier syncing to root workspace.


