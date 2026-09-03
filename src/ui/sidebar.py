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

        # Add New Server Accordion
        with st.expander("➕ Add New MCP Server"):
            transport_type = st.radio("Transport Type", ["SSE (Remote/URL)", "stdio (Local Command)"], horizontal=True)
            
            server_name = st.text_input("Server Name (unique identifier)", placeholder="e.g. weather_service")
            
            if "SSE" in transport_type:
                sse_url = st.text_input("SSE URL", placeholder="https://api.example.com/sse or http://localhost:8000/sse")
                headers_str = st.text_area("Optional Headers (JSON)", placeholder='{"Authorization": "Bearer ..."}')
                
                if st.button("Add SSE Server"):
                    if not server_name or not sse_url:
                        st.error("Server name and URL are required.")
                    elif server_name in server_configs:
                        st.error("A server with this name already exists.")
                    else:
                        headers_dict = {}
                        if headers_str.strip():
                            try:
                                headers_dict = json.loads(headers_str)
                            except Exception as e:
                                st.error(f"Invalid headers JSON: {e}")
                                return {
                                    "api_key": active_key,
                                    "model": selected_model,
                                    "temperature": temperature
                                }
                        
                        server_configs[server_name] = {
                            "transport": "sse",
                            "url": sse_url.strip(),
                            "headers": headers_dict,
                            "enabled": True
                        }
                        st.session_state["server_configs"] = server_configs
                        mcp_manager.update_configs(server_configs)
                        save_mcp_servers_config({"mcpServers": server_configs})
                        st.success(f"Added server {server_name}!")
                        st.rerun()
            else:
                cmd = st.text_input("Command", placeholder="e.g. uvx, python, node")
                args_str = st.text_input("Arguments (space-separated)", placeholder="e.g. mcp-server-sqlite --db-path sample.db")
                env_str = st.text_area("Optional Environment Variables (JSON)", placeholder='{"API_KEY": "..."}')
                
                if st.button("Add stdio Server"):
                    if not server_name or not cmd:
                        st.error("Server name and Command are required.")
                    elif server_name in server_configs:
                        st.error("A server with this name already exists.")
                    else:
                        env_dict = {}
                        if env_str.strip():
                            try:
                                env_dict = json.loads(env_str)
                            except Exception as e:
                                st.error(f"Invalid env JSON: {e}")
                                return {
                                    "api_key": active_key,
                                    "model": selected_model,
                                    "temperature": temperature
                                }
                        
                        args_list = args_str.split() if args_str.strip() else []
                        server_configs[server_name] = {
                            "transport": "stdio",
                            "command": cmd.strip(),
                            "args": args_list,
                            "env": env_dict,
                            "enabled": True
                        }
                        st.session_state["server_configs"] = server_configs
                        mcp_manager.update_configs(server_configs)
                        save_mcp_servers_config({"mcpServers": server_configs})
                        st.success(f"Added stdio server {server_name}!")
                        st.rerun()

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


