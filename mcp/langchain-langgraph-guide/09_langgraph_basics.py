"""
LANGGRAPH BASICS — Stateful AI Workflows
=========================================
LangGraph models AI workflows as a GRAPH (like a flowchart).
Each step is a NODE. Connections between steps are EDGES.
All steps share STATE — a dict that flows through the entire graph.

Your Mental Model:
  React/Redux:   State → Action → Reducer → New State → UI updates
  LangGraph:     State → Node  → New State → Next Node → ...

Install: pip install langgraph langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Graph
  - The entire workflow definition. Like a flowchart blueprint.
  - You define nodes + edges, then compile() it to make it runnable.

Node
  - A single step in the workflow. A Python function.
  - Takes State as input, returns partial State update as output.
  - Like a Redux reducer for one specific action.

Edge
  - Connection between two nodes. Defines "what runs after what".
  - Simple edge: always go from Node A → Node B.
  - Conditional edge: go to A or B depending on state/logic.

State
  - Shared data dict that all nodes can read and write.
  - Flows through the entire graph.
  - Like a Redux store but for the whole workflow.
  - Defined using TypedDict.

StateGraph
  - The main class for building graphs with shared state.

START
  - The entry point of the graph. Graph execution begins here.

END
  - The exit point. When a node goes to END, the graph stops.

Compile
  - graph.compile() → creates a runnable app from the graph definition.
  - Like building/bundling your code — you do it once, then run many times.

Checkpointer
  - Saves state between graph runs (persistence).
  - Enables: pause/resume, human-in-the-loop, debugging.
  - Like a save point in a video game.

MemorySaver
  - Simple in-memory checkpointer (for development).
  - Use Redis/Postgres checkpointer in production.
"""

# ─────────────────────────────────────────
# 1. HELLO WORLD — Simplest Possible Graph
# ─────────────────────────────────────────

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# STEP 1: Define State — the data shape shared by all nodes
class SimpleState(TypedDict):
    message: str
    result: str

# STEP 2: Define Nodes — functions that transform state
def greet_node(state: SimpleState) -> dict:
    """Node that creates a greeting."""
    name = state["message"]
    greeting = f"Hello, {name}! Welcome to LangGraph."
    return {"result": greeting}  # return only the fields you're updating

def shout_node(state: SimpleState) -> dict:
    """Node that makes the result uppercase."""
    return {"result": state["result"].upper()}

# STEP 3: Build the Graph
graph = StateGraph(SimpleState)

# Add nodes to the graph
graph.add_node("greet", greet_node)
graph.add_node("shout", shout_node)

# Add edges (define the flow)
graph.add_edge(START, "greet")   # START → greet
graph.add_edge("greet", "shout") # greet → shout
graph.add_edge("shout", END)     # shout → END

# STEP 4: Compile the graph
app = graph.compile()

# STEP 5: Run it!
result = app.invoke({"message": "Uzair", "result": ""})
print(result)
# {'message': 'Uzair', 'result': 'HELLO, UZAIR! WELCOME TO LANGGRAPH.'}

# You can also stream the state after each node
for step in app.stream({"message": "AI Engineer", "result": ""}):
    print("Step:", step)


# ─────────────────────────────────────────
# 2. CHATBOT GRAPH — LLM in a Loop
# ─────────────────────────────────────────
"""
The most fundamental LangGraph pattern: a chatbot that runs in a loop.
User input → LLM node → back to user input.
"""

from typing import Annotated
from langgraph.graph.message import add_messages

# Special State for conversations
# add_messages tells LangGraph to APPEND to messages (not replace)
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # list of HumanMessage/AIMessage

def chatbot_node(state: ChatState) -> dict:
    """Call the LLM with the current conversation history."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}  # add AI response to messages list

# Build chatbot graph
chatbot_graph = StateGraph(ChatState)
chatbot_graph.add_node("chatbot", chatbot_node)
chatbot_graph.add_edge(START, "chatbot")
chatbot_graph.add_edge("chatbot", END)

chatbot_app = chatbot_graph.compile()

# Run a conversation
result = chatbot_app.invoke({
    "messages": [HumanMessage(content="What is LangGraph in one sentence?")]
})
print("Chatbot:", result["messages"][-1].content)

# Multi-turn conversation
conversation = {"messages": []}

def chat(user_input: str):
    conversation["messages"].append(HumanMessage(content=user_input))
    result = chatbot_app.invoke(conversation)
    conversation["messages"] = result["messages"]
    return result["messages"][-1].content

print(chat("My name is Uzair and I am a frontend developer."))
print(chat("What is my name and background?"))


# ─────────────────────────────────────────
# 3. STATEFUL GRAPH — Multiple Fields in State
# ─────────────────────────────────────────

from typing import TypedDict, Optional

class WritingState(TypedDict):
    topic: str
    outline: Optional[str]
    draft: Optional[str]
    final: Optional[str]
    word_count: int

def create_outline_node(state: WritingState) -> dict:
    """Generate an outline for the topic."""
    prompt = f"Create a 3-point outline for an article about: {state['topic']}"
    response = llm.invoke(prompt)
    return {"outline": response.content}

def write_draft_node(state: WritingState) -> dict:
    """Write a draft based on the outline."""
    prompt = f"""Topic: {state['topic']}
Outline: {state['outline']}

Write a short draft article (100 words) following this outline."""
    response = llm.invoke(prompt)
    return {"draft": response.content}

def finalize_node(state: WritingState) -> dict:
    """Polish the draft."""
    prompt = f"Polish and improve this article draft:\n{state['draft']}"
    response = llm.invoke(prompt)
    return {
        "final": response.content,
        "word_count": len(response.content.split())
    }

writing_graph = StateGraph(WritingState)
writing_graph.add_node("outline", create_outline_node)
writing_graph.add_node("draft", write_draft_node)
writing_graph.add_node("finalize", finalize_node)

writing_graph.add_edge(START, "outline")
writing_graph.add_edge("outline", "draft")
writing_graph.add_edge("draft", "finalize")
writing_graph.add_edge("finalize", END)

writing_app = writing_graph.compile()

result = writing_app.invoke({
    "topic": "Why frontend developers should learn AI",
    "outline": None,
    "draft": None,
    "final": None,
    "word_count": 0
})

print("Final Article:")
print(result["final"])
print(f"Word count: {result['word_count']}")


# ─────────────────────────────────────────
# 4. VISUALIZING THE GRAPH
# ─────────────────────────────────────────

# See the graph structure
print(writing_app.get_graph().draw_ascii())

# Or get Mermaid diagram (paste into mermaid.live)
print(writing_app.get_graph().draw_mermaid())


# ─────────────────────────────────────────
# 5. STREAMING — See Each Node's Output
# ─────────────────────────────────────────

print("\n--- Streaming node outputs ---")
for step in writing_app.stream({
    "topic": "LangGraph for beginners",
    "outline": None, "draft": None, "final": None, "word_count": 0
}):
    # step = {"node_name": updated_state}
    node_name = list(step.keys())[0]
    print(f"\n✓ Node '{node_name}' completed")

    if node_name == "outline":
        print("Outline:", step[node_name]["outline"][:100], "...")
    elif node_name == "draft":
        print("Draft:", step[node_name]["draft"][:100], "...")
    elif node_name == "finalize":
        print("Final words:", step[node_name]["word_count"])


# ─────────────────────────────────────────
# 6. PERSISTENCE — Save State Between Runs
# ─────────────────────────────────────────

from langgraph.checkpoint.memory import MemorySaver

# Add a checkpointer — saves state after each node
checkpointer = MemorySaver()

chatbot_graph_persistent = StateGraph(ChatState)
chatbot_graph_persistent.add_node("chatbot", chatbot_node)
chatbot_graph_persistent.add_edge(START, "chatbot")
chatbot_graph_persistent.add_edge("chatbot", END)

# Compile WITH checkpointer
persistent_app = chatbot_graph_persistent.compile(checkpointer=checkpointer)

# thread_id = unique ID for this conversation thread
config = {"configurable": {"thread_id": "thread_001"}}

# First run
result1 = persistent_app.invoke(
    {"messages": [HumanMessage(content="My name is Uzair.")]},
    config=config
)
print("Run 1:", result1["messages"][-1].content)

# Second run — state is automatically loaded from checkpoint!
result2 = persistent_app.invoke(
    {"messages": [HumanMessage(content="What is my name?")]},
    config=config
)
print("Run 2:", result2["messages"][-1].content)  # Knows the name!

# Inspect saved state
state_snapshot = persistent_app.get_state(config)
print("\nSaved state messages count:", len(state_snapshot.values["messages"]))


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
LangGraph = State Machine for AI workflows.

Core concepts:
  State      → TypedDict with all shared data
  Node       → function: State → dict (partial state update)
  Edge       → connection: "after node A, go to node B"
  StateGraph → builder object
  compile()  → creates runnable app

Key patterns:
  add_messages → Annotated[list, add_messages] for chat state (appends, not replaces)
  MemorySaver  → save state between runs (persistence)
  thread_id    → unique ID per conversation thread

Next: Conditional Edges — make the graph branch based on logic or LLM decisions
"""
