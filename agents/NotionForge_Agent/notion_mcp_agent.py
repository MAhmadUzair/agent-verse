import argparse
import asyncio
import json
import os
import re
import sys
import uuid
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.memory.v2 import Memory
from mcp import StdioServerParameters

load_dotenv()

PAGE_ID_REGEX = re.compile(r"[0-9a-fA-F]{32}|[0-9a-fA-F-]{36}")

def is_probable_notion_page_id(candidate: str) -> bool:
    if not candidate:
        return False
    candidate = candidate.strip()
    return bool(PAGE_ID_REGEX.search(candidate))

async def run_agent(
    page_id: str,
    notion_token: str,
    openai_api_key: str = None,
    mcp_command: str = "npx",
    mcp_args: list = None,
):
    print("Starting run_agent")

    if not notion_token:
        raise ValueError("NOTION_API_KEY is required.")

    if not is_probable_notion_page_id(page_id):
        print("Warning: The provided page_id does not look like a standard Notion page id.")
    else:
        print("Page ID validation passed")

    openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY not set.")

    if mcp_args is None:
        mcp_args = ["-y", "@notionhq/notion-mcp-server"]

    server_params = StdioServerParameters(
        command=mcp_command,
        args=mcp_args,
        env={
            "OPENAPI_MCP_HEADERS": json.dumps(
                {"Authorization": f"Bearer {notion_token}", "Notion-Version": "2022-06-28"}
            )
        },
    )

    print(f"Server params prepared: {json.dumps({'command': mcp_command, 'args': mcp_args}, indent=2)[:400]}")

    try:
        async with MCPTools(server_params=server_params) as mcp_tools:
            print("Connected to Notion MCP server successfully")

            instructions = dedent(
                f"""
                You are an expert Notion assistant that helps users interact with their Notion pages.

                IMPORTANT INSTRUCTIONS:
                1. You have direct access to Notion documents through MCP tools - make full use of them.
                2. ALWAYS use the page ID: {page_id} for all operations unless the user explicitly provides another ID.
                3. When asked to update, read, or search pages, ALWAYS use the appropriate MCP tool calls.
                4. Be proactive in suggesting actions users can take with their Notion documents.
                5. When making changes, explain what you did and confirm the changes were made.
                6. If a tool call fails, explain the issue and suggest alternatives.

                Example tasks you can help with:
                - Reading page content
                - Searching for specific information
                - Adding new content or updating existing content
                - Creating lists, tables, and other Notion blocks
                - Explaining page structure
                - Adding comments to specific blocks

                The user's current page ID is: {page_id}
                """
            )

            print("Agent instructions prepared (truncated to 300 chars):\n" + instructions[:300])

            try:
                agent = Agent(
                    name="NotionDocsAgent",
                    model=OpenAIChat(id="gpt-4o", api_key=openai_api_key) if openai_api_key else None,
                    tools=[mcp_tools],
                    description="Agent to query and modify Notion docs via MCP",
                    instructions=instructions,
                    markdown=True,
                    show_tool_calls=True,
                    retries=3,
                    memory=Memory(),
                    add_history_to_messages=True,
                    num_history_runs=5,
                )

                print("Starting interactive session...")
                await agent.acli_app(
                    user_id=f"user_{uuid.uuid4().hex[:8]}",
                    session_id=f"session_{uuid.uuid4().hex[:8]}",
                    user="You",
                    emoji="🤖",
                    stream=True,
                    markdown=True,
                    exit_on=["exit", "quit", "bye", "goodbye"]
                )
                print("Interactive session ended.")
            except Exception as ex:
                print(f"Failed while creating or running agent: {ex}")
                raise

    except Exception as exc:
        print(f"Failed to start or communicate with MCP server: {exc}")
        raise

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="notion_mcp_agent", description="Run a terminal agent that interacts with Notion via MCP")
    p.add_argument("page_id", nargs="?", help="Notion page ID to target")
    p.add_argument("--notion-token", dest="notion_token", help="Notion API key")
    p.add_argument("--openai-key", dest="openai_api_key", help="OpenAI API key")
    p.add_argument("--mcp-cmd", dest="mcp_cmd", default="npx", help="Command to invoke the MCP server")
    p.add_argument("--mcp-args", dest="mcp_args", nargs="*", help="Additional args to pass to MCP command")
    p.add_argument("--non-interactive", action="store_true", help="Run a non-interactive dry-run")
    return p

async def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    notion_token = args.notion_token or os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    openai_api_key = args.openai_api_key or os.getenv("OPENAI_API_KEY")

    page_id = args.page_id
    if not page_id:
        if args.non_interactive:
            raise SystemExit("Missing required page_id in non-interactive mode.")
        try:
            print("Please enter your Notion page ID (or paste a full page URL):")
            user_input = input("> ").strip()
            if not user_input:
                raise ValueError("No page id provided")
            page_id = user_input
        except Exception as ex:
            print(f"Error reading page id from input: {ex}")
            raise

    m = PAGE_ID_REGEX.search(page_id)
    if m:
        page_id = m.group(0)

    print(f"User ID: user_{uuid.uuid4().hex[:8]}")
    print(f"Session ID: session_{uuid.uuid4().hex[:8]}")

    try:
        await run_agent(
            page_id=page_id,
            notion_token=notion_token,
            openai_api_key=openai_api_key,
            mcp_command=args.mcp_cmd,
            mcp_args=args.mcp_args,
        )
    except Exception as exc:
        print(f"Agent execution failed: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting on user interrupt (Ctrl+C). Goodbye!")
        sys.exit(0)
