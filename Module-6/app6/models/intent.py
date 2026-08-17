from enum import Enum
from pydantic import BaseModel


class IntentType(str, Enum):

    RETRIEVAL = "retrieval"
    SUMMARY = "summary"
    COMPARE = "compare"
    SQL = "sql"
    ACTION = "action"
    GREETING = "greeting"


class IntentResult(BaseModel):

    intent: IntentType
    confidence: float
    reason: str
