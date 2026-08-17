"""
Generic Action Agent
===================

Responsible for:

1. Understanding a user's requested business action.
2. Converting the request into a canonical action.
3. Validating the action structure.
4. Checking whether human approval is required.
5. Enforcing approval for critical actions.
6. Executing actions through BusinessActionTool.
7. Returning structured execution results.

Design
------

The ActionAgent is intentionally generic.

It does NOT contain business-specific phrases such as:

    "drop a mail"
    "mail my manager"
    "send this email"

Natural-language interpretation is performed by the LLM.

Business-specific actions are provided by:

    BusinessActionTool

Approval policies are provided by:

    ApprovalService

This keeps the agent reusable across different
applications and business domains.
"""

from typing import Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app6.agents.base_agent import BaseAgent
from app6.approval.approval_service import ApprovalService
from app6.llm.llm import LLMService
from app6.prompts.action_prompt import ACTION_PROMPT
from app6.tools.business_action_tool import BusinessActionTool


class ActionAgent(BaseAgent):
    """
    Generic business-action agent.

    Responsibilities:

        User Query
            ↓
        LLM Action Understanding
            ↓
        Action Normalization
            ↓
        Approval Evaluation
            ↓
        Human Approval
            ↓
        BusinessActionTool
    """

    def __init__(self):

        super().__init__(
            name="Action Agent",
            description=(
                "Validates and executes "
                "business actions using "
                "controlled business tools."
            ),
            version="2.0",
        )

        self.llm = LLMService()

        self.business_tool = BusinessActionTool()

        self.approval_service = ApprovalService()

    # =====================================================
    # ACTION NAME NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_action_name(
        action_name: Any,
    ) -> str:
        """
        Normalize an action name into a consistent format.

        This method does NOT maintain a list of user phrases.

        It only performs structural normalization such as:

            "Send Email"
                ->
            "send_email"

            "send-email"
                ->
            "send_email"

            " SEND_EMAIL "
                ->
            "send_email"

        Business meaning is determined by the LLM and
        supported actions are determined by BusinessActionTool.
        """

        if not isinstance(
            action_name,
            str,
        ):
            return ""

        normalized = action_name.strip().lower()

        if not normalized:
            return ""

        normalized = normalized.replace(
            "-",
            "_",
        )

        normalized = "_".join(normalized.split())

        return normalized

    # =====================================================
    # SUPPORTED ACTION CHECK
    # =====================================================

    def is_supported_action(
        self,
        action_name: str,
    ) -> bool:
        """
        Check whether the BusinessActionTool supports
        the requested canonical action.
        """

        normalized = self.normalize_action_name(action_name)

        if not normalized:
            return False

        return self.business_tool.supports(normalized)

    # =====================================================
    # CRITICAL ACTION CHECK
    # =====================================================

    def is_critical_action(
        self,
        action_name: str,
    ) -> bool:
        """
        Determine whether an action requires approval.

        The approval policy is delegated to ApprovalService.

        The ActionAgent does not hardcode business-specific
        action names here.
        """

        try:

            evaluation = self.approval_service.evaluate(
                action={
                    "action": action_name,
                },
                confidence=1.0,
            )

            return bool(
                evaluation.get(
                    "approval_required",
                    False,
                )
            )

        except Exception:

            # Fail closed.

            return True

    # =====================================================
    # VALIDATE ACTION
    # =====================================================

    def validate(
        self,
        state,
    ):
        """
        Understand and validate the requested business action.

        No business action is executed here.
        """

        query = state.get(
            "query",
            "",
        )

        if (
            not isinstance(
                query,
                str,
            )
            or not query.strip()
        ):

            return {
                "action_error": ("Action request cannot be empty."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        print("\n" + "=" * 80)

        print("ACTION AGENT")

        print("=" * 80)

        print(f"User Query : {query}")

        # =================================================
        # LLM ACTION UNDERSTANDING
        # =================================================

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    ACTION_PROMPT,
                ),
                (
                    "human",
                    "{query}",
                ),
            ]
        )

        chain = prompt | self.llm.llm | JsonOutputParser()

        try:

            action = chain.invoke(
                {
                    "query": query.strip(),
                }
            )

        except Exception as e:

            return {
                "action_error": ("Action validation failed: " f"{e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        # =================================================
        # VALIDATE LLM RESPONSE
        # =================================================

        if not isinstance(
            action,
            dict,
        ):

            return {
                "action_error": ("Action agent returned " "an invalid response."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        print("\nRaw Action Response:")

        print(action)

        # =================================================
        # EXTRACT ACTION
        # =================================================

        raw_action = action.get(
            "action",
            "",
        )

        action_name = self.normalize_action_name(raw_action)

        # =================================================
        # NO ACTION
        # =================================================

        if not action_name:

            return {
                "action": action,
                "action_error": ("No business action " "was identified."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        # =================================================
        # SUPPORTED ACTION VALIDATION
        # =================================================

        if not self.is_supported_action(action_name):

            available_actions = self.business_tool.available_actions()

            print("\nUnsupported Action")

            print(f"Requested : {action_name}")

            print(f"Supported : {available_actions}")

            return {
                "action": action,
                "action_error": (f"Unsupported business " f"action: {action_name}"),
                "supported_actions": (available_actions),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        # =================================================
        # CANONICAL ACTION
        # =================================================

        action["action"] = action_name

        # =================================================
        # PARAMETERS
        # =================================================

        parameters = action.get(
            "parameters",
            {},
        )

        if parameters is None:

            parameters = {}

        if not isinstance(
            parameters,
            dict,
        ):

            return {
                "action": action,
                "action_error": ("Action parameters must " "be a dictionary."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        action["parameters"] = parameters

        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = state.get(
            "confidence",
            0.0,
        )

        try:

            confidence = float(confidence)

        except (
            TypeError,
            ValueError,
        ):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                confidence,
                1.0,
            ),
        )

        # =================================================
        # APPROVAL EVALUATION
        # =================================================

        try:

            approval = self.approval_service.evaluate(
                action=action,
                confidence=confidence,
            )

        except Exception as e:

            return {
                "action": action,
                "action_error": ("Approval evaluation failed: " f"{e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["validate_action_failed"]
                ),
            }

        approval_required = bool(
            approval.get(
                "approval_required",
                False,
            )
        )

        approval_reason = str(
            approval.get(
                "approval_reason",
                "No approval reason provided.",
            )
        )

        confidence_threshold = approval.get(
            "confidence_threshold",
            0.0,
        )

        # =================================================
        # APPROVAL STATUS
        # =================================================

        approval_status = "pending" if approval_required else "not_required"

        # =================================================
        # DEBUG
        # =================================================

        print("\n" + "=" * 80)

        print("ACTION VALIDATION")

        print("=" * 80)

        print(f"Raw Action        : {raw_action}")

        print(f"Canonical Action  : {action_name}")

        print(f"Confidence        : {confidence}")

        print(f"Approval Required : {approval_required}")

        print(f"Approval Status   : {approval_status}")

        print(f"Approval Reason   : {approval_reason}")

        print(f"Parameters        : {parameters}")

        print("=" * 80)

        # =================================================
        # RETURN VALIDATED ACTION
        # =================================================

        return {
            "action": action,
            "approval_required": approval_required,
            "approval_status": approval_status,
            "approval_reason": approval_reason,
            "approval_request": {
                "action": action_name,
                "reason": approval_reason,
                "confidence": confidence,
                "threshold": confidence_threshold,
            },
            "action_execution_status": ("not_started"),
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["validate_action"]
            ),
        }

    # =====================================================
    # EXECUTE ACTION
    # =====================================================

    def execute(
        self,
        state,
    ):
        """
        Execute an already validated action.

        IMPORTANT:

        This method does not decide whether the action
        should be approved.

        It only verifies the approval state and executes
        the registered BusinessActionTool handler.
        """

        action = state.get(
            "action",
            {},
        )

        if not isinstance(
            action,
            dict,
        ):

            return {
                "action_execution_status": ("failed"),
                "action_error": ("Invalid action information."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        # =================================================
        # ACTION NAME
        # =================================================

        action_name = self.normalize_action_name(
            action.get(
                "action",
                "",
            )
        )

        if not action_name:

            return {
                "action_execution_status": ("failed"),
                "action_error": ("No action was identified."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        # =================================================
        # SUPPORTED ACTION SAFETY CHECK
        # =================================================

        if not self.is_supported_action(action_name):

            return {
                "action_execution_status": ("unsupported"),
                "action_error": (f"Unsupported business " f"action: {action_name}"),
                "supported_actions": (self.business_tool.available_actions()),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        # =================================================
        # APPROVAL SAFETY CHECK
        # =================================================

        approval_required = bool(
            state.get(
                "approval_required",
                False,
            )
        )

        approval_status = (
            str(
                state.get(
                    "approval_status",
                    "pending",
                )
            )
            .strip()
            .lower()
        )

        if approval_required:

            if approval_status != "approved":

                print("\n" + "=" * 80)

                print("ACTION EXECUTION BLOCKED")

                print("=" * 80)

                print(f"Action : {action_name}")

                print("Reason : Human approval " "has not been granted.")

                print("=" * 80)

                return {
                    "action_execution_status": ("blocked"),
                    "action_result": (
                        f"Action '{action_name}' "
                        "was not executed because "
                        "human approval was not granted."
                    ),
                    "action_error": ("Human approval required."),
                    "steps_executed": (
                        state.get(
                            "steps_executed",
                            [],
                        )
                        + ["execute_action_blocked"]
                    ),
                }

        # =================================================
        # PARAMETERS
        # =================================================

        parameters = action.get(
            "parameters",
            {},
        )

        if parameters is None:

            parameters = {}

        if not isinstance(
            parameters,
            dict,
        ):

            return {
                "action_execution_status": ("failed"),
                "action_error": ("Action parameters must " "be a dictionary."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        # =================================================
        # EXECUTE BUSINESS TOOL
        # =================================================

        print("\n" + "=" * 80)

        print("BUSINESS ACTION TOOL")

        print("=" * 80)

        print(f"Action     : {action_name}")

        print(f"Parameters : {parameters}")

        try:

            result = self.business_tool.execute(
                action_name=action_name,
                parameters=parameters,
            )

        except Exception as e:

            return {
                "action_execution_status": ("failed"),
                "action_error": ("Business action " f"execution failed: {e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        # =================================================
        # VALIDATE TOOL RESULT
        # =================================================

        if not isinstance(
            result,
            dict,
        ):

            return {
                "action_execution_status": ("failed"),
                "action_error": (
                    "BusinessActionTool " "returned an invalid " "response."
                ),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action_failed"]
                ),
            }

        success = bool(
            result.get(
                "success",
                False,
            )
        )

        status = (
            str(
                result.get(
                    "status",
                    "",
                )
            )
            .strip()
            .lower()
        )

        # =================================================
        # SUCCESS
        # =================================================

        if success:

            print("\n" + "=" * 80)

            print("ACTION EXECUTION SUCCESS")

            print("=" * 80)

            print(f"Action : {action_name}")

            print(f"Status : {status}")

            print("=" * 80)

            return {
                "action_result": result,
                "action_execution_status": ("executed"),
                "action_error": "",
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_action"]
                ),
            }

        # =================================================
        # FAILURE
        # =================================================

        error_message = str(
            result.get(
                "error",
                "Business action execution failed.",
            )
        )

        print("\n" + "=" * 80)

        print("ACTION EXECUTION FAILED")

        print("=" * 80)

        print(f"Action : {action_name}")

        print(f"Status : {status}")

        print(f"Error  : {error_message}")

        print("=" * 80)

        return {
            "action_result": result,
            "action_execution_status": ("failed"),
            "action_error": error_message,
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["execute_action_failed"]
            ),
        }
