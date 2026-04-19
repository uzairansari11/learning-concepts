"""
LANGCHAIN CHAINS & LCEL (LangChain Expression Language)
========================================================
LCEL is LangChain's way to compose steps together using the | pipe operator.
It works like Unix pipes or JavaScript's method chaining (.filter().map()).

This is the CORE of LangChain — everything builds on this.

Install: pip install langchain langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
LCEL (LangChain Expression Language)
  - A way to compose "Runnables" using the | pipe operator.
  - Just like Unix: cat file.txt | grep "error" | wc -l
  - Or JavaScript: array.filter(...).map(...).reduce(...)

Runnable
  - Any object that can be invoked: a prompt, a model, a parser, a function.
  - All Runnables have: .invoke(), .stream(), .batch(), .ainvoke()
  - The | operator connects Runnables into a chain.

Chain
  - A sequence of Runnables connected with |.
  - Data flows left to right: input → step1 → step2 → step3 → output

RunnablePassthrough
  - Passes the input through unchanged (useful for adding context).
  - Like the identity function: x => x

RunnableLambda
  - Wraps a regular Python function as a Runnable.
  - Like a custom middleware in Express.js.

RunnableParallel
  - Runs multiple chains at the same time, returns a dict of results.
  - Like Promise.all() but for chains.

StrOutputParser
  - Takes the AIMessage object and extracts just the .content string.
  - Final step in most chains when you want plain text output.
"""

# ─────────────────────────────────────────
# 1. BASIC CHAIN — Prompt | Model | Parser
# ─────────────────────────────────────────

from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise technical writer."),
    ("human", "Explain {topic} in exactly 2 sentences.")
])

parser = StrOutputParser()

# The | operator chains them together
# Data flows: prompt → model → parser
chain = prompt | llm | parser

# invoke() runs the whole chain with the given input
result = chain.invoke({"topic": "Python generators"})
print(type(result))   # str (not AIMessage — parser converted it)
print(result)


# ─────────────────────────────────────────
# 2. UNDERSTANDING THE PIPE OPERATOR
# ─────────────────────────────────────────

# What | actually does internally:
# step1_output = prompt.invoke({"topic": "..."})  → ChatPromptValue
# step2_output = llm.invoke(step1_output)          → AIMessage
# step3_output = parser.invoke(step2_output)       → str

# These three lines are IDENTICAL to chain.invoke({"topic": "..."})
# LCEL just makes it declarative and adds streaming/async for free.

# Long form (without LCEL):
def manual_chain(topic: str) -> str:
    formatted_prompt = prompt.invoke({"topic": topic})
    ai_message = llm.invoke(formatted_prompt)
    text = parser.invoke(ai_message)
    return text

# Short form (with LCEL):
chain = prompt | llm | parser

# Both do the same thing. LCEL is cleaner + gives you streaming/async free.
print(manual_chain("closures"))
print(chain.invoke({"topic": "closures"}))


# ─────────────────────────────────────────
# 3. CHAIN METHODS — invoke, stream, batch, ainvoke
# ─────────────────────────────────────────

chain = prompt | llm | parser

# invoke → single call, waits for full response
result = chain.invoke({"topic": "async programming"})
print(result)

# stream → yields tokens as they're generated
print("Streaming: ", end="")
for chunk in chain.stream({"topic": "decorators"}):
    print(chunk, end="", flush=True)
print()

# batch → multiple inputs at once (more efficient than calling invoke() in a loop)
results = chain.batch([
    {"topic": "closures"},
    {"topic": "generators"},
    {"topic": "decorators"},
])
for r in results:
    print(r, "\n")

# ainvoke → async version for use in FastAPI / async code
import asyncio

async def async_example():
    result = await chain.ainvoke({"topic": "Python type hints"})
    print(result)

asyncio.run(async_example())


# ─────────────────────────────────────────
# 4. RunnableLambda — Custom Function as a Step
# ─────────────────────────────────────────

from langchain_core.runnables import RunnableLambda

def add_context(input_dict: dict) -> dict:
    """Add extra context to the input before it hits the prompt."""
    input_dict["topic"] = f"Python concept: {input_dict['topic']}"
    return input_dict

def format_output(text: str) -> str:
    """Post-process the output."""
    return f"=== ANSWER ===\n{text}\n==============\n"

# Wrap plain functions as Runnables
preprocess = RunnableLambda(add_context)
postprocess = RunnableLambda(format_output)

chain = preprocess | prompt | llm | parser | postprocess

result = chain.invoke({"topic": "closures"})
print(result)


# ─────────────────────────────────────────
# 5. RunnablePassthrough — Pass Data Through Unchanged
# ─────────────────────────────────────────

from langchain_core.runnables import RunnablePassthrough

# Use case: you want to keep original input AND add LLM output
# Common in RAG: pass question through + add retrieved documents

from langchain_core.runnables import RunnableParallel

# Run two things in parallel: pass question through unchanged + run chain
chain_with_question = RunnableParallel({
    "question": RunnablePassthrough(),  # keeps the original input
    "answer": prompt | llm | parser,   # runs the chain
})

result = chain_with_question.invoke({"topic": "Python decorators"})
print("Question input:", result["question"])
print("Answer:", result["answer"])


# ─────────────────────────────────────────
# 6. RunnableParallel — Run Multiple Chains at the Same Time
# ─────────────────────────────────────────

from langchain_core.runnables import RunnableParallel

simple_prompt = ChatPromptTemplate.from_template("Explain {topic} simply.")
technical_prompt = ChatPromptTemplate.from_template("Explain {topic} technically.")
example_prompt = ChatPromptTemplate.from_template("Give a code example of {topic}.")

# All three run at the SAME TIME (parallel)
parallel_chain = RunnableParallel({
    "simple": simple_prompt | llm | parser,
    "technical": technical_prompt | llm | parser,
    "example": example_prompt | llm | parser,
})

results = parallel_chain.invoke({"topic": "Python generators"})
print("Simple explanation:", results["simple"])
print("Technical explanation:", results["technical"])
print("Code example:", results["example"])


# ─────────────────────────────────────────
# 7. BRANCHING — Different Chains Based on Input
# ─────────────────────────────────────────

from langchain_core.runnables import RunnableBranch

beginner_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} to a complete beginner. Use simple analogies."
)
expert_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} with technical depth. Include edge cases."
)

# Branch based on the "level" field in input
branch = RunnableBranch(
    (lambda x: x["level"] == "beginner", beginner_prompt | llm | parser),
    (lambda x: x["level"] == "expert",   expert_prompt | llm | parser),
    # default fallback:
    beginner_prompt | llm | parser
)

beginner_result = branch.invoke({"topic": "async/await", "level": "beginner"})
expert_result = branch.invoke({"topic": "async/await", "level": "expert"})

print("Beginner:", beginner_result)
print("Expert:", expert_result)


# ─────────────────────────────────────────
# 8. REAL-WORLD EXAMPLE — Multi-step Chain
# ─────────────────────────────────────────

# Goal: User gives a topic → generate concept → generate quiz → format output

concept_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in 3 clear bullet points."
)

quiz_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a quiz generator."),
    ("human", "Based on this explanation:\n{concept}\n\nCreate 2 quiz questions.")
])

def prepare_quiz_input(concept: str) -> dict:
    return {"concept": concept}

quiz_chain = (
    concept_prompt
    | llm
    | parser
    | RunnableLambda(prepare_quiz_input)
    | quiz_prompt
    | llm
    | parser
)

quiz = quiz_chain.invoke({"topic": "Python generators"})
print(quiz)


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
LCEL pipe operator (|) connects steps just like Unix pipes or JS method chaining.

Building blocks:
  ChatPromptTemplate  → formats the input
  ChatModel           → calls the LLM
  StrOutputParser     → extracts text from AIMessage
  RunnableLambda      → wraps a plain Python function as a chain step
  RunnablePassthrough → passes input through unchanged
  RunnableParallel    → runs multiple chains at the same time
  RunnableBranch      → conditional routing

All chains support:
  .invoke(input)      → single call
  .stream(input)      → streaming
  .batch([inputs])    → multiple calls
  .ainvoke(input)     → async

Next: Output Parsers — how to get structured data (JSON, lists) from LLMs
"""
