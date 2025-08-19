# Notion MCP Terminal Agent
2. Install dependencies:


```bash
pip install -r requirements.txt
```


3. Run the script interactively:


```bash
python notion_mcp_agent.py <page_id>
```


If you don't pass `<page_id>`, the CLI will prompt you for one.


---


## ⚙️ Environment variables


Place the following entries in your `.env` file (or export them in your shell):


```
NOTION_API_KEY=secret_notion_token_here
OPENAI_API_KEY=secret_openai_key_here # optional, only if you run models through the agent
LOG_LEVEL=INFO
```


---


## 🧩 How to wire into your production agent stack


1. Ensure `agno`, `mcp`, and related agent packages are installed in your environment.
2. Replace the placeholder `open_mcp_tools` context manager with the real
`MCPTools(server_params=StdioServerParameters(...))` context manager.
3. Uncomment the `Agent(...)` instantiation and provide the appropriate model
implementation (e.g., `OpenAIChat`).
4. Use your CI/CD tooling to pass secrets via environment variables or a
secrets manager — do NOT commit `.env` to source control.


---


## 📦 Files in this bundle


- `notion_mcp_agent.py` - main program file
- `requirements.txt` - python dependencies
- `README.md` - this file
- `.env.example` - example environment variables


---


## 🧪 Testing


- Run the script with a fake page id in non-interactive mode to verify validations:


```bash
python notion_mcp_agent.py --non-interactive <some-page-id>
```


- When integrating the real `MCPTools`, start the MCP server and then run the script
to verify the interactive flow.


---


## 🧾 Notes & Security


- Store secrets in environment variables or a proper secrets manager.
- Keep the `Notion-Version` header up to date if Notion updates the API.


---


If you need a packaged distribution (zip/tar) or a `dockerfile` to run this in a container,
I can generate that next.
```


### FILE: .env.example
```
# Copy this file to .env and fill the secrets
NOTION_API_KEY=your_notion_integration_token_here
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO