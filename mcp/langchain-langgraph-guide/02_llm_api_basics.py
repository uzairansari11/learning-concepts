"""
LLM API BASICS — Talk to AI Without Any Framework
==================================================
Before LangChain, understand what's happening under the hood.
LLMs are just HTTP APIs. A prompt goes in, text comes out.

Install: pip install anthropic openai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

# ─────────────────────────────────────────
# KEY TERMS EXPLAINED
# ─────────────────────────────────────────
"""
TOKEN
  - The unit LLMs think in. Not words — chunks (~4 chars average).
  - "Hello" = 1 token. "LangChain" = 2 tokens. "Uzair" = 2 tokens.
  - Why it matters: you pay per token. Context window is measured in tokens.

CONTEXT WINDOW
  - How much text the model can "see" at once.
  - Claude Sonnet: 200,000 tokens (~150,000 words — huge!)
  - GPT-4o: 128,000 tokens
  - Think of it as the model's "working memory"

TEMPERATURE
  - Controls randomness of output.
  - 0.0 = deterministic (same input → same output, every time)
  - 1.0 = creative (same input → different output each time)
  - For coding/data: use 0.0-0.3
  - For creative writing: use 0.7-1.0

SYSTEM PROMPT
  - Instructions that define the AI's role and behavior.
  - The AI always reads this first, before your message.
  - Think of it as the config/setup for the AI's personality.

HUMAN MESSAGE
  - The user's actual question or instruction.

ASSISTANT MESSAGE
  - The AI's response.

MAX TOKENS
  - Maximum length of the response. Prevents runaway long outputs.
"""

# ─────────────────────────────────────────
# 1. BASIC ANTHROPIC (CLAUDE) API CALL
# ─────────────────────────────────────────

import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def simple_call(user_message: str) -> str:
    """Simplest possible LLM call."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    return response.content[0].text

result = simple_call("What is a Python decorator? Explain in 2 sentences.")
print(result)


# ─────────────────────────────────────────
# 2. WITH SYSTEM PROMPT
# ─────────────────────────────────────────

def call_with_system_prompt(system: str, user_message: str) -> str:
    """Add a system prompt to control the AI's behavior."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,  # system prompt goes here
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    return response.content[0].text

system_prompt = """
You are a senior software engineer who explains concepts to frontend developers.
Always use JavaScript/React analogies when explaining new concepts.
Keep responses concise and practical.
"""

result = call_with_system_prompt(
    system=system_prompt,
    user_message="What is a Python generator?"
)
print(result)


# ─────────────────────────────────────────
# 3. MULTI-TURN CONVERSATION (Chat History)
# ─────────────────────────────────────────

def chat_with_history(messages: list[dict]) -> str:
    """
    Send a conversation with history.
    messages = [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "..."},  ← latest question
    ]
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=messages
    )
    return response.content[0].text

conversation = [
    {"role": "user", "content": "My name is Uzair. I am a frontend developer."},
    {"role": "assistant", "content": "Nice to meet you, Uzair! How can I help you today?"},
    {"role": "user", "content": "What should I learn first to enter AI engineering?"},
]

response = chat_with_history(conversation)
print(response)


# ─────────────────────────────────────────
# 4. TEMPERATURE — SEEING THE DIFFERENCE
# ─────────────────────────────────────────

def call_with_temperature(prompt: str, temperature: float) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

prompt = "Give me a one-sentence creative tagline for an AI startup."

print("Temperature 0.0 (deterministic):")
print(call_with_temperature(prompt, 0.0))

print("\nTemperature 1.0 (creative):")
print(call_with_temperature(prompt, 1.0))

# Run this multiple times — temp 0.0 gives same result, temp 1.0 varies


# ─────────────────────────────────────────
# 5. ASYNC VERSION (how real apps work)
# ─────────────────────────────────────────

import asyncio

async def async_llm_call(prompt: str) -> str:
    """Async call — use this in FastAPI or when calling multiple models."""
    client_async = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = await client_async.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

async def main():
    # Call multiple LLMs concurrently — like Promise.all()
    results = await asyncio.gather(
        async_llm_call("What is LangChain in one sentence?"),
        async_llm_call("What is LangGraph in one sentence?"),
        async_llm_call("What is RAG in one sentence?"),
    )
    for i, result in enumerate(results, 1):
        print(f"Answer {i}: {result}\n")

asyncio.run(main())


# ─────────────────────────────────────────
# 6. STREAMING — Token by Token
# ─────────────────────────────────────────
"""
Instead of waiting for the full response, you get tokens as they're generated.
This is what makes ChatGPT feel "live" — it streams tokens.
On the frontend you'd use SSE (Server-Sent Events) to show this in real time.
"""

def stream_response(prompt: str):
    """Stream tokens as they arrive."""
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)  # print each token immediately
    print()  # newline at end

stream_response("Explain Python list comprehensions step by step.")


# ─────────────────────────────────────────
# 7. UNDERSTANDING THE RESPONSE OBJECT
# ─────────────────────────────────────────

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello"}]
)

print(response.id)             # unique message ID
print(response.model)          # which model was used
print(response.stop_reason)    # why it stopped: "end_turn", "max_tokens"
print(response.usage.input_tokens)   # tokens in your prompt
print(response.usage.output_tokens)  # tokens in the response
print(response.content[0].text)      # the actual response text


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
LLMs at their core:
  Input:  system prompt + messages (conversation history)
  Output: text (or structured data if you ask for it)

Key parameters:
  model        → which AI brain to use
  max_tokens   → max response length
  temperature  → creativity level (0=deterministic, 1=creative)
  system       → AI's role/instructions
  messages     → conversation history

Next: LangChain wraps all this into reusable components.
"""
