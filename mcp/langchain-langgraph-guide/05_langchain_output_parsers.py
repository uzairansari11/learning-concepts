"""
LANGCHAIN OUTPUT PARSERS
========================
LLMs return plain text. But your app needs structured data.
Output parsers transform raw LLM text → Python objects (str, JSON, list, Pydantic model).

This is essential for: form filling, data extraction, API responses, structured workflows.

Install: pip install langchain langchain-anthropic pydantic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)  # temp=0 for consistent structured output

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Output Parser
  - A post-processing step that converts LLM text output into usable data.
  - Think of it like JSON.parse() after fetch() — you get raw text, parse it.

StrOutputParser
  - Simplest parser. Extracts the .content string from AIMessage.
  - Use when you just want plain text back.

JsonOutputParser
  - Parses LLM output as JSON. Returns a Python dict.
  - The LLM must return valid JSON — you guide it with the prompt.

PydanticOutputParser
  - Parses LLM output into a Pydantic model (typed object).
  - Gives you type safety + validation. Best for complex structured data.

CommaSeparatedListOutputParser
  - Parses "item1, item2, item3" → ["item1", "item2", "item3"]

with_structured_output()
  - The MODERN way (2024+). You pass a Pydantic model or JSON schema.
  - The LLM uses tool calling internally to guarantee valid structure.
  - More reliable than asking the LLM to "output JSON" in text.
"""

# ─────────────────────────────────────────
# 1. StrOutputParser — Just Get the Text
# ─────────────────────────────────────────

from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Tell me about {topic} in one sentence.")
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"topic": "Python"})
print(type(result))  # <class 'str'>
print(result)        # "Python is a high-level..."


# ─────────────────────────────────────────
# 2. CommaSeparatedListOutputParser
# ─────────────────────────────────────────

from langchain_core.output_parsers import CommaSeparatedListOutputParser

list_parser = CommaSeparatedListOutputParser()

prompt = ChatPromptTemplate.from_template(
    "List 5 Python libraries used in AI/ML. Return ONLY comma-separated values, no explanation.\n{format_instructions}"
)

chain = prompt | llm | list_parser

result = chain.invoke({
    "format_instructions": list_parser.get_format_instructions()
})
print(type(result))  # list
print(result)        # ['numpy', 'pandas', 'scikit-learn', 'torch', 'transformers']


# ─────────────────────────────────────────
# 3. JsonOutputParser — Get a Dict Back
# ─────────────────────────────────────────

from langchain_core.output_parsers import JsonOutputParser

json_parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You always respond with valid JSON only. No markdown, no explanation."),
    ("human", "Give me info about the programming language {language}. Include: name, year_created, creator, primary_use. Return as JSON.")
])

chain = prompt | llm | json_parser

result = chain.invoke({"language": "Python"})
print(type(result))   # dict
print(result)         # {'name': 'Python', 'year_created': 1991, ...}
print(result["creator"])  # Guido van Rossum


# ─────────────────────────────────────────
# 4. PydanticOutputParser — Typed and Validated Output
# ─────────────────────────────────────────

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class ProgrammingLanguage(BaseModel):
    name: str = Field(description="Name of the language")
    year_created: int = Field(description="Year the language was created")
    creator: str = Field(description="Who created it")
    strengths: List[str] = Field(description="List of 3 main strengths")
    best_for: str = Field(description="What the language is primarily used for")

pydantic_parser = PydanticOutputParser(pydantic_object=ProgrammingLanguage)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a programming language expert. Always respond with structured data."),
    ("human", "Describe the programming language: {language}\n\n{format_instructions}")
])

chain = prompt | llm | pydantic_parser

result = chain.invoke({
    "language": "Python",
    "format_instructions": pydantic_parser.get_format_instructions()
})

print(type(result))              # ProgrammingLanguage (Pydantic model!)
print(result.name)               # Python
print(result.year_created)       # 1991
print(result.strengths)          # ['readable syntax', 'huge ecosystem', ...]
print(result.model_dump())       # dict if you need it


# ─────────────────────────────────────────
# 5. with_structured_output() — THE MODERN WAY (Recommended)
# ─────────────────────────────────────────
"""
Instead of asking the LLM to "output JSON", this method uses tool calling.
The LLM is forced to return data matching your schema — much more reliable.
Use this in production instead of PydanticOutputParser.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class JobCandidate(BaseModel):
    """Extract candidate info from a job application text."""
    name: str = Field(description="Full name of the candidate")
    years_experience: int = Field(description="Total years of experience")
    skills: List[str] = Field(description="List of technical skills")
    current_role: Optional[str] = Field(description="Current job title, if mentioned")
    suitable: bool = Field(description="Is this candidate suitable for a senior AI engineer role?")

# .with_structured_output() wraps the model with a schema enforcer
structured_llm = llm.with_structured_output(JobCandidate)

application_text = """
Hi, I'm Sarah. I've been working as a software engineer for 6 years.
I specialize in Python, FastAPI, and have been building AI applications
using LangChain and LangGraph for the past 2 years. Previously I was
a full-stack developer at a startup. I'm looking for a senior AI engineer role.
"""

result = structured_llm.invoke(
    f"Extract candidate information from this job application:\n\n{application_text}"
)

print(type(result))            # JobCandidate (Pydantic model)
print(result.name)             # Sarah
print(result.skills)           # ['Python', 'FastAPI', 'LangChain', 'LangGraph']
print(result.suitable)         # True
print(result.model_dump())     # dict


# ─────────────────────────────────────────
# 6. DATA EXTRACTION CHAIN — Real Use Case
# ─────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import List

class CodeReview(BaseModel):
    issues: List[str] = Field(description="List of problems found in the code")
    suggestions: List[str] = Field(description="Suggestions for improvement")
    severity: str = Field(description="Overall severity: low, medium, or high")
    score: int = Field(description="Code quality score from 1 to 10")

code_review_llm = llm.with_structured_output(CodeReview)

bad_code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users WHERE id = " + str(id)
    result = conn.execute(query)
    return result
"""

review = code_review_llm.invoke(
    f"Review this Python code for issues:\n\n```python\n{bad_code}\n```"
)

print("Issues found:")
for issue in review.issues:
    print(f"  - {issue}")

print("\nSuggestions:")
for suggestion in review.suggestions:
    print(f"  - {suggestion}")

print(f"\nSeverity: {review.severity}")
print(f"Score: {review.score}/10")


# ─────────────────────────────────────────
# 7. CUSTOM OUTPUT PARSER
# ─────────────────────────────────────────

from langchain_core.output_parsers import BaseOutputParser

class BulletPointParser(BaseOutputParser):
    """Parse LLM output that returns bullet points into a clean list."""

    def parse(self, text: str) -> list[str]:
        lines = text.strip().split("\n")
        cleaned = []
        for line in lines:
            line = line.strip()
            # Remove bullet point markers
            for marker in ["- ", "• ", "* ", "· "]:
                if line.startswith(marker):
                    line = line[len(marker):]
            if line:
                cleaned.append(line)
        return cleaned

bullet_parser = BulletPointParser()

prompt = ChatPromptTemplate.from_template(
    "List 5 benefits of {topic}. Use bullet points."
)

chain = prompt | llm | bullet_parser

result = chain.invoke({"topic": "learning Python"})
print(type(result))   # list
for i, item in enumerate(result, 1):
    print(f"{i}. {item}")


# ─────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────
"""
Parser                      Output type    When to use
─────────────────────────── ────────────── ──────────────────────────────
StrOutputParser             str            Simple text output
CommaSeparatedListParser    list           Simple lists
JsonOutputParser            dict           When LLM returns JSON text
PydanticOutputParser        Pydantic model Complex structured data (older way)
with_structured_output()    Pydantic model BEST: uses tool calling, most reliable
Custom BaseOutputParser     anything       When none of the above fit

Recommendation: Use with_structured_output() for all new code.
"""

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
Output parsers transform raw LLM text into Python objects.

Steps:
  1. Define what shape you want (Pydantic model)
  2. Use llm.with_structured_output(YourModel)
  3. Invoke and get typed data back

This enables:
  - Type-safe LLM responses
  - Automatic validation
  - Easy integration with databases/APIs
  - Predictable data flow through your app

Next: Memory — how to give your chatbot conversation history
"""
