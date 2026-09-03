from typing import List, Dict, Any, Optional, AsyncIterator
import warnings
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool

# Suppress LangGraph deprecation notice for create_react_agent
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph


DEFAULT_SYSTEM_PROMPT = """You are a helpful, intelligent AI assistant connected to Model Context Protocol (MCP) servers.
You have access to tools provided by the user's active MCP servers.
Always consider which tools are best suited to answer the user's questions or execute requested tasks.
When calling tools, provide clear explanations of what you are doing. If a tool fails or returns an error, explain the issue and try alternative strategies if available.
Be concise, clear, and accurate.
"""

def create_mcp_agent(
    api_key: str,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.2,
    tools: Optional[List[BaseTool]] = None,
    system_prompt: Optional[str] = None,
) -> CompiledStateGraph:
    """Creates a LangGraph ReAct agent bound with ChatGroq or ChatOpenAI and provided MCP tools."""
    clean_model = model_name.replace("[Groq] ", "").replace("[OpenAI] ", "").strip()
    is_groq = "[Groq]" in model_name or "llama" in model_name.lower() or "mixtral" in model_name.lower() or "gemma" in model_name.lower()

    if is_groq:
        llm = ChatGroq(
            model=clean_model,
            temperature=temperature,
            api_key=api_key,
            streaming=True
        )
    else:
        llm = ChatOpenAI(
            model=clean_model,
            temperature=temperature,
            api_key=api_key,
            streaming=True
        )
    
    prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    tools_list = tools or []
    
    agent = create_react_agent(
        model=llm,
        tools=tools_list,
        prompt=prompt
    )
    return agent



async def run_agent_stream_async(
    agent: CompiledStateGraph,
    messages: List[BaseMessage]
) -> AsyncIterator[Dict[str, Any]]:
    """
    Executes the LangGraph agent asynchronously and yields intermediate state steps and messages.
    Yields events with structure:
    {
        "type": "tool_call" | "tool_result" | "agent_message" | "final_result",
        "data": ...
    }
    """
    inputs = {"messages": messages}
    
    async for event in agent.astream(inputs, stream_mode="updates"):
        for node_name, node_output in event.items():
            if "messages" in node_output:
                for msg in node_output["messages"]:
                    if isinstance(msg, AIMessage):
                        if getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                yield {
                                    "type": "tool_call",
                                    "name": tc.get("name"),
                                    "args": tc.get("args"),
                                    "id": tc.get("id"),
                                    "node": node_name
                                }
                        if msg.content:
                            yield {
                                "type": "agent_message",
                                "content": msg.content,
                                "node": node_name,
                                "raw_message": msg
                            }
                    elif isinstance(msg, ToolMessage):
                        yield {
                            "type": "tool_result",
                            "name": getattr(msg, "name", "tool"),
                            "content": msg.content,
                            "tool_call_id": getattr(msg, "tool_call_id", ""),
                            "status": getattr(msg, "status", "success"),
                            "node": node_name,
                            "raw_message": msg
                        }
                    else:
                        yield {
                            "type": "other_message",
                            "content": getattr(msg, "content", ""),
                            "raw_message": msg
                        }
