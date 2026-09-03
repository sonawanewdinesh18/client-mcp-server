import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
SERVERS_CONFIG_PATH = BASE_DIR / "mcp_servers.json"

AVAILABLE_MODELS = [
    "[Groq] openai/gpt-oss-120b",
    "[Groq] openai/gpt-oss-20b",
    "[Groq] qwen/qwen3.8-27b",
    "[OpenAI] gpt-4o",
    "[OpenAI] gpt-4o-mini",
    "[OpenAI] gpt-4-turbo",
    "[OpenAI] o1-mini",
]



def get_groq_api_key() -> Optional[str]:
    """
    Retrieve Groq API Key dynamically from:
    1. Local .env file (real-time reload)
    2. OS Environment Variables
    3. Streamlit Cloud Secrets (st.secrets)
    """
    if ENV_PATH.exists():
        try:
            from dotenv import dotenv_values
            env_vars = dotenv_values(ENV_PATH)
            if env_vars.get("GROQ_API_KEY"):
                val = env_vars["GROQ_API_KEY"]
                if val and val.strip():
                    return val.strip()
        except Exception:
            pass

    try:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    except Exception:
        pass

    key = os.getenv("GROQ_API_KEY")
    if key and key.strip():
        return key.strip()

    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            secret_key = st.secrets["GROQ_API_KEY"]
            if secret_key and secret_key.strip():
                return secret_key.strip()
    except Exception:
        pass

    return None


def get_openai_api_key() -> Optional[str]:
    """
    Retrieve OpenAI API Key dynamically from:
    1. Local .env file (real-time reload)
    2. OS Environment Variables
    3. Streamlit Cloud Secrets (st.secrets)
    """
    if ENV_PATH.exists():
        try:
            from dotenv import dotenv_values
            env_vars = dotenv_values(ENV_PATH)
            if env_vars.get("OPENAI_API_KEY"):
                val = env_vars["OPENAI_API_KEY"]
                if val and val.strip():
                    return val.strip()
        except Exception:
            pass

    try:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    except Exception:
        pass

    key = os.getenv("OPENAI_API_KEY")
    if key and key.strip():
        return key.strip()

    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            secret_key = st.secrets["OPENAI_API_KEY"]
            if secret_key and secret_key.strip():
                return secret_key.strip()
    except Exception:
        pass

    return None





def load_mcp_servers_config() -> Dict[str, Any]:
    """Load MCP server configurations from mcp_servers.json."""
    if not SERVERS_CONFIG_PATH.exists():
        return {"mcpServers": {}}
    
    try:
        with open(SERVERS_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) and "mcpServers" in data else {"mcpServers": {}}
    except Exception as e:
        print(f"Error reading {SERVERS_CONFIG_PATH}: {e}")
        return {"mcpServers": {}}


def save_mcp_servers_config(config_data: Dict[str, Any]) -> bool:
    """Save updated MCP server configurations to mcp_servers.json."""
    try:
        with open(SERVERS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {SERVERS_CONFIG_PATH}: {e}")
        return False
