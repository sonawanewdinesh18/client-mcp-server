import json
import streamlit as st
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.config import AVAILABLE_MODELS, get_openai_api_key, get_groq_api_key
from src.agent import create_mcp_agent, run_agent_stream_async
from src.mcp_manager import MCPManager

def render_tool_step(step: Dict[str, Any]):
    """Renders a single tool call and its execution result inside a Streamlit expander."""
    tool_name = step.get("name", "Tool")
    status = step.get("status", "success")
    icon = "✅" if status == "success" else "⚠️"
    
    with st.expander(f"{icon} Executed Tool: `{tool_name}`", expanded=False):
        st.markdown("**Tool Arguments:**")
        if isinstance(step.get("args"), (dict, list)):
            st.json(step.get("args"))
        else:
            st.code(str(step.get("args", "{}")), language="json")
        
        if "result" in step:
            st.markdown("**Result Output:**")
            result = step.get("result")
            if isinstance(result, (dict, list)):
                st.json(result)
            elif isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    st.json(parsed)
                except Exception:
                    st.code(result)
            else:
                st.code(str(result))


def render_chat_interface(mcp_manager: MCPManager):
    """Renders the main chat window with ChatGPT/Claude style top model picker and sample prompts."""
    
    # Top Header Bar (ChatGPT / Claude Style)
    col_title, col_guide, col_model, col_clear = st.columns([4, 2, 2, 1])
    with col_title:
        st.markdown('<div class="main-title">🤖 MCP Assistant</div>', unsafe_allow_html=True)
    with col_guide:
        show_guide = st.button("💡 How to Use MCP", help="View MCP guide & sample prompts", use_container_width=True)
    with col_model:
        selected_model = st.selectbox(
            "Model Selection",
            options=AVAILABLE_MODELS,
            index=0,
            label_visibility="collapsed",
            help="Switch Model Provider (Groq / OpenAI)"
        )
    with col_clear:
        if st.button("🗑️ Clear", help="Clear conversation history", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    st.markdown('<div class="sub-title">Connected to Model Context Protocol (MCP) servers • Built-in Mathematics & Manim</div>', unsafe_allow_html=True)

    # Quick Guide & Sample Prompts Modal / Expander
    if show_guide or st.session_state.get("show_guide_expanded", False):
        with st.expander("📖 **How to Use MCP & Sample Prompts**", expanded=True):
            st.markdown(
                """
                ### 🌟 What is Model Context Protocol (MCP)?
                **MCP** connects AI models to external tools and live databases. When you send a prompt:
                1. The AI decides which tool to invoke.
                2. It calls your MCP server in real-time.
                3. It returns the exact computed output with interactive visualizations.
                """
            )

            st.markdown("#### 🎯 Click any Sample Prompt to Try:")
            col_math, col_manim = st.columns(2)

            with col_math:
                st.markdown("**🧮 Mathematics Server Prompts:**")
                if st.button("▶️ Solve equation: `x^3 - 6x^2 + 11x - 6 = 0`", use_container_width=True):
                    st.session_state["queued_prompt"] = "Solve the polynomial equation x**3 - 6*x**2 + 11*x - 6 = 0 step by step."
                    st.rerun()
                if st.button("▶️ Find derivative of `x^2 * sin(x)`", use_container_width=True):
                    st.session_state["queued_prompt"] = "Find the derivative of x**2 * sin(x) with respect to x."
                    st.rerun()
                if st.button("▶️ Eigenvalues & Determinant of `[[4, 2], [1, 3]]`", use_container_width=True):
                    st.session_state["queued_prompt"] = "Calculate the determinant and eigenvalues of the matrix [[4, 2], [1, 3]]."
                    st.rerun()

            with col_manim:
                st.markdown("**🎬 Manim Math Animation Prompts:**")
                if st.button("▶️ Animate Pythagorean Theorem Proof", use_container_width=True):
                    st.session_state["queued_prompt"] = "Generate a Manim scene animation code proving the Pythagorean theorem visually."
                    st.rerun()
                if st.button("▶️ Animate Tangent Line Slope in Calculus", use_container_width=True):
                    st.session_state["queued_prompt"] = "Create a Manim Community animation code illustrating the tangent line to y = x^2 as x moves from 0 to 3."
                    st.rerun()
                if st.button("▶️ Manim 2D Vector Transformation", use_container_width=True):
                    st.session_state["queued_prompt"] = "Generate a Manim LinearTransformationScene code animating matrix [[2, 1], [1, 2]]."
                    st.rerun()

    # Initialize messages list
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Render existing conversation history
    for msg in st.session_state["messages"]:
        role = msg.get("role", "user")
        with st.chat_message(role):
            # Render tool executions if any
            if "tool_steps" in msg:
                for step in msg["tool_steps"]:
                    render_tool_step(step)
            # Render main text content
            if msg.get("content"):
                st.markdown(msg["content"])

    # Check for queued sample prompt or standard chat input
    user_prompt = st.chat_input("Ask a question or request a task using your MCP tools...")
    if not user_prompt and st.session_state.get("queued_prompt"):
        user_prompt = st.session_state.pop("queued_prompt")

    if user_prompt:

        is_groq = "[Groq]" in selected_model
        
        # Check corresponding API Key from .env / environment
        if is_groq:
            api_key = get_groq_api_key()
            if not api_key:
                st.error("❌ **Groq API Key is missing!** Please add `GROQ_API_KEY=gsk_...` to your `.env` or Streamlit Cloud Secrets. (Get a free key at [console.groq.com/keys](https://console.groq.com/keys)).")
                return
        else:
            api_key = get_openai_api_key()
            if not api_key:
                st.error("❌ **OpenAI API Key is missing!** Please add `OPENAI_API_KEY=sk-...` to your `.env` or Streamlit Cloud Secrets.")
                return

        # Display and record user message
        st.session_state["messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Assistant processing
        with st.chat_message("assistant"):
            # Fetch currently enabled tools
            tools = st.session_state.get("loaded_tools")
            if tools is None:
                with st.spinner("Connecting to MCP servers and discovering tools..."):
                    try:
                        tools = mcp_manager.fetch_tools()
                        st.session_state["loaded_tools"] = tools
                    except Exception as e:
                        st.warning(f"Could not fetch all MCP tools: {e}")
                        tools = []

            # Create agent
            agent = create_mcp_agent(
                api_key=api_key,
                model_name=selected_model,
                temperature=0.2,
                tools=tools
            )


            # Build message history for LangGraph

            langchain_messages: List[BaseMessage] = []
            for m in st.session_state["messages"]:
                if m["role"] == "user":
                    langchain_messages.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=m.get("content", "")))

            # Streaming execution
            response_container = st.empty()
            status_container = st.container()
            
            tool_steps: List[Dict[str, Any]] = []
            active_tool_calls: Dict[str, Dict[str, Any]] = {}
            final_content = ""

            async def process_stream():
                nonlocal final_content
                async for event in run_agent_stream_async(agent, langchain_messages):
                    ev_type = event.get("type")
                    
                    if ev_type == "tool_call":
                        tc_id = event.get("id") or event.get("name")
                        tc_entry = {
                            "name": event.get("name"),
                            "args": event.get("args"),
                            "status": "running"
                        }
                        active_tool_calls[tc_id] = tc_entry
                        tool_steps.append(tc_entry)
                        with status_container:
                            render_tool_step(tc_entry)

                    elif ev_type == "tool_result":
                        tc_id = event.get("tool_call_id") or event.get("name")
                        if tc_id in active_tool_calls:
                            active_tool_calls[tc_id]["result"] = event.get("content")
                            active_tool_calls[tc_id]["status"] = event.get("status", "success")
                        else:
                            tool_steps.append({
                                "name": event.get("name"),
                                "args": {},
                                "result": event.get("content"),
                                "status": event.get("status", "success")
                            })
                        # Re-render tool status
                        status_container.empty()
                        with status_container:
                            for step in tool_steps:
                                render_tool_step(step)

                    elif ev_type == "agent_message":
                        content = event.get("content", "")
                        if content:
                            final_content = content
                            response_container.markdown(final_content)

            # Run async stream within Streamlit execution thread
            with st.spinner("Agent is reasoning..."):
                from src.mcp_manager import _run_async
                try:
                    _run_async(process_stream())
                except Exception as e:
                    err_msg = str(e)
                    if "RateLimitError" in type(e).__name__ or "429" in err_msg or "quota" in err_msg.lower():
                        st.error(
                            "⚠️ **OpenAI Rate Limit / Quota Exceeded (429 Error)**\n\n"
                            "This usually happens for one of two reasons:\n"
                            "1. **Account has $0 balance**: OpenAI requires prepaid API credits. Check your balance at [OpenAI Billing](https://platform.openai.com/settings/organization/billing/overview).\n"
                            "2. **Rate Limit on `gpt-4o`**: Try switching the model dropdown at the top to **`gpt-4o-mini`** which has much higher request limits."
                        )
                    elif "AuthenticationError" in type(e).__name__ or "401" in err_msg:
                        st.error("❌ **Invalid OpenAI API Key**. Please verify the `OPENAI_API_KEY` in your `.env` or Streamlit Cloud Secrets.")
                    else:
                        st.error(f"❌ **Execution Error:** {err_msg}")
                    return

            # Save assistant message to session history
            st.session_state["messages"].append({
                "role": "assistant",
                "content": final_content,
                "tool_steps": tool_steps
            })

