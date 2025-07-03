import os
from uuid import uuid4
import streamlit as st
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.eleven_labs import ElevenLabsTools
from agno.tools.firecrawl import FirecrawlTools
from agno.utils.audio import write_audio_to_file
from agno.utils.log import logger

# --- Streamlit Page Setup ---
st.set_page_config(page_title="📰➡️🎙️ Blog to Podcast Agent", page_icon="🎙️")
st.title("📰➡️🎙️ Blog to Podcast Agent")
st.markdown("Convert any blog post into an engaging podcast episode! 🎧")

# --- Sidebar: API Key Inputs ---
with st.sidebar:
    st.header("🔑 API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    elevenlabs_api_key = st.text_input("ElevenLabs API Key", type="password")
    firecrawl_api_key = st.text_input("Firecrawl API Key", type="password")

# --- Check API Keys ---
keys_provided = all([openai_api_key, elevenlabs_api_key, firecrawl_api_key])

if not keys_provided:
    st.warning("⚠️ Please enter all required API keys in the sidebar to proceed.")

# --- Blog URL Input ---
url = st.text_input("🔗 Enter Blog URL:")

# --- Generate Podcast Button ---
generate_button = st.button("🎙️ Generate Podcast", disabled=not keys_provided)

# --- Podcast Generation Logic ---
def generate_podcast(url: str):
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["ELEVEN_LABS_API_KEY"] = elevenlabs_api_key
    os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key

    agent = Agent(
        name="Blog to Podcast Agent",
        agent_id="blog_to_podcast_agent",
        model=OpenAIChat(id="gpt-4o"),
        tools=[
            ElevenLabsTools(
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                target_directory="audio_generations",
            ),
            FirecrawlTools(),
        ],

        description="An AI agent that scrapes, summarizes, and converts blogs into podcasts.",
        instructions=[
            "1. Use FirecrawlTools to scrape the blog content.",
            "2. Summarize the content within 2000 characters in an engaging and conversational tone.",
            "3. Immediately use ElevenLabsTools to convert the summary to audio, without asking for user confirmation or permission. Do not wait for any further prompt; always perform this step after summarizing.",
        ],

        markdown=True,
        debug_mode=True,
    )

    return agent.run(f"Convert the blog content to a podcast: {url}")

# --- On Button Click ---
if generate_button:
    if not url.strip():
        st.warning("⚠️ Please enter a valid blog URL.")
    else:
        with st.spinner("🚀 Processing: Scraping, Summarizing, and Generating Podcast..."):
            try:
                podcast: RunResponse = generate_podcast(url)
                save_dir = "audio_generations"
                os.makedirs(save_dir, exist_ok=True)

                if podcast.audio and len(podcast.audio) > 0:
                    filename = f"{save_dir}/podcast_{uuid4()}.wav"
                    write_audio_to_file(
                        audio=podcast.audio[0].base64_audio,
                        filename=filename,
                    )

                    st.success("✅ Podcast generated successfully!")
                    audio_bytes = open(filename, "rb").read()
                    st.audio(audio_bytes, format="audio/wav")

                    st.download_button(
                        label="⬇️ Download Podcast",
                        data=audio_bytes,
                        file_name="generated_podcast.wav",
                        mime="audio/wav"
                    )
                else:
                    st.error("❌ No audio was generated. Please try again.")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")
                logger.error(f"Streamlit app error: {e}")
