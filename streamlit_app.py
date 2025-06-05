import os
import json
from datetime import datetime, date

import streamlit as st
from dotenv import load_dotenv

from analyze_transactions import fetch_transactions, analyze as one_month_analyze
from analyze_patterns import fetch_range, detect_patterns
from recommendations import make_recommendations
from utils import months_back

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="CreditMaestro Dashboard", layout="wide")

st.title("💳 CreditMaestro Financial Insights")

# Sidebar for date selection
st.sidebar.header("Date Range Selection")
def iso_to_date(s: str) -> date:
    return datetime.fromisoformat(s).date()

def date_to_iso(d: date) -> str:
    return d.isoformat()

# Default one-month range
default_start = os.getenv("ANALYSIS_START", "2025-04-01")
default_end = os.getenv("ANALYSIS_END", "2025-04-30")

start_date = st.sidebar.date_input(
    "One-Month Start Date", value=iso_to_date(default_start)
)
end_date = st.sidebar.date_input(
    "One-Month End Date", value=iso_to_date(default_end)
)

# Button to run analysis
if st.sidebar.button("Run Analysis"):
    # Convert back to ISO strings
    start_iso = date_to_iso(start_date)
    end_iso = date_to_iso(end_date)
    # Fetch and analyze one-month snapshot
    with st.spinner("Fetching one-month transactions…"):
        txs_one = fetch_transactions(start_iso, end_iso)
    # <-- Insert these two lines to show the raw data -->
    st.subheader("Raw Transactions JSON (One Month)")
    st.json(txs_one)

    with st.spinner("Analyzing one-month data…"):
        summary_one = one_month_analyze(txs_one, start_iso, end_iso)
    # Fetch and analyze 90-day patterns
    pat_start, pat_end = months_back(3)
    with st.spinner("Fetching 90-day transactions…"):
        txs_pat = fetch_range(pat_start, pat_end)
    with st.spinner("Detecting patterns…"):
        summary_pat = detect_patterns(txs_pat, pat_start, pat_end)
    # Generate recommendations
    with st.spinner("Generating recommendations…"):
        recos = make_recommendations(summary_one, summary_pat)

    # Display results in three columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📊 One-Month Analysis")
        st.write(summary_one)
    with col2:
        st.subheader("🔎 90-Day Patterns")
        st.write(summary_pat)
    with col3:
        st.subheader("💡 Recommendations")
        st.write(recos)
else:
    st.info("Select dates on the sidebar and click 'Run Analysis' to get started.")
