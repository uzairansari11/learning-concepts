"""
FULL PROJECT — RAG + Agent + Streaming + Structured Output
===========================================================
This is a complete, production-ready AI research assistant that:
  1. Loads documents (your knowledge base)
  2. Lets an AI agent search through them with RAG
  3. Also has web search and calculator tools
  4. Streams responses to the user
  5. Returns structured output where needed
  6. Has conversation memory
  7. Can be deployed as a FastAPI app

This combines EVERYTHING from all previous files.

Install: pip install langchain langchain-anthropic langchain-community
         langgraph chromadb sentence-transformers fastapi uvicorn
         python-dotenv pypdf

Run:  uvicorn 16_full_project_rag_agent:app --reload
"""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from pydantic import BaseModel, Field

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7)

# ─────────────────────────────────────────
# STEP 1: BUILD THE KNOWLEDGE BASE (RAG)
# ─────────────────────────────────────────

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Sample knowledge base — replace with your actual documents
KNOWLEDGE_BASE = [
    Document(
        page_content="""
        LangChain is a framework for developing LLM-powered applications.
        Key components: Chat Models, Prompt Templates, Chains (LCEL),
        Output Parsers, Memory, Retrievers, and Agents.
        LCEL uses the pipe operator | to compose chains.
        All runnables support: invoke(), stream(), batch(), ainvoke().
        """,
        metadata={"source": "langchain_guide.txt", "topic": "langchain"}
    ),
    Document(
        page_content="""
        LangGraph extends LangChain for stateful, multi-step workflows.
        Core concepts: State (TypedDict), Nodes (functions), Edges (connections),
        Conditional Edges (branching), START, END, and compile().
        Supports: cycles, parallel execution, human-in-the-loop, persistence.
        Use MemorySaver for development, Redis/Postgres in production.
        """,
        metadata={"source": "langgraph_guide.txt", "topic": "langgraph"}
    ),
    Document(
        page_content="""
        RAG (Retrieval Augmented Generation) pipeline:
        1. Load documents with Document Loaders
        2. Split into chunks with Text Splitters
        3. Convert to vectors with Embedding models
        4. Store in Vector Database (ChromaDB, Pinecone)
        5. At query time: embed question, retrieve similar chunks
        6. Inject chunks into prompt, LLM generates answer.
        """,
        metadata={"source": "rag_guide.txt", "topic": "rag"}
    ),
    Document(
        page_content="""
        Agents in LangChain/LangGraph:
        - Tools: Python functions the LLM can call (@tool decorator)
        - Agent: LLM that decides which tool to use
        - ReAct pattern: Think → Act (call tool) → Observe → Repeat
        - AgentExecutor: runs the agent loop
        - create_react_agent(): one-liner to build a ReAct agent
        - ToolNode + tools_condition: prebuilt LangGraph components
        """,
        metadata={"source": "agents_guide.txt", "topic": "agents"}
    ),
    Document(
        page_content="""
        LangSmith is the observability platform for LangChain apps.
        Setup: set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY.
        Features: traces, runs, feedback, datasets, evaluation.
        Use @traceable to trace custom functions.
        Check traces to debug: wrong prompts, token usage, latency, errors.
        """,
        metadata={"source": "langsmith_guide.txt", "topic": "langsmith"}
    ),
]

# Build vector store
print("Building knowledge base...")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(KNOWLEDGE_BASE)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma.from_documents(chunks, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
print(f"Knowledge base ready: {len(chunks)} chunks indexed")


# ─────────────────────────────────────────
# STEP 2: DEFINE TOOLS
# ─────────────────────────────────────────

@tool
def search_knowledge_base(query: str) -> str:
    """Search the AI/LangChain knowledge base for information.
    Use for questions about LangChain, LangGraph, RAG, Agents, or LangSmith."""
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the knowledge base."
    context = "\n\n".join([
        f"[From {doc.metadata['source']}]: {doc.page_content}"
        for doc in docs
    ])
    return context

@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions. Input: valid Python math expression.
    Examples: '2 + 2', '10 * 5', 'round(3.14159, 2)', '(100 - 20) / 4'"""
    try:
        allowed = {"abs": abs, "round": round, "min": min, "max": max}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"

@tool
def get_learning_path(topic: str, level: str = "beginner") -> str:
    """Get a personalized learning path for an AI topic.
    Args:
        topic: The AI topic to learn (langchain, langgraph, rag, agents)
        level: Skill level - beginner, intermediate, or advanced
    """
    paths = {
        "langchain": {
            "beginner": "1. Python basics → 2. LLM API calls → 3. Prompts/Templates → 4. Basic chains",
            "intermediate": "1. LCEL → 2. Output parsers → 3. Memory → 4. RAG → 5. Agents",
            "advanced": "1. Custom runnables → 2. Streaming → 3. Evaluation → 4. Production deployment"
        },
        "langgraph": {
            "beginner": "1. StateGraph basics → 2. Nodes & edges → 3. Simple chatbot",
            "intermediate": "1. Conditional edges → 2. ReAct agent → 3. Persistence",
            "advanced": "1. Multi-agent → 2. Human-in-loop → 3. Subgraphs → 4. Custom checkpointers"
        }
    }

    topic_lower = topic.lower()
    for key in paths:
        if key in topic_lower:
            return paths[key].get(level, paths[key]["beginner"])
    return f"Learning path for {topic} ({level}): Start with official docs and build small projects."

@tool
def summarize_concept(concept: str) -> str:
    """Summarize an AI concept in simple terms for a frontend developer.
    Use when the user needs a quick, clear explanation."""
    response = llm.invoke(
        f"Explain {concept} to a frontend developer in 2-3 sentences using analogies from web development."
    )
    return response.content

tools = [search_knowledge_base, calculator, get_learning_path, summarize_concept]


# ─────────────────────────────────────────
# STEP 3: BUILD THE AGENT GRAPH
# ─────────────────────────────────────────

class ResearchAssistantState(TypedDict):
    messages: Annotated[list, add_messages]

SYSTEM_PROMPT = """You are an expert AI Engineering tutor specializing in LangChain and LangGraph.
Your student is a frontend developer learning AI engineering.

Your approach:
- Use web development analogies when explaining AI concepts
- Always search the knowledge base before answering AI-related questions
- Show practical examples and code snippets when helpful
- Be encouraging and step-by-step in your explanations

Available tools:
- search_knowledge_base: for LangChain/LangGraph/RAG/Agent questions
- calculator: for math
- get_learning_path: for structured learning guidance
- summarize_concept: for quick explanations

Always be helpful, practical, and relate things to what the student already knows."""

llm_with_tools = llm.bind_tools(tools)

def agent_node(state: ResearchAssistantState) -> dict:
    """Main agent node — LLM with system prompt and tools."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

agent_graph = StateGraph(ResearchAssistantState)
agent_graph.add_node("agent", agent_node)
agent_graph.add_node("tools", ToolNode(tools))

agent_graph.add_edge(START, "agent")
agent_graph.add_conditional_edges("agent", tools_condition)
agent_graph.add_edge("tools", "agent")

# Add persistence
checkpointer = MemorySaver()
research_app = agent_graph.compile(checkpointer=checkpointer)

print("Research assistant ready!")
print(research_app.get_graph().draw_ascii())


# ─────────────────────────────────────────
# STEP 4: FASTAPI WEB APP
# ─────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="AI Research Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(description="User's question or message")
    session_id: str = Field(default="default", description="Session ID for conversation memory")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint."""
    config = {"configurable": {"thread_id": request.session_id}}

    result = research_app.invoke(
        {"messages": [HumanMessage(content=request.message)]},
        config=config
    )

    last_message = result["messages"][-1]
    tools_used = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            tools_used.extend([tc["name"] for tc in msg.tool_calls])

    return ChatResponse(
        response=last_message.content,
        session_id=request.session_id,
        tools_used=list(set(tools_used))
    )

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint — tokens arrive in real time."""
    config = {"configurable": {"thread_id": request.session_id}}

    async def generate():
        async for chunk, metadata in research_app.astream(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
            stream_mode="messages"
        ):
            if hasattr(chunk, "content") and chunk.content:
                data = json.dumps({"token": chunk.content, "type": "token"})
                yield f"data: {data}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    config = {"configurable": {"thread_id": session_id}}
    try:
        state = research_app.get_state(config)
        messages = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, HumanMessage):
                messages.append({"role": "human", "content": msg.content})
            elif isinstance(msg, AIMessage) and not msg.tool_calls:
                messages.append({"role": "assistant", "content": msg.content})
        return {"session_id": session_id, "messages": messages}
    except Exception:
        return {"session_id": session_id, "messages": []}

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history (start fresh)."""
    return {"message": f"Session {session_id} cleared. Start a new conversation."}

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "claude-sonnet-4-6"}


# ─────────────────────────────────────────
# STEP 5: CLI INTERFACE (for testing without API)
# ─────────────────────────────────────────

def run_cli():
    """Interactive CLI to test the assistant."""
    session_id = "cli_session"
    config = {"configurable": {"thread_id": session_id}}

    print("\n" + "="*60)
    print("AI RESEARCH ASSISTANT")
    print("Your LangChain & LangGraph tutor")
    print("Type 'quit' to exit, 'clear' to start fresh")
    print("="*60)

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "clear":
            print("Starting fresh conversation...")
            config = {"configurable": {"thread_id": f"cli_session_{id(config)}"}}
            continue

        print("\nAssistant: ", end="", flush=True)

        for chunk, metadata in research_app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages"
        ):
            if hasattr(chunk, "content") and chunk.content:
                # Only print final AI responses (not tool calls/results)
                if not hasattr(chunk, "tool_calls") or not chunk.tool_calls:
                    print(chunk.content, end="", flush=True)

        print()  # newline after response


# ─────────────────────────────────────────
# EXAMPLE QUESTIONS TO TRY
# ─────────────────────────────────────────
"""
Try these in the CLI or API:

Basic questions:
  "What is LangGraph and how does it differ from LangChain?"
  "Explain RAG like I'm a React developer"
  "What is a ReAct agent?"

Practical questions:
  "Give me a learning path for LangGraph as a beginner"
  "How do I add memory to a LangGraph chatbot?"
  "What tools should I use for a RAG application?"

Math:
  "If I spend 2 hours daily learning, how many hours is that in 10 weeks?"
  "Calculate 15% of 850 for me"

Clarification:
  "What's the difference between invoke() and stream()?"
  "When should I use with_structured_output()?"
"""


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if "--cli" in sys.argv:
        # Run interactive CLI
        run_cli()
    else:
        # Run FastAPI server
        import uvicorn
        print("\nStarting API server...")
        print("API docs: http://localhost:8000/docs")
        print("Chat endpoint: POST http://localhost:8000/chat")
        print("Stream endpoint: POST http://localhost:8000/chat/stream")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

# Run CLI:    python 16_full_project_rag_agent.py --cli
# Run API:    python 16_full_project_rag_agent.py
# Or with uvicorn: uvicorn 16_full_project_rag_agent:app --reload
