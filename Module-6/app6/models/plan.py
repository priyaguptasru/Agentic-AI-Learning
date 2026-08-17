from enum import Enum

from pydantic import BaseModel, Field


class PlanStep(str, Enum):

    GREETING = "greeting"

    RETRIEVE_DOCUMENTS = "retrieve_documents"

    GENERATE_RESPONSE = "generate_response"

    EXECUTE_SQL = "execute_sql"

    VALIDATE_ACTION = "validate_action"

    EXECUTE_ACTION = "execute_action"


class PlanResult(BaseModel):

    steps: list[PlanStep] = Field(
        min_length=1,
        max_length=5,
    )

    reason: str
