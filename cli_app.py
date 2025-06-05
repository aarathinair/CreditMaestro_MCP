# cli_app.py

import os
from datetime import datetime
from utils import months_back
from analyze_transactions import fetch_transactions, analyze as one_month_analyze
from analyze_patterns import fetch_range, detect_patterns
from recommendations import make_recommendations

def prompt_date(prompt_text: str, default: str) -> str:
    val = input(f"{prompt_text} [{default}]: ").strip()
    try:
        datetime.fromisoformat(val or default)
        return val or default
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return prompt_date(prompt_text, default)

if __name__ == "__main__":
    # 1) Get one-month range
    def_start = os.getenv("ANALYSIS_START", "2025-04-01")
    def_end   = os.getenv("ANALYSIS_END",   "2025-04-30")
    start = prompt_date("Enter analysis start date", def_start)
    end   = prompt_date("Enter analysis end   date", def_end)

    # 2) Compute and display analyses
    txs_one = fetch_transactions(start, end)
    summary_one = one_month_analyze(txs_one, start, end)
    print("\n--- One-Month Analysis ---\n", summary_one)

    # 3) Patterns (last 3 months from end date)
    #    Use months_back relative to end
    pat_start, pat_end = months_back(3)
    txs_pat = fetch_range(pat_start, pat_end)
    summary_pat = detect_patterns(txs_pat, pat_start, pat_end)
    print("\n--- 90-Day Patterns ---\n", summary_pat)

    # 4) Recommendations
    recs = make_recommendations(summary_one, summary_pat)
    print("\n--- Recommendations ---\n", recs)
