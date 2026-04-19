"""
LANGCHAIN — MODELS & PROMPTS
=============================
LangChain wraps raw API calls into reusable, composable objects.
This file covers: Chat Models, Messages, Prompt Templates, and invoke().

Install: pip install langchain langchain-anthropic langchain-openai python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
ChatModel
  - LangChain's wrapper around an LLM API (Claude, GPT-4, Gemini etc.)
  - Instead of writing raw API code each time, you create one ChatModel object
    and reuse it across your app.
  - Think of it like an Axios instance configured with base URL + headers.

invoke()
  - The method to send a message and get a response (synchronous).
  - Like .then() resolved value — you get the full response back.

stream()
  - Like invoke() but returns tokens one by one (async generator).

HumanMessage / AIMessage / SystemMessage
  - LangChain's typed message objects (instead of plain dicts).
  - HumanMessage  = {"role": "user", "content": "..."}
  - AIMessage     = {"role": "assistant", "content": "..."}
  - SystemMessage = {"role": "system", "content": "..."}

PromptTemplate
  - A reusable prompt with variables — like a React component with props.
  - Define once, fill variables at runtime.

ChatPromptTemplate
  - Same but for multi-message chat prompts (system + human messages).

format_messages()
  - Fills the variables in a template and returns the final messages list.
"""

# ─────────────────────────────────────────
# 1. BASIC CHAT MODEL SETUP
# ─────────────────────────────────────────

from langchain_anthropic import ChatAnthropic

# Creating the model — like creating an axios instance
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Simple invoke — send a string, get a response
response = llm.invoke("What is Python in one sentence?")

print(type(response))        # AIMessage (not just a string!)
print(response.content)      # the actual text
print(response.usage_metadata)  # token usage info


# ─────────────────────────────────────────
# 2. MESSAGE TYPES — HumanMessage, AIMessage, SystemMessage
# ─────────────────────────────────────────

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Instead of raw dicts like {"role": "user", "content": "..."}
# LangChain uses typed objects:

messages = [
    SystemMessage(content="You are a helpful coding assistant. Always use code examples."),
    HumanMessage(content="What is a closure in JavaScript?"),
]

response = llm.invoke(messages)
print(response.content)

# Multi-turn conversation — add AI response and continue
messages.append(AIMessage(content=response.content))
messages.append(HumanMessage(content="Now explain the same concept in Python."))

follow_up = llm.invoke(messages)
print(follow_up.content)


# ─────────────────────────────────────────
# 3. PROMPT TEMPLATES — Reusable Prompts with Variables
# ─────────────────────────────────────────

from langchain_core.prompts import PromptTemplate

# Simple template with one variable
template = PromptTemplate.from_template(
    "Explain {concept} to a {level} developer in 3 bullet points."
)

# Format fills in the variables
formatted = template.format(concept="async/await", level="frontend")
print(formatted)
# Output: "Explain async/await to a frontend developer in 3 bullet points."

# You can invoke the template + model together (we'll see this in chains)
response = llm.invoke(formatted)
print(response.content)


# ─────────────────────────────────────────
# 4. CHAT PROMPT TEMPLATE — System + Human Messages with Variables
# ─────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate

# This is the most commonly used template in LangChain
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}. Explain things simply with examples."),
    ("human", "Explain {topic} and show a practical code example.")
])

# format_messages() fills variables → returns list of message objects
messages = chat_prompt.format_messages(
    domain="Python programming",
    topic="decorators"
)

print(messages)  # [SystemMessage(...), HumanMessage(...)]

response = llm.invoke(messages)
print(response.content)


# ─────────────────────────────────────────
# 5. PARTIAL TEMPLATES — Pre-fill Some Variables
# ─────────────────────────────────────────

# Like React: create a partially applied component with some props fixed

base_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {domain} teacher."),
    ("human", "{question}")
])

# Pre-fill domain, leave question for later
python_teacher_prompt = base_prompt.partial(domain="Python")

# Later, only provide question
messages = python_teacher_prompt.format_messages(
    question="What is a generator function?"
)
print(messages)


# ─────────────────────────────────────────
# 6. INVOKING DIFFERENT MODELS — Easy Swap
# ─────────────────────────────────────────

# One of LangChain's big wins: same code, different models

from langchain_anthropic import ChatAnthropic
# from langchain_openai import ChatOpenAI  # uncomment if you have OpenAI key

claude = ChatAnthropic(model="claude-sonnet-4-6")
# gpt4  = ChatOpenAI(model="gpt-4o")  # exactly same interface!

prompt = "What is the difference between a list and a tuple in Python?"

claude_response = claude.invoke(prompt)
print("Claude:", claude_response.content)

# gpt4_response = gpt4.invoke(prompt)
# print("GPT-4:", gpt4_response.content)

# Both use .invoke(), same interface — swapping models is trivial


# ─────────────────────────────────────────
# 7. ASYNC INVOKE — For Production Apps
# ─────────────────────────────────────────

import asyncio

async def get_explanation(topic: str) -> str:
    response = await llm.ainvoke(f"Explain {topic} in one sentence.")
    return response.content

async def main():
    # Run multiple LLM calls concurrently
    topics = ["closures", "generators", "decorators", "async/await"]
    tasks = [get_explanation(topic) for topic in topics]
    results = await asyncio.gather(*tasks)

    for topic, result in zip(topics, results):
        print(f"{topic}: {result}\n")

asyncio.run(main())


# ─────────────────────────────────────────
# 8. STREAMING — Token by Token
# ─────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("human", "Write a short poem about {topic}")
])

messages = prompt.format_messages(topic="coding at midnight")

# Stream tokens as they arrive — great for UI
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
print()


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
ChatModel    → wrapper around LLM API. Use .invoke() to get response.
Messages     → HumanMessage, AIMessage, SystemMessage (typed wrappers)
PromptTemplate       → reusable prompt string with variables
ChatPromptTemplate   → reusable multi-message prompt with variables

Key methods:
  llm.invoke(input)    → synchronous call, returns AIMessage
  llm.ainvoke(input)   → async call
  llm.stream(input)    → returns token stream
  llm.batch([inputs])  → run multiple calls, returns list

Next: connect prompt + model + parser using LCEL (pipe operator |)
"""
