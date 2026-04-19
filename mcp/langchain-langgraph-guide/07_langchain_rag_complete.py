"""
LANGCHAIN RAG — Retrieval Augmented Generation (Complete Guide)
===============================================================
RAG = Give LLMs access to YOUR data (PDFs, docs, databases).

LLMs don't know your private data. RAG solves this by:
  1. Converting your data to searchable vectors
  2. At query time, finding relevant chunks
  3. Injecting those chunks into the prompt as context

This is the #1 most-used AI pattern in production apps.

Install: pip install langchain langchain-anthropic langchain-community
         chromadb sentence-transformers pypdf python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# ─────────────────────────────────────────
# KEY TERMS — The RAG Pipeline
# ─────────────────────────────────────────
"""
RAG (Retrieval Augmented Generation)
  - A technique where you retrieve relevant information and add it to the prompt.
  - Solves the problem: LLMs don't know your private data.

Document Loader
  - Reads files and converts them to LangChain Document objects.
  - Supports: PDF, CSV, Word, web pages, Notion, GitHub, YouTube, etc.

Document
  - LangChain object with two fields:
    - page_content: str  → the actual text
    - metadata: dict     → source file, page number, etc.

Text Splitter
  - Breaks large documents into smaller chunks.
  - Why: LLMs have context limits + you only want relevant sections.
  - Each chunk becomes one searchable unit.

Embedding
  - A mathematical representation of text as a list of numbers (a vector).
  - Similar meaning → similar vectors.
  - Example: "dog" and "puppy" have similar embeddings.
  - "dog" and "database" have very different embeddings.

Vector Store (Vector Database)
  - A database that stores embeddings and can search by similarity.
  - You ask: "what chunks are similar to my question?"
  - It returns the top-K most relevant chunks.
  - Options: ChromaDB (local), Pinecone (cloud), FAISS, Weaviate, Qdrant.

Retriever
  - An interface that takes a query string and returns relevant documents.
  - Internally: embeds the query → searches vector store → returns top chunks.

Similarity Search
  - Finding stored vectors that are "close" to your query vector.
  - Measured by cosine similarity (0=unrelated, 1=identical).

Context Window Stuffing
  - Taking retrieved chunks and "stuffing" them into the prompt as context.
  - The LLM then reads both the context and the question to answer it.
"""

# ─────────────────────────────────────────
# RAG PIPELINE — TWO PHASES
# ─────────────────────────────────────────
"""
PHASE 1: INDEXING (done once, or when data changes)
  Your docs → Load → Split → Embed → Store in VectorDB

PHASE 2: RETRIEVAL + GENERATION (done on every user query)
  User question → Embed question → Search VectorDB → Get relevant chunks
                → Inject chunks into prompt → LLM answers → Response
"""

# ─────────────────────────────────────────
# PHASE 1A: DOCUMENT LOADERS
# ─────────────────────────────────────────

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    WebBaseLoader,
)
from langchain_core.documents import Document

# TextLoader — load a plain text file
# loader = TextLoader("my_document.txt")
# documents = loader.load()

# PyPDFLoader — load a PDF (each page = one Document)
# loader = PyPDFLoader("report.pdf")
# documents = loader.load()

# CSVLoader — load a CSV file
# loader = CSVLoader("data.csv")
# documents = loader.load()

# WebBaseLoader — load a web page
# loader = WebBaseLoader("https://docs.python.org/3/")
# documents = loader.load()

# For this demo, create Documents manually (simulating loaded data)
documents = [
    Document(
        page_content="""
        LangChain is a framework for developing applications powered by language models.
        It provides tools for connecting LLMs to various data sources and allows you to
        build complex AI workflows. Key components include: Chains, Agents, Tools,
        Memory, and Retrievers.
        """,
        metadata={"source": "langchain_overview.txt", "page": 1}
    ),
    Document(
        page_content="""
        LangGraph is a library built on top of LangChain for building stateful,
        multi-actor applications with LLMs. It models workflows as graphs where nodes
        are computation steps and edges define transitions. It supports cycles, which
        is essential for agent-like behavior. LangGraph is ideal for multi-agent systems.
        """,
        metadata={"source": "langgraph_overview.txt", "page": 1}
    ),
    Document(
        page_content="""
        RAG (Retrieval Augmented Generation) is a technique that enhances LLM responses
        by providing relevant context from external knowledge bases. The process involves:
        1. Converting documents to embeddings
        2. Storing embeddings in a vector database
        3. Retrieving relevant chunks at query time
        4. Providing context to the LLM for answer generation
        """,
        metadata={"source": "rag_guide.txt", "page": 1}
    ),
    Document(
        page_content="""
        Vector databases are specialized databases optimized for storing and searching
        high-dimensional vectors (embeddings). Popular options include:
        - ChromaDB: open-source, great for local development
        - Pinecone: managed cloud service, production-ready
        - FAISS: Facebook's library, fast in-memory search
        - Qdrant: open-source, production-ready
        - Weaviate: open-source with GraphQL interface
        """,
        metadata={"source": "vector_databases.txt", "page": 1}
    ),
]

print(f"Loaded {len(documents)} documents")
print("First doc preview:", documents[0].page_content[:100])


# ─────────────────────────────────────────
# PHASE 1B: TEXT SPLITTERS — Break Docs into Chunks
# ─────────────────────────────────────────

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,         # max characters per chunk
    chunk_overlap=50,       # overlap between chunks (prevents missing context at boundaries)
    separators=["\n\n", "\n", " ", ""],  # try these separators in order
)

chunks = splitter.split_documents(documents)

print(f"\nSplit {len(documents)} documents into {len(chunks)} chunks")
print(f"First chunk: {chunks[0].page_content[:100]}...")
print(f"Chunk metadata: {chunks[0].metadata}")

"""
Why chunk_overlap matters:
  If a sentence spans two chunks, overlap ensures context isn't lost.
  chunk_overlap=50 means the last 50 chars of chunk N appear at the start of chunk N+1.

chunk_size guide:
  200-500:  precise retrieval, less context per chunk
  500-1000: balance (most common)
  1000+:    more context, but retrieval less precise
"""


# ─────────────────────────────────────────
# PHASE 1C: EMBEDDINGS — Convert Text to Vectors
# ─────────────────────────────────────────

from langchain_community.embeddings import HuggingFaceEmbeddings

# Free, local embeddings (no API key needed)
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # small, fast, good quality
)

# See what an embedding looks like
sample_text = "What is LangChain?"
vector = embeddings.embed_query(sample_text)

print(f"\nEmbedding dimensions: {len(vector)}")  # 384 for this model
print(f"First 5 values: {vector[:5]}")  # list of floats

# Two similar sentences → similar vectors
v1 = embeddings.embed_query("What is LangChain?")
v2 = embeddings.embed_query("Tell me about LangChain framework")
v3 = embeddings.embed_query("What is the weather today?")

# Cosine similarity (higher = more similar)
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"\nSimilarity (LangChain vs LangChain): {cosine_similarity(v1, v2):.3f}")  # high ~0.9
print(f"Similarity (LangChain vs weather):    {cosine_similarity(v1, v3):.3f}")  # low ~0.2


# ─────────────────────────────────────────
# PHASE 1D: VECTOR STORE — Store Embeddings
# ─────────────────────────────────────────

from langchain_community.vectorstores import Chroma

# Create vector store from chunks
# This embeds each chunk and stores them in ChromaDB
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # saved to disk (optional)
)

print(f"\nVector store created with {vector_store._collection.count()} vectors")

# Or load an existing vector store
# vector_store = Chroma(
#     persist_directory="./chroma_db",
#     embedding_function=embeddings
# )


# ─────────────────────────────────────────
# PHASE 2A: RETRIEVER — Search Similar Chunks
# ─────────────────────────────────────────

retriever = vector_store.as_retriever(
    search_type="similarity",  # or "mmr" for diverse results
    search_kwargs={"k": 3}     # return top 3 most similar chunks
)

# Test the retriever
query = "What is RAG and how does it work?"
relevant_docs = retriever.invoke(query)

print(f"\nQuery: {query}")
print(f"Retrieved {len(relevant_docs)} relevant chunks:\n")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Chunk {i} (from {doc.metadata['source']}):")
    print(doc.page_content[:200])
    print()


# ─────────────────────────────────────────
# PHASE 2B: RAG CHAIN — Put It All Together
# ─────────────────────────────────────────

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

def format_docs(docs: list[Document]) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer questions based ONLY on the provided context.
If the answer is not in the context, say "I don't have that information in my knowledge base."

Context:
{context}"""),
    ("human", "{question}")
])

# The complete RAG chain
rag_chain = (
    {
        "context": retriever | format_docs,    # retrieve docs, format as text
        "question": RunnablePassthrough()       # pass question through unchanged
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Ask questions!
questions = [
    "What is LangGraph and what is it used for?",
    "What are some popular vector databases?",
    "What is the process for RAG?",
    "What is the capital of France?",  # Not in our docs
]

for question in questions:
    print(f"Q: {question}")
    answer = rag_chain.invoke(question)
    print(f"A: {answer}\n")


# ─────────────────────────────────────────
# ADVANCED: RAG WITH SOURCES
# ─────────────────────────────────────────

from langchain_core.runnables import RunnableParallel

rag_chain_with_sources = RunnableParallel({
    "answer": rag_chain,
    "sources": retriever | (lambda docs: [d.metadata["source"] for d in docs])
})

result = rag_chain_with_sources.invoke("What is LangGraph?")
print("Answer:", result["answer"])
print("Sources:", result["sources"])


# ─────────────────────────────────────────
# ADVANCED: MMR RETRIEVAL — Diverse Results
# ─────────────────────────────────────────
"""
MMR = Maximal Marginal Relevance
Problem: Top-3 similar chunks might all say the same thing.
MMR returns chunks that are relevant BUT also diverse from each other.
"""

mmr_retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,           # return 3 chunks
        "fetch_k": 10,    # initially fetch 10, then pick 3 diverse ones
        "lambda_mult": 0.7  # 0=max diversity, 1=max relevance
    }
)


# ─────────────────────────────────────────
# REAL WORLD: LOADING A PDF
# ─────────────────────────────────────────

def build_rag_from_pdf(pdf_path: str):
    """Complete RAG setup from a PDF file."""
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma

    # 1. Load
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")

    # 2. Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")

    # 3. Embed + Store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(chunks, embeddings)

    # 4. Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # 5. RAG Chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer based on context:\n{context}"),
        ("human", "{question}")
    ])

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

# Usage:
# chain = build_rag_from_pdf("your_document.pdf")
# answer = chain.invoke("What is this document about?")


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
RAG Pipeline:

INDEXING (once):
  Load docs → Split into chunks → Embed each chunk → Store in VectorDB

QUERY (each request):
  User question → Embed question → Find similar chunks → Format as context
  → Inject into prompt → LLM generates answer → Return to user

Key components:
  Document Loader    → reads your data source
  Text Splitter      → breaks docs into manageable chunks
  Embedding Model    → converts text to vectors
  Vector Store       → stores and searches vectors (ChromaDB, Pinecone)
  Retriever          → searches VectorDB for relevant chunks
  RAG Chain          → connects retriever + prompt + LLM

Next: Tools & Agents — let LLMs take actions, not just answer questions
"""
