from app6.llm.llm import LLMService


class IntentClassifier:

    def __init__(self):

        self.llm = LLMService()

    def classify(self, query: str):

        return self.llm.classify_intent(query)
