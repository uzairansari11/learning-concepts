"""
LANGCHAIN TOOLS & AGENTS
=========================
Tools = functions the LLM can call.
Agents = LLMs that decide which tool to use and when.

Without tools: LLM can only generate text.
With tools: LLM can search the web, run code, query databases, call APIs.

Install: pip install langchain langchain-anthropic langchain-community
         duckduckgo-search numexpr python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Tool
  - A Python function the LLM can choose to call.
  - Has a name, description, and input schema.
  - LLM reads the description to know WHEN to use it.
  - Examples: search_web, run_calculator, query_database, send_email

Tool Calling (Function Calling)
  - The LLM outputs a structured request: "call tool X with args Y"
  - Your code executes the actual function and returns results.
  - LLM never directly runs code — it just requests it.

Agent
  - An LLM in a loop: think → act → observe → think → act → ...
  - It decides which tool to call based on the user's question.
  - Stops when it has enough info to answer.

AgentExecutor
  - The loop runner that executes agent iterations.
  - Passes tool results back to the LLM automatically.

ReAct Pattern (Reasoning + Acting)
  - The most common agent pattern.
  - LLM reasons: "I need to find X" → acts: calls search tool
  - Observes: gets search results → reasons again → acts again...

create_tool_calling_agent
  - Modern way to create an agent that uses tool calling.
  - More reliable than older string-parsing approaches.
"""

# ─────────────────────────────────────────
# 1. CREATING TOOLS — @tool Decorator
# ─────────────────────────────────────────

from langchain_core.tools import tool

# The simplest way to create a tool is the @tool decorator.
# The docstring becomes the tool's description — LLM reads this!

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together. Use this when the user wants to add numbers."""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers. Use this when the user needs multiplication."""
    return a * b

@tool
def get_word_count(text: str) -> int:
    """Count the number of words in a piece of text."""
    return len(text.split())

# Inspect the tool
print(add_numbers.name)         # add_numbers
print(add_numbers.description)  # "Add two numbers together..."
print(add_numbers.args_schema)  # Pydantic schema for inputs

# Tools can be called directly (for testing)
result = add_numbers.invoke({"a": 5, "b": 3})
print(f"5 + 3 = {result}")


# ─────────────────────────────────────────
# 2. TOOLS WITH COMPLEX INPUTS — Using Pydantic
# ─────────────────────────────────────────

from pydantic import BaseModel, Field
from langchain_core.tools import tool

class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up")
    max_results: int = Field(default=3, description="Number of results to return")

@tool("web_search", args_schema=SearchInput)
def web_search(query: str, max_results: int = 3) -> str:
    """Search the web for current information. Use for recent events, facts, data."""
    # In real code, use DuckDuckGo or Tavily API
    # This is a mock for demonstration
    return f"Search results for '{query}': Found {max_results} results about {query}."

print(web_search.invoke({"query": "LangChain latest version", "max_results": 5}))


# ─────────────────────────────────────────
# 3. TOOL CALLING WITHOUT AGENT — Direct LLM Tool Use
# ─────────────────────────────────────────
"""
You can let the LLM decide which tool to call WITHOUT a full agent loop.
Useful when you want one round of tool selection + execution.
"""

from langchain_core.messages import HumanMessage

tools = [add_numbers, multiply_numbers, get_word_count]

# Bind tools to the LLM — now it knows what tools are available
llm_with_tools = llm.bind_tools(tools)

# Send a message — LLM decides to call a tool
response = llm_with_tools.invoke("What is 42 multiplied by 17?")

print("Response type:", type(response))
print("Tool calls:", response.tool_calls)
# [{'name': 'multiply_numbers', 'args': {'a': 42, 'b': 17}, 'id': '...'}]

# Now execute the tool manually
if response.tool_calls:
    tool_call = response.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    # Find and execute the tool
    tool_map = {t.name: t for t in tools}
    result = tool_map[tool_name].invoke(tool_args)
    print(f"Tool result: {result}")  # 714


# ─────────────────────────────────────────
# 4. FULL AGENT — Automatic Tool Loop
# ─────────────────────────────────────────

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Define tools
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Input should be a valid Python math expression.
    Examples: '2 + 2', '10 * 5 / 2', '(100 - 20) * 3'"""
    try:
        result = eval(expression)  # In production, use a safe math library
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def reverse_string(text: str) -> str:
    """Reverse a string. Useful when the user asks to reverse or flip text."""
    return text[::-1]

@tool
def count_characters(text: str) -> dict:
    """Count characters, words, and sentences in a text."""
    import re
    return {
        "characters": len(text),
        "words": len(text.split()),
        "sentences": len(re.split(r'[.!?]+', text.strip()))
    }

agent_tools = [calculator, get_current_time, reverse_string, count_characters]

# Agent prompt — must include agent_scratchpad for the agent's thinking
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant with access to tools.
Use tools when needed to answer questions accurately.
Always show your work and reasoning."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # REQUIRED for agents
])

# Create the agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=agent_tools,
    prompt=agent_prompt
)

# AgentExecutor runs the think → act → observe loop
agent_executor = AgentExecutor(
    agent=agent,
    tools=agent_tools,
    verbose=True,     # shows the agent's thinking process
    max_iterations=5  # prevent infinite loops
)

# Test the agent
questions = [
    "What is 15% of 850 plus 42?",
    "What time is it right now?",
    "Reverse this text: 'Hello World' and tell me how many characters the result has",
]

for question in questions:
    print(f"\n{'='*50}")
    print(f"Question: {question}")
    result = agent_executor.invoke({"input": question})
    print(f"Final Answer: {result['output']}")


# ─────────────────────────────────────────
# 5. REAL-WORLD TOOLS — Web Search + Python REPL
# ─────────────────────────────────────────

from langchain_community.tools import DuckDuckGoSearchRun

# DuckDuckGo search tool (free, no API key)
search_tool = DuckDuckGoSearchRun()

# Test it
result = search_tool.invoke("LangChain latest version 2024")
print("Search result:", result[:500])


# Python code execution tool
from langchain_experimental.tools import PythonREPLTool

python_tool = PythonREPLTool()
result = python_tool.invoke("import math; print(math.factorial(10))")
print("Python result:", result)  # 3628800


# ─────────────────────────────────────────
# 6. AGENT WITH MEMORY
# ─────────────────────────────────────────

from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

agent_prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with tools. Use tools when needed."),
    MessagesPlaceholder(variable_name="chat_history"),  # conversation history
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent_with_history = create_tool_calling_agent(llm, agent_tools, agent_prompt_with_history)
executor_with_history = AgentExecutor(agent=agent_with_history, tools=agent_tools, verbose=False)

session_histories = {}

def get_history(session_id: str):
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

agent_with_memory = RunnableWithMessageHistory(
    executor_with_history,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

config = {"configurable": {"session_id": "user_123"}}

r1 = agent_with_memory.invoke({"input": "Calculate 25 * 4"}, config=config)
print("Turn 1:", r1["output"])

r2 = agent_with_memory.invoke({"input": "Now add 50 to that result"}, config=config)
print("Turn 2:", r2["output"])  # Agent remembers 100 from previous turn


# ─────────────────────────────────────────
# 7. CUSTOM TOOL — Calling an External API
# ─────────────────────────────────────────

from langchain_core.tools import tool
import json

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Use when user asks about weather."""
    # In real code, call a weather API like OpenWeatherMap
    # Mock response:
    weather_data = {
        "city": city,
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "45%",
        "wind": "10 km/h"
    }
    return json.dumps(weather_data)

@tool
def search_database(query: str, table: str) -> str:
    """Search the database for records. Use for finding user data, orders, products.
    Args:
        query: What to search for
        table: Which table (users, orders, products)
    """
    # In real code: run a DB query
    return f"Found 3 records matching '{query}' in table '{table}'"

# Combine all tools into a powerful agent
all_tools = [calculator, get_current_time, get_weather, search_database, web_search]

powerful_executor = AgentExecutor(
    agent=create_tool_calling_agent(llm, all_tools, agent_prompt),
    tools=all_tools,
    verbose=True
)

result = powerful_executor.invoke({
    "input": "What's the weather in London and calculate how many days are in 3 months?"
})
print(result["output"])


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
Tools:
  - Python functions decorated with @tool
  - The docstring is the description (LLM reads this to decide when to use it)
  - Called by the LLM, executed by your code

Agent loop:
  1. LLM reads user question + available tools
  2. LLM decides which tool to call and with what args
  3. Your code executes the tool
  4. Result is fed back to LLM
  5. LLM decides: done? or need another tool?
  6. Loop until answer is found

Key classes:
  @tool                      → create a tool from a function
  llm.bind_tools(tools)      → make LLM aware of tools
  create_tool_calling_agent  → create agent with tool calling
  AgentExecutor              → runs the agent loop

Next: LangGraph — build stateful multi-step AI workflows
"""
