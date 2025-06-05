# recommendations.py

import os
from dotenv import load_dotenv
from analyze_transactions import fetch_transactions, analyze as one_month_analyze
from analyze_patterns import fetch_range, detect_patterns
from anthropic import Anthropic, NotFoundError

load_dotenv()

# Config
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL      = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
client            = Anthropic(api_key=ANTHROPIC_API_KEY)

# Date ranges
ONE_START = os.getenv("ANALYSIS_START", "2025-04-01")
ONE_END   = os.getenv("ANALYSIS_END",   "2025-04-30")
PAT_START, PAT_END = __import__("utils").months_back(3)

def make_recommendations(one_month_summary: str, patterns: str) -> str:
    prompt = (
        f"You have two pieces of analysis:\n\n"
        f"1) One-month summary:\n{one_month_summary}\n\n"
        f"2) 90-day patterns:\n{patterns}\n\n"
        "Based on these, provide:\n"
        "• Top 3 personalized recommendations to improve financial health.\n"
        "• For each, estimate potential monthly savings.\n"
    )
    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=700,
            temperature=0.2,
            messages=[{"role":"user","content":prompt}],
        )
    except NotFoundError:
        raise RuntimeError(f"Model '{CLAUDE_MODEL}' not found.")
    return resp.content[0].text.strip()

if __name__ == "__main__":
    # Fetch & analyze
    one_tx = fetch_transactions(ONE_START, ONE_END)
    one_summary = one_month_analyze(one_tx, ONE_START, ONE_END)

    pat_tx = fetch_range(PAT_START, PAT_END)
    pat_summary = detect_patterns(pat_tx, PAT_START, PAT_END)

    # Generate recommendations
    recos = make_recommendations(one_summary, pat_summary)
    print("\n=== Recommendations ===\n")
    print(recos)
