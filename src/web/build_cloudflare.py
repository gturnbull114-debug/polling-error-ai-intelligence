"""Cloudflare Pages Static & Edge Bundle Builder (`dist/`).

Program: "Polling Error" — AI Polling Intelligence Agentic System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Assembles the production `dist/` directory for Cloudflare Pages deployment,
packaging only public web assets, publication PDFs, and verified handoff dossiers
while excluding Python virtualenvs, source code, and `.env` secrets.
"""

from __future__ import annotations
import shutil
from pathlib import Path
from typing import Dict, Any


HEADERS_CONTENT = """/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Access-Control-Allow-Origin: *

/*.pdf
  Content-Type: application/pdf
  Cache-Control: public, max-age=3600
"""


def build_cloudflare_dist(workspace_dir: Path | None = None, output_dir_name: str = "dist") -> Dict[str, Any]:
    """Assemble the `dist/` directory for Cloudflare Pages deployment."""
    root = workspace_dir or Path.cwd()
    dist = root / output_dir_name
    dist.mkdir(parents=True, exist_ok=True)

    copied_files = []

    # 1. Copy root web & PDF files
    root_assets = [
        "index.html",
        "statbot_categorized_findings.pdf",
        "sequential_pipeline_report.pdf",
        "collaborative_intelligence_report.pdf",
    ]
    for asset in root_assets:
        src = root / asset
        if src.exists():
            shutil.copy2(src, dist / asset)
            copied_files.append(asset)

    # 2. Copy public handoff ledger artifacts (data/pollbot_to_statbot/)
    handoff_src = root / "data" / "pollbot_to_statbot"
    if handoff_src.exists():
        handoff_dest = dist / "data" / "pollbot_to_statbot"
        handoff_dest.mkdir(parents=True, exist_ok=True)
        for item in handoff_src.iterdir():
            if item.is_file() and item.suffix.lower() in (".json", ".md", ".pdf"):
                shutil.copy2(item, handoff_dest / item.name)
                copied_files.append(f"data/pollbot_to_statbot/{item.name}")

    # 3. Copy public documentation (docs/)
    docs_src = root / "docs"
    if docs_src.exists():
        docs_dest = dist / "docs"
        docs_dest.mkdir(parents=True, exist_ok=True)
        for item in docs_src.iterdir():
            if item.is_file() and item.suffix.lower() in (".md", ".pdf"):
                shutil.copy2(item, docs_dest / item.name)
                copied_files.append(f"docs/{item.name}")

    # 4. Write Cloudflare Pages `_headers` file
    headers_path = dist / "_headers"
    headers_path.write_text(HEADERS_CONTENT, encoding="utf-8")
    copied_files.append("_headers")

    # 5. Create a ready-to-upload ZIP bundle (`cloudflare_pages_deploy.zip`) for Direct Upload
    zip_base = root / "cloudflare_pages_deploy"
    zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=str(dist))

    return {
        "status": "SUCCESS",
        "output_dir": str(dist),
        "zip_path": str(zip_path),
        "files_count": len(copied_files),
        "files": copied_files,
    }


def main() -> None:
    """CLI entry point to build the Cloudflare Pages `dist/` bundle."""
    res = build_cloudflare_dist()
    print("\n======================================================================")
    print("  'Polling Error' — Cloudflare Pages Production Bundle Built (dist/)  ")
    print("======================================================================")
    print(f"  Output Directory: {res['output_dir']}")
    print(f"  Uploadable ZIP:   {res['zip_path']}")
    print(f"  Packaged Assets:  {res['files_count']} files")
    for f in res["files"]:
        print(f"    * {f}")
    print("======================================================================\n")


if __name__ == "__main__":
    main()
