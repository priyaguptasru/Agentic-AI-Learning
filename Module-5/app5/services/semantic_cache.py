"""
Semantic Cache

Caches responses for repeated user queries
to avoid unnecessary retrieval and LLM calls.
"""


class SemanticCache:

    def __init__(self):

        print("\nSemantic Cache Ready!")

        self.cache = {}

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    def get(self, question: str):

        return self.cache.get(question.lower().strip())

    # ---------------------------------------------------------
    # PUT
    # ---------------------------------------------------------

    def put(self, question: str, response):

        self.cache[question.lower().strip()] = response

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear(self):

        self.cache.clear()

    # ---------------------------------------------------------
    # SIZE
    # ---------------------------------------------------------

    def size(self):

        return len(self.cache)


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    cache = SemanticCache()

    cache.put(
        "What is AI?",
        "Artificial Intelligence is ...",
    )

    print(cache.get("What is AI?"))

    print(cache.size())
