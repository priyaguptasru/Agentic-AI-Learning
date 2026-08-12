"""
RAG Service

Retrieval-Augmented Generation Pipeline

Flow

1. Intent Detection
2. Semantic Cache
3. Conversation Memory
4. Context-Aware Query Generation
5. Hybrid Search
6. Validate Search Results
7. Prompt Construction
8. LLM Response
9. Save Conversation
10. Save Semantic Cache
11. Return Final Answer
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------
# MODULE-5
# ---------------------------------------------------------

from app5.schemas import (
    PromptRequest,
    RetrievedDocument,
    RAGResponse,
)

from app5.services.intent_parser import IntentParser
from app5.services.prompt_builder import PromptBuilder
from app5.services.llm_service import LLMService
from app5.services.conversation_memory import ConversationMemory
from app5.services.semantic_cache import SemanticCache

# ---------------------------------------------------------
# MODULE-4
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE4_PATH = PROJECT_ROOT / "Module-4"

sys.path.insert(0, str(MODULE4_PATH))

from app.services.hybrid_search import HybridSearchService


class RAGService:

    # Minimum similarity required before calling the LLM
    MIN_CONFIDENCE = 0.40

    def __init__(self):

        print("\nInitializing RAG Service...")

        self.intent_parser = IntentParser()
        self.memory = ConversationMemory()
        self.semantic_cache = SemanticCache()
        self.search_service = HybridSearchService()
        self.prompt_builder = PromptBuilder()
        self.llm_service = LLMService()

        print("RAG Service Ready!")

    # -----------------------------------------------------
    # FOLLOW-UP QUESTION DETECTION
    # -----------------------------------------------------

    def is_followup_question(self, question: str) -> bool:

        # ----------------------------------
        # Normalize Question
        # ----------------------------------

        question = re.sub(
            r"[^\w\s]",
            "",
            question.lower(),
        ).strip()

        if not question:
            return False

        # ----------------------------------
        # Follow-up Keywords
        # ----------------------------------

        followup_keywords = {
            "explain",
            "summarize",
            "summary",
            "simplify",
            "continue",
            "more",
            "detail",
            "details",
            "example",
            "examples",
            "elaborate",
            "why",
            "how",
            "difference",
            "compare",
            "can you explain",
            "could you explain",
            "tell me",
            "tell me about",
            "in simple words",
            "easy explanation",
            "simplify this",
            "more",
            "details",
        }

        # ----------------------------------
        # Check if any follow-up keyword
        # exists anywhere in the question
        # ----------------------------------

        for keyword in followup_keywords:

            if keyword in question:
                return True

        # ----------------------------------
        # Pronoun Detection
        # ----------------------------------

        pronouns = {
            "it",
            "its",
            "this",
            "that",
            "these",
            "those",
            "they",
            "them",
        }

        words = question.split()

        if any(word in pronouns for word in words):
            return True

        return False

    def process_question(self, question: str):

        # -------------------------------------------------
        # Step 1 : Intent Detection
        # -------------------------------------------------

        intent = self.intent_parser.parse(question)

        print(f"\nDetected Intent : {intent.intent}")
        print(f"Topic           : {intent.topic}")

        # -------------------------------------------------
        # Greeting
        # -------------------------------------------------

        if intent.intent == "greeting":

            return RAGResponse(
                question=question,
                answer="Hello! How can I help you today?",
                confidence=1.0,
                sources=[],
            )

        # -------------------------------------------------
        # Step 2 : Semantic Cache
        # -------------------------------------------------

        cached_response = self.semantic_cache.get(question)

        if cached_response:

            print("\nResponse returned from Semantic Cache.")

            return cached_response

        # -------------------------------------------------
        # Step 3 : Conversation Memory
        # -------------------------------------------------

        if not self.is_followup_question(question):

            print("\nNew topic detected. Clearing conversation memory.")

            self.memory.clear()

        conversation_history = self.memory.get_history()

        # -------------------------------------------------
        # Step 4 : Context-Aware Search Query
        # -------------------------------------------------

        search_query = question

        if conversation_history:

            previous_questions = [
                conversation["question"] for conversation in conversation_history[-3:]
            ]

            search_query = " ".join(previous_questions)

            search_query += f" {question}"

        print("\nSearch Query:")
        print(search_query)

        # -------------------------------------------------
        # Step 5 : Hybrid Search
        # -------------------------------------------------

        search_results = self.search_service.search(search_query)

        if not search_results:

            return RAGResponse(
                question=question,
                answer="I could not find the answer in the provided documents.",
                confidence=0.0,
                sources=[],
            )

        retrieved_docs = []

        highest_similarity = 0.0

        for result in search_results:

            similarity = (
                result["similarity"] if isinstance(result["similarity"], float) else 0.0
            )

            highest_similarity = max(
                highest_similarity,
                similarity,
            )

            retrieved_docs.append(
                RetrievedDocument(
                    document=result["document"],
                    page=result["page"],
                    section=result["section"],
                    text=result["text"],
                    similarity=similarity,
                    source=result["source"],
                )
            )

        # -------------------------------------------------
        # Step 6 : Confidence Check
        # -------------------------------------------------

        if highest_similarity < self.MIN_CONFIDENCE:

            return RAGResponse(
                question=question,
                answer="I could not find the answer in the provided documents.",
                confidence=round(highest_similarity, 2),
                sources=[],
            )

        # -------------------------------------------------
        # Step 7 : Prompt Builder
        # -------------------------------------------------

        prompt_request = PromptRequest(
            question=question,
            context=retrieved_docs[:3],
            history=conversation_history,
        )

        prompt = self.prompt_builder.build_prompt(prompt_request)

        print("\nSending Prompt to LLM...\n")

        # -------------------------------------------------
        # Step 8 : Generate Streaming LLM Response
        # -------------------------------------------------

        print("\nGenerating Response...\n")

        llm_response = self.llm_service.generate_response(
            prompt,
            stream=True,
        )

        print("\n")

        # -------------------------------------------------
        # Step 9 : Save Conversation
        # -------------------------------------------------

        self.memory.add_interaction(
            question=question,
            answer=llm_response.answer,
        )

        # -------------------------------------------------
        # Step 10 : Final Response
        # -------------------------------------------------

        response = RAGResponse(
            question=question,
            answer=llm_response.answer,
            confidence=round(highest_similarity, 2),
            sources=[
                f"{doc.document} | Page {doc.page} | {doc.section}"
                for doc in retrieved_docs[:5]
            ],
        )

        # -------------------------------------------------
        # Step 11 : Save Semantic Cache
        # -------------------------------------------------

        self.semantic_cache.put(
            question,
            response,
        )

        return response


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    service = RAGService()

    while True:

        question = input(
            "\nAsk a question (type 'exit' or 'quit' or 'q' to quit): "
        ).strip()

        if question.lower() in ["exit", "quit", "q"]:

            print("\nExiting RAG Service...")
            break

        if not question:

            print("Please enter a valid question.")
            continue

        response = service.process_question(question)

        print("\n" + "=" * 80)
        print("FINAL RESPONSE")
        print("=" * 80)

        print(f"\nQuestion   : {response.question}")
        print(f"\nAnswer     : {response.answer}")
        print(f"\nConfidence : {response.confidence}")

        print("\nSources:")

        if response.sources:

            for source in response.sources:
                print(f"- {source}")

        else:

            print("No sources found.")
