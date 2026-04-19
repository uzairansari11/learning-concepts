"""
PYTHON FUNDAMENTALS FOR AI ENGINEERING
======================================
You know JS/TS. This file maps Python concepts to what you already know.
Focus areas: TypedDict, Pydantic, async/await, type hints.
These appear in EVERY LangChain and LangGraph file.
"""

# ─────────────────────────────────────────
# 1. TYPE HINTS  (like TypeScript types)
# ─────────────────────────────────────────

# TypeScript:  const name: string = "Uzair"
# Python:
name: str = "Uzair"
age: int = 25
scores: list[int] = [90, 85, 95]
info: dict[str, str] = {"role": "developer"}

# Function with typed params and return type
# TypeScript: function greet(name: string): string { ... }
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional type (can be None)
# TypeScript: name?: string  OR  string | null
from typing import Optional

def find_user(id: int) -> Optional[str]:
    if id == 1:
        return "Uzair"
    return None  # explicitly allowed because Optional


# ─────────────────────────────────────────
# 2. TypedDict  (like TypeScript interface)
# ─────────────────────────────────────────
# This is used EVERYWHERE in LangGraph for defining State shape.

from typing import TypedDict

# TypeScript equivalent:
# interface AgentState {
#   messages: string[];
#   next: string;
# }

class AgentState(TypedDict):
    messages: list[str]
    next: str

# Usage — just a dict with enforced shape
state: AgentState = {
    "messages": ["Hello", "How are you?"],
    "next": "agent_node"
}

print(state["messages"])  # ['Hello', 'How are you?']


# ─────────────────────────────────────────
# 3. PYDANTIC  (like Zod in TypeScript)
# ─────────────────────────────────────────
# Pydantic validates data at runtime. Used for structured LLM output.

from pydantic import BaseModel, Field

# TypeScript + Zod equivalent:
# const UserSchema = z.object({ name: z.string(), age: z.number().min(0) })

class User(BaseModel):
    name: str
    age: int = Field(ge=0, description="Age must be non-negative")
    email: Optional[str] = None  # optional field

# Create instance — validates automatically
user = User(name="Uzair", age=25, email="dev@nourma.ai")
print(user.name)   # Uzair
print(user.model_dump())  # {'name': 'Uzair', 'age': 25, 'email': 'dev@nourma.ai'}

# Validation error example (uncomment to see)
# bad_user = User(name="Uzair", age=-5)  # raises ValidationError


# ─────────────────────────────────────────
# 4. ASYNC / AWAIT  (same as JavaScript!)
# ─────────────────────────────────────────
# LLM calls are async. This is nearly identical to JS async/await.

import asyncio

# JavaScript:
# async function fetchData() {
#   const result = await someApiCall();
#   return result;
# }

async def fetch_llm_response(prompt: str) -> str:
    await asyncio.sleep(1)  # simulating API call delay
    return f"Response to: {prompt}"

async def main():
    result = await fetch_llm_response("What is Python?")
    print(result)

    # Run multiple async calls concurrently (like Promise.all)
    results = await asyncio.gather(
        fetch_llm_response("Question 1"),
        fetch_llm_response("Question 2"),
        fetch_llm_response("Question 3"),
    )
    print(results)

# Run the async function
asyncio.run(main())


# ─────────────────────────────────────────
# 5. LIST COMPREHENSIONS  (like .map() in JS)
# ─────────────────────────────────────────

numbers = [1, 2, 3, 4, 5]

# JavaScript: numbers.map(n => n * 2)
doubled = [n * 2 for n in numbers]

# JavaScript: numbers.filter(n => n > 2)
filtered = [n for n in numbers if n > 2]

# JavaScript: numbers.filter(n => n > 2).map(n => n * 2)
filtered_and_doubled = [n * 2 for n in numbers if n > 2]

print(doubled)             # [2, 4, 6, 8, 10]
print(filtered)            # [3, 4, 5]
print(filtered_and_doubled)  # [6, 8, 10]


# ─────────────────────────────────────────
# 6. DATACLASSES  (lightweight alternative to Pydantic)
# ─────────────────────────────────────────
from dataclasses import dataclass

@dataclass
class Document:
    content: str
    source: str
    page: int = 0

doc = Document(content="Hello world", source="file.pdf", page=1)
print(doc.content)  # Hello world


# ─────────────────────────────────────────
# 7. F-STRINGS  (like template literals in JS)
# ─────────────────────────────────────────

topic = "async programming"
level = "frontend"

# JavaScript: `Explain ${topic} to a ${level} developer`
prompt = f"Explain {topic} to a {level} developer"
print(prompt)

# Multiline f-string (used in system prompts)
system_prompt = f"""
You are an expert in {topic}.
Your audience is a {level} developer.
Keep explanations practical and use analogies.
"""
print(system_prompt)


# ─────────────────────────────────────────
# 8. *args AND **kwargs  (used in LangChain internals)
# ─────────────────────────────────────────

# *args = rest params in JS: function foo(...args)
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4))  # 10

# **kwargs = spreading named args
def create_model(**config):
    print(config)  # {'model': 'claude', 'temperature': 0.7}

create_model(model="claude", temperature=0.7)


# ─────────────────────────────────────────
# SUMMARY: What You Need Before LangChain
# ─────────────────────────────────────────
"""
Must know:
  ✅ Type hints (str, int, list[str], dict[str, Any])
  ✅ TypedDict — defines shape of LangGraph state
  ✅ Pydantic BaseModel — structured output from LLMs
  ✅ async/await — all LLM calls are async
  ✅ List comprehensions — data transformation
  ✅ f-strings — building prompts

You already know the concepts from JS/TS.
Python syntax is just slightly different.
"""
