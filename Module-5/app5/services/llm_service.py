"""
LLM Service

This service communicates with the Groq LLM.

Features
--------
- Groq API Integration
- Streaming Response
- Optional Streaming
- Automatic Retry
- Response Validation
- Error Handling
"""

import logging
import os
import time

from dotenv import load_dotenv
from groq import Groq

from app5.schemas import LLMResponse

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


class LLMService:
    """
    Groq LLM Service
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self):

        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

        logger.info("Groq LLM Service Ready")

    # ---------------------------------------------------------
    # Response Validation
    # ---------------------------------------------------------

    def _is_valid_response(self, answer: str) -> bool:

        if answer is None:
            return False

        answer = answer.strip()

        if not answer:
            logger.warning("Validation Failed: Empty response.")
            return False

        if len(answer) < 15:
            logger.warning("Validation Failed: Response too short.")
            return False

        if answer.startswith("LLM Error"):
            logger.warning("Validation Failed: LLM Error.")
            return False

        if answer.lower() == "error":
            logger.warning("Validation Failed: Generic Error.")
            return False

        return True

    # ---------------------------------------------------------
    # Generate Response
    # ---------------------------------------------------------

    def generate_response(
        self,
        prompt: str,
        stream: bool = True,
    ) -> LLMResponse:

        for attempt in range(1, self.MAX_RETRIES + 1):

            try:

                logger.info(f"Calling Groq API (Attempt {attempt}/{self.MAX_RETRIES})")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.2,
                    max_tokens=800,
                    stream=stream,
                )

                # -------------------------------------------------
                # Streaming Response
                # -------------------------------------------------

                if stream:

                    answer = ""

                    for chunk in response:

                        if (
                            chunk.choices
                            and chunk.choices[0].delta
                            and chunk.choices[0].delta.content
                        ):

                            token = chunk.choices[0].delta.content

                            print(token, end="", flush=True)

                            answer += token

                    print()

                # -------------------------------------------------
                # Normal Response
                # -------------------------------------------------

                else:

                    answer = response.choices[0].message.content

                answer = answer.strip()

                # -------------------------------------------------
                # Validate Response
                # -------------------------------------------------

                if not self._is_valid_response(answer):

                    logger.warning(f"Attempt {attempt}: Invalid response received.")

                    if attempt == self.MAX_RETRIES:

                        return LLMResponse(
                            answer="I could not generate a valid response.",
                            confidence=0.0,
                        )

                    logger.info(f"Retrying in {self.RETRY_DELAY} second(s)...")

                    time.sleep(self.RETRY_DELAY)

                    continue

                logger.info("LLM Response Generated Successfully")

                return LLMResponse(
                    answer=answer,
                    confidence=1.0,
                )

            except Exception as e:

                logger.exception(f"Attempt {attempt} failed.")

                if attempt == self.MAX_RETRIES:

                    return LLMResponse(
                        answer=f"LLM Error: {str(e)}",
                        confidence=0.0,
                    )

                logger.info(f"Retrying in {self.RETRY_DELAY} second(s)...")

                time.sleep(self.RETRY_DELAY)

        return LLMResponse(
            answer="Unexpected error occurred.",
            confidence=0.0,
        )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    service = LLMService()

    response = service.generate_response(
        "Explain Retrieval Augmented Generation.",
        stream=True,
    )

    print("\n")
    print("=" * 80)
    print("FINAL RESPONSE")
    print("=" * 80)
    print(response.answer)
