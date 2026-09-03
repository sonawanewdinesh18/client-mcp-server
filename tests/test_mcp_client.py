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


    def test_math_tools_execution(self):
        from src.servers.math_server import calculate_expression, solve_equation, matrix_operations
        import json
        
        calc_res = json.loads(calculate_expression("2**8 + 44"))
        self.assertEqual(calc_res.get("simplified"), "300")
        
        eq_res = json.loads(solve_equation("x**2 - 9 = 0", "x"))
        self.assertIn("-3", eq_res.get("solutions", []))
        self.assertIn("3", eq_res.get("solutions", []))
        
        mat_res = json.loads(matrix_operations([[1, 2], [3, 4]], "determinant"))
        self.assertEqual(mat_res.get("determinant"), -2.0)

    def test_manim_tools_execution(self):
        from src.servers.manim_server import generate_manim_animation_code, get_manim_template
        import json
        
        gen_res = json.loads(generate_manim_animation_code("Calculus Limit", "Demonstrating limit as x approaches 0"))
        self.assertEqual(gen_res.get("status"), "success")
        self.assertIn("class CalculusLimitScene", gen_res.get("manim_code", ""))
        
        tmpl_res = json.loads(get_manim_template("calculus"))
        self.assertIn("TangentLineScene", tmpl_res.get("template", ""))

    def test_mcp_manager_empty(self):
        manager = MCPManager({})
        self.assertIsNone(manager.client)
        tools = manager.fetch_tools()
        self.assertEqual(tools, [])

if __name__ == "__main__":
    unittest.main()

