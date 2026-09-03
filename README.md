# 🚀 Streamlit MCP Client & Agent Studio

A modern, interactive **Model Context Protocol (MCP)** Client UI built with **Streamlit**, **LangGraph**, **langchain-mcp-adapters**, and **OpenAI**. 

Connect multiple remote SSE or local stdio MCP servers, inspect tool definitions in real-time, and run tool-calling LLM agents with live execution tracing — designed with a **ChatGPT / Claude** style interface.

---

## 🌟 Key Features

- 🔌 **Multi-Server Connection**: Concurrently connect to multiple MCP servers via Server-Sent Events (SSE) or local subprocesses (`stdio`).
- 🧠 **ChatGPT / Claude Style UI**: Sleek top header model selector (`gpt-4o`, `gpt-4o-mini`, etc.) and a dedicated MCP server manager in the sidebar.
- 🛠️ **Real-Time Tool Discovery**: Inspect tool names, parameter schemas, and descriptions dynamically pulled from connected MCP servers.
- ⚡ **LangGraph ReAct Agent Loop**: Autonomous tool-calling agent with live streaming reasoning and tool invocation steps.
- 📊 **Visual Execution Traces**: Expandable cards displaying exact tool inputs, status badges (✅/⚠️), and structured JSON output results.
- 🚀 **Built with UV**: Super-fast Python virtual environment and dependency resolution.
- ☁️ **Streamlit Cloud Deployment**: Ready for one-click deployment to Streamlit Community Cloud.

---

## 📂 Project Layout

```
CLIENT-MCP-SERVER/
├── pyproject.toml              # UV project dependencies & configuration
├── requirements.txt            # Streamlit Cloud deployment requirements
├── .env                        # Local environment variables (OpenAI Key)
├── .env.example                # Template for environment settings
├── mcp_servers.json            # Persisted MCP server configurations
├── README.md                   # Complete documentation & deployment guide
├── .vscode/
│   └── settings.json           # VS Code Python interpreter & path settings
├── src/
│   ├── __init__.py
│   ├── config.py               # Dynamic .env loading & model settings
│   ├── mcp_manager.py          # MultiServerMCPClient wrapper & tool fetcher
│   ├── agent.py                # LangGraph ReAct agent builder & runner
│   ├── app.py                  # Streamlit application entrypoint
│   └── ui/
│       ├── __init__.py
│       ├── styles.py           # Custom CSS badges, gradients & cards
│       ├── sidebar.py          # MCP Server manager (Add/Test/Toggle/Delete)
│       └── chat.py             # Chat interface with top model selector
└── tests/
    └── test_mcp_client.py      # Automated unit tests
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites
- **Python**: `>= 3.10`
- **uv**: Fast Python package manager ([Install uv](https://github.com/astral-sh/uv))

### 2. Initialize Virtual Environment & Dependencies
```bash
# Create virtual environment
uv venv

# Install project dependencies
uv pip install -e .
```

### 3. Configure Your OpenAI API Key
Open `.env` in the project root and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
DEFAULT_MODEL=gpt-4o
DEFAULT_TEMPERATURE=0.2
```

> **How to get an OpenAI API Key:**
> 1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
> 2. Log in and click **`+ Create new secret key`**.
> 3. Copy the key and paste it into `.env`.

---

## 🖥️ Running the Application Locally

Run the Streamlit application using `uv`:

### Windows (PowerShell):
```powershell
$env:PYTHONUTF8=1; uv run streamlit run src/app.py
```

### Linux / macOS:
```bash
PYTHONUTF8=1 uv run streamlit run src/app.py
```

Open your browser at: **`http://localhost:8501`**

---

## 🔌 Connecting MCP Servers

You can manage servers in real time directly from the **Streamlit Sidebar**:

### 1. Server-Sent Events (SSE) — Remote / Cloud MCP Servers
- **Transport**: Select `SSE (Remote/URL)`
- **Server Name**: e.g., `weather_service`
- **SSE URL**: e.g., `https://my-mcp-service.com/sse` or `http://localhost:8000/sse`
- **Optional Headers**: `{"Authorization": "Bearer TOKEN"}`

### 2. stdio — Local MCP Subprocesses
- **Transport**: Select `stdio (Local Command)`
- **Server Name**: e.g., `sqlite_db`
- **Command**: `uvx`
- **Arguments**: `mcp-server-sqlite --db-path sample.db`

### 3. Test & Reload
- Click **🔍 Test Connection** on any server to verify connectivity.
- Click **🔄 Reload Tools** to sync tools with the agent.

---

## ☁️ Deploying to Streamlit Community Cloud

1. **Push to GitHub**:
   Push your repository to GitHub (ensure `.env` is in `.gitignore`).
2. **Deploy on Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
   - Select your repository, branch, and set **Main file path** to: `src/app.py`.
3. **Configure Secrets**:
   - In **App settings > Secrets**, add:
     ```toml
     OPENAI_API_KEY = "sk-proj-your-key"
     DEFAULT_MODEL = "gpt-4o"
     ```
4. **Deploy**:
   Click **Deploy**! Connect remote SSE MCP servers through the sidebar.

---

## 🧪 Running Unit Tests

Run the test suite with:
```powershell
.venv\Scripts\python -m unittest tests/test_mcp_client.py
```

---

## ❓ Troubleshooting & Tips

- **VS Code Diagnostics / Red Numbers**: If VS Code flags missing imports, press `Ctrl+Shift+P` -> `Python: Select Interpreter` -> choose `.venv\Scripts\python.exe`.
- **Windows Terminal Unicode Encoding**: If you encounter character errors in PowerShell, prepend `$env:PYTHONUTF8=1;` before running Streamlit.
