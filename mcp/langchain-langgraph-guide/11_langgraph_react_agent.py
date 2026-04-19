"""
LANGGRAPH REACT AGENT — The Core Agent Pattern
===============================================
ReAct = Reasoning + Acting

The agent loop:
  Think ("I need to find X") → Act (call a tool) → Observe (get result)
  → Think again → Act again → ... → Final answer

This is the MOST IMPORTANT pattern in AI engineering.
Almost every production AI agent uses this pattern.

Install: pip install langgraph langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
ReAct Pattern (Reasoning + Acting)
  - Agent alternates between THINKING (LLM decides what to do)
    and ACTING (executing a tool).
  - Loop continues until LLM says it has the final answer.

ToolNode
  - A prebuilt LangGraph node that executes tool calls.
  - Reads tool_calls from the last AIMessage, runs each tool,
    wraps results in ToolMessages, returns them.
  - You don't write this yourself — LangGraph provides it.

tools_condition
  - A prebuilt routing function for ReAct agents.
  - If last message has tool_calls → route to "tools" node.
  - If last message has no tool_calls → route to END (agent is done).

ToolMessage
  - A message containing the result of a tool call.
  - Has: tool_call_id (matches the request), content (the result).
  - Sent back to the LLM so it can reason about the result.

Agent Loop:
  START → agent node → [has tool calls?]
             ↑                ↓ yes
             │          tools node (executes tools)
             └──────────── returns ToolMessages
              no tool calls → END
"""

# ─────────────────────────────────────────
# 1. DEFINE TOOLS
# ─────────────────────────────────────────

@tool
def search_web(query: str) -> str:
    """Search the web for current information. Use for facts, news, recent events."""
    # Mock — in real code use DuckDuckGo or Tavily
    results = {
        "LangGraph": "LangGraph is a library for building stateful, multi-actor AI apps.",
        "Python": "Python 3.12 is the latest stable release as of 2024.",
        "React": "React 19 was released in December 2024 with major improvements.",
    }
    for key, value in results.items():
        if key.lower() in query.lower():
            return value
    return f"Search results for '{query}': Found general information about the topic."

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. Input: valid Python math like '10 * 5 + 3'."""
    try:
        result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    mock_weather = {
        "London": "15°C, Partly cloudy, 70% humidity",
        "New York": "22°C, Sunny, 45% humidity",
        "Tokyo": "18°C, Rainy, 85% humidity",
    }
    return mock_weather.get(city, f"Weather data for {city}: 20°C, Clear skies")

@tool
def save_note(title: str, content: str) -> str:
    """Save a note for the user. Use when the user asks to remember or save something."""
    print(f"[NOTE SAVED] {title}: {content}")
    return f"Note '{title}' saved successfully."

tools = [search_web, calculator, get_weather, save_note]


# ─────────────────────────────────────────
# 2. BUILD THE REACT AGENT GRAPH
# ─────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState) -> dict:
    """The thinking node: LLM decides what to do next."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Build the graph
react_graph = StateGraph(AgentState)

react_graph.add_node("agent", agent_node)
react_graph.add_node("tools", ToolNode(tools))  # prebuilt node that runs tools

react_graph.add_edge(START, "agent")

# Conditional edge: does the agent want to call a tool?
react_graph.add_conditional_edges(
    "agent",
    tools_condition,    # prebuilt: checks if last message has tool_calls
    # routes to "tools" if yes, END if no
)

react_graph.add_edge("tools", "agent")  # after tools, think again

react_app = react_graph.compile()

# Print the graph
print(react_app.get_graph().draw_ascii())


# ─────────────────────────────────────────
# 3. RUN THE AGENT
# ─────────────────────────────────────────

def run_agent(question: str, verbose: bool = True):
    """Run the ReAct agent and print the conversation."""
    state = {"messages": [HumanMessage(content=question)]}
    result = react_app.invoke(state)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        for msg in result["messages"]:
            if isinstance(msg, HumanMessage):
                print(f"[USER]: {msg.content}")
            elif isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"[AGENT THINKS]: Call tool '{tc['name']}' with {tc['args']}")
                else:
                    print(f"[AGENT FINAL]: {msg.content}")
            elif isinstance(msg, ToolMessage):
                print(f"[TOOL RESULT]: {msg.content}")
    else:
        return result["messages"][-1].content

run_agent("What is the weather in London and Tokyo? And what is 15% of 850?")
run_agent("Search for information about LangGraph and save a note with what you find.")
run_agent("I have 5 projects. Each takes 3 weeks. How many months is that total?")


# ─────────────────────────────────────────
# 4. REACT AGENT WITH MEMORY (Persistent Conversation)
# ─────────────────────────────────────────

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
persistent_app = react_graph.compile(checkpointer=checkpointer)

def chat_with_agent(session_id: str, user_input: str):
    config = {"configurable": {"thread_id": session_id}}
    result = persistent_app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    return result["messages"][-1].content

session = "user_session_001"
print(chat_with_agent(session, "My name is Uzair. I am a frontend developer."))
print(chat_with_agent(session, "What is 25 * 4?"))
print(chat_with_agent(session, "What is my name and what is my job?"))


# ─────────────────────────────────────────
# 5. STREAMING THE AGENT — See Each Step
# ─────────────────────────────────────────

print("\n--- Agent Stream ---")
for step in react_app.stream({
    "messages": [HumanMessage(content="What's the weather in New York and calculate 100 / 4?")]
}):
    for node_name, state_update in step.items():
        print(f"\n[{node_name.upper()} NODE]")
        for msg in state_update.get("messages", []):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  → Calling: {tc['name']}({tc['args']})")
            elif isinstance(msg, ToolMessage):
                print(f"  → Result: {msg.content}")
            elif isinstance(msg, AIMessage):
                print(f"  → Answer: {msg.content}")


# ─────────────────────────────────────────
# 6. USING prebuilt.create_react_agent — SHORTCUT
# ─────────────────────────────────────────
"""
LangGraph provides a shortcut that builds the entire ReAct graph for you.
For most use cases, use this instead of building it manually.
"""

from langgraph.prebuilt import create_react_agent

# One-liner ReAct agent!
quick_agent = create_react_agent(
    model=llm,
    tools=tools,
    # Optional: add system prompt
    state_modifier="You are a helpful assistant. Always show your reasoning."
)

result = quick_agent.invoke({
    "messages": [HumanMessage(content="Search for Python info and then calculate 2^10")]
})
print(result["messages"][-1].content)


# ─────────────────────────────────────────
# 7. ADDING SYSTEM PROMPT TO REACT AGENT
# ─────────────────────────────────────────

from langchain_core.messages import SystemMessage

def agent_with_system(state: AgentState) -> dict:
    """Agent node with system prompt injected."""
    system = SystemMessage(content="""You are an expert assistant with tools.
When solving problems:
1. Break them into steps
2. Use tools when you need external data
3. Show your reasoning
4. Give a clear final answer""")

    messages = [system] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Replace agent node with the system-prompt version
advanced_graph = StateGraph(AgentState)
advanced_graph.add_node("agent", agent_with_system)
advanced_graph.add_node("tools", ToolNode(tools))
advanced_graph.add_edge(START, "agent")
advanced_graph.add_conditional_edges("agent", tools_condition)
advanced_graph.add_edge("tools", "agent")

advanced_app = advanced_graph.compile()
result = advanced_app.invoke({"messages": [HumanMessage(content="Plan: what is the weather in Tokyo, multiply it by 2")]})
print(result["messages"][-1].content)


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
ReAct Agent = LLM + Tools in a loop.

Graph structure:
  START → agent → (has tool calls?) → tools → agent → (no tool calls?) → END

Prebuilt helpers:
  ToolNode         → executes tool calls from AIMessage automatically
  tools_condition  → routing function (tools vs END)
  create_react_agent → builds entire ReAct graph in one line

Key state:
  messages: Annotated[list, add_messages]  ← chat history grows each turn

Memory:
  Add MemorySaver checkpointer to persist conversation across sessions.

Next: Multi-Agent Systems — multiple specialized agents working together
"""
