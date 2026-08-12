"""
Schemas

This file contains all Pydantic models
used throughout Module-5.
"""

from typing import List, Optional

from pydantic import BaseModel

# ---------------------------------------------------------
# Intent Parser
# ---------------------------------------------------------


class IntentResponse(BaseModel):

    original_query: str

    intent: str

    topic: str


# ---------------------------------------------------------
# Vector Retrieval
# ---------------------------------------------------------


class RetrievedDocument(BaseModel):

    document: str

    page: int

    section: str

    text: str

    similarity: float

    source: str


# ---------------------------------------------------------
# SQL Retrieval
# ---------------------------------------------------------


class SQLResult(BaseModel):

    columns: List[str]

    rows: List[dict]


# ---------------------------------------------------------
# Conversation Memory
# ---------------------------------------------------------


class ConversationHistory(BaseModel):

    question: str

    answer: str


# ---------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------


class PromptRequest(BaseModel):

    question: str

    context: List[RetrievedDocument]

    history: List[ConversationHistory] = []


# ---------------------------------------------------------
# LLM Response
# ---------------------------------------------------------


class LLMResponse(BaseModel):

    answer: str

    confidence: Optional[float] = None


# ---------------------------------------------------------
# Final RAG Response
# ---------------------------------------------------------


class RAGResponse(BaseModel):

    question: str

    answer: str

    sources: List[str]

    confidence: Optional[float] = None


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    intent = IntentResponse(
        original_query="What is Routing?",
        intent="document_search",
        topic="routing",
    )

    print("\nIntent Schema")

    print(intent)

    document = RetrievedDocument(
        document="AI_Paper.pdf",
        page=18,
        section="Routing",
        text="Routing selects the best model.",
        similarity=0.91,
        source="Semantic Search",
    )

    print("\nRetrieved Document")

    print(document)

    response = RAGResponse(
        question="What is Routing?",
        answer="Routing is the process of selecting the best LLM.",
        sources=["AI_Paper.pdf Page 18"],
        confidence=0.95,
    )

    print("\nFinal RAG Response")

    print(response)
