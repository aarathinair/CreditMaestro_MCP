
# analyze_patterns.py
import os
import json
import requests
from dotenv import load_dotenv
from anthropic import Anthropic, NotFoundError
from utils import months_back

load_dotenv()

# Config
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("Set ANTHROPIC_API_KEY in your .env file")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
MCP_BASE = os.getenv("MCP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
MCP_PATH = os.getenv("MCP_PATH", "/getTransactions")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Fetch helper
def fetch_range(start: str, end: str) -> list[dict]:
    url = f"{MCP_BASE}{MCP_PATH}"
    resp = requests.post(url, json={"startDate": start, "endDate": end}, timeout=30)
    resp.raise_for_status()
    return resp.json()

# Pattern detection
def detect_patterns(transactions: list[dict], start: str, end: str) -> str:
    prompt = (
        f"You are a finance analyst. The JSON below spans {start} to {end}:\n"
        f"{json.dumps(transactions, indent=2)}\n\n"
        "Find patterns:\n"
        "• Recurring subscriptions (same merchant ≈ same amount).\n"
        "• Categories with a clear upward or downward trend.\n"
        "• Any suspicious duplicates or fees.\n\n"
        "Return a concise bullet list of insights."
    )
    try:
        msg = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=700,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
    except NotFoundError:
        raise RuntimeError(f"Model '{CLAUDE_MODEL}' not found – update CLAUDE_MODEL in .env.")
    return msg.content[0].text.strip()

# Entrypoint
if __name__ == "__main__":
    # Use the 90-day window via utils.months_back
    start, end = months_back(3)  # last 3×30 days ≈ 90 days

    # Fetch transactions for the window
    transactions = fetch_range(start, end)

    # Run pattern detection
    insights = detect_patterns(transactions, start, end)

    print("\n=== Pattern Analysis (90 days) ===\n")
    print(insights)
