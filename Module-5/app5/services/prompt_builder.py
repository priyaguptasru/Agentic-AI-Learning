"""
Prompt Builder Service

Builds the final prompt using:

1. Conversation History
2. Retrieved Context
3. Current User Question
"""

from app5.schemas import PromptRequest


class PromptBuilder:

    def __init__(self):

        print("\nPrompt Builder Ready!")

    # ---------------------------------------------------------
    # BUILD PROMPT
    # ---------------------------------------------------------

    def build_prompt(self, request: PromptRequest) -> str:

        # -----------------------------------------------------
        # Conversation History
        # -----------------------------------------------------

        history = ""

        if request.history:

            history += "Previous Conversation\n"
            history += "-" * 30 + "\n"

            for conversation in request.history:

                history += (
                    f"User      : {conversation.question}\n"
                    f"Assistant : {conversation.answer}\n\n"
                )

        else:

            history = "No previous conversation.\n"

        # -----------------------------------------------------
        # Retrieved Context
        # -----------------------------------------------------

        context = ""

        seen_chunks = set()

        unique_documents = []

        for document in request.context:

            normalized_text = document.text.strip().lower()

            if normalized_text not in seen_chunks:

                seen_chunks.add(normalized_text)

                unique_documents.append(document)

        for index, document in enumerate(unique_documents, start=1):

            trimmed_text = document.text[:600]

            context += (
                f"\nContext {index}\n"
                f"Document : {document.document}\n"
                f"Page     : {document.page}\n"
                f"Section  : {document.section}\n"
                f"Text:\n"
                f"{trimmed_text}\n"
            )

        # -----------------------------------------------------
        # Final Prompt
        # -----------------------------------------------------

        prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the Context below.

If the answer is not found in the Context, reply exactly:

"I could not find the answer in the provided documents."

History:
{history}

Context:
{context}

Question:
{request.question}

Answer:
"""

        return prompt.strip()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    from app5.schemas import (
        ConversationHistory,
        PromptRequest,
        RetrievedDocument,
    )

    builder = PromptBuilder()

    previous_question = input("Previous Question : ").strip()
    previous_answer = input("Previous Answer   : ").strip()
    current_question = input("Current Question  : ").strip()

    request = PromptRequest(
        question=current_question,
        history=[
            ConversationHistory(
                question=previous_question,
                answer=previous_answer,
            )
        ],
        context=[
            RetrievedDocument(
                document="Sample.pdf",
                page=1,
                section="Sample Section",
                text="This is sample retrieved context used only for Prompt Builder testing.",
                similarity=0.95,
                source="Semantic Search",
            )
        ],
    )

    prompt = builder.build_prompt(request)

    print("\n")
    print("=" * 80)
    print("GENERATED PROMPT")
    print("=" * 80)
    print(prompt)
