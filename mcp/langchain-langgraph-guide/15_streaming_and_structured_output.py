"""
STREAMING & STRUCTURED OUTPUT — Production Patterns
=====================================================
Two critical patterns for production AI apps:

1. STREAMING — Show tokens as they arrive (ChatGPT-like experience)
2. STRUCTURED OUTPUT — Force LLM to return valid JSON/typed data

As a frontend developer, streaming maps directly to SSE/WebSockets.
Structured output maps to API response schemas.

Install: pip install langchain langchain-anthropic fastapi uvicorn pydantic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7)

# ─────────────────────────────────────────
# PART 1: STREAMING
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# KEY STREAMING TERMS
# ─────────────────────────────────────────
"""
Token Streaming
  - LLM generates text token by token (not all at once).
  - Instead of waiting 5 seconds for a full response, you see words appear
    immediately — just like ChatGPT.

Stream vs Invoke:
  invoke()  → waits for COMPLETE response → returns full string
  stream()  → returns tokens ONE BY ONE as they're generated

AIMessageChunk
  - A partial AIMessage returned during streaming.
  - Has a .content field with the text fragment so far.
  - Multiple chunks combine to form the complete AIMessage.

astream()
  - Async version of stream(). Use in FastAPI, async code.

SSE (Server-Sent Events)
  - HTTP protocol for server → client streaming.
  - Used in web apps to push LLM tokens to the browser in real time.
  - FastAPI has native SSE support via StreamingResponse.

Streaming in LangGraph
  - stream_mode="messages" → stream tokens from LLM nodes
  - stream_mode="updates"  → stream state after each node completes
  - stream_mode="values"   → stream complete state after each step
"""

# ─────────────────────────────────────────
# 1. BASIC STREAMING — Print Tokens as They Arrive
# ─────────────────────────────────────────

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful writing assistant."),
    ("human", "Write a short poem about {topic}")
])

chain = prompt | llm | StrOutputParser()

print("=== Streaming Output ===")
print("Poem: ", end="")
for chunk in chain.stream({"topic": "learning to code"}):
    print(chunk, end="", flush=True)  # flush=True ensures immediate display
print("\n")


# ─────────────────────────────────────────
# 2. ASYNC STREAMING — For FastAPI / Async Code
# ─────────────────────────────────────────

import asyncio

async def stream_response_async(topic: str):
    """Async streaming — use in FastAPI endpoints."""
    async for chunk in chain.astream({"topic": topic}):
        yield chunk  # yield each token to the caller

async def demo_async_stream():
    print("=== Async Streaming ===")
    async for token in stream_response_async("artificial intelligence"):
        print(token, end="", flush=True)
    print()

asyncio.run(demo_async_stream())


# ─────────────────────────────────────────
# 3. FASTAPI STREAMING ENDPOINT — Real Web App
# ─────────────────────────────────────────

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/stream")
async def stream_endpoint(topic: str = "Python programming"):
    """
    Frontend calls: GET /stream?topic=Python
    Response streams tokens as they arrive.
    Frontend uses EventSource or fetch with ReadableStream.
    """
    async def generate():
        async for token in chain.astream({"topic": topic}):
            # SSE format: "data: <token>\n\n"
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"  # signal end of stream

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Frontend JavaScript to consume:
# const source = new EventSource('/stream?topic=Python');
# source.onmessage = (event) => {
#   if (event.data === '[DONE]') { source.close(); return; }
#   document.getElementById('output').textContent += event.data;
# };


# ─────────────────────────────────────────
# 4. STREAMING IN LANGGRAPH
# ─────────────────────────────────────────

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage

class StreamState(TypedDict):
    messages: Annotated[list, add_messages]

def chat_node(state: StreamState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

stream_graph = StateGraph(StreamState)
stream_graph.add_node("chat", chat_node)
stream_graph.add_edge(START, "chat")
stream_graph.add_edge("chat", END)
stream_app = stream_graph.compile()

# Stream mode: "messages" → get LLM tokens in real time
print("=== LangGraph Token Streaming ===")
for chunk, metadata in stream_app.stream(
    {"messages": [HumanMessage(content="Write 3 tips for learning Python")]},
    stream_mode="messages"   # ← enables token-level streaming
):
    if hasattr(chunk, "content") and chunk.content:
        print(chunk.content, end="", flush=True)
print()

# Stream mode: "updates" → get state after each node completes
print("\n=== LangGraph Node Updates ===")
for step in stream_app.stream(
    {"messages": [HumanMessage(content="Say hello")]},
    stream_mode="updates"    # ← state update per node
):
    node_name = list(step.keys())[0]
    print(f"Node '{node_name}' completed")


# ─────────────────────────────────────────
# PART 2: STRUCTURED OUTPUT
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# KEY STRUCTURED OUTPUT TERMS
# ─────────────────────────────────────────
"""
Structured Output
  - Forcing the LLM to return data in a specific shape (JSON, Pydantic model).
  - Essential for: data extraction, form filling, API responses, pipelines.

with_structured_output()
  - The BEST way to get structured output from an LLM.
  - Uses tool calling internally → more reliable than asking for JSON in text.
  - Returns a Pydantic model instance or dict (depending on what you pass).

Pydantic Model
  - Python class that defines the exact shape of output you want.
  - Fields have types, descriptions, and validations.
  - LLM reads the field descriptions to understand what to fill in.

Field(description=...)
  - CRITICAL: The description tells the LLM what each field means.
  - Write clear descriptions — the LLM uses them to fill the fields correctly.
  - Think of it like documentation for the LLM.

JSON Schema
  - Alternative to Pydantic — pass a dict schema if you prefer.
  - Less Pythonic but works the same way.

Streaming + Structured Output (JsonOutputParser)
  - You can stream structured output using JsonOutputParser.
  - Returns partial JSON objects as they stream in.
"""

# ─────────────────────────────────────────
# 5. with_structured_output — Basic Example
# ─────────────────────────────────────────

class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    rating: float = Field(description="Rating from 1.0 to 10.0")
    genre: str = Field(description="Primary genre (action, drama, comedy, etc.)")
    summary: str = Field(description="One sentence plot summary")
    recommended: bool = Field(description="Would you recommend this movie?")
    similar_movies: List[str] = Field(description="List of 2-3 similar movies")

structured_llm = llm.with_structured_output(MovieReview)

review = structured_llm.invoke(
    "Write a review for the movie 'The Matrix' (1999)"
)

print(f"Title: {review.title}")
print(f"Rating: {review.rating}/10")
print(f"Genre: {review.genre}")
print(f"Summary: {review.summary}")
print(f"Recommended: {review.recommended}")
print(f"Similar: {review.similar_movies}")
print(f"Type: {type(review)}")  # MovieReview — not a dict!


# ─────────────────────────────────────────
# 6. DATA EXTRACTION — Real Use Case
# ─────────────────────────────────────────

class Invoice(BaseModel):
    """Extract invoice details from text."""
    invoice_number: str = Field(description="Invoice number or ID")
    date: str = Field(description="Invoice date in YYYY-MM-DD format")
    vendor: str = Field(description="Name of the vendor/company")
    amount: float = Field(description="Total amount to pay in dollars")
    items: List[str] = Field(description="List of items/services listed on the invoice")
    due_date: Optional[str] = Field(description="Payment due date, if mentioned")
    is_overdue: bool = Field(description="Is the invoice past its due date?")

invoice_extractor = llm.with_structured_output(Invoice)

invoice_text = """
INVOICE #INV-2024-0892
Date: March 15, 2024
Due: April 15, 2024

From: Acme Cloud Services Ltd.

Services Provided:
- Cloud hosting (March 2024): $450.00
- SSL Certificate renewal: $99.00
- Support package (Professional): $200.00

TOTAL DUE: $749.00

Please remit payment within 30 days.
"""

extracted = invoice_extractor.invoke(
    f"Extract all invoice information from this document:\n{invoice_text}"
)

print(f"Invoice: {extracted.invoice_number}")
print(f"Vendor: {extracted.vendor}")
print(f"Amount: ${extracted.amount}")
print(f"Items: {extracted.items}")
print(f"Due: {extracted.due_date}")


# ─────────────────────────────────────────
# 7. COMPLEX NESTED STRUCTURES
# ─────────────────────────────────────────

class Address(BaseModel):
    street: str
    city: str
    country: str

class Contact(BaseModel):
    name: str = Field(description="Full name")
    email: Optional[str] = Field(description="Email address if provided")
    phone: Optional[str] = Field(description="Phone number if provided")
    address: Optional[Address] = Field(description="Physical address if provided")
    role: Literal["customer", "vendor", "employee", "partner"] = Field(
        description="Their relationship to the company"
    )

class MeetingNotes(BaseModel):
    title: str = Field(description="Meeting title or topic")
    date: str = Field(description="Meeting date")
    duration_minutes: int = Field(description="How long the meeting lasted in minutes")
    attendees: List[Contact] = Field(description="List of all meeting attendees")
    action_items: List[str] = Field(description="List of action items with assignee names")
    decisions_made: List[str] = Field(description="Key decisions made in the meeting")
    next_meeting_date: Optional[str] = Field(description="Date of next scheduled meeting")

meeting_extractor = llm.with_structured_output(MeetingNotes)

meeting_text = """
Product Review Meeting - April 20, 2024 (45 minutes)

Attendees:
- Uzair (Frontend Developer, uzair@company.com) - +92-300-1234567
- Sarah (Product Manager, sarah@company.com)
- Mike (Backend Developer)

Discussion:
We reviewed the AI integration timeline. The team decided to use LangGraph for the
agent workflow and LangSmith for monitoring. We agreed to launch in beta by May 15.

Action Items:
- Uzair: Complete UI streaming component by April 25
- Sarah: Write product spec for approval workflow by April 22
- Mike: Set up LangSmith integration by April 23

Next meeting: April 27, 2024
"""

notes = meeting_extractor.invoke(
    f"Extract all information from these meeting notes:\n{meeting_text}"
)

print(f"\nMeeting: {notes.title}")
print(f"Duration: {notes.duration_minutes} minutes")
print(f"Attendees: {[a.name for a in notes.attendees]}")
print(f"Action items: {len(notes.action_items)}")
for item in notes.action_items:
    print(f"  - {item}")


# ─────────────────────────────────────────
# 8. STREAMING + STRUCTURED OUTPUT
# ─────────────────────────────────────────

from langchain_core.output_parsers import JsonOutputParser

# JsonOutputParser allows streaming while building JSON incrementally
json_parser = JsonOutputParser(pydantic_object=MovieReview)

streaming_structured_chain = (
    ChatPromptTemplate.from_template("Review the movie {movie}. Return JSON.{format_instructions}")
    | llm
    | json_parser
)

print("\n=== Streaming Structured Output ===")
for partial_result in streaming_structured_chain.stream({
    "movie": "Inception",
    "format_instructions": json_parser.get_format_instructions()
}):
    # Shows partial JSON being built up as tokens arrive
    print(f"\rBuilding: {str(partial_result)[:80]}...", end="", flush=True)

print("\nDone!")


# ─────────────────────────────────────────
# 9. VALIDATION AND ERROR HANDLING
# ─────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator

class StrictOutput(BaseModel):
    score: int = Field(description="Score between 1 and 10", ge=1, le=10)
    category: Literal["excellent", "good", "average", "poor"]
    explanation: str = Field(description="2-3 sentence explanation", min_length=20)

    @field_validator("explanation")
    @classmethod
    def explanation_must_be_detailed(cls, v):
        if len(v.split()) < 5:
            raise ValueError("Explanation must be at least 5 words")
        return v

strict_llm = llm.with_structured_output(StrictOutput)

# Retry on validation failure
from langchain_core.runnables import RunnableRetry

strict_chain = strict_llm.with_retry(
    retry_if_exception_type=(Exception,),
    stop_after_attempt=3
)

try:
    result = strict_chain.invoke("Rate this code: def add(a,b): return a+b")
    print(f"Score: {result.score}/10")
    print(f"Category: {result.category}")
    print(f"Explanation: {result.explanation}")
except Exception as e:
    print(f"Validation failed after retries: {e}")


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
STREAMING:
  chain.stream(input)         → sync token stream
  chain.astream(input)        → async token stream (use in FastAPI)
  StreamingResponse           → FastAPI SSE endpoint
  stream_mode="messages"      → LangGraph token streaming
  stream_mode="updates"       → LangGraph node update streaming

STRUCTURED OUTPUT:
  llm.with_structured_output(Model)   → returns typed Pydantic object
  Field(description=...)              → CRITICAL: tells LLM what to fill
  Literal[...]                        → restrict to specific values
  Optional[...]                       → field may be None

Best practices:
  - Write detailed Field descriptions — LLM accuracy depends on them
  - Use Literal for categorical fields (status, category, role)
  - Use Optional for fields that may not exist in input text
  - Add validators for business logic constraints
  - Use .with_retry() for production reliability

Next: Full Project — combine everything into a real AI application
"""
