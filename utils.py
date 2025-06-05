# utils.py

from datetime import date, timedelta

def months_back(n: int) -> tuple[str, str]:
    """
    Return (start_iso, end_iso) covering the last n months until today.

    E.g. if today is 2025-05-18 and n is 3,
    start_iso will be 2025-02-17 and end_iso  2025-05-18.
    """
    end = date.today()
    start = end - timedelta(days=30 * n)
    return start.isoformat(), end.isoformat()

