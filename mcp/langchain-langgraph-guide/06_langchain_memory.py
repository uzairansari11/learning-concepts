"""
LANGCHAIN MEMORY — Give Your Chatbot Conversation History
==========================================================
LLMs are stateless by default — every call is independent.
Memory gives the illusion of a continuous conversation by injecting
previous messages into each new prompt.

Think of it like: localStorage for your chatbot.

Install: pip install langchain langchain-anthropic python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.7)

# ─────────────────────────────────────────
# KEY TERMS
# ─────────────────────────────────────────
"""
Stateless LLM
  - Each API call is completely independent. The model has no memory.
  - Like a serverless function — it starts fresh every time.

Memory
  - Code that stores and injects conversation history into prompts.
  - Not magic — just adding previous messages to the messages[] array.

ChatMessageHistory
  - A simple list that stores HumanMessage and AIMessage objects.
  - Like an array of chat bubbles in a React state.

MessagesPlaceholder
  - A special prompt variable that injects a list of messages.
  - Like {messages} but specifically for chat history.

InMemoryHistory
  - Stores chat history in Python memory (lost when server restarts).
  - Good for development. Use Redis/database in production.

RunnableWithMessageHistory
  - Wraps a chain to automatically manage message history per session.
  - You just invoke() it — it handles saving/loading history automatically.

session_id
  - Unique ID for each conversation (like a chat room ID).
  - Allows multiple users to have separate conversation histories.
"""

# ─────────────────────────────────────────
# 1. THE PROBLEM — LLMs Have No Memory
# ─────────────────────────────────────────

chain = ChatPromptTemplate.from_template("{input}") | llm | StrOutputParser()

# First message
response1 = chain.invoke({"input": "My name is Uzair. I am a frontend developer."})
print("Response 1:", response1)

# Second message — LLM forgot who you are!
response2 = chain.invoke({"input": "What is my name?"})
print("Response 2:", response2)  # Says it doesn't know your name!


# ─────────────────────────────────────────
# 2. MANUAL MEMORY — The Simple Way to Understand
# ─────────────────────────────────────────

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Store messages manually — like React state
chat_history = []

def chat_with_memory(user_input: str) -> str:
    """Chat function that manually maintains history."""

    # Add user's message to history
    chat_history.append(HumanMessage(content=user_input))

    # Build the full message list (system + history)
    messages = [
        SystemMessage(content="You are a helpful assistant. Remember details the user tells you."),
        *chat_history  # unpack all history messages
    ]

    # Call the LLM with full history
    response = llm.invoke(messages)

    # Add AI response to history
    chat_history.append(AIMessage(content=response.content))

    return response.content

# Now the LLM remembers across calls!
print(chat_with_memory("My name is Uzair. I am a frontend developer."))
print(chat_with_memory("I am currently learning LangChain."))
print(chat_with_memory("What is my name and what am I learning?"))


# ─────────────────────────────────────────
# 3. ChatMessageHistory — LangChain's History Store
# ─────────────────────────────────────────

from langchain_community.chat_message_histories import ChatMessageHistory

# ChatMessageHistory is just a wrapper around a list
history = ChatMessageHistory()

history.add_user_message("Hello! My name is Uzair.")
history.add_ai_message("Hello Uzair! Nice to meet you.")
history.add_user_message("I am learning AI engineering.")
history.add_ai_message("That's great! LangChain is a good place to start.")

print(history.messages)  # list of HumanMessage and AIMessage objects

# Access messages
for msg in history.messages:
    role = "Human" if isinstance(msg, HumanMessage) else "AI"
    print(f"{role}: {msg.content}")


# ─────────────────────────────────────────
# 4. MessagesPlaceholder — Inject History into Prompt
# ─────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# MessagesPlaceholder is a variable that accepts a LIST of messages
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Remember details the user shares."),
    MessagesPlaceholder(variable_name="history"),  # ← inject history here
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

# Manually manage history
history_list = []

def chat(user_input: str) -> str:
    from langchain_core.messages import HumanMessage, AIMessage

    # Call chain with current history
    response = chain.invoke({
        "history": history_list,
        "input": user_input
    })

    # Update history
    history_list.append(HumanMessage(content=user_input))
    history_list.append(AIMessage(content=response))

    return response

print(chat("My name is Uzair and I work with React and Node.js"))
print(chat("I want to learn LangChain and LangGraph"))
print(chat("Based on what I told you, what tech stack do I know?"))


# ─────────────────────────────────────────
# 5. RunnableWithMessageHistory — Automatic Memory Management
# ─────────────────────────────────────────

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# In-memory store: session_id → ChatMessageHistory
session_store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Return history for a given session, create if not exists."""
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful coding assistant. Remember user details."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

# Wrap the chain — it auto-manages history per session
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,              # function to get/create history
    input_messages_key="input",       # which key is the user's message
    history_messages_key="history",   # which key is the history placeholder
)

# Session 1 — Uzair's conversation
config_uzair = {"configurable": {"session_id": "uzair_session"}}

r1 = chain_with_memory.invoke({"input": "My name is Uzair. I use React."}, config=config_uzair)
print("Uzair session, msg 1:", r1)

r2 = chain_with_memory.invoke({"input": "What frontend framework do I use?"}, config=config_uzair)
print("Uzair session, msg 2:", r2)  # Remembers React!

# Session 2 — Sara's separate conversation (completely separate history)
config_sara = {"configurable": {"session_id": "sara_session"}}

r3 = chain_with_memory.invoke({"input": "My name is Sara. I use Vue.js."}, config=config_sara)
print("Sara session, msg 1:", r3)

r4 = chain_with_memory.invoke({"input": "What is my name?"}, config=config_sara)
print("Sara session, msg 2:", r4)  # Says Sara, not Uzair

# Sessions are isolated — different histories
print("\nSession store has", len(session_store), "sessions")


# ─────────────────────────────────────────
# 6. MEMORY STRATEGIES — Handling Long Conversations
# ─────────────────────────────────────────
"""
Problem: Long conversations use lots of tokens (expensive + hits context limit).

Strategies:

1. Buffer Memory (default above)
   - Keep all messages
   - Pros: nothing lost
   - Cons: grows forever, hits token limit

2. Window Memory — keep last N messages
3. Summary Memory — summarize old messages into 1 message
4. Token Limit Memory — trim when over N tokens
"""

# STRATEGY 2: Window Memory — Keep Last N Messages
def trim_history(history: list, max_messages: int = 10) -> list:
    """Keep only the last N messages."""
    return history[-max_messages:]

# STRATEGY 3: Summary Memory — Summarize Old Messages
from langchain_core.prompts import PromptTemplate

summary_chain = (
    PromptTemplate.from_template(
        "Summarize this conversation in 2 sentences:\n{conversation}"
    )
    | llm
    | StrOutputParser()
)

def summarize_and_trim(history: list, keep_last: int = 4) -> list:
    """Summarize old messages, keep recent ones."""
    if len(history) <= keep_last:
        return history

    old_messages = history[:-keep_last]
    recent_messages = history[-keep_last:]

    # Format old messages as text
    conversation_text = "\n".join([
        f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in old_messages
    ])

    summary = summary_chain.invoke({"conversation": conversation_text})

    # Replace old messages with summary
    from langchain_core.messages import SystemMessage
    summary_message = SystemMessage(content=f"Previous conversation summary: {summary}")

    return [summary_message] + recent_messages


# ─────────────────────────────────────────
# 7. PERSISTENT MEMORY — Survive Server Restarts
# ─────────────────────────────────────────
"""
In-memory history is lost when the server restarts.
For production, use a database-backed history store.

Options:
  - Redis:    RedisChatMessageHistory (from langchain-community)
  - Postgres: PostgresChatMessageHistory
  - MongoDB:  MongoDBChatMessageHistory
  - SQLite:   SQLiteChatMessageHistory (good for local dev)

Example (SQLite — no server needed):
"""

# from langchain_community.chat_message_histories import SQLChatMessageHistory
#
# def get_persistent_history(session_id: str):
#     return SQLChatMessageHistory(
#         session_id=session_id,
#         connection="sqlite:///chat_history.db"  # local file
#     )
#
# chain_with_persistent_memory = RunnableWithMessageHistory(
#     chain,
#     get_persistent_history,
#     input_messages_key="input",
#     history_messages_key="history",
# )
# History survives restarts because it's stored in a file.


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
"""
Memory = injecting conversation history into each prompt.

Tools:
  ChatMessageHistory           → stores messages in a list
  MessagesPlaceholder          → injects history into prompt template
  RunnableWithMessageHistory   → auto-manages history per session_id

Memory strategies:
  Buffer    → keep everything (simple, but grows)
  Window    → keep last N messages (practical)
  Summary   → compress old messages into a summary (best for long chats)

Production: use Redis/Postgres instead of in-memory store.

Next: RAG — how to answer questions from your own documents/data
"""
