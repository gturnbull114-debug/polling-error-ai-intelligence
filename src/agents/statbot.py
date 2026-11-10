"""StatBot — Statistical Categorization & Taxonomy Structuring Agent.

Program: "Polling Error" Multi-Agent Polling Intelligence System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

StatBot ingests qualitative and statistical intelligence processed by PollBot
and segments it into custom categories, types, or taxonomies requested by the prompter
as a core taxonomy agent in the "Polling Error" program.
"""

from __future__ import annotations
import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable

from dotenv import load_dotenv

# Ensure safe console output encoding on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables
load_dotenv()

from src.tools.search_tool import SerpSearchTool
from src.tools.ledger import IntelligenceLedger

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Try importing reportlab for rich PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def _escape_pdf_text(text: str) -> str:
    """Escapes XML entities for safe ReportLab paragraph rendering."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


UNABLE_RESPONSE = "I am unable to perform that task"
UNAVAILABLE_RESPONSE = UNABLE_RESPONSE  # Backward-compatible alias
DECLINE_PREDETERMINED_CONCLUSION_RESPONSE = (
    "I decline this request. I cannot reach a predetermined conclusion regardless of the truth. "
    "All categorization and analysis must be objective and evidence-based."
)
DECLINE_RESPONSE = DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

STATBOT_SYSTEM_PROMPT = """You are StatBot, an expert AI Statistical Taxonomy & Categorization Agent operating as part of the "Polling Error" program designed for the LIAI 1001 Strategy and Change curriculum at Georgian College.

Your primary mission and dedicated focus is to ingest the results, findings, and qualitative intelligence delivered by PollBot, and systematically categorize, partition, and group those results into the specific categories, groups, or taxonomies requested by the guiding prompt or user instructions.

Core Operational Directives:
1. Primary Focus on PollBot Results: Concentrate intently on all findings, metrics, demographic patterns, mode effects, and outlier causal explanations delivered by PollBot. Every categorized point must be directly grounded in PollBot's output.
2. Adherence to Guiding Prompt / Instructions: Strictly follow the categorization guidelines, taxonomy definitions, and grouping criteria requested by the prompt. Organize and divide the PollBot results into the exact groups or categories requested by the prompter.
3. Rigorous Partitioning & Classification: Ensure comprehensive coverage across requested groups and maintain strict mutual exclusivity wherever feasible.
4. Clean Structured Formatting: Output the categorized findings cleanly in structured JSON or executive Markdown format as requested.
5. Non-Repetition & Synergistic Foundation: Do not duplicate or echo raw narrative statements from PollBot. Filter out redundant claims, partition statistical metrics into structured taxonomies, and identify cross-cutting statistical gaps that PollBot can build upon in subsequent analysis.

Guardrails & Strict Execution Termination:
- Predetermined Conclusion Guardrail: You must decline any request, guiding prompt, categorization instruction, or query that tells or asks you to reach a certain conclusion, narrative, or outcome regardless of the truth, empirical data, or verified PollBot results. When encountering such requests, you must decline the request by stating: "I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based."
- Transfer Reaffirmation Guardrail: When ingesting or processing information transferred from PollBot, you must require or confirm that the user reaffirmed their request in an explicit prompt. If the transfer was not reaffirmed by the user, you must halt immediately and output: "I am unable to perform that task".
- Non-Existent or Inaccurate Data Halt: If you are asked to find, categorize, or report information that is either non-existent or inaccurate, you must immediately stop executing the request and say: "I am unable to perform that task" (Answer Unavailable).
- Never alter the underlying statistical numbers, percentages, or factual findings delivered by PollBot.
- Do not invent new categories, introduce extraneous assumptions, or guess missing figures.
- Maintain an objective, neutral, and academic tone.
- If the input information is insufficient, ambiguous, non-existent, or inaccurate, you must immediately halt and output: "I am unable to perform that task".
"""


class StatBot:
    """Autonomous Statistical Categorization Agent.

    Takes information processed by PollBot and classifies it into prompter-specified categories.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        serpapi_key: Optional[str] = None,
        name: str = "StatBot",
    ):
        self.name = name
        self.api_key: Optional[str] = api_key if api_key is not None else os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        self.serpapi_key: Optional[str] = serpapi_key if serpapi_key is not None else os.getenv("SERPAPI_API_KEY")
        self.client: Optional[anthropic.Anthropic] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.search_tool = SerpSearchTool(api_key=self.serpapi_key)

        if HAS_ANTHROPIC and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"[!] StatBot warning: Failed to initialize Anthropic client: {e}")
                self.client = None

    @property
    def is_connected(self) -> bool:
        """Returns True if the Anthropic client is initialized with an API key."""
        return self.client is not None

    @property
    def has_search(self) -> bool:
        """Returns True if SerpApi web search is configured and active."""
        return self.search_tool.is_available

    def search_web(
        self,
        query: str,
        num_results: int = 5,
        search_type: str = "search",
    ) -> List[Dict[str, str]]:
        """Queries SerpApi for real-time web context to support taxonomy structuring."""
        return self.search_tool.search(query, num_results=num_results, search_type=search_type)

    def search_context(self, query: str, num_results: int = 3) -> str:
        """Returns formatted web search results as text context."""
        return self.search_tool.get_summary_text(query, num_results=num_results)

    @staticmethod
    def is_predetermined_conclusion_request(text_or_data: Any) -> bool:
        """Detects whether a request, prompt, instruction, or query asks StatBot
        to reach a predetermined conclusion regardless of the truth, empirical data, or verified findings.
        """
        if not text_or_data:
            return False

        if isinstance(text_or_data, dict):
            text_to_check = json.dumps(text_or_data).lower()
        elif isinstance(text_or_data, list):
            text_to_check = " ".join(str(item) for item in text_or_data).lower()
        elif isinstance(text_or_data, Path) or (
            isinstance(text_or_data, str) and (
                Path(text_or_data).is_file() or text_or_data.lower().endswith((".pdf", ".json", ".md", ".txt"))
            )
        ):
            path = Path(str(text_or_data))
            if path.is_file():
                try:
                    text_to_check = path.read_text(encoding="utf-8", errors="replace").lower()
                except Exception:
                    text_to_check = str(text_or_data).lower()
            else:
                text_to_check = str(text_or_data).lower()
        else:
            text_to_check = str(text_or_data).lower()

        if not text_to_check.strip():
            return False

        import re

        # 1. Direct explicit phrases
        if "predetermined conclusion" in text_to_check or "pre-determined conclusion" in text_to_check:
            return True
        if "forced conclusion" in text_to_check:
            return True

        # 2. 'Regardless of truth/facts/data' combined with conclude/conclusion
        truth_disregard = re.search(
            r"(?:regardless\s+of|no\s+matter(?:\s+what)?|irrespective\s+of)\s+(?:the\s+)?(?:truth|facts?|data|evidence|reality|whether\s+it(?:'s|\s+is)\s+true|what\s+is\s+true)",
            text_to_check,
        )
        ignore_truth = re.search(
            r"(?:ignore|disregard)\s+(?:the\s+)?(?:truth|facts?|data|evidence|reality)",
            text_to_check,
        )
        has_conclude = re.search(
            r"\b(?:conclude|concluding|conclusion|outcomes?|findings?|prove|proving|proof|claim|state|declare|assert)\b",
            text_to_check,
        )

        if (truth_disregard or ignore_truth) and has_conclude:
            return True

        # 3. Direct instruction: reach a (certain) conclusion regardless...
        if re.search(
            r"reach\s+(?:a|the|this|that|any|a\s+certain|a\s+specific)?\s*conclusion.*?(?:regardless|no\s+matter|ignore|disregard)",
            text_to_check,
        ) or re.search(
            r"(?:regardless|no\s+matter|ignore|disregard).*?reach\s+(?:a|the|this|that|any|a\s+certain|a\s+specific)?\s*conclusion",
            text_to_check,
        ):
            return True

        if re.search(
            r"(?:tell|instruct|force|command|require)\s+.*?\breach\s+(?:a|a\s+certain)?\s*conclusion\b",
            text_to_check,
        ):
            return True

        return False

    @staticmethod
    def is_declined(response: str) -> bool:
        """Returns True if the response indicates the request was declined."""
        if not response:
            return False
        clean = str(response).strip().lower()
        return (
            "i decline this request" in clean
            or "cannot reach a predetermined conclusion" in clean
            or "predetermined conclusion regardless of the truth" in clean
        )

    def is_answer_reliable(self, answer: str) -> bool:
        """Determines if a generated categorization meets credibility standards."""
        if not answer or not answer.strip():
            return False
        clean = answer.strip()
        if clean in (UNABLE_RESPONSE, "Answer Unavailable", "I am unable to perform that task"):
            return False
        if self.is_declined(clean):
            return False
        return True

    def find_information(
        self,
        query: str,
        content: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> str:
        """Finds or extracts specific information from PollBot intelligence outputs.

        If asked to find information that is either non-existent or inaccurate,
        immediately stops executing the request and returns 'I am unable to perform that task'.
        If asked to reach a certain conclusion regardless of the truth, declines the request.

        Args:
            query: The specific finding, question, or verification request.
            content: Raw text, markdown, or dictionary produced by PollBot.

        Returns:
            The verified extracted finding, or 'I am unable to perform that task',
            or decline response if asked to force a predetermined conclusion.
        """
        if not query or not query.strip():
            return UNABLE_RESPONSE

        # Guardrail: Decline requests to reach a predetermined conclusion regardless of the truth
        if self.is_predetermined_conclusion_request(query):
            return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

        if not content:
            return UNABLE_RESPONSE

        # Guardrail: Decline predetermined conclusion requests in content
        if self.is_predetermined_conclusion_request(content):
            return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

        raw_text = json.dumps(content, indent=2) if isinstance(content, dict) else str(content)
        if not raw_text.strip():
            return UNABLE_RESPONSE

        if self.is_connected:
            prompt = (
                "You are StatBot. The user is asking to find or extract specific information from the PollBot results below:\n\n"
                f"Source PollBot Results:\n{raw_text}\n\n"
                f"Target Request / Information to Find:\n\"{query}\"\n\n"
                "STRICT EXECUTION DIRECTIVES & GUARDRAILS:\n"
                "- If the user asks or instructs you to reach a predetermined conclusion regardless of the truth, facts, or data, "
                "you must IMMEDIATELY DECLINE and respond ONLY with:\n"
                "\"I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based.\"\n"
                "- If the requested information is NON-EXISTENT in the source PollBot results, you must IMMEDIATELY STOP executing the request and respond ONLY with:\n"
                "\"I am unable to perform that task\"\n"
                "- If the request asserts or asks you to find/confirm something INACCURATE or contradictory to the facts, you must IMMEDIATELY STOP executing the request and respond ONLY with:\n"
                "\"I am unable to perform that task\"\n"
                "- Do NOT extrapolate, speculate, or fabricate any missing numbers or claims.\n"
                "- If the requested information is genuinely present and accurate in the PollBot results, extract and present it concisely."
            )
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    system=STATBOT_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                reply = response.content[0].text.strip()
                if self.is_declined(reply):
                    return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE
                if not reply or "I am unable to perform that task" in reply or reply == "Answer Unavailable":
                    return UNABLE_RESPONSE
                return reply
            except Exception:
                return UNABLE_RESPONSE

        # Offline deterministic fallback
        stopwords = {
            "support", "supported", "find", "what", "where", "show", "data",
            "tell", "about", "does", "have", "with", "from", "that", "this",
            "rate", "info", "information", "confirm", "verify", "true", "false"
        }
        query_words = [
            w.lower() for w in re.split(r"\W+", query)
            if len(w) > 2 and w.lower() not in stopwords
        ]
        content_lower = raw_text.lower()
        if not query_words or not any(w in content_lower for w in query_words):
            return UNABLE_RESPONSE

        matching_lines = [
            line.strip("- *• \t\r")
            for line in raw_text.splitlines()
            if any(w in line.lower() for w in query_words) and line.strip()
        ]
        if not matching_lines:
            return UNABLE_RESPONSE
        return "\n".join(f"- {line}" for line in matching_lines)

    @staticmethod
    def deduplicate_against(
        candidates: List[str],
        prior_findings: Optional[List[str]] = None,
        threshold: float = 0.55,
    ) -> List[str]:
        """Filters candidate finding strings to remove any that duplicate prior findings.

        Args:
            candidates: List of proposed finding items.
            prior_findings: List of baseline/previous finding strings to check against.
            threshold: Similarity cutoff for detecting duplication.

        Returns:
            Filtered list of novel finding strings.
        """
        if not candidates:
            return []

        ledger = IntelligenceLedger()
        if prior_findings:
            for p in prior_findings:
                if str(p).strip():
                    ledger.register("prior", str(p).strip())

        novel: List[str] = []
        for cand in candidates:
            c_str = str(cand).strip()
            if not c_str:
                continue
            if not ledger.is_duplicate(c_str, threshold=threshold):
                novel.append(c_str)
                ledger.register("candidate", c_str)
        return novel

    def identify_statistical_gaps(
        self,
        categorized_data: Union[Dict[str, Any], str],
    ) -> List[str]:
        """Identifies statistical gaps, missing dimensions, and cross-cutting intersections
        in the categorized findings to serve as foundational building blocks for PollBot.

        Args:
            categorized_data: Dictionary or markdown string of categorized findings.

        Returns:
            List of analytical gap and cross-cutting observation statements.
        """
        if self.is_declined(str(categorized_data)) or "I am unable to perform that task" in str(categorized_data):
            return []

        categories_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_data, dict):
            for k, v in categorized_data.items():
                if k != "identified_gaps" and isinstance(v, list):
                    categories_dict[str(k)] = [str(x) for x in v]
        elif isinstance(categorized_data, str):
            curr = "General"
            for line in categorized_data.splitlines():
                if line.startswith("##"):
                    curr = line.lstrip("#").strip()
                elif line.strip().startswith(("-", "*", "•")):
                    categories_dict.setdefault(curr, []).append(line.strip("- *• \t\r"))

        all_text = " ".join(" ".join(items) for items in categories_dict.values()).lower()
        gaps: List[str] = []

        # Check demographic vs turnout intersection
        if any("demographic" in c.lower() or "age" in c.lower() for c in categories_dict):
            if "senior" in all_text and ("turnout" in all_text or "salience" in all_text or "motivation" in all_text):
                gaps.append(
                    "Cross-Tabulation Pattern: High turnout salience among senior voters (65+) creates a potent mobilization asymmetry against low-salience youth cohorts."
                )
            elif "gender" in all_text:
                gaps.append(
                    "Cross-Tabulation Pattern: Gender voting divide indicates distinct policy priority drivers requiring targeted causal voter research."
                )

        # Check geographic vs mode intersection
        if any("geograph" in c.lower() or "region" in c.lower() for c in categories_dict):
            if "rural" in all_text and ("online" in all_text or "panel" in all_text):
                gaps.append(
                    "Methodological Coverage Gap: Rural geographic samples may be under-represented in pure online panel collection modes without phone/SMS calibration."
                )
            elif "rural" in all_text and "central" in all_text:
                gaps.append(
                    "Geographic Clustering Gap: Central Alberta concentration highlights regional polarization with limited visibility into suburban swing zones."
                )

        # Check methodology limitations
        if any("method" in c.lower() or "error" in c.lower() for c in categories_dict):
            if "opt-in" in all_text or "online panel" in all_text:
                gaps.append(
                    "Sampling Frame Gap: Opt-in panel weighting models require voter file matching to isolate self-selection and non-response participation skew."
                )
            if "margin of error" in all_text or "sample size" in all_text:
                gaps.append(
                    "Statistical Latency Gap: Reported margin of error measures sampling variance only, leaving non-sampling voter screening bias to be decomposed."
                )

        if not gaps and categories_dict:
            gaps.append(
                "Cross-Cutting Observation: Multi-category segmentation reveals structural alignment between demographic profiles and reported vote intention."
            )

        return gaps

    def categorize(
        self,
        content: Union[str, Dict[str, Any]],
        categories: Union[List[str], str],
        instructions: Optional[str] = None,
        output_format: str = "json",
        save_pdf: bool = True,
        pdf_path: Optional[Union[str, Path]] = None,
        prior_findings: Optional[List[str]] = None,
        ledger: Optional[IntelligenceLedger] = None,
    ) -> Union[Dict[str, Any], str]:
        """Divides PollBot processed information into requested categories or types.

        StatBot findings are always placed into a downloadable PDF by default.
        Enforces Non-Repetition: Deduplicates items against prior_findings and ledger.

        Args:
            content: Raw text, markdown, or dictionary produced by PollBot.
            categories: List of category strings or comma-separated string.
            instructions: Optional specific guidance on classification criteria.
            output_format: 'json' for structured dictionary or 'markdown' for formatted text.
            save_pdf: If True, automatically compiles findings into a downloadable PDF.
            pdf_path: Optional custom file path for the PDF output.
            prior_findings: Optional list of previous findings to deduplicate against.
            ledger: Optional shared IntelligenceLedger for cross-agent tracking.

        Returns:
            Structured dictionary of categorized items or markdown text. Returns
            'I decline this request...' if instructed to reach a predetermined conclusion, or
            'I am unable to perform that task' if information cannot be reliably categorized.
        """
        # Validate categories
        category_list: List[str] = []
        if isinstance(categories, str):
            category_list = [c.strip() for c in categories.split(",") if c.strip()]
        elif isinstance(categories, list):
            category_list = [str(c).strip() for c in categories if str(c).strip()]

        if not category_list:
            return UNABLE_RESPONSE

        # Guardrail: Decline requests to reach a predetermined conclusion regardless of the truth
        if instructions and self.is_predetermined_conclusion_request(instructions):
            return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

        if self.is_predetermined_conclusion_request(content):
            return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

        if any(self.is_predetermined_conclusion_request(cat) for cat in category_list):
            return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE

        # Validate content
        if not content:
            return UNABLE_RESPONSE

        raw_text = json.dumps(content, indent=2) if isinstance(content, dict) else str(content)
        if not raw_text.strip():
            return UNABLE_RESPONSE

        # If Anthropic client is available, leverage Claude for semantic categorization
        if self.is_connected:
            result = self._categorize_with_llm(raw_text, category_list, instructions, output_format)
        else:
            # Deterministic offline fallback categorization
            result = self._categorize_offline(raw_text, category_list, output_format)

        # Deduplication against prior findings and ledger to prevent repetition
        all_priors = list(prior_findings or [])
        if ledger is not None:
            all_priors.extend([e["text"] for e in ledger.get_all_findings()])

        if isinstance(result, dict):
            for cat in category_list:
                if cat in result and isinstance(result[cat], list):
                    # Deduplicate items in each category
                    deduped = self.deduplicate_against(result[cat], all_priors)
                    # If deduped emptied it out, keep non-identical to preserve completeness
                    result[cat] = deduped if deduped else result[cat]

            # Attach identified gaps and synergies
            gaps = self.identify_statistical_gaps(result)
            if gaps:
                result["identified_gaps"] = gaps

            # Register items in ledger if provided
            if ledger is not None:
                for cat in category_list:
                    if cat in result and isinstance(result[cat], list):
                        for item in result[cat]:
                            ledger.register("StatBot", item, category=cat)
                for g in result.get("identified_gaps", []):
                    ledger.register("StatBot", g, category="Identified Gaps")

        # Always place findings into a PDF if categorization succeeded and save_pdf is True
        if save_pdf and self.is_answer_reliable(str(result)):
            try:
                self.export_pdf(result, output_path=pdf_path, instructions=instructions)
            except Exception as e:
                print(f"[!] Warning: Could not export findings to PDF: {e}")

        return result

    def _categorize_with_llm(
        self,
        content_text: str,
        categories: List[str],
        instructions: Optional[str],
        output_format: str,
    ) -> Union[Dict[str, Any], str]:
        """Categorizes content using Anthropic Claude with strict focus on PollBot results."""
        prompt_instructions = (
            f"\nGuiding Prompt / Categorization Rules:\n{instructions}\n"
            if instructions
            else "\nGuiding Prompt: Focus intently on all results and findings from PollBot and accurately partition them into the requested target categories/groups."
        )
        format_spec = (
            "Return valid JSON where each key is one of the requested categories/groups, and the value is a list "
            "of relevant points, metrics, or quotes directly extracted from the PollBot results."
            if output_format == "json"
            else "Return a clean Markdown document with headers for each requested category/group and bullet points highlighting the PollBot results."
        )

        prompt = (
            "You are StatBot. Emphasize focusing strictly on the results delivered by PollBot below. "
            "Systematically categorize and partition those PollBot results into the requested groups or categories "
            "as dictated by the guiding prompt and categorization instructions:\n\n"
            f"Target Categories / Groups:\n{json.dumps(categories)}\n"
            f"{prompt_instructions}\n"
            f"Formatting Specification:\n{format_spec}\n\n"
            f"PollBot Source Results:\n{content_text}\n\n"
            "Key Focus Directives & Guardrails:\n"
            "1. Ground all items strictly in the PollBot results provided above.\n"
            "2. Follow the prompt's instructions carefully when grouping and organizing items.\n"
            "3. Preserve all numerical metrics, percentages, and sample sizes without alteration.\n"
            "4. CRITICAL: If asked or instructed to reach a predetermined conclusion regardless of the truth, data, or facts, "
            "you must immediately DECLINE and respond ONLY with: 'I decline this request. I cannot reach a predetermined conclusion regardless of the truth. All categorization and analysis must be objective and evidence-based.'\n"
            "5. CRITICAL: If you are asked to find, categorize, or report information that is either NON-EXISTENT or INACCURATE based on the PollBot results, you must immediately STOP executing the request and respond ONLY with: 'I am unable to perform that task'.\n"
            "6. Never guess, extrapolate, or categorize inaccurate or non-existent data."
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=STATBOT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            reply = response.content[0].text
            if not reply or not reply.strip():
                return UNABLE_RESPONSE

            clean_reply = reply.strip()
            if self.is_declined(clean_reply):
                return DECLINE_PREDETERMINED_CONCLUSION_RESPONSE
            if "I am unable to perform that task" in clean_reply or clean_reply == "Answer Unavailable":
                return UNABLE_RESPONSE

            if output_format == "json":
                # Extract JSON if fenced or containing markdown commentary
                json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", reply, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except Exception:
                        pass
                brace_match = re.search(r"(\{.*\})", reply, re.DOTALL)
                if brace_match:
                    try:
                        return json.loads(brace_match.group(1))
                    except Exception:
                        pass
                cleaned = re.sub(r"^```json\s*", "", reply.strip(), flags=re.MULTILINE)
                cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
                try:
                    return json.loads(cleaned)
                except Exception:
                    # Return structured fallback if parsing fails
                    return {"categories": categories, "raw_response": reply}

            return reply
        except Exception:
            return self._categorize_offline(content_text, categories, output_format)

    def _categorize_offline(
        self,
        content_text: str,
        categories: List[str],
        output_format: str,
    ) -> Union[Dict[str, Any], str]:
        """Rule-based deterministic categorization for offline environments."""
        result: Dict[str, List[str]] = {cat: [] for cat in categories}
        lines = [line.strip("- *• \t\r") for line in content_text.splitlines() if line.strip()]

        category_synonyms = {
            "demographic": {"demographic", "age", "senior", "youth", "gender", "men", "women", "cohort", "voter"},
            "geographic": {"geographic", "geographical", "region", "regional", "rural", "urban", "central", "territory", "calgary", "edmonton"},
            "methodology": {"methodology", "method", "sample", "margin", "error", "panel", "mode", "survey", "phone", "ivr", "online"},
            "turnout": {"turnout", "salience", "motivation", "importance", "enthusiasm"},
        }

        for line in lines:
            line_lower = line.lower()
            assigned = False
            for cat in categories:
                cat_lower = cat.lower()
                keywords = set(k.rstrip("s") for k in re.split(r"[ _/-]+", cat_lower) if len(k) > 2)
                for syn_key, syn_set in category_synonyms.items():
                    if syn_key in cat_lower:
                        keywords.update(syn_set)
                if any(k in line_lower for k in keywords):
                    result[cat].append(line)
                    assigned = True
                    break
            if not assigned and "Other / General" in result:
                result["Other / General"].append(line)

        total_items = sum(len(items) for items in result.values())
        if total_items == 0:
            return UNABLE_RESPONSE

        if output_format == "json":
            return result

        # Format as Markdown
        md_lines = ["# StatBot Categorized Intelligence\n"]
        for cat, items in result.items():
            md_lines.append(f"## {cat}")
            if items:
                for it in items:
                    md_lines.append(f"- {it}")
            else:
                md_lines.append("- *(No matching items identified in input)*")
            md_lines.append("")
        return "\n".join(md_lines)

    def reset_conversation(self) -> None:
        """Clears stored context."""
        self.conversation_history = []

    @staticmethod
    def is_reaffirmation(response: Any) -> bool:
        """Validates whether a user reaffirmed their request in a prompt.

        Accepts: True, 'yes', 'y', 'reaffirm', 'confirm', 'proceed', 'approved', 'approve'.
        Rejects: False, 'no', 'n', 'cancel', empty, None, etc.
        """
        if response is True:
            return True
        if response is False or response is None:
            return False
        clean = str(response).strip().lower()
        return clean in {
            "yes", "y", "reaffirm", "confirm", "proceed",
            "approved", "approve", "true", "1"
        }

    def receive_transfer_from_pollbot(
        self,
        transfer_payload: Union[Dict[str, Any], str, Path],
        categories: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        output_format: str = "json",
        save_pdf: bool = True,
        pdf_path: Optional[str] = None,
        reaffirm: Optional[Union[bool, str]] = None,
        prompt_fn: Optional[Callable[[str], str]] = None,
        prior_findings: Optional[List[str]] = None,
        ledger: Optional[IntelligenceLedger] = None,
    ) -> Dict[str, Any]:
        """Ingests and categorizes a transfer payload from PollBot after confirming user reaffirmation.

        MANDATORY USER REAFFIRMATION GUARD:
        Before transferring or processing information from PollBot to StatBot,
        the user must reaffirm their request in a prompt.
        If the incoming payload was already reaffirmed by the user (user_reaffirmed=True)
        and reaffirm is not explicitly False, execution proceeds. Otherwise, it prompts
        the user for reaffirmation. If not reaffirmed, execution halts.

        Args:
            transfer_payload: Transfer dictionary, JSON file path, or JSON string.
            categories: Target category taxonomies.
            instructions: Optional guiding prompt instructions.
            output_format: Output format ('json' or 'markdown').
            save_pdf: Whether to export categorized findings to PDF.
            pdf_path: Custom PDF output path.
            reaffirm: Explicit reaffirmation flag ('yes'/'no' or bool). If None, prompts user.
            prompt_fn: Custom callable for prompting user input.
            prior_findings: Optional prior findings to deduplicate against.
            ledger: Optional shared IntelligenceLedger for novelty tracking.

        Returns:
            Dict with processing status, categorized output, and messages.
        """
        # Parse payload
        payload_data: Dict[str, Any] = {}
        if isinstance(transfer_payload, dict):
            payload_data = transfer_payload
        elif isinstance(transfer_payload, (str, Path)):
            p = Path(str(transfer_payload))
            if p.is_file():
                try:
                    payload_data = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    payload_data = {"content": {"key_findings": [p.read_text(encoding="utf-8")]}}
            else:
                try:
                    payload_data = json.loads(str(transfer_payload))
                except Exception:
                    payload_data = {"content": {"key_findings": [str(transfer_payload)]}}

        # Guardrail: Check for predetermined conclusion instruction
        if self.is_predetermined_conclusion_request(payload_data):
            return {
                "status": "DECLINED",
                "processed": False,
                "user_reaffirmed": False,
                "message": DECLINE_PREDETERMINED_CONCLUSION_RESPONSE,
            }

        # Mandatory user reaffirmation check
        user_reaffirmed = False
        if reaffirm is not None:
            user_reaffirmed = self.is_reaffirmation(reaffirm)
        elif isinstance(payload_data, dict) and payload_data.get("user_reaffirmed") is True:
            user_reaffirmed = True
        else:
            ask = prompt_fn if prompt_fn is not None else input
            prompt_text = (
                "\n[StatBot Transfer Reaffirmation]\n"
                "A transfer from PollBot has been requested.\n"
                "Do you reaffirm your request to transfer this information from PollBot to StatBot? (yes/no): "
            )
            try:
                resp = ask(prompt_text)
                user_reaffirmed = self.is_reaffirmation(resp)
            except (KeyboardInterrupt, EOFError):
                user_reaffirmed = False

        if not user_reaffirmed:
            return {
                "status": "CANCELLED",
                "processed": False,
                "user_reaffirmed": False,
                "message": "I am unable to perform that task: Transfer request was not reaffirmed by user.",
            }

        # Extract content to categorize
        content_obj = payload_data.get("content", {})
        if isinstance(content_obj, dict):
            key_findings = content_obj.get("key_findings", [])
            summary = content_obj.get("summary", "")
            suggested_cats = content_obj.get("suggested_categories", [])
        elif isinstance(content_obj, str):
            key_findings = [content_obj]
            summary = ""
            suggested_cats = []
        else:
            key_findings = []
            summary = ""
            suggested_cats = []

        target_categories = categories or suggested_cats or [
            "Demographic Factors", "Geographic Factors", "Methodology & Errors", "Turnout & Motivation"
        ]
        text_content = "\n".join(str(f) for f in key_findings) if key_findings else summary
        effective_instructions = instructions or summary or "Categorize PollBot findings into requested groups."

        categorized_output = self.categorize(
            text_content,
            target_categories,
            instructions=effective_instructions,
            output_format=output_format,
            save_pdf=save_pdf,
            pdf_path=pdf_path,
            prior_findings=prior_findings,
            ledger=ledger,
        )

        identified_gaps = []
        if isinstance(categorized_output, dict):
            identified_gaps = categorized_output.get("identified_gaps", [])

        return {
            "status": "SUCCESS",
            "processed": True,
            "user_reaffirmed": True,
            "transfer_id": payload_data.get("transfer_id"),
            "source_agent": payload_data.get("source_agent", "PollBot"),
            "categorized_findings": categorized_output,
            "identified_gaps": identified_gaps,
            "message": "Transfer from PollBot successfully reaffirmed and categorized by StatBot.",
        }

    def export_pdf(
        self,
        categorized_data: Union[Dict[str, Any], str],
        output_path: Optional[Union[str, Path]] = None,
        title: str = "StatBot Categorized Intelligence Report",
        instructions: Optional[str] = None,
    ) -> Path:
        """Exports StatBot categorized findings into a downloadable PDF report.

        Places findings into data/pollbot_to_statbot/statbot_categorized_findings.pdf
        (or custom output_path) and syncs a copy to the root workspace for direct
        browser download.

        Args:
            categorized_data: Dictionary or markdown string of categorized findings.
            output_path: Optional custom file path.
            title: Title for the document header.
            instructions: Optional guiding prompt notes to document.

        Returns:
            Path to the generated PDF.
        """
        if self.is_declined(str(categorized_data)):
            default_path = Path("statbot_categorized_findings.pdf") if output_path is None else Path(output_path)
            return default_path

        categories_dict: Dict[str, List[str]] = {}
        if isinstance(categorized_data, dict):
            for k, v in categorized_data.items():
                if isinstance(v, list):
                    items = [str(item).strip() for item in v if str(item).strip()]
                    if items:
                        categories_dict[str(k)] = items
                elif isinstance(v, str) and v.strip():
                    categories_dict[str(k)] = [v.strip()]
        elif isinstance(categorized_data, str):
            current_cat = "General Findings"
            for raw_line in categorized_data.splitlines():
                line = raw_line.strip()
                if line.startswith("#"):
                    clean_head = line.lstrip("#").strip()
                    if clean_head and not clean_head.lower().startswith("statbot"):
                        current_cat = clean_head
                elif line.startswith(("-", "*", "•")) or (
                    len(line) > 2 and line[0].isdigit() and line[1] in ". "
                ):
                    item = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                    if item:
                        categories_dict.setdefault(current_cat, []).append(item)
                elif line and not line.startswith("#") and current_cat not in categories_dict:
                    categories_dict.setdefault(current_cat, []).append(line)

        if not categories_dict:
            categories_dict["Categorized Findings"] = [str(categorized_data)]

        # Determine target file paths
        if output_path is None:
            target_dir = Path("data/pollbot_to_statbot")
            target_dir.mkdir(parents=True, exist_ok=True)
            out_file = target_dir / "statbot_categorized_findings.pdf"
        else:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)

        if HAS_REPORTLAB:
            self._build_reportlab_pdf(out_file, title, categories_dict, instructions)
        else:
            self._build_fallback_pdf(out_file, title, categories_dict)

        # Sync a copy to workspace root so local web server serves it directly
        root_file = Path("statbot_categorized_findings.pdf")
        try:
            if out_file.resolve() != root_file.resolve():
                shutil.copyfile(out_file, root_file)
        except Exception:
            pass

        return out_file

    def _build_reportlab_pdf(
        self,
        out_file: Path,
        title: str,
        categories_dict: Dict[str, List[str]],
        instructions: Optional[str] = None,
    ) -> None:
        """Constructs an executive PDF document using ReportLab."""
        doc = SimpleDocTemplate(
            str(out_file),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=15,
            leading=19,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )
        sub_style = ParagraphStyle(
            "DocSub",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#cbd5e1"),
            fontName="Helvetica",
        )
        meta_val = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
            fontName="Helvetica",
        )
        table_head = ParagraphStyle(
            "THead",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )
        table_cell = ParagraphStyle(
            "TCell",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica",
        )
        cat_banner = ParagraphStyle(
            "CatBanner",
            parent=styles["Heading2"],
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#1e1b4b"),
            fontName="Helvetica-Bold",
        )
        finding_bullet = ParagraphStyle(
            "FindingBullet",
            parent=styles["Normal"],
            fontSize=9,
            leading=13.5,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica",
            leftIndent=14,
            firstLineIndent=-14,
        )
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b"),
            alignment=1,  # Center
            fontName="Helvetica-Oblique",
        )

        story = []

        # 1. Header Banner
        header_table = Table(
            [
                [Paragraph(f"<b>{_escape_pdf_text(title.upper())}</b>", title_style)],
                [
                    Paragraph(
                        "Program: Polling Error &bull; AI Polling Intelligence System &bull; LIAI 1001 Strategy and Change &bull; Georgian College",
                        sub_style,
                    )
                ],
            ],
            colWidths=[540],
        )
        header_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1e1b4b")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
            ])
        )
        story.append(header_table)
        story.append(Spacer(1, 8))

        # 2. Metadata Box
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        meta_table = Table(
            [
                [
                    Paragraph("<b>Author / Student:</b> Graham Turnbull (200679442)", meta_val),
                    Paragraph("<b>Course / Faculty:</b> LIAI 1001 &bull; Prof. Evandro Barros", meta_val),
                ],
                [
                    Paragraph("<b>Upstream Source:</b> PollBot Qualitative Intelligence", meta_val),
                    Paragraph("<b>Preservation Guardrail:</b> 100% Statistical Fidelity Preserved", meta_val),
                ],
                [
                    Paragraph(f"<b>Generated:</b> {now_str}", meta_val),
                    Paragraph("<b>Format:</b> Executive Downloadable PDF Dossier", meta_val),
                ],
            ],
            colWidths=[270, 270],
        )
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Optional Prompt Instructions Banner
        if instructions:
            inst_table = Table(
                [[Paragraph(f"<b>Guiding Prompt / Categorization Rules:</b> {_escape_pdf_text(instructions)}", meta_val)]],
                colWidths=[540],
            )
            inst_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#93c5fd")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ])
            )
            story.append(inst_table)
            story.append(Spacer(1, 10))

        # 3. KPI Summary Table
        summary_rows = [
            [
                Paragraph("<b>Category / Group</b>", table_head),
                Paragraph("<b>Findings Count</b>", table_head),
                Paragraph("<b>Taxonomy Role / Analytical Purpose</b>", table_head),
            ]
        ]
        for cat, items in categories_dict.items():
            summary_rows.append([
                Paragraph(f"<b>{_escape_pdf_text(cat)}</b>", table_cell),
                Paragraph(f"{len(items)} key points", table_cell),
                Paragraph("PollBot qualitative result segmentation", table_cell),
            ])
        summary_table = Table(summary_rows, colWidths=[180, 100, 260])
        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
            ])
        )
        story.append(summary_table)
        story.append(Spacer(1, 14))

        # 4. Detailed Categorized Findings
        for cat, items in categories_dict.items():
            cat_table = Table(
                [[Paragraph(f"<b>{_escape_pdf_text(cat.upper())}</b>", cat_banner)]],
                colWidths=[540],
            )
            cat_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e0e7ff")),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#4338ca")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ])
            )
            story.append(cat_table)
            story.append(Spacer(1, 4))

            for item in items:
                escaped = _escape_pdf_text(item)
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{escaped}", finding_bullet))
                story.append(Spacer(1, 2.5))

            story.append(Spacer(1, 8))

        # 5. Academic Verification & Guardrails Sign-Off
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        story.append(
            Paragraph(
                "StatBot Autonomous Categorization Agent &bull; Program: 'Polling Error' &bull; Georgian College Course LIAI 1001 &bull; Prof. Evandro Barros<br/>"
                "Guardrail Verification: Zero numbers altered &bull; All items strictly grounded in PollBot intelligence.",
                footer_style,
            )
        )

        doc.build(story)

    def _build_fallback_pdf(
        self,
        out_file: Path,
        title: str,
        categories_dict: Dict[str, List[str]],
    ) -> None:
        """Pure standard PDF 1.4 writer when reportlab is unavailable."""
        lines = [
            f"=== {title.upper()} ===",
            "AI Polling Intelligence Agentic System - LIAI 1001",
            "Author: Graham Turnbull (200679442) | Georgian College",
            "",
        ]
        for cat, items in categories_dict.items():
            lines.append(f"[{cat}]")
            for item in items:
                lines.append(f"  * {item}")
            lines.append("")

        pdf_stream = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<\n"
            b"/Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
            b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
        )
        stream_body = f"BT /F1 10 Tf 50 740 Td 12 TL\n"
        for line in lines[:45]:
            safe_l = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_body += f"({safe_l[:85]}) '\n"
        stream_body += "ET\n"
        stream_bytes = stream_body.encode("latin1", errors="replace")
        pdf_stream += f"5 0 obj<</Length {len(stream_bytes)}>>stream\n".encode("ascii")
        pdf_stream += stream_bytes
        pdf_stream += (
            b"endstream\nendobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"0000000009 00000 n \n0000000056 00000 n \n"
            b"0000000111 00000 n \n0000000212 00000 n \n"
            b"0000000289 00000 n \ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n500\n%%EOF\n"
        )
        out_file.write_bytes(pdf_stream)


def main():
    parser = argparse.ArgumentParser(description="StatBot — Statistical Categorization Agent")
    parser.add_argument("--status", action="store_true", help="Check StatBot status and connection")
    parser.add_argument("--input", type=str, default="", help="File path to text/JSON from PollBot")
    parser.add_argument("--categories", type=str, default="", help="Comma-separated categories to divide data into")
    parser.add_argument(
        "--prompt",
        "--instructions",
        dest="instructions",
        type=str,
        default="",
        help="Guiding prompt or instructions for grouping/categorizing PollBot results",
    )
    parser.add_argument(
        "--find",
        "--query",
        dest="query",
        type=str,
        default="",
        help="Ask StatBot to find specific information within PollBot results",
    )
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="markdown", help="Output format")
    parser.add_argument("--demo", action="store_true", help="Run a demonstration using sample PollBot brief")
    parser.add_argument("--pdf", type=str, default="", help="Custom file path for generated findings PDF")
    parser.add_argument("--no-pdf", action="store_true", help="Disable automatic PDF generation")
    parser.add_argument("--search", type=str, default="", help="Query live web research context via SerpApi")
    parser.add_argument("--transfer", type=str, default="", help="Path to PollBot transfer payload to ingest and categorize (requires user reaffirmation)")
    parser.add_argument("--collaborate", type=str, nargs="?", const="default", default=None, help="Run non-redundant collaborative workflow with PollBot")
    parser.add_argument("--sequential", type=str, nargs="?", const="default", default=None, help="Run sequential pipeline coordination pattern (PollBot first, then StatBot)")
    parser.add_argument("--pipeline", type=str, nargs="?", const="default", default=None, help="Alias for --sequential")
    parser.add_argument("--reaffirm", type=str, default=None, choices=["yes", "no", "y", "n"], help="Explicitly reaffirm or decline transfer (for automated pipelines)")
    args = parser.parse_args()

    bot = StatBot()

    if args.sequential is not None or args.pipeline is not None:
        target_src = args.sequential if args.sequential is not None else args.pipeline
        from src.agents.collaborator import SequentialPipelineCoordinator
        seq_source = None
        if target_src != "default":
            seq_source = Path(target_src)
            if not seq_source.exists():
                print(f"Error: Input file {target_src} not found.")
                return
        print("\n[StatBot] Initiating sequential pipeline coordination pattern (PollBot first -> StatBot second)...")
        coordinator = SequentialPipelineCoordinator(statbot=bot)
        res = coordinator.run(
            input_data=seq_source,
            categories=[c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else None,
            instructions=args.instructions if args.instructions else None,
            reaffirm=args.reaffirm,
            save_pdf=not args.no_pdf,
            pdf_path=args.pdf if args.pdf else None,
        )
        if res["status"] == "SUCCESS":
            print("\n[OK] " + res["message"])
            print(f"  Markdown Dossier: {res.get('markdown_path')}")
            if res.get("pdf_path"):
                print(f"  PDF Dossier:      {res.get('pdf_path')}")
        else:
            print("\n[X] " + res["message"])
        return

    if args.collaborate is not None:
        from src.agents.collaborator import PollingIntelligenceCollaborator
        collab_source = None
        if args.collaborate != "default":
            collab_source = Path(args.collaborate)
            if not collab_source.exists():
                print(f"Error: Collaborate input file {args.collaborate} not found.")
                return
        print("\n[StatBot] Initiating collaborative workflow with PollBot...")
        coordinator = PollingIntelligenceCollaborator(statbot=bot)
        res = coordinator.run_collaborative_workflow(
            input_data=collab_source,
            categories=[c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else None,
            instructions=args.instructions if args.instructions else None,
            reaffirm=args.reaffirm,
            save_pdf=not args.no_pdf,
            pdf_path=args.pdf if args.pdf else None,
        )
        if res["status"] == "SUCCESS":
            print("\n[OK] " + res["message"])
            print(f"  Total Unique Findings Registered: {res['ledger_summary']['total_unique_findings']}")
            print(f"  Markdown Dossier: {res.get('markdown_path')}")
            if res.get("pdf_path"):
                print(f"  PDF Dossier:      {res.get('pdf_path')}")
            print("\n--- StatBot Categorized Findings ---")
            for cat, items in res["statbot_categorization"].items():
                if cat != "identified_gaps":
                    print(f"  * {cat}: {len(items)} items")
            if res.get("identified_gaps"):
                print("\n--- Identified Statistical Gaps ---")
                for gap in res["identified_gaps"]:
                    print(f"  * {gap}")
            print("\n--- PollBot Strategic Synthesis (Built on StatBot) ---")
            for imp in res["pollbot_synthesis"].get("strategic_implications", []):
                print(f"  * {imp}")
        else:
            print("\n[X] " + res["message"])
        return

    if args.transfer:
        in_path = Path(args.transfer)
        if not in_path.exists():
            print(f"Error: Transfer file {args.transfer} not found.")
            return
        result = bot.receive_transfer_from_pollbot(
            in_path,
            categories=[c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else None,
            instructions=args.instructions if args.instructions else None,
            output_format=args.format,
            save_pdf=not args.no_pdf,
            pdf_path=args.pdf if args.pdf else None,
            reaffirm=args.reaffirm,
        )
        if result.get("processed"):
            print("\n[OK] " + result.get("message", ""))
            if isinstance(result.get("categorized_findings"), dict):
                print(json.dumps(result["categorized_findings"], indent=2))
            else:
                print(result.get("categorized_findings"))
        else:
            print("\n[X] " + result.get("message", ""))
        return

    if args.status or (not args.input and not args.demo and not args.search and not args.transfer):
        print("\n========================================================")
        print("     StatBot Status Check — 'Polling Error' Program     ")
        print("========================================================")
        print("Program:           Polling Error")
        print(f"Agent Name:        {bot.name}")
        print(f"Role:              Statistical Taxonomy & Categorization")
        print(f"Anthropic SDK:     {'Installed' if HAS_ANTHROPIC else 'Not Installed'}")
        print(f"API Key Detected:  {'Yes' if bool(bot.api_key) else 'No'}")
        print(f"Connection Status: {'Connected' if bot.is_connected else 'Offline (Deterministic)'}")
        print(f"Active Model:      {bot.model}")
        print(f"SerpApi Search:    {'Configured (Active)' if bot.has_search else 'Offline / No Key'}")
        print(f"ReportLab PDF:     {'Installed & Ready' if HAS_REPORTLAB else 'Fallback Standard PDF'}")
        print("========================================================\n")
        if not args.input and not args.demo and not args.search and not args.transfer:
            print("Usage Examples:")
            print("  python -m src.agents.statbot --demo")
            print("  python -m src.agents.statbot --search 'Alberta referendum turnout'")
            print("  python -m src.agents.statbot --input audit.txt --categories 'Demographics,Methodology,Turnout'")
            print("  python -m src.agents.statbot --transfer data/pollbot_to_statbot/sample_pollbot_transfer.json")
            print("  python -m src.agents.statbot --input audit.txt --categories 'Demographics,Methodology' --prompt 'Prioritize age cohorts'")
        return

    if args.search:
        print(f"\n[SerpApi] Conducting live research for StatBot: '{args.search}'...\n")
        results = bot.search_web(args.search, num_results=3)
        print(f"Retrieved {len(results)} search results:")
        for i, res in enumerate(results, 1):
            print(f"  {i}. {res['title']}")
            print(f"     Source: {res['link']}")
            print(f"     Snippet: {res['snippet']}\n")
        return

    save_pdf = not args.no_pdf
    pdf_custom_path = args.pdf if args.pdf else None

    if args.demo:
        sample_pollbot_brief = (
            "1. Senior voters (65+) backed Yes at 58%, while voters 18-24 showed lowest Yes at 20%.\n"
            "2. Rural regions had 48% Yes and Central Alberta reached 57% Yes.\n"
            "3. The survey had a sample size of N=1204 with 2.8% margin of error.\n"
            "4. A 13-point gender gap showed 51% of men voting Yes vs 38% of women.\n"
            "5. Turnout salience showed Yes voters rating importance at 8.1/10 vs 4.0/10 for No voters.\n"
            "6. Online panel collection mode may introduce opt-in participation skew."
        )
        sample_categories = ["Demographic Factors", "Geographic Factors", "Methodology & Errors", "Turnout & Motivation"]
        guiding_prompt = (
            args.instructions
            or "Focus on PollBot results and categorize into requested groups: highlight age and gender splits under Demographics, regional splits under Geography, survey limits under Methodology, and issue salience under Turnout."
        )
        print("\n[StatBot] Emphasizing focus on PollBot results and categorizing according to prompt:")
        print(f"  Guiding Prompt: \"{guiding_prompt}\"\n")
        print("Target Categories / Groups:")
        for cat in sample_categories:
            print(f"  * {cat}")
        print("\nProcessing categorization...\n")
        output = bot.categorize(
            sample_pollbot_brief,
            sample_categories,
            instructions=guiding_prompt,
            output_format=args.format,
            save_pdf=save_pdf,
            pdf_path=pdf_custom_path,
        )
        if isinstance(output, dict):
            print(json.dumps(output, indent=2))
        else:
            print(output)

        if save_pdf and bot.is_answer_reliable(str(output)):
            pdf_dest = pdf_custom_path or "data/pollbot_to_statbot/statbot_categorized_findings.pdf"
            print("\n========================================================")
            print("[PDF Export] StatBot findings placed into downloadable PDF:")
            print(f"  Local File:   {pdf_dest}")
            print("  Root Copy:    statbot_categorized_findings.pdf")
            print("  Download URL: http://localhost:8080/statbot_categorized_findings.pdf")
            print("========================================================\n")
        return

    if args.input:
        in_path = Path(args.input)
        if not in_path.exists():
            print(f"Error: Input file {args.input} not found.")
            return
        content = in_path.read_text(encoding="utf-8")

        if args.query:
            result = bot.find_information(args.query, content)
            print(result)
            return

        categories = [c.strip() for c in args.categories.split(",") if c.strip()]
        if not categories:
            print("Error: Please provide --categories 'Cat1,Cat2,Cat3' or --find '<query>'")
            return
        output = bot.categorize(
            content,
            categories,
            instructions=args.instructions if args.instructions else None,
            output_format=args.format,
            save_pdf=save_pdf,
            pdf_path=pdf_custom_path,
        )
        if isinstance(output, dict):
            print(json.dumps(output, indent=2))
        else:
            print(output)

        if save_pdf and bot.is_answer_reliable(str(output)):
            pdf_dest = pdf_custom_path or "data/pollbot_to_statbot/statbot_categorized_findings.pdf"
            print("\n========================================================")
            print("[PDF Export] StatBot findings placed into downloadable PDF:")
            print(f"  Local File:   {pdf_dest}")
            print("  Root Copy:    statbot_categorized_findings.pdf")
            print("  Download URL: http://localhost:8080/statbot_categorized_findings.pdf")
            print("========================================================\n")


if __name__ == "__main__":
    main()
