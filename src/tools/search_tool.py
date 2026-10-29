"""SerpApi Search Tool for Polling Intelligence Agent.

Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Enables autonomous agents (such as PollBot) to conduct live web research on
election news, pollster methodology statements, and historical house effects.
"""

from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()


class SerpSearchTool:
    """Tool for querying real-time web search and news results via SerpApi."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the SerpSearchTool with an optional API key.

        Args:
            api_key: SerpApi key string. If None, falls back to SERPAPI_API_KEY env var.
        """
        self.api_key: Optional[str] = api_key if api_key is not None else os.getenv("SERPAPI_API_KEY")

    @property
    def is_available(self) -> bool:
        """Returns True if a SerpApi key is present and configured."""
        return bool(self.api_key and self.api_key.strip())

    def search(
        self,
        query: str,
        engine: str = "google",
        num_results: int = 5,
        search_type: str = "search",
    ) -> List[Dict[str, str]]:
        """Executes a search query via SerpApi.

        Args:
            query: The search keywords or question.
            engine: Search engine endpoint (defaults to 'google').
            num_results: Maximum results to retrieve.
            search_type: 'search' for organic web results or 'news' for Google News.

        Returns:
            List of structured result dictionaries with 'title', 'snippet', 'link', and 'source'.
        """
        if not self.is_available:
            return [{
                "title": "SerpApi Offline Mode",
                "snippet": f"No SerpApi key configured. Query was: '{query}'",
                "link": "https://serpapi.com",
                "source": "Offline Fallback",
            }]

        params: Dict[str, Any] = {
            "engine": engine,
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
        }
        if search_type == "news":
            params["tbm"] = "nws"

        url = f"https://serpapi.com/search.json?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AIPollingIntelligenceAgent/1.0"},
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))

            results: List[Dict[str, str]] = []

            # Check organic results or news results
            items = payload.get("organic_results", [])
            if not items and "news_results" in payload:
                items = payload.get("news_results", [])

            for item in items[:num_results]:
                results.append({
                    "title": item.get("title", "No Title"),
                    "snippet": item.get("snippet", item.get("description", "")),
                    "link": item.get("link", ""),
                    "source": item.get("source", item.get("displayed_link", "")),
                })

            # Check top stories if organic results were empty
            if not results and "top_stories" in payload:
                for item in payload.get("top_stories", [])[:num_results]:
                    results.append({
                        "title": item.get("title", "Top Story"),
                        "snippet": item.get("date", ""),
                        "link": item.get("link", ""),
                        "source": item.get("source", ""),
                    })

            return results
        except Exception as e:
            return [{
                "title": "SerpApi Request Error",
                "snippet": f"Failed to retrieve search results: {e}",
                "link": "",
                "source": "Error Handler",
            }]

    def get_summary_text(self, query: str, num_results: int = 3) -> str:
        """Returns search results as a formatted markdown text block suitable for LLM prompts."""
        results = self.search(query, num_results=num_results)
        if not results:
            return f"No search results returned for query: '{query}'."

        lines = [f"**Live Search Results for:** `{query}`\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            snippet = r.get("snippet", "").strip()
            link = r.get("link", "")
            source = r.get("source", "")
            source_tag = f" ({source})" if source else ""
            lines.append(f"{i}. **{title}**{source_tag}\n   {snippet}\n   Link: {link}")
        return "\n\n".join(lines)

    def search_pollster_context(self, pollster_name: str, num_results: int = 3) -> str:
        """Convenience query for pollster methodology and credibility context."""
        query = f"{pollster_name} polling methodology house bias track record"
        return self.get_summary_text(query, num_results=num_results)
