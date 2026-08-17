from typing import Any, Dict, List, TypedDict


class AgentState(TypedDict, total=False):

    # =====================================================
    # USER INPUT
    # =====================================================

    query: str

    # =====================================================
    # INTENT CLASSIFICATION
    # =====================================================

    intent: str
    confidence: float
    intent_reason: str

    # =====================================================
    # PLANNER
    # =====================================================

    plan: List[str]
    plan_reason: str
    current_step: str
    next_step: str

    # =====================================================
    # EXECUTION CONTROL
    # =====================================================

    execution_count: int
    execution_status: str
    stop_reason: str

    # =====================================================
    # RETRIEVAL
    # =====================================================

    retrieval_response: Dict[str, Any]

    # =====================================================
    # SQL
    # =====================================================

    sql_query: str
    sql_result: Any
    sql_error: str

    # =====================================================
    # ACTION
    # =====================================================

    action: Dict[str, Any]
    action_result: Any
    action_error: str
    approval_required: bool

    # =====================================================
    # HUMAN APPROVAL
    # =====================================================

    approval_required: bool
    approval_status: str
    approval_reason: str
    approval_request: Dict[str, Any]

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    answer: str

    # =====================================================
    # EXECUTION TRACKING
    # =====================================================

    steps_executed: List[str]

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    error: str
