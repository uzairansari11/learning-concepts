"""
LANGGRAPH CONDITIONAL EDGES — Branching Logic
==============================================
Conditional edges let the graph take DIFFERENT paths based on:
  - State values
  - LLM decisions
  - Business logic

Like an if/else or switch statement, but for your entire workflow.

Install: pip install langgraph langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Literal, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Conditional Edge
  - An edge where the next node depends on a function's return value.
  - add_conditional_edges(source, routing_function, mapping)

Routing Function
  - A Python function that looks at the state and returns a string.
  - The string is used to look up which node to go to next.
  - Like a switch statement that returns a route name.

Mapping (path_map)
  - Dict that maps routing function return values → node names.
  - Example: {"continue": "node_a", "stop": END}

Literal type hint
  - Tells Python (and LangGraph) the exact string values your router can return.
  - Literal["continue", "stop"] means it can only return one of those two.
"""

# ─────────────────────────────────────────
# 1. BASIC CONDITIONAL EDGE — Route by State Value
# ─────────────────────────────────────────

class ReviewState(TypedDict):
    text: str
    sentiment: str      # "positive" or "negative"
    response: str

def analyze_sentiment(state: ReviewState) -> dict:
    """Classify the sentiment of the text."""
    prompt = f"""Classify the sentiment of this text as exactly one word: positive OR negative.
Text: {state['text']}
Return only: positive or negative"""
    response = llm.invoke(prompt)
    return {"sentiment": response.content.strip().lower()}

def handle_positive(state: ReviewState) -> dict:
    """Handle positive reviews."""
    return {"response": f"Thank you for your positive feedback! We're glad you enjoyed it."}

def handle_negative(state: ReviewState) -> dict:
    """Handle negative reviews."""
    return {"response": f"We're sorry to hear that. A support agent will contact you shortly."}

# ROUTING FUNCTION — reads state, returns the next node name
def route_by_sentiment(state: ReviewState) -> Literal["positive_handler", "negative_handler"]:
    if state["sentiment"] == "positive":
        return "positive_handler"
    else:
        return "negative_handler"

# Build graph
graph = StateGraph(ReviewState)
graph.add_node("analyze", analyze_sentiment)
graph.add_node("positive_handler", handle_positive)
graph.add_node("negative_handler", handle_negative)

graph.add_edge(START, "analyze")

# Conditional edge: after "analyze", call route_by_sentiment() to decide next node
graph.add_conditional_edges(
    "analyze",                # source node
    route_by_sentiment,       # routing function
    # optional explicit mapping (can be omitted if function returns exact node names)
    {
        "positive_handler": "positive_handler",
        "negative_handler": "negative_handler",
    }
)

graph.add_edge("positive_handler", END)
graph.add_edge("negative_handler", END)

app = graph.compile()

# Test with different inputs
reviews = [
    "This product is amazing! Best purchase I've ever made.",
    "Terrible quality. Broke after one day. Very disappointed.",
]

for review in reviews:
    result = app.invoke({"text": review, "sentiment": "", "response": ""})
    print(f"Review: {review[:50]}...")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Response: {result['response']}\n")


# ─────────────────────────────────────────
# 2. LLM-DRIVEN ROUTING — LLM Decides the Path
# ─────────────────────────────────────────
"""
The LLM reads the user's intent and decides which specialized node to route to.
This is the "supervisor" pattern used in multi-agent systems.
"""

from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    intent: Literal["technical", "billing", "general"] = Field(
        description="The category of the user's question"
    )
    confidence: float = Field(description="Confidence score 0-1")

class SupportState(TypedDict):
    question: str
    intent: str
    answer: str

def classify_intent(state: SupportState) -> dict:
    """LLM classifies the user's question intent."""
    classifier = llm.with_structured_output(IntentClassification)
    result = classifier.invoke(
        f"Classify this customer support question:\n{state['question']}"
    )
    return {"intent": result.intent}

def technical_support(state: SupportState) -> dict:
    response = llm.invoke(
        f"You are a technical support expert. Answer: {state['question']}"
    )
    return {"answer": f"[TECH SUPPORT] {response.content}"}

def billing_support(state: SupportState) -> dict:
    response = llm.invoke(
        f"You are a billing specialist. Answer: {state['question']}"
    )
    return {"answer": f"[BILLING] {response.content}"}

def general_support(state: SupportState) -> dict:
    response = llm.invoke(
        f"You are a helpful support agent. Answer: {state['question']}"
    )
    return {"answer": f"[GENERAL] {response.content}"}

def route_by_intent(state: SupportState) -> str:
    intent_map = {
        "technical": "technical_support",
        "billing": "billing_support",
        "general": "general_support",
    }
    return intent_map.get(state["intent"], "general_support")

support_graph = StateGraph(SupportState)
support_graph.add_node("classify", classify_intent)
support_graph.add_node("technical_support", technical_support)
support_graph.add_node("billing_support", billing_support)
support_graph.add_node("general_support", general_support)

support_graph.add_edge(START, "classify")
support_graph.add_conditional_edges("classify", route_by_intent)
support_graph.add_edge("technical_support", END)
support_graph.add_edge("billing_support", END)
support_graph.add_edge("general_support", END)

support_app = support_graph.compile()

questions = [
    "My API key is not working. I get a 401 error.",
    "I was charged twice this month. Can you refund?",
    "What are your business hours?",
]

for q in questions:
    result = support_app.invoke({"question": q, "intent": "", "answer": ""})
    print(f"Q: {q}")
    print(f"Intent: {result['intent']}")
    print(f"A: {result['answer'][:100]}...\n")


# ─────────────────────────────────────────
# 3. LOOPING — Graph That Runs Until Condition Met
# ─────────────────────────────────────────
"""
LangGraph supports CYCLES (loops). Unlike LangChain chains which are linear,
graphs can loop back to earlier nodes.

Use case: retry until quality threshold met, iterative refinement, agent loops.
"""

class WritingState(TypedDict):
    topic: str
    draft: str
    feedback: str
    iteration: int
    approved: bool

def write_draft(state: WritingState) -> dict:
    """Write or revise a draft."""
    if state["iteration"] == 0:
        prompt = f"Write a 3-sentence article introduction about: {state['topic']}"
    else:
        prompt = f"""Revise this draft based on feedback:
Draft: {state['draft']}
Feedback: {state['feedback']}
Write improved version:"""

    response = llm.invoke(prompt)
    return {
        "draft": response.content,
        "iteration": state["iteration"] + 1
    }

def review_draft(state: WritingState) -> dict:
    """Review the draft and decide if it's good enough."""
    from pydantic import BaseModel

    class Review(BaseModel):
        approved: bool = Field(description="Is the draft good enough to publish?")
        feedback: str = Field(description="Specific feedback for improvement")

    reviewer = llm.with_structured_output(Review)
    result = reviewer.invoke(
        f"Review this draft for quality and clarity:\n{state['draft']}\n\nIs it ready to publish?"
    )
    return {"approved": result.approved, "feedback": result.feedback}

def should_continue_writing(state: WritingState) -> Literal["write", "done"]:
    """Route: if not approved AND under max iterations, write again."""
    if state["approved"] or state["iteration"] >= 3:  # max 3 iterations
        return "done"
    return "write"

writing_graph = StateGraph(WritingState)
writing_graph.add_node("write", write_draft)
writing_graph.add_node("review", review_draft)

writing_graph.add_edge(START, "write")
writing_graph.add_edge("write", "review")
writing_graph.add_conditional_edges(
    "review",
    should_continue_writing,
    {"write": "write", "done": END}  # "write" loops back!
)

writing_app = writing_graph.compile()

result = writing_app.invoke({
    "topic": "Why Python is great for AI development",
    "draft": "",
    "feedback": "",
    "iteration": 0,
    "approved": False
})

print(f"Final draft (after {result['iteration']} iterations):")
print(result["draft"])
print(f"Approved: {result['approved']}")


# ─────────────────────────────────────────
# 4. MULTIPLE CONDITIONAL EXITS — Fan-out Routing
# ─────────────────────────────────────────
"""
A node can route to multiple different destinations based on complex logic.
"""

class CodeState(TypedDict):
    code: str
    language: str
    has_syntax_error: bool
    has_security_issue: bool
    has_performance_issue: bool
    report: str

def analyze_code(state: CodeState) -> dict:
    """Analyze code for different types of issues."""
    from pydantic import BaseModel

    class CodeAnalysis(BaseModel):
        language: str
        has_syntax_error: bool
        has_security_issue: bool
        has_performance_issue: bool

    analyzer = llm.with_structured_output(CodeAnalysis)
    result = analyzer.invoke(f"Analyze this code for issues:\n{state['code']}")

    return {
        "language": result.language,
        "has_syntax_error": result.has_syntax_error,
        "has_security_issue": result.has_security_issue,
        "has_performance_issue": result.has_performance_issue,
    }

def fix_syntax(state: CodeState) -> dict:
    response = llm.invoke(f"Fix the syntax errors in:\n{state['code']}")
    return {"report": f"Syntax Fixed:\n{response.content}"}

def fix_security(state: CodeState) -> dict:
    response = llm.invoke(f"Fix the security vulnerabilities in:\n{state['code']}")
    return {"report": f"Security Fixed:\n{response.content}"}

def optimize_performance(state: CodeState) -> dict:
    response = llm.invoke(f"Optimize the performance of:\n{state['code']}")
    return {"report": f"Optimized:\n{response.content}"}

def code_is_clean(state: CodeState) -> dict:
    return {"report": "Code analysis complete. No critical issues found."}

def route_code_issues(state: CodeState) -> str:
    """Priority: syntax > security > performance > clean."""
    if state["has_syntax_error"]:
        return "fix_syntax"
    elif state["has_security_issue"]:
        return "fix_security"
    elif state["has_performance_issue"]:
        return "optimize_performance"
    return "code_is_clean"

code_graph = StateGraph(CodeState)
code_graph.add_node("analyze", analyze_code)
code_graph.add_node("fix_syntax", fix_syntax)
code_graph.add_node("fix_security", fix_security)
code_graph.add_node("optimize_performance", optimize_performance)
code_graph.add_node("code_is_clean", code_is_clean)

code_graph.add_edge(START, "analyze")
code_graph.add_conditional_edges("analyze", route_code_issues)
for node in ["fix_syntax", "fix_security", "optimize_performance", "code_is_clean"]:
    code_graph.add_edge(node, END)

code_app = code_graph.compile()

bad_code = """
def login(user, password):
    query = "SELECT * FROM users WHERE user='" + user + "' AND pass='" + password + "'"
    return db.execute(query)
"""

result = code_app.invoke({
    "code": bad_code, "language": "", "report": "",
    "has_syntax_error": False, "has_security_issue": False, "has_performance_issue": False
})
print(result["report"])


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
Conditional edges = if/else for your graph.

Pattern:
  1. Define routing function: reads state → returns string (node name)
  2. graph.add_conditional_edges(source, routing_fn, optional_mapping)
  3. The returned string maps to the next node

Use cases:
  - Route by sentiment, intent, language, user role
  - Retry/loop until quality threshold (iteration loops)
  - Error handling (success → next step, error → retry node)
  - Multi-path workflows (A → [B or C or D] based on LLM decision)

Next: ReAct Agent in LangGraph — the most important agent pattern
"""
