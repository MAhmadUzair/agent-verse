# app_alpha_twin.py

import os
import uuid
import time
import logging
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Agentic framework & tools
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

# ------------------------------
# Bootstrap & Logging
# ------------------------------
load_dotenv()

# Configure logging for advanced tracking
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_event(event: str, **kwargs):
    """Lightweight structured logger for important checkpoints."""
    payload = {"event": event, "ts": datetime.utcnow().isoformat() + "Z"}
    if kwargs:
        payload.update(kwargs)
    logging.info(payload)
    # Also print for environments that capture stdout
    print(payload)

RUN_ID = str(uuid.uuid4())  # Unique id per session run for traceability
log_event("app_boot", run_id=RUN_ID, user=os.getenv("USER", "unknown"))

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="AlphaTwin — AI Stock Comparator", page_icon="📈", layout="wide")
st.title("AlphaTwin — AI Stock Comparator 📈🤖")
st.caption("Compare two stock tickers with analyst recommendations, price history, and fundamentals.")

with st.sidebar:
    st.subheader("🔐 API Configuration")
    ui_api_key = st.text_input("OpenAI API Key (optional if set in .env)", type="password", help="If not provided here, the app will try to read OPENAI_API_KEY from your environment/.env.")
    use_env_fallback = st.toggle("Use environment fallback", value=True, help="If enabled and the field above is empty, the app will use OPENAI_API_KEY from .env or system env.")
    show_tool_calls = st.toggle("Show tool calls in trace", value=True)

openai_api_key = ui_api_key or (os.getenv("OPENAI_API_KEY") if use_env_fallback else None)

if not openai_api_key:
    st.warning("Please provide an OpenAI API key in the sidebar or set `OPENAI_API_KEY` in your `.env`.")
    log_event("missing_api_key", run_id=RUN_ID)
    st.stop()

# Advanced toggles
with st.sidebar:
    st.subheader("⚙️ Analysis Options")
    price = st.checkbox("Stock Price", value=True)
    analyst = st.checkbox("Analyst Recommendations", value=True)
    fundamentals = st.checkbox("Stock Fundamentals", value=True)
    st.markdown("---")
    st.write("💡 Tip: Use short, valid tickers like **AAPL**, **MSFT**, **NVDA**, **GOOGL**.")

# Columns for user inputs
col1, col2 = st.columns(2)
with col1:
    stock1 = st.text_input("Enter first stock symbol (e.g. AAPL)").strip().upper()
with col2:
    stock2 = st.text_input("Enter second stock symbol (e.g. MSFT)").strip().upper()

# Validate tickers
def is_valid_ticker(t: str) -> bool:
    return len(t) > 0 and t.isalnum() and len(t) <= 10

if stock1 and not is_valid_ticker(stock1):
    st.error("First symbol looks invalid. Use alphanumeric ticker up to 10 chars.")
if stock2 and not is_valid_ticker(stock2):
    st.error("Second symbol looks invalid. Use alphanumeric ticker up to 10 chars.")

# Build Agent
log_event("agent_init_start", run_id=RUN_ID)
assistant = Agent(
    model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
    tools=[
        YFinanceTools(
            stock_price=price,
            analyst_recommendations=analyst,
            stock_fundamentals=fundamentals
        )
    ],
    show_tool_calls=show_tool_calls,
    description=(
        "You are a meticulous investment analyst. You specialize in researching stock prices, "
        "analyst recommendations, and company fundamentals. You compare two tickers and produce "
        "a balanced, risk-aware investment memo."
    ),
    instructions=[
        "Format your response in GitHub-flavored Markdown.",
        "Use clear section headers (Overview, Valuation, Momentum, Analyst View, Risks, Verdict).",
        "When you present tabular data, use Markdown tables.",
        "Cite the data source (Yahoo Finance) when applicable.",
        "If a metric is unavailable, state it explicitly instead of guessing.",
        "Conclude with a concise investor takeaway and a risk checklist."
    ],
)
log_event("agent_init_done", run_id=RUN_ID)

# Action
analyze_clicked = st.button("🔎 Analyze Stocks", type="primary", use_container_width=True)

if analyze_clicked:
    if not (stock1 and stock2):
        st.error("Please enter both stock symbols to continue.")
        log_event("missing_tickers", run_id=RUN_ID, stock1=stock1, stock2=stock2)
        st.stop()

    if not (is_valid_ticker(stock1) and is_valid_ticker(stock2)):
        st.error("Please provide valid ticker symbols (alphanumeric, ≤ 10 chars).")
        log_event("invalid_tickers", run_id=RUN_ID, stock1=stock1, stock2=stock2)
        st.stop()

    query = (
        f"Compare both stocks {stock1} and {stock2}. "
        "Create a detailed, investor-friendly memo with:\n"
        "- 60-second overview\n"
        "- Business summary & key segments\n"
        "- Price trends & simple momentum (1M/3M/6M/1Y) if available\n"
        "- Valuation snapshot (P/E, P/S, P/B) if available\n"
        "- Analyst recommendations & target price ranges\n"
        "- Fundamental highlights (revenue, income, margins) if available\n"
        "- Major risks specific to each company/industry\n"
        "- Your balanced verdict for different investor profiles (growth/dividend/defensive)\n"
        "Use Markdown tables where possible and cite Yahoo Finance for data."
    )

    log_event("analysis_start", run_id=RUN_ID, stock1=stock1, stock2=stock2)

    with st.spinner(f"Analyzing {stock1} vs {stock2} …"):
        t0 = time.time()
        try:
            response = assistant.run(query, stream=False)
            elapsed = round(time.time() - t0, 2)
            log_event("analysis_success", run_id=RUN_ID, elapsed_s=elapsed, chars=len(str(response.content)))
            st.success(f"Analysis complete in {elapsed}s.")
            st.markdown(response.content)
        except Exception as e:
            elapsed = round(time.time() - t0, 2)
            log_event("analysis_error", run_id=RUN_ID, elapsed_s=elapsed, error=str(e))
            st.error("Something went wrong while generating the analysis. Check logs for details.")
            st.exception(e)

# Footer diagnostics
with st.expander("🛠 Diagnostics (for troubleshooting)"):
    st.code(f"RUN_ID: {RUN_ID}", language="text")
    st.write("🔎 Logging to app console. If running locally, see your terminal output.")
    st.write("Toggles:", {"price": price, "analyst": analyst, "fundamentals": fundamentals, "show_tool_calls": show_tool_calls})
    st.write("API via:", "UI input" if ui_api_key else ("Environment (.env/OS)" if openai_api_key else "N/A"))
