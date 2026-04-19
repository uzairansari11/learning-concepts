"""
LANGGRAPH HUMAN-IN-THE-LOOP
============================
Sometimes you want a HUMAN to review or approve before the AI continues.

Use cases:
  - Agent about to execute a sensitive action (delete files, send email, deploy code)
  - Approval workflow (manager approves AI-generated report before publishing)
  - Clarification (AI asks human for more info before proceeding)

LangGraph supports pausing execution and resuming after human input.

Install: pip install langgraph langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Interrupt
  - Pauses graph execution at a specific node.
  - The graph saves its state (using checkpointer) and waits.
  - Human provides input, then graph resumes from where it paused.
  - Like a debugger breakpoint, but for AI workflows.

interrupt() function
  - Call inside a node to pause execution.
  - interrupt("What is your approval decision?")
  - The value passed in is shown to the human.
  - Returns the human's response when execution resumes.

Command
  - Used to resume graph execution and optionally update state.
  - Command(resume="human's answer")  → resume with human input
  - Command(goto="node_name")         → redirect to a different node

Checkpointer (REQUIRED for Human-in-the-Loop)
  - Without a checkpointer, state is lost when graph pauses.
  - MemorySaver → in-memory (dev only)
  - Use Redis/Postgres in production

thread_id
  - Unique ID for each workflow instance.
  - Allows pausing/resuming a specific conversation.

graph.get_state(config)
  - Get current state of a paused graph.
  - Returns StateSnapshot with current values + next nodes to run.

graph.invoke(Command(resume=...), config)
  - Resume a paused graph with human input.
"""

# ─────────────────────────────────────────
# 1. BASIC INTERRUPT — Simple Approval Flow
# ─────────────────────────────────────────

class ApprovalState(TypedDict):
    task: str
    ai_output: str
    human_decision: str
    final_result: str

def generate_content(state: ApprovalState) -> dict:
    """AI generates content."""
    response = llm.invoke(f"Write a short email about: {state['task']}")
    return {"ai_output": response.content}

def human_review_node(state: ApprovalState) -> dict:
    """PAUSE HERE and wait for human to review."""
    print(f"\n{'='*50}")
    print("AI GENERATED THIS EMAIL:")
    print(state["ai_output"])
    print(f"{'='*50}")

    # interrupt() pauses the graph and returns human input when resumed
    human_input = interrupt(
        f"Review this email. Type 'approve' to send, or type feedback to revise:"
    )
    return {"human_decision": human_input}

def process_decision(state: ApprovalState) -> dict:
    """Handle the human's decision."""
    decision = state["human_decision"].lower().strip()

    if decision == "approve":
        return {"final_result": f"EMAIL SENT:\n{state['ai_output']}"}
    else:
        # Human gave feedback — revise
        revised = llm.invoke(
            f"Revise this email based on feedback:\nEmail: {state['ai_output']}\nFeedback: {state['human_decision']}"
        )
        return {"final_result": f"REVISED EMAIL SENT:\n{revised.content}"}

approval_graph = StateGraph(ApprovalState)
approval_graph.add_node("generate", generate_content)
approval_graph.add_node("human_review", human_review_node)
approval_graph.add_node("process", process_decision)

approval_graph.add_edge(START, "generate")
approval_graph.add_edge("generate", "human_review")
approval_graph.add_edge("human_review", "process")
approval_graph.add_edge("process", END)

# MUST have checkpointer for interrupt to work
checkpointer = MemorySaver()
approval_app = approval_graph.compile(checkpointer=checkpointer)

thread_config = {"configurable": {"thread_id": "approval_001"}}

# --- STEP 1: Start the graph (runs until interrupt) ---
print("Starting graph...")
result = approval_app.invoke(
    {"task": "schedule a team meeting for Friday", "ai_output": "", "human_decision": "", "final_result": ""},
    config=thread_config
)
# Graph pauses at human_review_node — result is the interrupt value
print("Graph paused. Waiting for human input...")

# Check state while paused
snapshot = approval_app.get_state(thread_config)
print(f"Next nodes to run: {snapshot.next}")
print(f"Interrupt value: {snapshot.tasks[0].interrupts[0].value if snapshot.tasks else 'None'}")

# --- STEP 2: Human provides input and graph resumes ---
human_response = "approve"  # In real app, this comes from UI

final = approval_app.invoke(
    Command(resume=human_response),  # resume with human input
    config=thread_config
)
print("\nFinal result:", final["final_result"])


# ─────────────────────────────────────────
# 2. INTERRUPT BEFORE TOOL EXECUTION — Safety Check
# ─────────────────────────────────────────
"""
Critical pattern: agent wants to execute a dangerous action.
Before running it, ask human "are you sure?".
"""

class SafeAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    pending_action: Optional[str]
    approved: bool

@tool
def delete_file(path: str) -> str:
    """Delete a file at the given path."""
    return f"File deleted: {path}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

@tool
def safe_search(query: str) -> str:
    """Search for information (safe, no approval needed)."""
    return f"Search results for {query}"

# Dangerous tools that need approval
DANGEROUS_TOOLS = {"delete_file", "send_email"}
ALL_TOOLS = [delete_file, send_email, safe_search]

llm_with_tools = llm.bind_tools(ALL_TOOLS)

def safe_agent_node(state: SafeAgentState) -> dict:
    """Agent decides what to do."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def safety_check_node(state: SafeAgentState) -> dict:
    """Check if the tool call needs human approval."""
    last_msg = state["messages"][-1]

    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        for tc in last_msg.tool_calls:
            if tc["name"] in DANGEROUS_TOOLS:
                # This action needs approval — interrupt!
                action_desc = f"Tool: {tc['name']}\nArgs: {tc['args']}"
                approval = interrupt(
                    f"APPROVAL REQUIRED\n{action_desc}\n\nType 'yes' to approve or 'no' to cancel:"
                )
                return {"pending_action": tc["name"], "approved": approval.lower() == "yes"}

    return {"pending_action": None, "approved": True}

def route_after_safety(state: SafeAgentState) -> str:
    """Route based on approval."""
    if state["pending_action"] and not state["approved"]:
        return "rejected"
    return "execute_tools"

def execute_tools_node(state: SafeAgentState) -> dict:
    """Execute approved tool calls."""
    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode(ALL_TOOLS)
    return tool_node.invoke(state)

def rejected_node(state: SafeAgentState) -> dict:
    """Handle rejected action."""
    return {"messages": [AIMessage(content="Action cancelled. The operation was not approved.")]}

safe_graph = StateGraph(SafeAgentState)
safe_graph.add_node("agent", safe_agent_node)
safe_graph.add_node("safety_check", safety_check_node)
safe_graph.add_node("execute_tools", execute_tools_node)
safe_graph.add_node("rejected", rejected_node)

safe_graph.add_edge(START, "agent")
safe_graph.add_edge("agent", "safety_check")
safe_graph.add_conditional_edges(
    "safety_check",
    route_after_safety,
    {"execute_tools": "execute_tools", "rejected": "rejected"}
)
safe_graph.add_edge("execute_tools", "agent")
safe_graph.add_edge("rejected", END)

safe_app = safe_graph.compile(checkpointer=MemorySaver())
safe_config = {"configurable": {"thread_id": "safe_001"}}

# Start — agent will decide to delete a file (triggers approval)
safe_app.invoke(
    {
        "messages": [HumanMessage(content="Delete the file /tmp/old_report.pdf")],
        "pending_action": None,
        "approved": False
    },
    config=safe_config
)

# Resume with approval
safe_app.invoke(Command(resume="yes"), config=safe_config)


# ─────────────────────────────────────────
# 3. MULTI-STEP APPROVAL WORKFLOW
# ─────────────────────────────────────────
"""
Real workflow: AI writes a blog post → human reviews → human edits → publish.
"""

class BlogWorkflowState(TypedDict):
    topic: str
    draft: str
    human_edits: str
    published: bool

def write_draft_node(state: BlogWorkflowState) -> dict:
    response = llm.invoke(f"Write a 150-word blog post about: {state['topic']}")
    return {"draft": response.content}

def editorial_review_node(state: BlogWorkflowState) -> dict:
    """Human reads draft and makes edits."""
    print("\n--- DRAFT FOR REVIEW ---")
    print(state["draft"])
    print("------------------------")

    human_edits = interrupt(
        "Review the draft above. Provide your edits, or type 'publish' to publish as-is:"
    )
    return {"human_edits": human_edits}

def publish_or_revise_node(state: BlogWorkflowState) -> dict:
    if state["human_edits"].lower() == "publish":
        final = state["draft"]
    else:
        # Incorporate human edits
        revised = llm.invoke(
            f"Incorporate these edits into the article:\nOriginal: {state['draft']}\nEdits: {state['human_edits']}"
        )
        final = revised.content

    print(f"\n✓ PUBLISHED:\n{final[:200]}...")
    return {"draft": final, "published": True}

blog_graph = StateGraph(BlogWorkflowState)
blog_graph.add_node("write", write_draft_node)
blog_graph.add_node("review", editorial_review_node)
blog_graph.add_node("publish", publish_or_revise_node)

blog_graph.add_edge(START, "write")
blog_graph.add_edge("write", "review")
blog_graph.add_edge("review", "publish")
blog_graph.add_edge("publish", END)

blog_app = blog_graph.compile(checkpointer=MemorySaver())
blog_config = {"configurable": {"thread_id": "blog_001"}}

# Phase 1: Write draft (runs until human review interrupt)
blog_app.invoke(
    {"topic": "How LangGraph changes AI development", "draft": "", "human_edits": "", "published": False},
    config=blog_config
)

# Phase 2: Human decides to publish as-is
blog_app.invoke(Command(resume="publish"), config=blog_config)


# ─────────────────────────────────────────
# 4. CONDITIONAL INTERRUPT — Only Pause When Needed
# ─────────────────────────────────────────

class ConditionalState(TypedDict):
    action_cost: float
    action_description: str
    result: str

def plan_action(state: ConditionalState) -> dict:
    return {
        "action_cost": 150.0,
        "action_description": "Purchase 10 API credits for $150"
    }

def conditional_approval(state: ConditionalState) -> dict:
    """Only interrupt if cost exceeds threshold."""
    APPROVAL_THRESHOLD = 100.0

    if state["action_cost"] > APPROVAL_THRESHOLD:
        # Need approval for expensive actions
        decision = interrupt(
            f"Action: {state['action_description']}\nCost: ${state['action_cost']}\nApprove? (yes/no):"
        )
        if decision.lower() != "yes":
            return {"result": "Action cancelled by user."}

    return {"result": f"Action completed: {state['action_description']}"}

conditional_graph = StateGraph(ConditionalState)
conditional_graph.add_node("plan", plan_action)
conditional_graph.add_node("approve", conditional_approval)
conditional_graph.add_edge(START, "plan")
conditional_graph.add_edge("plan", "approve")
conditional_graph.add_edge("approve", END)

cond_app = conditional_graph.compile(checkpointer=MemorySaver())
cond_config = {"configurable": {"thread_id": "cond_001"}}

# Start
cond_app.invoke(
    {"action_cost": 0, "action_description": "", "result": ""},
    config=cond_config
)

# Approve the action
final = cond_app.invoke(Command(resume="yes"), config=cond_config)
print("Result:", final["result"])


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
Human-in-the-Loop = pause graph, get human input, resume.

Key APIs:
  interrupt(message)          → pause + show message to human
  Command(resume=human_input) → resume with human's answer
  graph.get_state(config)     → see current state while paused
  MemorySaver checkpointer    → REQUIRED to save state during pause

Use cases:
  1. Approval workflows (expensive actions, sensitive operations)
  2. Content review (human edits AI drafts before publishing)
  3. Clarification (AI asks human for more info)
  4. Safety checks (verify before deleting/sending/deploying)

Pattern:
  1. Add checkpointer to compile()
  2. Call interrupt() inside a node to pause
  3. Human sees the interrupt value
  4. Human calls graph.invoke(Command(resume=answer), config)
  5. Graph continues from where it paused

Next: LangSmith — trace, debug, and monitor your AI applications
"""
