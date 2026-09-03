import json
import streamlit as st
from src.config import save_mcp_servers_config
from src.mcp_manager import MCPManager



def render_sidebar(mcp_manager: MCPManager) -> None:
    """Renders the Streamlit sidebar controls for MCP servers and tools."""
    with st.sidebar:
        st.markdown("## 🔌 MCP Server Settings")

        
        server_configs = st.session_state.get("server_configs", {})

        # List existing servers
        for name, cfg in list(server_configs.items()):
            transport = cfg.get("transport", "sse").lower()
            enabled = cfg.get("enabled", True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                badge_class = "badge-sse" if transport == "sse" else "badge-stdio"
                st.markdown(
                    f"**{name}** <span class='{badge_class}'>{transport}</span>",
                    unsafe_allow_html=True
                )
                if transport == "sse":
                    st.caption(f"🔗 `{cfg.get('url', '')}`")
                else:
                    st.caption(f"💻 `{cfg.get('command', '')} {' '.join(cfg.get('args', []))}`")

            with col2:
                new_enabled = st.checkbox("On", value=enabled, key=f"enable_{name}")
                if new_enabled != enabled:
                    server_configs[name]["enabled"] = new_enabled
                    st.session_state["server_configs"] = server_configs
                    mcp_manager.update_configs(server_configs)
                    save_mcp_servers_config({"mcpServers": server_configs})
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"del_{name}", help="Delete server"):
                    del server_configs[name]
                    st.session_state["server_configs"] = server_configs
                    mcp_manager.update_configs(server_configs)
                    save_mcp_servers_config({"mcpServers": server_configs})
                    st.rerun()

            # Test connection button
            if st.button(f"🔍 Test Connection", key=f"test_{name}"):
                with st.spinner(f"Testing connection to {name}..."):
                    success, msg, tools = mcp_manager.test_server_connection(name, cfg)
                    if success:
                        st.success(f"{msg}")
                    else:
                        st.error(f"{msg}")
            
            st.divider()

        # Add New Server Section
        with st.expander("➕ Add New MCP Server", expanded=False):
            tab_wizard, tab_json = st.tabs(["📝 Quick Form", "📋 Paste JSON (Claude Style)"])

            with tab_wizard:
                transport_type = st.radio(
                    "Transport Type",
                    ["🌐 Remote SSE (Cloud / URL)", "💻 Local stdio (uvx / Python)"],
                    horizontal=False
                )

                if "Remote SSE" in transport_type:
                    server_name = st.text_input("Server Name", placeholder="e.g. Expense-Tracker")
                    sse_url = st.text_input("SSE URL", placeholder="https://your-server.fastmcp.app/mcp or /sse")
                    auth_token = st.text_input(
                        "API Key / Auth Token (Optional)",
                        type="password",
                        placeholder="Paste your FastMCP or Bearer token here (if protected)"
                    )
                    
                    if st.button("➕ Connect Remote Server", use_container_width=True):
                        if not server_name.strip() or not sse_url.strip():
                            st.error("Please provide both Server Name and SSE URL.")
                        else:
                            clean_name = server_name.strip()
                            headers = {}
                            if auth_token.strip():
                                token = auth_token.strip()
                                if not token.lower().startswith("bearer "):
                                    token = f"Bearer {token}"
                                headers["Authorization"] = token

                            server_configs[clean_name] = {
                                "transport": "sse",
                                "url": sse_url.strip(),
                                "headers": headers,
                                "enabled": True
                            }
                            st.session_state["server_configs"] = server_configs
                            mcp_manager.update_configs(server_configs)
                            save_mcp_servers_config({"mcpServers": server_configs})
                            st.success(f"Added {clean_name}!")
                            st.rerun()

                else:
                    preset = st.selectbox(
                        "Preset Template",
                        [
                            "Custom Command",
                            "SQLite Database (uvx mcp-server-sqlite)",
                            "Local Python Script (python server.py)",
                            "Node / NPX Server (npx -y ...)"
                        ]
                    )

                    default_cmd = "uvx"
                    default_args = ""
                    if "SQLite" in preset:
                        default_cmd = "uvx"
                        default_args = "mcp-server-sqlite --db-path sample.db"
                    elif "Python" in preset:
                        default_cmd = "python"
                        default_args = "server.py"
                    elif "Node" in preset:
                        default_cmd = "npx"
                        default_args = "-y @modelcontextprotocol/server-filesystem ."

                    server_name = st.text_input("Server Name", placeholder="e.g. local_sqlite")
                    cmd = st.text_input("Command", value=default_cmd)
                    args_str = st.text_input("Arguments", value=default_args)

                    if st.button("➕ Connect Local Server", use_container_width=True):
                        if not server_name.strip() or not cmd.strip():
                            st.error("Please provide Server Name and Command.")
                        else:
                            clean_name = server_name.strip()
                            args_list = args_str.split() if args_str.strip() else []
                            server_configs[clean_name] = {
                                "transport": "stdio",
                                "command": cmd.strip(),
                                "args": args_list,
                                "env": {},
                                "enabled": True
                            }
                            st.session_state["server_configs"] = server_configs
                            mcp_manager.update_configs(server_configs)
                            save_mcp_servers_config({"mcpServers": server_configs})
                            st.success(f"Added {clean_name}!")
                            st.rerun()

            with tab_json:
                st.caption("Paste your `claude_desktop_config.json` or `mcpServers` block directly:")
                json_paste = st.text_area(
                    "JSON Config",
                    height=160,
                    placeholder='{\n  "mcpServers": {\n    "my_server": {\n      "transport": "sse",\n      "url": "https://..."\n    }\n  }\n}'
                )
                if st.button("📥 Import JSON Config", use_container_width=True):
                    if json_paste.strip():
                        try:
                            parsed = json.loads(json_paste.strip())
                            servers_to_add = parsed.get("mcpServers", parsed)
                            if isinstance(servers_to_add, dict):
                                for s_name, s_cfg in servers_to_add.items():
                                    if isinstance(s_cfg, dict):
                                        if "transport" not in s_cfg:
                                            s_cfg["transport"] = "sse" if "url" in s_cfg else "stdio"
                                        s_cfg["enabled"] = s_cfg.get("enabled", True)
                                        server_configs[s_name] = s_cfg
                                st.session_state["server_configs"] = server_configs
                                mcp_manager.update_configs(server_configs)
                                save_mcp_servers_config({"mcpServers": server_configs})
                                st.success("Imported configuration successfully!")
                                st.rerun()
                            else:
                                st.error("JSON must contain an object mapping server names to configurations.")
                        except Exception as e:
                            st.error(f"Invalid JSON: {e}")


        # --- Discovered Tools Inspector ---
        st.markdown("---")
        st.markdown("### 🛠️ Discovered Tools")
        
        if st.button("🔄 Reload Tools"):
            try:
                with st.spinner("Fetching active tools..."):
                    loaded_tools = mcp_manager.fetch_tools()
                    st.session_state["loaded_tools"] = loaded_tools
                    st.success(f"Loaded {len(loaded_tools)} tool(s)")
            except Exception as e:
                st.error(f"Failed to fetch tools: {e}")

        tools = st.session_state.get("loaded_tools", [])
        if tools:
            st.caption(f"**{len(tools)}** active tool(s) available for the agent.")
            for t in tools:
                with st.expander(f"🔧 {t.name}"):
                    st.markdown(f"**Description:** {t.description or 'No description'}")
                    if hasattr(t, "args_schema") and t.args_schema:
                        try:
                            schema = t.args_schema.schema() if hasattr(t.args_schema, "schema") else t.args_schema.model_json_schema()
                            st.json(schema)
                        except Exception:
                            st.code(str(t.args_schema))
        else:
            st.info("No tools loaded. Connect an MCP server and click 'Reload Tools' or send a chat prompt.")


