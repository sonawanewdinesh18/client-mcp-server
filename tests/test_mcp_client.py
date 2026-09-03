import unittest
from langchain_core.tools import tool
from src.agent import create_mcp_agent
from src.config import load_mcp_servers_config
from src.mcp_manager import MCPManager


@tool
def sample_adder(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b

class TestMCPClient(unittest.TestCase):

    def test_config_load_and_save(self):
        cfg = load_mcp_servers_config()
        self.assertIn("mcpServers", cfg)

    def test_agent_creation(self):
        agent_openai = create_mcp_agent(
            api_key="sk-dummy-test-key",
            model_name="[OpenAI] gpt-4o-mini",
            temperature=0.0,
            tools=[sample_adder]
        )
        self.assertIsNotNone(agent_openai)

        agent_groq = create_mcp_agent(
            api_key="gsk_dummy_test_key",
            model_name="[Groq] llama-3.3-70b-versatile",
            temperature=0.0,
            tools=[sample_adder]
        )
        self.assertIsNotNone(agent_groq)


    def test_mcp_manager_empty(self):
        manager = MCPManager({})
        self.assertIsNone(manager.client)
        tools = manager.fetch_tools()
        self.assertEqual(tools, [])

if __name__ == "__main__":
    unittest.main()
