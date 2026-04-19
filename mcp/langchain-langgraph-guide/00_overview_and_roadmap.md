# LangChain & LangGraph — Complete Learning Roadmap

## Who This Guide Is For
Frontend developer with backend knowledge who wants to enter AI engineering.
You already know: APIs, async, state management, component composition.
That knowledge maps DIRECTLY to LangChain and LangGraph concepts.

---

## Your Advantage as a Frontend/Backend Dev

| What You Know | AI Equivalent |
|---------------|--------------|
| fetch() / REST API | LLM API calls |
| Redux / Zustand state | LangGraph State |
| .filter().map() chaining | LCEL chain with pipe operator |
| React components | LangChain Runnables |
| XState / state machines | LangGraph nodes & edges |
| localStorage / DB | Vector Store / Memory |
| SSE / WebSockets streaming | LLM token streaming |

---

## 10-Week Learning Roadmap

```
Week 1  → Python fundamentals for AI (TypedDict, Pydantic, async)
          → Call LLM API directly (no framework)

Week 2  → LangChain: Models, Prompts, LCEL chains, Output parsers

Week 3  → LangChain: RAG (loaders, splitters, embeddings, vector store)

Week 4  → LangChain: Tools + basic Agents

Week 5  → LangGraph: StateGraph, nodes, edges, basic chatbot

Week 6  → LangGraph: Conditional edges, ReAct agent with tools

Week 7  → LangGraph: Multi-agent, Human-in-the-loop

Week 8  → LangSmith tracing, streaming, structured output

Week 9  → Build a full project (RAG + Agent + UI)

Week 10 → Deploy, optimize, measure
```

---

## Folder Structure of This Guide

```
00_overview_and_roadmap.md          ← You are here
01_python_fundamentals_for_ai.py    ← Python you need before anything
02_llm_api_basics.py                ← Talk to LLM without framework
03_langchain_models_prompts.py      ← LangChain core: models & prompts
04_langchain_chains_lcel.py         ← Chaining with pipe operator
05_langchain_output_parsers.py      ← Parse LLM output into structured data
06_langchain_memory.py              ← Give LLM conversation memory
07_langchain_rag_complete.py        ← RAG: load PDF, embed, retrieve, answer
08_langchain_tools_agents.py        ← Tools + Agents
09_langgraph_basics.py              ← LangGraph: state, nodes, edges
10_langgraph_conditional_edges.py   ← Branching logic in graphs
11_langgraph_react_agent.py         ← ReAct agent in LangGraph
12_langgraph_multi_agent.py         ← Multiple agents working together
13_langgraph_human_in_loop.py       ← Pause graph for human approval
14_langsmith_tracing.py             ← Debug and trace LLM calls
15_streaming_and_structured_output.py ← Stream tokens, force JSON output
16_full_project_rag_agent.py        ← Complete project putting it all together
```

---

## Key Principle
Build after EVERY file. Don't just read.
Pattern: Read → Copy → Modify → Break → Fix → Add feature
