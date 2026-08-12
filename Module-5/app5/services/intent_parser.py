"""
Intent Parser Service

This service identifies the user's intent
and extracts the primary topic from a query.
"""

import re

from app5.schemas import IntentResponse


class IntentParser:

    def __init__(self):

        print("\nIntent Parser Ready!")

        # -------------------------------
        # Intent Keywords
        # -------------------------------

        self.intent_patterns = {
            "document_search": [
                "what",
                "who",
                "where",
                "when",
                "why",
                "how",
                "explain",
                "define",
                "describe",
            ],
            "sql_query": [
                "list",
                "show",
                "count",
                "find",
                "employee",
                "department",
                "salary",
            ],
            "summarization": [
                "summarize",
                "summary",
                "brief",
            ],
            "comparison": [
                "compare",
                "difference",
                "vs",
                "versus",
            ],
            "greeting": [
                "hi",
                "hello",
                "hey",
            ],
        }

    # ----------------------------------
    # CLEAN QUERY
    # ----------------------------------

    def clean_query(self, query: str) -> str:

        query = query.lower().strip()

        query = re.sub(r"[^\w\s]", "", query)

        return query

    # ----------------------------------
    # DETECT INTENT
    # ----------------------------------

    def detect_intent(self, query: str) -> str:

        cleaned_query = self.clean_query(query)

        scores = {}

        # -------------------------------
        # Calculate score for each intent
        # -------------------------------

        for intent, keywords in self.intent_patterns.items():

            score = 0

            for keyword in keywords:

                if keyword in cleaned_query:

                    score += 1

            scores[intent] = score

        # -------------------------------
        # Select highest scoring intent
        # -------------------------------

        best_intent = max(scores, key=scores.get)

        # Default intent if no keyword matched

        if scores[best_intent] == 0:

            return "document_search"

        return best_intent

    # ----------------------------------
    # EXTRACT TOPIC
    # ----------------------------------

    def extract_topic(self, query: str) -> str:

        cleaned_query = self.clean_query(query)

        stop_words = {
            "what",
            "is",
            "who",
            "where",
            "when",
            "why",
            "how",
            "the",
            "a",
            "an",
            "show",
            "list",
            "find",
            "count",
            "explain",
            "define",
            "describe",
            "summarize",
            "summary",
            "brief",
            "compare",
            "difference",
            "vs",
            "versus",
            "me",
            "about",
        }

        words = cleaned_query.split()

        topic = [word for word in words if word not in stop_words]

        return " ".join(topic)

    # ----------------------------------
    # PARSE
    # ----------------------------------

    def parse(self, query: str) -> IntentResponse:

        intent = self.detect_intent(query)

        topic = self.extract_topic(query)

        return IntentResponse(
            original_query=query,
            intent=intent,
            topic=topic,
        )


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    parser = IntentParser()

    print("\n" + "=" * 70)
    print("INTENT PARSER")
    print("=" * 70)
    print("Type 'exit' or 'quit' to quit.")

    while True:

        query = input("\nEnter Query : ").strip()

        if query.lower() in ["exit", "quit"]:

            print("\nExiting Intent Parser...")

            break

        if not query:

            print("Please enter a valid query.")

            continue

        result = parser.parse(query)

        print("\nDetected Intent")
        print(result.intent)

        print("\nExtracted Topic")
        print(result.topic)

        print("\nStructured Output")
        print(result)

        print("\n" + "-" * 70)
