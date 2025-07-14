import streamlit as st
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from datetime import datetime
from textwrap import dedent

# ------------------------- CONFIG --------------------------
st.set_page_config(
    page_title="LaunchLens – AI Launch Intelligence",
    page_icon=":mag_right:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Load ENV VARS (from .env) -----------------
print("[INFO] Loading environment variables...")
load_dotenv()

def get_secret_env(key, default=""):
    """Get secret value, prioritizing sidebar input, fallback to .env"""
    return st.session_state.get(key) or os.getenv(key, default)

# ------------------ SIDEBAR: API KEYS -------------------
st.sidebar.header("🔑 API Configuration")
openai_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=get_secret_env("OPENAI_API_KEY"),
    help="Required for AI agent functionality"
)
firecrawl_key = st.sidebar.text_input(
    "Firecrawl API Key",
    type="password",
    value=get_secret_env("FIRECRAWL_API_KEY"),
    help="Required for web search and crawling"
)
st.session_state["OPENAI_API_KEY"] = openai_key
st.session_state["FIRECRAWL_API_KEY"] = firecrawl_key

if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
if firecrawl_key:
    os.environ["FIRECRAWL_API_KEY"] = firecrawl_key

# --------------- AGENT/TEAM CREATION -----------------
print("[INFO] Initializing agent team...")
if openai_key and firecrawl_key:
    launch_analyst = Agent(
        name="Product Launch Analyst",
        description=dedent("""
            You are a senior Go-To-Market strategist who evaluates competitor product launches with a critical, evidence-driven lens.
            Your objective is to uncover:
            • How the product is positioned in the market
            • Which launch tactics drove success (strengths)
            • Where execution fell short (weaknesses)
            • Actionable learnings competitors can leverage
            Always cite observable signals (messaging, pricing actions, channel mix, timing, engagement metrics). Maintain a crisp, executive tone and focus on strategic value.
            IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )
    sentiment_analyst = Agent(
        name="Market Sentiment Specialist",
        description=dedent("""
            You are a market research expert specializing in sentiment analysis and consumer perception tracking.
            Your expertise includes:
            • Analyzing social media sentiment and customer feedback
            • Identifying positive and negative sentiment drivers
            • Tracking brand perception trends across platforms
            • Monitoring customer satisfaction and review patterns
            • Providing actionable insights on market reception
            Focus on extracting sentiment signals from social platforms, review sites, forums, and customer feedback channels.
            IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )
    metrics_analyst = Agent(
        name="Launch Metrics Specialist",
        description=dedent("""
            You are a product launch performance analyst who specializes in tracking and analyzing launch KPIs.
            Your focus areas include:
            • User adoption and engagement metrics
            • Revenue and business performance indicators
            • Market penetration and growth rates
            • Press coverage and media attention analysis
            • Social media traction and viral coefficient tracking
            • Competitive market share analysis
            Always provide quantitative insights with context and benchmark against industry standards when possible.
            IMPORTANT: Conclude your report with a 'Sources:' section, listing all URLs of websites you crawled or searched for this analysis.
        """),
        model=OpenAIChat(id="gpt-4o"),
        tools=[FirecrawlTools(search=True, crawl=True, poll_interval=10)],
        show_tool_calls=True,
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=2,
    )
    product_intel_team = Team(
        name="Product Intelligence Team",
        mode="coordinate",
        model=OpenAIChat(id="gpt-4o"),
        members=[launch_analyst, sentiment_analyst, metrics_analyst],
        instructions=[
            "Coordinate the analysis based on the user's request type:",
            "1. For competitor analysis: Use the Product Launch Analyst to evaluate positioning, strengths, weaknesses, and strategic insights",
            "2. For market sentiment: Use the Market Sentiment Specialist to analyze social media sentiment, customer feedback, and brand perception",
            "3. For launch metrics: Use the Launch Metrics Specialist to track KPIs, adoption rates, press coverage, and performance indicators",
            "Always provide evidence-based insights with specific examples and data points",
            "Structure responses with clear sections and actionable recommendations",
            "Include sources section with all URLs crawled or searched"
        ],
        show_tool_calls=True,
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
    )
    print("[INFO] Product Intelligence Team initialized.")
else:
    product_intel_team = None
    st.warning("⚠️ Please enter both API keys in the sidebar to use the application.")
    print("[WARN] API keys missing; not initializing team.")

# -------------------- HELPERS ----------------------
def display_agent_response(resp):
    """Display response content nicely in Streamlit."""
    if hasattr(resp, "content") and resp.content:
        st.markdown(resp.content)
    elif hasattr(resp, "messages"):
        for m in resp.messages:
            if m.role == "assistant" and m.content:
                st.markdown(m.content)
    else:
        st.markdown(str(resp))

def expand_competitor_report(bullets, competitor):
    """Craft a competitor-focused report in markdown."""
    if not product_intel_team:
        st.error("API keys missing.")
        return ""
    prompt = (
        f"Transform the insight bullets below into a professional launch review for product managers analysing {competitor}.\n\n"
        f"Produce well-structured **Markdown** with a mix of tables, call-outs and concise bullet points — avoid long paragraphs.\n\n"
        f"=== FORMAT SPECIFICATION ===\n"
        f"# {competitor} – Launch Review\n\n"
        f"## 1. Market & Product Positioning\n"
        f"• Bullet point summary of how the product is positioned (max 6 bullets).\n\n"
        f"## 2. Launch Strengths\n"
        f"| Strength | Evidence / Rationale |\n|---|---|\n| … | … | (add 4-6 rows)\n\n"
        f"## 3. Launch Weaknesses\n"
        f"| Weakness | Evidence / Rationale |\n|---|---|\n| … | … | (add 4-6 rows)\n\n"
        f"## 4. Strategic Takeaways for Competitors\n"
        f"1. … (max 5 numbered recommendations)\n\n"
        f"=== SOURCE BULLETS ===\n{bullets}\n\n"
        f"Guidelines:\n"
        f"• Populate the tables with specific points derived from the bullets.\n"
        f"• Only include rows that contain meaningful data; omit any blank entries."
    )
    resp = product_intel_team.run(prompt)
    print(f"[INFO] Generated competitor report for {competitor}")
    return resp.content if hasattr(resp, "content") else str(resp)

def expand_sentiment_report(bullets, product):
    """Craft a market sentiment report."""
    if not product_intel_team:
        st.error("API keys missing.")
        return ""
    prompt = (
        f"Use the tagged bullets below to create a concise market-sentiment brief for **{product}**.\n\n"
        f"### Positive Sentiment\n"
        f"• List each positive point as a separate bullet (max 6).\n\n"
        f"### Negative Sentiment\n"
        f"• List each negative point as a separate bullet (max 6).\n\n"
        f"### Overall Summary\n"
        f"Provide a short paragraph (≤120 words) summarising the overall sentiment balance and key drivers.\n\n"
        f"Tagged Bullets:\n{bullets}"
    )
    resp = product_intel_team.run(prompt)
    print(f"[INFO] Generated sentiment report for {product}")
    return resp.content if hasattr(resp, "content") else str(resp)

def expand_metrics_report(bullets, launch):
    """Craft a launch performance metrics report."""
    if not product_intel_team:
        st.error("API keys missing.")
        return ""
    prompt = (
        f"Convert the KPI bullets below into a launch-performance snapshot for **{launch}** suitable for an executive dashboard.\n\n"
        f"## Key Performance Indicators\n"
        f"| Metric | Value / Detail | Source |\n"
        f"|---|---|---|\n"
        f"| … | … | … |  (include one row per KPI)\n\n"
        f"## Qualitative Signals\n"
        f"• Bullet list of notable qualitative insights (max 5).\n\n"
        f"## Summary & Implications\n"
        f"Brief paragraph (≤120 words) highlighting what the metrics imply about launch success and next steps.\n\n"
        f"KPI Bullets:\n{bullets}"
    )
    resp = product_intel_team.run(prompt)
    print(f"[INFO] Generated metrics report for {launch}")
    return resp.content if hasattr(resp, "content") else str(resp)

# ---------------------- UI LOGIC ---------------------
st.title("🔍 LaunchLens – Product & Market Intelligence MVP")
st.markdown("*AI-powered launch, competitor, and market sentiment insights*")
st.divider()

st.subheader("🏢 Company Analysis")
company_name = st.text_input(
    label="Company Name",
    placeholder="Enter company name (e.g., OpenAI, Tesla, Spotify)",
    help="This company will be analyzed by the coordinated team of specialized agents",
    label_visibility="collapsed"
)
if company_name:
    st.success(f"✓ Ready to analyze **{company_name}**")
st.divider()

tabs = st.tabs([
    "🔍 Competitor Analysis",
    "💬 Market Sentiment",
    "📈 Launch Metrics"
])

if "competitor_response" not in st.session_state:
    st.session_state.competitor_response = None
if "sentiment_response" not in st.session_state:
    st.session_state.sentiment_response = None
if "metrics_response" not in st.session_state:
    st.session_state.metrics_response = None

# ------- Tab 1: Competitor Analysis -------
with tabs[0]:
    st.markdown("### 🔍 Competitor Launch Analysis")
    if company_name:
        analyze_btn = st.button("🚀 Analyze Competitor Strategy", key="competitor_btn", use_container_width=True)
        if analyze_btn:
            if not product_intel_team:
                st.error("Please enter both API keys.")
            else:
                with st.spinner("Analyzing competitor..."):
                    try:
                        print(f"[INFO] Running competitor analysis for {company_name}")
                        bullets = product_intel_team.run(
                            f"Generate up to 16 evidence-based insight bullets about {company_name}'s most recent product launches.\n"
                            f"Format requirements:\n"
                            f"• Start every bullet with exactly one tag: Positioning | Strength | Weakness | Learning\n"
                            f"• Follow the tag with a concise statement (max 30 words) referencing concrete observations: messaging, differentiation, pricing, channel selection, timing, engagement metrics, or customer feedback."
                        )
                        long_text = expand_competitor_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.competitor_response = long_text
                        st.success("✅ Competitor analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    if st.session_state.competitor_response:
        st.divider()
        st.markdown("### 📊 Analysis Results")
        st.markdown(st.session_state.competitor_response)

# ------- Tab 2: Market Sentiment -------
with tabs[1]:
    st.markdown("### 💬 Market Sentiment Analysis")
    if company_name:
        sentiment_btn = st.button("📊 Analyze Market Sentiment", key="sentiment_btn", use_container_width=True)
        if sentiment_btn:
            if not product_intel_team:
                st.error("Please enter both API keys.")
            else:
                with st.spinner("Analyzing sentiment..."):
                    try:
                        print(f"[INFO] Running sentiment analysis for {company_name}")
                        bullets = product_intel_team.run(
                            f"Summarize market sentiment for {company_name} in <=10 bullets. "
                            f"Cover top positive & negative themes with source mentions (G2, Reddit, Twitter, customer reviews)."
                        )
                        long_text = expand_sentiment_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.sentiment_response = long_text
                        st.success("✅ Sentiment analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    if st.session_state.sentiment_response:
        st.divider()
        st.markdown("### 📈 Analysis Results")
        st.markdown(st.session_state.sentiment_response)

# ------- Tab 3: Launch Metrics -------
with tabs[2]:
    st.markdown("### 📈 Launch Performance Metrics")
    if company_name:
        metrics_btn = st.button("📊 Analyze Launch Metrics", key="metrics_btn", use_container_width=True)
        if metrics_btn:
            if not product_intel_team:
                st.error("Please enter both API keys.")
            else:
                with st.spinner("Analyzing launch metrics..."):
                    try:
                        print(f"[INFO] Running metrics analysis for {company_name}")
                        bullets = product_intel_team.run(
                            f"List (max 10 bullets) the most important publicly available KPIs & qualitative signals for {company_name}'s recent product launches. "
                            f"Include engagement stats, press coverage, adoption metrics, and market traction data if available."
                        )
                        long_text = expand_metrics_report(
                            bullets.content if hasattr(bullets, "content") else str(bullets),
                            company_name
                        )
                        st.session_state.metrics_response = long_text
                        st.success("✅ Metrics analysis ready")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    if st.session_state.metrics_response:
        st.divider()
        st.markdown("### 📊 Analysis Results")
        st.markdown(st.session_state.metrics_response)

# ---------------- SIDEBAR SYSTEM STATUS ----------------
with st.sidebar:
    st.markdown("### 🤖 System Status")
    if openai_key and firecrawl_key:
        st.success("✅ Product Intelligence Team ready")
    else:
        st.error("❌ API keys required")
    st.divider()
    st.markdown("### 🎯 Coordinated Team")
    for icon, name, desc in [
        ("🔍", "Product Launch Analyst", "Strategic GTM expert"),
        ("💬", "Market Sentiment Specialist", "Consumer perception expert"),
        ("📈", "Launch Metrics Specialist", "Performance analytics expert")
    ]:
        st.markdown(f"**{icon} {name}**")
        st.caption(desc)
    st.divider()
    if company_name:
        st.markdown("### 📊 Analysis Status")
        for icon, name, status in [
            ("🔍", "Competitor Analysis", st.session_state.competitor_response),
            ("💬", "Sentiment Analysis", st.session_state.sentiment_response),
            ("📈", "Metrics Analysis", st.session_state.metrics_response)
        ]:
            if status:
                st.success(f"{icon} {name} ✓")
            else:
                st.info(f"{icon} {name} ⏳")
        st.divider()
    st.markdown("### ⚡ Quick Actions")
    st.markdown("**J** - Competitor analysis  \n**K** - Market sentiment  \n**L** - Launch metrics")

print("[INFO] App fully loaded and ready.")
