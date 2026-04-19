"""
LANGSMITH — Trace, Debug, and Monitor Your AI Apps
====================================================
LangSmith is the observability tool for LangChain/LangGraph.
Think of it as: Chrome DevTools, but for your LLM calls.

Without LangSmith: you're guessing what's happening inside your app.
With LangSmith: you see EVERY prompt sent, EVERY token used, EVERY error.

Setup:
  1. Go to smith.langchain.com → create account → get API key
  2. Set env vars (shown below)
  3. Run your code — traces appear automatically

Install: pip install langsmith langchain langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────
# SETUP — These 3 env vars enable LangSmith
# ─────────────────────────────────────────

os.environ["LANGCHAIN_TRACING_V2"] = "true"       # enable tracing
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "your-key-here")
os.environ["LANGCHAIN_PROJECT"] = "ai-learning-guide"  # project name in LangSmith

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Trace
  - A complete record of one run of your chain/agent.
  - Shows every step: what input went in, what came out, how long it took.
  - Like an HTTP request log, but for LLM calls.

Run
  - A single node/step within a trace.
  - Each chain step (prompt → llm → parser) creates its own run.

Span
  - Same as Run — a unit of work with start time, end time, input, output.

Latency
  - How long each step took. Critical for performance optimization.
  - LangSmith shows latency for each node separately.

Token Usage
  - Input tokens + output tokens for each LLM call.
  - Directly maps to cost. LangSmith shows this per run.

Feedback
  - Human-provided scores on traces (thumbs up/down, 1-5 rating).
  - Use to identify which outputs are good or bad.

Dataset
  - A collection of input/output examples used for testing and evaluation.

Evaluation
  - Running your chain against a dataset and scoring outputs.
  - Like unit tests, but for LLM quality.

@traceable
  - Decorator that makes any Python function appear in LangSmith traces.
  - Use this to trace custom functions that aren't LangChain components.
"""

# ─────────────────────────────────────────
# 1. AUTOMATIC TRACING — Just Works
# ─────────────────────────────────────────
"""
Once env vars are set, ALL LangChain/LangGraph code is automatically traced.
No code changes needed.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

chain = prompt | llm | parser

# This call is automatically traced in LangSmith
result = chain.invoke({"question": "What is LangGraph?"})
print(result)

# Go to smith.langchain.com to see the trace!
# You'll see:
# - Exact prompt sent to Claude
# - Raw response from Claude
# - Latency (total + per step)
# - Token counts (input + output)
# - Errors (if any)


# ─────────────────────────────────────────
# 2. @traceable — Trace Custom Functions
# ─────────────────────────────────────────

from langsmith import traceable

@traceable(name="preprocess_user_input")
def preprocess(text: str) -> str:
    """This function will appear in LangSmith traces."""
    return text.strip().lower()

@traceable(name="postprocess_output")
def postprocess(text: str) -> str:
    """Format the output nicely."""
    return f"Answer: {text}"

@traceable(name="full_pipeline")
def run_pipeline(question: str) -> str:
    """The whole pipeline shows as one trace with nested steps."""
    clean_question = preprocess(question)
    raw_answer = chain.invoke({"question": clean_question})
    final = postprocess(raw_answer)
    return final

result = run_pipeline("What is RAG in AI?")
print(result)


# ─────────────────────────────────────────
# 3. ADDING METADATA — Annotate Your Traces
# ─────────────────────────────────────────

from langchain_core.runnables import RunnableConfig

# Add metadata to a run for filtering in LangSmith
config = RunnableConfig(
    tags=["production", "rag-app"],       # group traces by tag
    metadata={
        "user_id": "user_123",
        "session_id": "session_456",
        "feature": "document_search",
        "environment": "development"
    }
)

result = chain.invoke({"question": "Explain embeddings"}, config=config)
# This trace in LangSmith will show the metadata
# Great for filtering: show me all traces for user_123


# ─────────────────────────────────────────
# 4. ADDING FEEDBACK — Score Your AI Outputs
# ─────────────────────────────────────────

from langsmith import Client

langsmith_client = Client()

# Run your chain and capture the run_id
from langchain_core.tracers import LangChainTracer

tracer = LangChainTracer(project_name="ai-learning-guide")
result = chain.invoke(
    {"question": "What is LangChain?"},
    config={"callbacks": [tracer]}
)

# Get the run_id from the last run
# In production, you'd get this from the trace or store it
# run_id = tracer.latest_run.id

# Add feedback programmatically (usually from your UI)
# langsmith_client.create_feedback(
#     run_id=run_id,
#     key="quality",              # feedback dimension name
#     score=1.0,                  # 0.0 to 1.0
#     comment="Great explanation, very clear"
# )

# Common feedback keys:
# "quality"     → overall quality (0-1)
# "correctness" → factually correct (0-1)
# "helpfulness" → was it helpful (0-1)
# "thumbs_up"   → simple thumbs up/down (0 or 1)


# ─────────────────────────────────────────
# 5. CREATING A DATASET — Test Cases for Evaluation
# ─────────────────────────────────────────

# A dataset = list of {input, expected_output} examples
# Use to evaluate if your chain is improving or regressing

# dataset = langsmith_client.create_dataset(
#     dataset_name="rag-qa-test-cases",
#     description="Test cases for our RAG Q&A system"
# )

# Add examples
# examples = [
#     {"input": {"question": "What is LangGraph?"}, "output": "LangGraph is a library..."},
#     {"input": {"question": "What is RAG?"}, "output": "RAG is Retrieval Augmented..."},
#     {"input": {"question": "What is LangChain?"}, "output": "LangChain is a framework..."},
# ]

# for example in examples:
#     langsmith_client.create_example(
#         inputs=example["input"],
#         outputs={"answer": example["output"]},
#         dataset_id=dataset.id
#     )


# ─────────────────────────────────────────
# 6. EVALUATION — Test Your Chain Quality
# ─────────────────────────────────────────

from langsmith.evaluation import evaluate, LangChainStringEvaluator

def run_chain(inputs: dict) -> dict:
    """Function that runs your chain — used by the evaluator."""
    result = chain.invoke({"question": inputs["question"]})
    return {"output": result}

# Built-in evaluators
# qa_evaluator = LangChainStringEvaluator("qa")          # checks factual correctness
# relevance_evaluator = LangChainStringEvaluator("relevance")  # checks relevance

# Custom evaluator — your own scoring logic
def custom_length_evaluator(run, example) -> dict:
    """Penalize very short or very long answers."""
    output = run.outputs.get("output", "")
    word_count = len(output.split())
    score = 1.0 if 20 <= word_count <= 200 else 0.5
    return {"key": "length_score", "score": score}

# Run evaluation
# results = evaluate(
#     run_chain,
#     data="rag-qa-test-cases",         # dataset name
#     evaluators=[custom_length_evaluator],
#     experiment_prefix="baseline-chain"  # name for this experiment
# )
# print(results.to_pandas())  # see scores in a DataFrame


# ─────────────────────────────────────────
# 7. WHAT TO LOOK FOR IN LANGSMITH
# ─────────────────────────────────────────
"""
When debugging a bad AI response, check in order:

1. PROMPT TAB
   → Did the prompt contain the right context/variables?
   → Was the system prompt correct?

2. OUTPUT TAB
   → What exactly did the LLM return?
   → Was it cut off? (max_tokens too low)

3. LATENCY
   → Which step is slow?
   → Is the retriever taking too long?

4. TOKEN USAGE
   → How many input tokens? (size of your context)
   → Is the context too large? (too many retrieved docs?)

5. ERROR TAB
   → Did any step throw an exception?
   → What was the exact error message?

Common issues found with LangSmith:
  - Wrong chunks retrieved (RAG not finding relevant docs)
  - Prompt template variable not filled in correctly
  - LLM ignoring instructions (need better system prompt)
  - Token limit hit (output truncated)
  - Slow retrieval (need to optimize vector search)
"""


# ─────────────────────────────────────────
# 8. LANGSMITH IN PRODUCTION — Key Practices
# ─────────────────────────────────────────
"""
Sampling (don't trace 100% in production):
  LANGCHAIN_TRACING_SAMPLING_RATE = "0.1"  # trace 10% of calls

Project organization:
  LANGCHAIN_PROJECT = "my-app-production"  # or "my-app-staging"
  Tag by feature, user segment, model version.

Alerts:
  Set up alerts in LangSmith UI for:
  - Error rate > 5%
  - P95 latency > 5 seconds
  - Token usage spikes

Cost monitoring:
  Each trace shows token counts.
  LangSmith dashboard shows total token usage over time.
  Set alerts for unexpected spikes.
"""


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
LangSmith = observability for your AI app.

Setup:
  LANGCHAIN_TRACING_V2 = "true"
  LANGCHAIN_API_KEY = "your-key"
  LANGCHAIN_PROJECT = "your-project"

Then all LangChain/LangGraph code is traced automatically.

Key features:
  Traces      → full history of each AI call
  @traceable  → trace custom functions too
  Metadata    → tag traces for filtering
  Feedback    → score outputs (human evaluation)
  Datasets    → store test cases
  Evaluation  → run regression tests on your chains

Use LangSmith from day 1. Debugging blind is painful.

Next: Streaming and Structured Output — advanced production patterns
"""
