import os
import time
from typing import Dict, Tuple

import streamlit as st
from dotenv import load_dotenv

# Agentic framework
from agno.agent import Agent
from agno.models.google import Gemini

# -----------------------------
# Utility: verbose tracking
# -----------------------------
APP_TAG = "FitFusionPro"


def tlog(msg: str) -> None:
    """Timestamped print logging for advanced tracking in server logs."""
    print(f"[{APP_TAG}][{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# -----------------------------
# App Config + Theming
# -----------------------------
st.set_page_config(
    page_title="FitFusion Pro — Agentic Health & Fitness Planner",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inline styles
st.markdown(
    """
    <style>
      .main { padding: 1.2rem; }
      .stButton>button {
          width: 100%;
          border-radius: 10px;
          height: 3em;
          font-weight: 600;
      }
      .success-box, .warning-box {
          padding: 1rem;
          border-radius: 0.75rem;
          border: 1px solid rgba(0,0,0,0.1);
      }
      .success-box { background-color: #f0fff4; border-color: #9ae6b4; }
      .warning-box { background-color: #fffaf0; border-color: #fbd38d; }
      div[data-testid="stExpander"] div[role="button"] p {
          font-size: 1.1rem;
          font-weight: 700;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helpers
# -----------------------------
def init_session_state() -> None:
    if "dietary_plan" not in st.session_state:
        st.session_state.dietary_plan = {}
    if "fitness_plan" not in st.session_state:
        st.session_state.fitness_plan = {}
    if "qa_pairs" not in st.session_state:
        st.session_state.qa_pairs = []
    if "plans_generated" not in st.session_state:
        st.session_state.plans_generated = False
    tlog("Session state initialized.")


def load_api_key_from_env() -> str:
    load_dotenv()  # loads .env if present
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        tlog("GEMINI_API_KEY loaded from environment.")
    else:
        tlog("GEMINI_API_KEY not found in environment.")
    return key


def build_user_profile(
    age: int,
    height: float,
    weight: float,
    sex: str,
    activity_level: str,
    dietary_preferences: str,
    fitness_goals: str,
) -> str:
    profile = f"""
    Age: {age}
    Weight: {weight} kg
    Height: {height} cm
    Sex: {sex}
    Activity Level: {activity_level}
    Dietary Preferences: {dietary_preferences}
    Fitness Goals: {fitness_goals}
    """
    tlog("User profile constructed.")
    return profile.strip()


def safe_agent_init(model_id: str, api_key: str) -> Gemini:
    tlog(f"Initializing Gemini model: {model_id}")
    return Gemini(id=model_id, api_key=api_key)


def run_agent(agent: Agent, prompt: str) -> str:
    """Runs an agent safely and returns text content."""
    tlog(f"Agent '{agent.name}' run started.")
    try:
        response = agent.run(prompt)
        # agno responses typically have .content
        content = getattr(response, "content", "")
        if not content:
            tlog(f"Agent '{agent.name}' returned empty content.")
            return "No content was produced. Please try again."
        tlog(f"Agent '{agent.name}' run completed successfully.")
        return content
    except Exception as e:
        tlog(f"Agent '{agent.name}' error: {e}")
        return f"An error occurred while generating a response: {e}"


def display_dietary_plan(plan_content: Dict) -> None:
    with st.expander("📋 Your Personalized Dietary Plan", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Why this plan works")
            st.info(plan_content.get("why_this_plan_works", "Information not available"))
            st.markdown("### 🍽️ Meal Plan")
            st.write(plan_content.get("meal_plan", "Plan not available"))

        with col2:
            st.markdown("### ⚠️ Important Considerations")
            considerations = plan_content.get("important_considerations", "").split("\n")
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)


def display_fitness_plan(plan_content: Dict) -> None:
    with st.expander("💪 Your Personalized Fitness Plan", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🎯 Goals")
            st.success(plan_content.get("goals", "Goals not specified"))
            st.markdown("### 🏋️‍♂️ Exercise Routine")
            st.write(plan_content.get("routine", "Routine not available"))

        with col2:
            st.markdown("### 💡 Pro Tips")
            tips = plan_content.get("tips", "").split("\n")
            for tip in tips:
                if tip.strip():
                    st.info(tip)


def validate_inputs(age: int, height: float, weight: float) -> Tuple[bool, str]:
    if not (10 <= age <= 100):
        return False, "Age must be between 10 and 100."
    if not (100.0 <= height <= 250.0):
        return False, "Height must be between 100 cm and 250 cm."
    if not (20.0 <= weight <= 300.0):
        return False, "Weight must be between 20 kg and 300 kg."
    return True, ""


# -----------------------------
# Main App
# -----------------------------
def main():
    tlog("App started.")
    init_session_state()

    st.title("🏋️‍♀️ FitFusion Pro — Agentic Health & Fitness Planner")
    st.markdown(
        """
        <div style='background: linear-gradient(90deg, #0b5, #08f); color: white; padding: 1rem; border-radius: 0.75rem; margin-bottom: 1.25rem;'>
          Get personalized dietary and fitness plans tailored to your goals and preferences.
          Powered by agentic Gemini models for clarity, coherence, and actionability.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------- Sidebar: API Config -------------
    with st.sidebar:
        st.header("🔑 API Configuration")
        env_key = load_api_key_from_env()
        st.caption("You can paste your key here or rely on `GEMINI_API_KEY` from `.env`. Sidebar value overrides environment.")
        gemini_api_key = st.text_input(
            "Gemini API Key (optional if provided via .env)",
            type="password",
            placeholder="Paste your Gemini API Key",
            help="Get your key from https://aistudio.google.com/apikey",
            value="",
        )
        effective_api_key = gemini_api_key or env_key

        if not effective_api_key:
            st.warning("⚠️ Provide a Gemini API Key via sidebar or .env (GEMINI_API_KEY) to proceed.")
            tlog("No API key provided. Halting UI.")
            return
        else:
            st.success("API key ready.")
            tlog("API key available for model initialization.")

        model_id = st.text_input(
            "Gemini model ID",
            value="gemini-2.5-flash-preview-05-20",
            help="Override if unavailable in your account/region (e.g., gemini-1.5-flash).",
        )

    # ------------- Initialize Model -------------
    try:
        gemini_model = safe_agent_init(model_id, effective_api_key)
        tlog("Gemini model initialized.")
    except Exception as e:
        st.error(f"❌ Error initializing Gemini model: {e}")
        tlog(f"Model initialization error: {e}")
        return

    # ------------- Profile Inputs -------------
    st.header("👤 Your Profile")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, step=1, help="Enter your age")
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, step=0.1)
        activity_level = st.selectbox(
            "Activity Level",
            options=[
                "Sedentary",
                "Lightly Active",
                "Moderately Active",
                "Very Active",
                "Extremely Active",
            ],
            help="Choose your typical activity level",
        )
        dietary_preferences = st.selectbox(
            "Dietary Preferences",
            options=["No Preference", "Vegetarian", "Keto", "Gluten Free", "Low Carb", "Dairy Free"],
            help="Select your dietary preference",
        )

    with col2:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1)
        sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
        fitness_goals = st.selectbox(
            "Fitness Goals",
            options=["Lose Weight", "Gain Muscle", "Endurance", "Stay Fit", "Strength Training"],
            help="What do you want to achieve?",
        )

    # ------------- Generate Plan Button -------------
    if st.button("🎯 Generate My Personalized Plan", use_container_width=True):
        tlog("Generate button clicked.")
        valid, err = validate_inputs(age, height, weight)
        if not valid:
            st.error(f"Input validation failed: {err}")
            tlog(f"Validation error: {err}")
            return

        with st.spinner("Creating your perfect health and fitness routine..."):
            try:
                # Dietary Agent
                dietary_agent = Agent(
                    name="Dietary Expert",
                    role="Provides personalized dietary recommendations",
                    model=gemini_model,
                    instructions=[
                        "Consider the user's input, including dietary restrictions and preferences.",
                        "Suggest a detailed meal plan for a full day: breakfast, lunch, dinner, and snacks.",
                        "Provide a brief explanation of why the plan is aligned with the user's goals.",
                        "Be clear, coherent, and practical. Include approximate portion sizes.",
                    ],
                )
                tlog("Dietary agent constructed.")

                # Fitness Agent
                fitness_agent = Agent(
                    name="Fitness Expert",
                    role="Provides personalized fitness recommendations",
                    model=gemini_model,
                    instructions=[
                        "Provide exercises tailored to the user's goals and experience level.",
                        "Include warm-up, main workout (with sets/reps or time), and cool-down.",
                        "Explain the benefits or focus of each block briefly.",
                        "Ensure the plan is actionable and safe; include rest guidance.",
                    ],
                )
                tlog("Fitness agent constructed.")

                # Build user profile and prompts
                user_profile = build_user_profile(
                    age=age,
                    height=height,
                    weight=weight,
                    sex=sex,
                    activity_level=activity_level,
                    dietary_preferences=dietary_preferences,
                    fitness_goals=fitness_goals,
                )

                # Run agents
                dietary_plan_text = run_agent(dietary_agent, user_profile)
                fitness_plan_text = run_agent(fitness_agent, user_profile)

                dietary_plan = {
                    "why_this_plan_works": "High protein, sufficient fiber, smart carbs, and balanced calories tailored to your goal.",
                    "meal_plan": dietary_plan_text,
                    "important_considerations": """
- Hydration: Drink water regularly throughout the day.
- Electrolytes: Maintain sodium, potassium, and magnesium levels.
- Fiber: Include vegetables, fruits, and whole grains as appropriate.
- Biofeedback: Adjust portion sizes and training load based on energy and recovery.
                    """.strip(),
                }

                fitness_plan = {
                    "goals": "Improve body composition, build strength, and enhance cardiovascular fitness.",
                    "routine": fitness_plan_text,
                    "tips": """
- Track progress (volume, weights, RPE, or time).
- Prioritize form over load to reduce injury risk.
- Recover well: sleep 7–9h, schedule rest days, and fuel appropriately.
- Consistency beats intensity. Progressively overload.
                    """.strip(),
                }

                st.session_state.dietary_plan = dietary_plan
                st.session_state.fitness_plan = fitness_plan
                st.session_state.plans_generated = True
                st.session_state.qa_pairs = []
                tlog("Plans stored in session state.")

                display_dietary_plan(dietary_plan)
                display_fitness_plan(fitness_plan)
                tlog("Plans rendered in UI.")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                tlog(f"Plan generation error: {e}")

    # ------------- Q&A -------------
    if st.session_state.plans_generated:
        st.header("❓ Questions about your plan?")
        question_input = st.text_input("Ask anything—nutrition, substitutes, scheduling, progression, etc.")

        if st.button("💬 Get Answer", use_container_width=True):
            tlog("Q&A button clicked.")
            if question_input.strip():
                with st.spinner("Thinking..."):
                    dietary_plan = st.session_state.dietary_plan
                    fitness_plan = st.session_state.fitness_plan

                    # Ground the Q&A in current plan context
                    context = (
                        f"Dietary Plan: {dietary_plan.get('meal_plan', '')}\n\n"
                        f"Fitness Plan: {fitness_plan.get('routine', '')}"
                    )
                    full_prompt = (
                        "You are a helpful, precise assistant. Use the plan context below to answer the user question.\n\n"
                        f"{context}\n\n"
                        f"User Question: {question_input}"
                    )
                    try:
                        qa_agent = Agent(
                            name="Q&A Assistant",
                            role="Answers user questions using the previously generated plans as context.",
                            model=gemini_model,
                            show_tool_calls=True,
                            markdown=True,
                            instructions=[
                                "Ground answers in the provided plan context.",
                                "Be concise and practical. Offer alternatives where helpful.",
                            ],
                        )
                        tlog("Q&A agent constructed.")
                        answer = run_agent(qa_agent, full_prompt)

                        st.session_state.qa_pairs.append((question_input, answer))
                        tlog("Q&A pair appended to session history.")
                    except Exception as e:
                        st.error(f"❌ An error occurred while getting the answer: {e}")
                        tlog(f"Q&A error: {e}")
            else:
                st.warning("Please enter a question first.")
                tlog("Empty Q&A question submitted; warning shown.")

        # Render history
        if st.session_state.qa_pairs:
            st.header("💬 Q&A History")
            for idx, (q, a) in enumerate(st.session_state.qa_pairs, start=1):
                st.markdown(f"**Q{idx}:** {q}")
                st.markdown(f"**A{idx}:** {a}")

    tlog("App cycle completed.")


if __name__ == "__main__":
    main()
