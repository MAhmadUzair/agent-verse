# 🔍 LaunchLens

AI-powered multi-agent MVP for competitor analysis, market sentiment, and launch KPIs.

---

## 🧠 Features

- **Multi-agent** architecture (Launch Analyst, Sentiment Analyst, Metrics Specialist)
- Coordinates insights from web + LLMs for actionable launch intelligence
- Interactive, clean **Streamlit** UI
- Fully modular—easy to add new agents or analysis types
- Runs locally, no cloud needed

---

## ⚡ Quickstart

### 1️⃣ Requirements

- Python **3.8+**
- OpenAI API key (get from [openai.com/api](https://platform.openai.com/))
- Firecrawl API key (get from [firecrawl.dev](https://firecrawl.dev/))

---

### 2️⃣ Installation

```bash
git clone <your-repo-url>
cd product-intelligence-agent
pip install -r requirements.txt
```

---

### 3️⃣ Setup Your Secrets

Create a file called `.env` in the project root:

```
OPENAI_API_KEY=sk-xxxxxxx
FIRECRAWL_API_KEY=fc-xxxxxxx
```

**Never share or commit your `.env` file!**

---

### 4️⃣ Run the App

```bash
streamlit run app.py
```
or use your preferred Streamlit deployment workflow.

---

## 🧑‍💻 How It Works

1. Enter your API keys in the sidebar or via `.env`.
2. Enter a company name to analyze.
3. Select an analysis tab:  
   - **Competitor Analysis:** See how a competitor is positioned, strengths, weaknesses, and actionable learnings.
   - **Market Sentiment:** Get a bullet-style snapshot of customer & public sentiment.
   - **Launch Metrics:** See quantified KPIs, adoption metrics, and performance benchmarks.
4. Review results and sources—all in markdown, ready to copy.

---

## 🔑 Environment Variables

Set these in your `.env` file for backend (never expose in public repos):

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxx
```

---

## 📦 Project Structure

```
product-intelligence-agent/
├── app.py             # Main Streamlit app (production-ready)
├── requirements.txt   # All dependencies
├── .env               # Your API keys (never commit!)
└── README.md          # This file
```

---

## 📝 Notes

- Requires both OpenAI and Firecrawl keys for full multi-agent operation.
- All analysis is evidence-driven and includes sources (when available).
- Modular design lets you add more agent roles or swap models easily.

---

## 📬 Questions or Improvements?

Open an [issue](https://github.com/your-repo/issues) or PR to contribute!

---
