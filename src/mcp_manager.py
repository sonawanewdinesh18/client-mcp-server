import asyncio
from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

def _run_async(coro):
    """Run an async coroutine safely in Streamlit's script worker thread."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If loop is already running in this thread, create a task in a separate thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return loop.run_until_complete(coro)



import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _normalize_connection_spec(config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes connection spec for cross-platform and virtualenv execution."""
    transport = config.get("transport", "sse").lower()
    conn_spec = {"transport": transport}

    if transport == "sse":
        conn_spec["url"] = config.get("url", "")
        if config.get("headers"):
            conn_spec["headers"] = config.get("headers")
    elif transport == "stdio":
        raw_cmd = config.get("command", "").strip()
        raw_args = config.get("args", [])
        
        # Resolve python / python3 to active sys.executable
        if raw_cmd.lower() in ["python", "python3", "python.exe", "python3.exe"]:
            cmd = sys.executable
        else:
            cmd = raw_cmd
            
        # Resolve any relative .py scripts to absolute path based on project root
        args = []
        for a in raw_args:
            if isinstance(a, str) and (a.endswith(".py") or a.startswith("src/")):
                candidate = (BASE_DIR / a).resolve()
                if candidate.exists():
                    args.append(str(candidate))
                else:
                    args.append(a)
            else:
                args.append(str(a))
                
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        if config.get("env") and isinstance(config.get("env"), dict):
            env.update(config.get("env"))

        conn_spec["command"] = cmd
        conn_spec["args"] = args
        conn_spec["env"] = env

    return conn_spec


class MCPManager:
    """Manages MCP Server connections and tool fetching using MultiServerMCPClient."""

    def __init__(self, server_configs: Optional[Dict[str, Any]] = None):
        self.server_configs: Dict[str, Any] = server_configs or {}
        self.client: Optional[MultiServerMCPClient] = None
        self._cached_tools: List[BaseTool] = []
        self._refresh_client()

    def _refresh_client(self):
        """Re-initializes the MultiServerMCPClient with active enabled connections."""
        active_connections = {}
        for name, config in self.server_configs.items():
            if config.get("enabled", True):
                active_connections[name] = _normalize_connection_spec(config)

        if active_connections:
            self.client = MultiServerMCPClient(active_connections)
        else:
            self.client = None

    def update_configs(self, server_configs: Dict[str, Any]):
        """Updates the configuration and refreshes the client."""
        self.server_configs = server_configs
        self._refresh_client()


    async def fetch_tools_async(self) -> List[BaseTool]:
        """Fetch all tools from configured and enabled MCP servers asynchronously."""
        if not self.client:
            return []
        
        all_tools: List[BaseTool] = []
        errors: List[str] = []

        for name, config in self.server_configs.items():
            if not config.get("enabled", True):
                continue
            try:
                tools = await self.client.get_tools(server_name=name)
                all_tools.extend(tools)
            except Exception as e:
                err_str = str(e)
                # Unwrap ExceptionGroup if present
                if hasattr(e, "exceptions") and getattr(e, "exceptions", None):
                    sub_errs = [str(sub) for sub in getattr(e, "exceptions")]
                    err_str = " | ".join(sub_errs)
                
                if "401" in err_str or "unauthorized" in err_str.lower():
                    clean_err = f"'{name}': HTTP 401 Unauthorized (Requires Auth Token/Key)"
                elif "404" in err_str:
                    clean_err = f"'{name}': HTTP 404 Not Found (Check URL path)"
                elif "FileNotFoundError" in err_str or "No such file" in err_str or "command not found" in err_str.lower() or "uvx" in err_str:
                    clean_err = f"'{name}': Command '{config.get('command')}' not found (stdio servers only run locally, not on Streamlit Cloud)"
                else:
                    clean_err = f"'{name}': {err_str}"
                
                errors.append(clean_err)

        self._cached_tools = all_tools

        if errors and not all_tools:
            # Format clean multiline error message
            error_details = "\n• " + "\n• ".join(errors)
            raise RuntimeError(
                f"Could not connect to enabled servers:{error_details}\n\n"
                "👉 Tip: Uncheck 'On' or 🗑️ delete servers you are not using, or enter required Auth Tokens."
            )

        return all_tools


    def fetch_tools(self) -> List[BaseTool]:
        """Synchronous wrapper to fetch tools for Streamlit runtime."""
        return _run_async(self.fetch_tools_async())

    async def test_server_connection_async(self, name: str, config: Dict[str, Any]) -> tuple[bool, str, List[Dict[str, Any]]]:
        """
        Tests connection to a single MCP server configuration.
        Returns: (success: bool, message: str, tools_list: list)
        """
        try:
            test_conn = _normalize_connection_spec(config)
            test_client = MultiServerMCPClient({name: test_conn})
            tools = await test_client.get_tools(server_name=name)
            tool_meta = []
            for t in tools:
                args_schema = {}
                if hasattr(t, "args_schema") and t.args_schema:
                    try:
                        args_schema = t.args_schema.schema() if hasattr(t.args_schema, "schema") else t.args_schema.model_json_schema()
                    except Exception:
                        args_schema = str(t.args_schema)
                
                tool_meta.append({
                    "name": t.name,
                    "description": t.description or "No description provided",
                    "args": args_schema
                })
            return True, f"Successfully connected! Found {len(tools)} tool(s).", tool_meta
        except Exception as e:
            err_str = str(e)
            if hasattr(e, "exceptions") and getattr(e, "exceptions", None):
                err_str = " | ".join(str(sub) for sub in getattr(e, "exceptions"))
            
            if "401" in err_str or "unauthorized" in err_str.lower():
                return False, "HTTP 401 Unauthorized: Server requires Authorization headers or an API token.", []
            elif "404" in err_str:
                return False, "HTTP 404 Not Found: Check if URL path is correct (e.g., /sse or /mcp).", []
            return False, f"Connection error: {err_str}", []



    def test_server_connection(self, name: str, config: Dict[str, Any]) -> tuple[bool, str, List[Dict[str, Any]]]:
        """Synchronous wrapper for test_server_connection_async."""
        return _run_async(self.test_server_connection_async(name, config))

