import streamlit as st
import requests
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List
import json

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

def search_for_urls(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    print("[search_for_urls] Searching for URLs for:", company_description)
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json"
    }
    query = f"quora websites where people are looking for {company_description} services"
    payload = {
        "query": query,
        "limit": num_links,
        "lang": "en",
        "location": "United States",
        "timeout": 60000,
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"[search_for_urls] Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                results = data.get("data", [])
                urls = [result["url"] for result in results]
                print(f"[search_for_urls] URLs found: {urls}")
                return urls
        print("[search_for_urls] No URLs found or error in response.")
        return []
    except Exception as e:
        print(f"[search_for_urls] Exception: {e}")
        return []

def extract_user_info_from_urls(urls: List[str], firecrawl_api_key: str) -> List[dict]:
    print("[extract_user_info_from_urls] Extracting from URLs:", urls)
    user_info_list = []
    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
    try:
        for url in urls:
            response = firecrawl_app.extract(
                [url],
                schema=QuoraPageSchema.model_json_schema(),
                prompt=(
                    'Extract all user information including username, bio, post type (question/answer), timestamp, upvotes, and any links from Quora posts. Focus on identifying potential leads who are asking questions or providing answers related to the topic.'
                )
            )
            print(f"[extract_user_info_from_urls] URL: {url} - Response: {response}")
            # --- Use attributes, not dict .get() ---
            if response.success and response.status == 'completed':
                interactions = response.data.get('interactions', []) if response.data else []
                if interactions:
                    user_info_list.append({
                        "website_url": url,
                        "user_info": interactions
                    })
    except Exception as e:
        print(f"[extract_user_info_from_urls] Exception: {e}")
    print("[extract_user_info_from_urls] User info list length:", len(user_info_list))
    return user_info_list

def format_user_info_to_flattened_json(user_info_list: List[dict]) -> List[dict]:
    print("[format_user_info_to_flattened_json] Formatting user info.")
    flattened_data = []
    for info in user_info_list:
        website_url = info["website_url"]
        user_info = info["user_info"]
        for interaction in user_info:
            flattened_interaction = {
                "Website URL": website_url,
                "Username": interaction.get("username", ""),
                "Bio": interaction.get("bio", ""),
                "Post Type": interaction.get("post_type", ""),
                "Timestamp": interaction.get("timestamp", ""),
                "Upvotes": interaction.get("upvotes", 0),
                "Links": ", ".join(interaction.get("links", [])),
            }
            flattened_data.append(flattened_interaction)
    print(f"[format_user_info_to_flattened_json] Total flattened entries: {len(flattened_data)}")
    return flattened_data

def create_prompt_transformation_agent(openai_api_key: str) -> Agent:
    print("[create_prompt_transformation_agent] Creating prompt transformation agent.")
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
        instructions=(
            "You are an expert at transforming detailed user queries into concise company descriptions.\n"
            "Your task is to extract the core business/product focus in 3-4 words.\n\n"
            "Examples:\n"
            'Input: "Generate leads looking for AI-powered customer support chatbots for e-commerce stores."\n'
            'Output: "AI customer support chatbots for e commerce"\n\n'
            'Input: "Find people interested in voice cloning technology for creating audiobooks and podcasts"\n'
            'Output: "voice cloning technology"\n\n'
            'Input: "Looking for users who need automated video editing software with AI capabilities"\n'
            'Output: "AI video editing software"\n\n'
            'Input: "Need to find businesses interested in implementing machine learning solutions for fraud detection"\n'
            'Output: "ML fraud detection"\n\n'
            "Always focus on the core product/service and keep it concise but clear."
        ),
        markdown=True
    )

def main():
    st.set_page_config(page_title="QuoraLeadCraft AI", page_icon="🧩")
    st.title("🧩 QuoraLeadCraft AI")
    st.info("This Firecrawl-powered agent generates leads from Quora by searching for relevant posts and extracting user information.")

    with st.sidebar:
        st.header("API Keys")
        firecrawl_api_key = st.text_input("Firecrawl API Key", type="password")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        num_links = st.number_input("Number of links to search", min_value=1, max_value=10, value=3)
        if st.button("Reset"):
            st.session_state.clear()
            st.experimental_rerun()

    user_query = st.text_area(
        "Describe what kind of leads you're looking for:",
        placeholder="e.g., Looking for users who need automated video editing software with AI capabilities",
        help="Be specific about the product/service and target audience. The AI will convert this into a focused search query."
    )

    if st.button("Generate Leads"):
        if not all([firecrawl_api_key, openai_api_key, user_query]):
            st.error("Please fill in all the API keys and describe what leads you're looking for.")
            return

        with st.spinner("🔎 Transforming your query..."):
            transform_agent = create_prompt_transformation_agent(openai_api_key)
            company_description = transform_agent.run(
                f"Transform this query into a concise 3-4 word company description: {user_query}")
            st.write("🔍 Searching for:", company_description.content)

        with st.spinner("🔗 Searching for relevant URLs..."):
            urls = search_for_urls(company_description.content, firecrawl_api_key, num_links)

        if urls:
            st.subheader("🔗 Quora Links Used:")
            for url in urls:
                st.write(url)

            with st.spinner("👤 Extracting user info from URLs..."):
                user_info_list = extract_user_info_from_urls(urls, firecrawl_api_key)

            with st.spinner("🧾 Formatting user info..."):
                flattened_data = format_user_info_to_flattened_json(user_info_list)

            if not flattened_data:
                st.warning(
                    "⚠️ No user interactions were extracted from the Quora links found.\n\n"
                    "This can happen if the threads are empty, require login, or Firecrawl couldn't extract public answers.\n\n"
                    "👉 Try a broader topic, increase the number of links, or check the thread is public and has answers."
                )
                st.markdown("#### Quora URLs tried:")
                for url in urls:
                    st.markdown(f"- [{url}]({url})")
                return

            st.success("🎉 Leads extracted successfully! See the results below.")
            st.dataframe(flattened_data)

        else:
            st.warning("No relevant URLs found.")

if __name__ == "__main__":
    main()
