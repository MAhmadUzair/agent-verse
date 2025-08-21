# 📈 AlphaTwin — AI Stock Comparator

Compare two stocks side-by-side and get a concise, investor-ready memo with **AlphaTwin**.  
Under the hood, a vetted **agentic workflow** (via `agno`) pulls **Yahoo Finance** data (price, analysts, fundamentals) and uses an **OpenAI** model to produce a structured, risk-aware write-up.

## 🚀 What You Get
- One-click comparison of **two tickers** (e.g., `AAPL` vs `MSFT`).
- Pulls **stock price**, **analyst recommendations**, and **fundamentals** via `YFinanceTools`.
- Clean, **Markdown-formatted** investment memo with tables, risks, and verdict.
- **Advanced tracking** with timestamps, run IDs, and tool-call visibility.

## 🔧 Setup
1) `pip install -r requirements.txt`  
2) Configure API via sidebar or `.env` (`OPENAI_API_KEY=...`)  
3) `streamlit run app_alpha_twin.py`
