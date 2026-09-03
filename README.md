# 🚀 Streamlit MCP Client & Agent Studio

A modern, production-grade **Model Context Protocol (MCP)** Client UI built with **Streamlit**, **LangGraph**, **langchain-mcp-adapters**, **Groq**, and **OpenAI**. 

Connect multiple remote SSE or local stdio MCP servers, inspect tool definitions in real-time, and run autonomous tool-calling LLM agents with live execution tracing — designed with a **ChatGPT / Claude** style interface.

---

## 🌟 Key Features

- 🔌 **Multi-Server Connection**: Connect concurrently to multiple MCP servers via Server-Sent Events (SSE) or local subprocesses (`stdio`).
- 🧮 **Built-in Default MCP Servers**: Includes pre-configured, zero-setup **Mathematics (SymPy)** and **Manim Math Animation** servers.
- ⚡ **Multi-Provider Support**: Supports **100% Free Groq API** (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen3.8-27b`) as well as **OpenAI** (`gpt-4o`, `gpt-4o-mini`).
- 💡 **Instant Sample Prompts Guide**: 1-click prompt chips for math calculations, symbolic equation solving, and Manim code generation.
- 📋 **Claude-Style Quick Form & JSON Import**: Add remote SSE servers with simple token inputs (no raw JSON required) or paste `claude_desktop_config.json` blocks directly.
- 🛠️ **Real-Time Tool Discovery**: Inspect tool schemas, arguments, and descriptions dynamically pulled from connected servers.
- 📊 **Visual Execution Traces**: Expandable cards displaying exact tool inputs, status badges (✅/⚠️), and structured JSON output results.
- ☁️ **Streamlit Cloud Deployment**: Ready for one-click deployment to Streamlit Community Cloud.

---

## 📂 Project Layout

```
CLIENT-MCP-SERVER/
├── pyproject.toml              # UV project dependencies & configuration
├── requirements.txt            # Streamlit Cloud deployment requirements
├── .env                        # Local environment variables (Groq / OpenAI Key)
├── .env.example                # Template for environment settings
├── mcp_servers.json            # Persisted MCP server configurations
├── README.md                   # Complete documentation & deployment guide
├── src/
│   ├── config.py               # Dynamic .env loading & model settings
│   ├── mcp_manager.py          # MultiServerMCPClient wrapper & tool fetcher
│   ├── agent.py                # LangGraph ReAct agent builder & runner
│   ├── app.py                  # Streamlit application entrypoint
│   ├── servers/                # Built-in Default MCP Servers
│   │   ├── math_server.py      # Symbolic Math, Calculus & Linear Algebra
│   │   └── manim_server.py     # Manim Math Animation & Scene Generator
│   └── ui/
│       ├── styles.py           # CSS design tokens, containment & animations
│       ├── sidebar.py          # Claude-style Server manager & JSON importer
│       └── chat.py             # Chat interface with sample prompt chips
└── tests/
    └── test_mcp_client.py      # Automated unit tests
```

---

## 🛠️ Setup Guide

### 1. Prerequisites
- **Python**: `>= 3.10`
- **uv**: Fast Python package manager ([Install uv](https://github.com/astral-sh/uv))

### 2. Install Dependencies
```bash
# Create and activate virtual environment
uv venv

# Install project dependencies
uv pip install -r requirements.txt
```

### 3. Configure API Keys in `.env`
Open `.env` in the project root:
```env
# Free Groq API Key (Recommended - https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_groq_key_here

# OpenAI API Key (Optional)
OPENAI_API_KEY=sk-proj-your_openai_key_here

DEFAULT_MODEL=[Groq] openai/gpt-oss-120b
DEFAULT_TEMPERATURE=0.2
```

---

## 🖥️ Running Locally

```bash
uv run streamlit run src/app.py
```

Open your browser at: **`http://localhost:8501`**


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
