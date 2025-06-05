# analyze_transactions.py
"""CreditMaestro – Transaction Analyzer (Anthropic 2025‑05 API)

Fetches transactions from the local MCP adapter (Plaid sandbox) and asks a
Claude 3 model for an analytical summary.

Environment variables (.env):
- ANTHROPIC_API_KEY  (required)  → your Claude key
- CLAUDE_MODEL       (optional) → default "claude-3-haiku-20240307"
- MCP_BASE_URL       (optional) → default "http://127.0.0.1:5000"
- MCP_PATH           (optional) → default "/getTransactions"
- ANALYSIS_START     (optional) → default "2025-04-01"
- ANALYSIS_END       (optional) → default "2025-04-30"
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests
from anthropic import Anthropic, NotFoundError
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# Config & client setup
# ──────────────────────────────────────────────────────────────────────────────

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Set ANTHROPIC_API_KEY in your .env file")

# Default to a Claude 3 model that is generally available; override if needed.
ANTHROPIC_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

MCP_BASE = os.getenv("MCP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
MCP_PATH = os.getenv("MCP_PATH", "/getTransactions")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def fetch_transactions(start: str, end: str) -> List[Dict[str, Any]]:
    """Call the MCP endpoint and return sandbox transactions."""
    url = f"{MCP_BASE}{MCP_PATH}"
    resp = requests.post(url, json={"startDate": start, "endDate": end}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def build_prompt(transactions: List[Dict[str, Any]], start: str, end: str) -> str:
    """Return the user‑facing prompt for Claude."""
    tx_json = json.dumps(transactions, indent=2)
    return (
        f"You are a personal finance analyst. Here are raw credit‑card transactions from {start} to {end}:\n"
        f"{tx_json}\n\n"
        "Please provide:\n"
        "1. A categorized breakdown (e.g. by merchant or type).\n"
        "2. The top 3 spending categories and their totals.\n"
        "3. One actionable suggestion to reduce expenses or improve cashflow."
    )

def analyze(transactions: List[Dict[str, Any]], start: str, end: str) -> str:
    """Send the transaction list to Claude and return its analysis."""
    prompt = build_prompt(transactions, start, end)

    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=700,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
    except NotFoundError as err:
        raise RuntimeError(
            f"Model '{ANTHROPIC_MODEL}' not found – set CLAUDE_MODEL to an available model."
        ) from err

    # Claude 3 responses use a list of messages; the assistant reply is at index 0
    return response.content[0].text.strip() if hasattr(response, "content") else str(response)

# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    start = os.getenv("ANALYSIS_START", "2025-05-01")
    end   = os.getenv("ANALYSIS_END",   "2025-05-30")

    txs = fetch_transactions(start, end)
    analysis = analyze(txs, start, end)

    print("\n=== Claude Analysis ===\n")
    print(analysis)
