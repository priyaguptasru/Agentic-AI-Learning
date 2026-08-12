"""
Query Expansion Service

This service expands user queries using
predefined synonyms to improve retrieval.
"""


class QueryExpansionService:

    def __init__(self):

        print("\nQuery Expansion Service Ready!")

        self.synonyms = {
            "routing": ["router", "route", "orchestration"],
            "llm": ["language model", "large language model"],
            "embedding": ["vector", "vector representation"],
            "search": ["retrieval", "lookup"],
            "document": ["pdf", "file"],
        }

    # ----------------------------------
    # EXPAND QUERY
    # ----------------------------------

    def expand(self, query: str):

        words = query.split()

        expanded_words = []

        for word in words:

            expanded_words.append(word)

            if word in self.synonyms:

                expanded_words.extend(self.synonyms[word])

        expanded_query = " ".join(expanded_words)

        return expanded_query


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    service = QueryExpansionService()

    queries = ["routing", "llm", "embedding search", "document retrieval"]

    for query in queries:

        print("\nOriginal Query :")

        print(query)

        print("\nExpanded Query :")

        print(service.expand(query))

        print("-" * 60)
