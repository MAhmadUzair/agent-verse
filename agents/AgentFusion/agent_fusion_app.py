import streamlit as st
import asyncio
import os
from together import AsyncTogether, Together

st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🌟 Mixture-of-Agents LLM App 🌟</h1>",
    unsafe_allow_html=True,
)

st.markdown("### 🔑 API Key")
together_api_key = st.text_input("Enter your Together API Key:", type="password")

if together_api_key:
    os.environ["TOGETHER_API_KEY"] = together_api_key
    client = Together(api_key=together_api_key)
    async_client = AsyncTogether(api_key=together_api_key)

    reference_models = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "mistralai/Mistral-Small-24B-Instruct-2501",
        "Qwen/Qwen2.5-7B-Instruct-Turbo",
    ]

    aggregator_model = "mistralai/Mistral-7B-Instruct-v0.3"

    aggregator_system_prompt = """You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability. Responses from models:"""

    st.markdown("### ❓ Ask a Question")
    user_prompt = st.text_input("Enter your question:")

    async def run_llm(model):
        """Run a single LLM call with debug info."""
        st.info(f"⏳ Sending prompt to {model}...")
        response = await async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
            max_tokens=512,
        )
        debug_msg = f"✅ Received response from {model}: {response.choices[0].message.content[:100]}..."
        st.code(debug_msg, language="markdown")
        return model, response.choices[0].message.content

    async def main():
        st.success("🚀 Querying models...")
        results = await asyncio.gather(*[run_llm(model) for model in reference_models])

        st.markdown("## 🧠 Individual Model Responses")
        for model, response in results:
            with st.expander(f"📨 Response from `{model}`"):
                st.write(response)

        st.markdown("## 🪄 Aggregated Response")
        st.info("Synthesizing responses with aggregator model...")

        finalStream = client.chat.completions.create(
            model=aggregator_model,
            messages=[
                {"role": "system", "content": aggregator_system_prompt},
                {"role": "user", "content": ",".join(response for _, response in results)},
            ],
            stream=True,
        )

        response_container = st.empty()
        full_response = ""
        for chunk in finalStream:
            content = chunk.choices[0].delta.content or ""
            full_response += content
            response_container.markdown(full_response + "▌")
        response_container.markdown(full_response)
        st.code("✅ Aggregation Complete", language="markdown")


    st.markdown("### 🚦 Actions")
    if st.button("✨ Get Answer"):
        if user_prompt:
            with st.spinner("Processing... Please wait..."):
                asyncio.run(main())
        else:
            st.warning("⚠️ Please enter a question before proceeding.")

else:
    st.warning("⚠️ Please enter your Together API key to use the app.")

st.sidebar.title("📖 About This App")
st.sidebar.info(
    "This app demonstrates a **Mixture-of-Agents** approach using multiple Language Models (LLMs) to answer a single question."
)

st.sidebar.subheader("⚙️ How it works")
st.sidebar.markdown(
    """
1. Your question is sent to multiple LLMs:
   - Mistralai/Mistral-7B-Instruct-v0.3 
   - Mistralai/Mistral-Small-24B-Instruct-2501  
   - Qwen/Qwen2.5-7B-Instruct-Turbo  

2. Each model returns its own answer.

3. An aggregator model (Mistralai/Mistral-7B-Instruct-v0.3) refines and merges these into a final response.

4. You receive a detailed and synthesized reply.
"""
)

st.sidebar.success("This technique enables more comprehensive, balanced answers via multiple models.")
