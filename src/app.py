import sys

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    try:
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import streamlit as st

from src.config import load_mcp_servers_config

from src.mcp_manager import MCPManager
from src.ui.styles import inject_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.chat import render_chat_interface

# Configure page layout and metadata
st.set_page_config(
    page_title="MCP Client & Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Inject custom CSS styles
    inject_custom_css()

    # Initialize server configs in session state
    if "server_configs" not in st.session_state:
        cfg = load_mcp_servers_config()
        st.session_state["server_configs"] = cfg.get("mcpServers", {})

    # Initialize MCP Manager in session state
    if "mcp_manager" not in st.session_state:
        st.session_state["mcp_manager"] = MCPManager(st.session_state["server_configs"])
    else:
        # Keep manager configs in sync with session state
        st.session_state["mcp_manager"].update_configs(st.session_state["server_configs"])

    mcp_manager: MCPManager = st.session_state["mcp_manager"]

    # Render sidebar controls (MCP servers & tools)
    render_sidebar(mcp_manager)

    # Render main chat interface with top model selector
    render_chat_interface(mcp_manager)


if __name__ == "__main__":
    main()
