"""
Conversation Memory Service

Maintains session-based conversation history.
"""

from collections import deque


class ConversationMemory:

    MAX_HISTORY = 5

    def __init__(self):

        print("\nConversation Memory Ready!")

        # Stores last few conversation turns
        self.history = deque(maxlen=self.MAX_HISTORY)

    # ----------------------------------------
    # Add conversation
    # ----------------------------------------

    def add_interaction(self, question: str, answer: str):

        self.history.append(
            {
                "question": question,
                "answer": answer,
            }
        )

    # ----------------------------------------
    # Return history
    # ----------------------------------------

    def get_history(self):

        return list(self.history)

    # ----------------------------------------
    # Clear memory
    # ----------------------------------------

    def clear(self):

        self.history.clear()
