"""Direct Cloudflare Pages Deployer (`src/web/deploy_cloudflare.py`).

Program: "Polling Error" — AI Polling Intelligence Agentic System
Course: LIAI 1001 – Strategy and Change (Georgian College)
Student: Graham Turnbull (200679442)

Builds the `dist/` bundle and deploys directly to Cloudflare Pages over HTTPS (port 443)
using Wrangler (`wrangler pages deploy dist --project-name=polling-error-ai-intelligence`).
"""

from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from src.web.build_cloudflare import build_cloudflare_dist

load_dotenv()

PROJECT_NAME = "polling-error-ai-intelligence"
DEFAULT_PORTABLE_NODE = Path(
    r"C:\Users\gturn\.gemini\antigravity\brain\2beb3af5-bfda-4909-90f1-ed9a21294719\scratch\node-v22.11.0-win-x64"
)


def find_npx_executable(custom_node_dir: Optional[Path] = None) -> Optional[str]:
    """Locate `npx.cmd` in PATH or in the portable Node directory."""
    for candidate_dir in (custom_node_dir, DEFAULT_PORTABLE_NODE):
        if candidate_dir and candidate_dir.exists():
            npx_candidate = candidate_dir / "npx.cmd"
            if npx_candidate.exists():
                return str(npx_candidate)
    return "npx.cmd" if sys.platform == "win32" else "npx"


def deploy_to_cloudflare_pages(
    project_name: str = PROJECT_NAME,
    node_dir: Optional[Path] = None,
) -> int:
    """Build `dist/` and deploy to Cloudflare Pages via Wrangler."""
    print("\n[1/3] Building production Cloudflare Pages bundle (dist/)...")
    build_res = build_cloudflare_dist()
    print(f"      [OK] Built {build_res['files_count']} files into {build_res['output_dir']}")

    active_node_dir = node_dir or (DEFAULT_PORTABLE_NODE if DEFAULT_PORTABLE_NODE.exists() else None)
    env = os.environ.copy()
    if active_node_dir and active_node_dir.exists():
        env["PATH"] = f"{active_node_dir}{os.pathsep}{env.get('PATH', '')}"

    npx_cmd = find_npx_executable(node_dir)
    if not npx_cmd:
        print("[!] Error: Could not locate npx to run Wrangler.")
        return 1

    # Check if CLOUDFLARE_API_TOKEN is set or Wrangler OAuth config exists
    wrangler_cfg = Path(os.environ.get("APPDATA", "")) / "xdg.config" / ".wrangler" / "config" / "default.toml"
    if not env.get("CLOUDFLARE_API_TOKEN") and not wrangler_cfg.exists():
        print("\n[Auth] Launching Cloudflare OAuth login in your browser (`wrangler login`)...")
        login_cmd = [npx_cmd, "--yes", "wrangler@3", "login"]
        subprocess.run(login_cmd, env=env, check=False)

    print(f"\n[2/3] Ensuring Cloudflare Pages project '{project_name}' exists...")
    create_cmd = [
        npx_cmd,
        "--yes",
        "wrangler@3",
        "pages",
        "project",
        "create",
        project_name,
        "--production-branch=main",
    ]
    subprocess.run(create_cmd, env=env, check=False)

    print(f"\n[3/3] Deploying dist/ directly to Cloudflare Pages ('{project_name}')...")
    deploy_cmd = [
        npx_cmd,
        "--yes",
        "wrangler@3",
        "pages",
        "deploy",
        "dist",
        f"--project-name={project_name}",
        "--branch=main",
        "--commit-dirty=true",
    ]
    proc = subprocess.run(deploy_cmd, env=env, check=False)
    return proc.returncode


def main() -> None:
    """CLI entry point for direct Cloudflare Pages deployment."""
    parser = argparse.ArgumentParser(description="Deploy 'Polling Error' directly to Cloudflare Pages")
    parser.add_argument("--project", type=str, default=PROJECT_NAME, help="Cloudflare Pages project name")
    parser.add_argument("--node-dir", type=str, default="", help="Optional path to portable Node.js directory")
    args = parser.parse_args()

    node_path = Path(args.node_dir) if args.node_dir else None
    code = deploy_to_cloudflare_pages(project_name=args.project, node_dir=node_path)
    sys.exit(code)


if __name__ == "__main__":
    main()

