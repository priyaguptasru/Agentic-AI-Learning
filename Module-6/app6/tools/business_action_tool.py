"""
Business Action Tool
====================

Provides a controlled, generic interface for executing
business operations requested by ActionAgent.

Responsibilities
----------------

1. Maintain a registry of supported business actions.
2. Maintain metadata/definitions for each action.
3. Validate action names.
4. Validate action parameters.
5. Execute registered handlers.
6. Return structured execution results.
7. Keep business-specific implementation separate
   from ActionAgent and AgentWorkflow.

Important
---------

This tool does NOT perform human approval.

Human approval is handled by:

    ActionAgent
        +
    ApprovalService
        +
    AgentWorkflow

The tool only executes an action after the workflow
has already authorized it.

The implementation is intentionally generic.

Business-specific adapters can later be connected for:

    - Email
    - ServiceNow
    - CRM
    - REST APIs
    - File systems
    - Database operations
    - Other enterprise systems

The default handlers in this module are SAFE
demonstration handlers. They do not perform real
external operations.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable

# =========================================================
# ACTION DEFINITION
# =========================================================


@dataclass(frozen=True)
class ActionDefinition:
    """
    Metadata describing a registered business action.

    Parameters
    ----------
    name:
        Canonical action name.

    handler:
        Callable that performs the action.

    required_parameters:
        Parameters that must be present before the
        handler can execute.

    optional_parameters:
        Parameters that may be supplied but are not required.

    description:
        Human-readable description of the action.
    """

    name: str

    handler: Callable[
        [Dict[str, Any]],
        Any,
    ]

    required_parameters: tuple[str, ...] = ()

    optional_parameters: tuple[str, ...] = ()

    description: str = ""


class BusinessActionTool:
    """
    Generic business-action execution tool.

    The tool uses a registry-based design.

    ActionAgent does not need to know how the underlying
    business operation is implemented.

    Example
    -------

        tool.register(
            action_name="send_email",
            handler=send_email_handler,
            required_parameters={
                "to",
                "subject",
                "body",
            },
        )
    """

    name = "business_action"

    description = (
        "Executes approved business operations " "through registered action handlers."
    )

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self._actions: Dict[
            str,
            ActionDefinition,
        ] = {}

        self._register_default_actions()

    # =====================================================
    # NORMALIZE ACTION NAME
    # =====================================================

    @staticmethod
    def _normalize_action_name(
        action_name: str,
    ) -> str:
        """
        Normalize action names consistently.

        Examples
        --------

        "Send Email"
            -> "send_email"

        "send-email"
            -> "send_email"

        " SEND_EMAIL "
            -> "send_email"
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
    # REGISTER ACTION
    # =====================================================

    def register(
        self,
        action_name: str,
        handler: Callable[
            [Dict[str, Any]],
            Any,
        ],
        required_parameters: Iterable[str] | None = None,
        optional_parameters: Iterable[str] | None = None,
        description: str = "",
    ) -> None:
        """
        Register a business action.

        This method is intentionally generic.

        New business capabilities can be added without
        modifying ActionAgent.

        Parameters
        ----------
        action_name:
            Canonical logical action name.

        handler:
            Callable responsible for executing the action.

        required_parameters:
            Parameter names that must be supplied.

        optional_parameters:
            Parameter names that may be supplied.

        description:
            Human-readable action description.
        """

        # -------------------------------------------------
        # Validate action name
        # -------------------------------------------------

        if not isinstance(
            action_name,
            str,
        ):

            raise TypeError("Action name must be a string.")

        normalized_name = self._normalize_action_name(action_name)

        if not normalized_name:

            raise ValueError("Action name cannot be empty.")

        # -------------------------------------------------
        # Validate handler
        # -------------------------------------------------

        if not callable(handler):

            raise TypeError("Action handler must be callable.")

        # -------------------------------------------------
        # Normalize required parameters
        # -------------------------------------------------

        if required_parameters is None:

            required_parameters = ()

        required = tuple(
            str(parameter).strip()
            for parameter in required_parameters
            if str(parameter).strip()
        )

        # -------------------------------------------------
        # Normalize optional parameters
        # -------------------------------------------------

        if optional_parameters is None:

            optional_parameters = ()

        optional = tuple(
            str(parameter).strip()
            for parameter in optional_parameters
            if str(parameter).strip()
        )

        # -------------------------------------------------
        # Prevent contradictory definition
        # -------------------------------------------------

        overlapping = set(required) & set(optional)

        if overlapping:

            raise ValueError(
                "Parameter cannot be both required "
                f"and optional: {sorted(overlapping)}"
            )

        # -------------------------------------------------
        # Create action definition
        # -------------------------------------------------

        definition = ActionDefinition(
            name=normalized_name,
            handler=handler,
            required_parameters=required,
            optional_parameters=optional,
            description=description.strip(),
        )

        self._actions[normalized_name] = definition

    # =====================================================
    # AVAILABLE ACTIONS
    # =====================================================

    def available_actions(
        self,
    ) -> list[str]:
        """
        Return all registered business actions.
        """

        return sorted(self._actions.keys())

    # =====================================================
    # GET ACTION DEFINITION
    # =====================================================

    def get_action_definition(
        self,
        action_name: str,
    ) -> ActionDefinition | None:
        """
        Return the definition for a registered action.

        Returns None when the action is unsupported.
        """

        normalized = self._normalize_action_name(action_name)

        if not normalized:

            return None

        return self._actions.get(normalized)

    # =====================================================
    # CHECK ACTION
    # =====================================================

    def supports(
        self,
        action_name: str,
    ) -> bool:
        """
        Check whether an action is supported.
        """

        return self.get_action_definition(action_name) is not None

    # =====================================================
    # REQUIRED PARAMETERS
    # =====================================================

    def required_parameters(
        self,
        action_name: str,
    ) -> list[str]:
        """
        Return required parameters for an action.
        """

        definition = self.get_action_definition(action_name)

        if definition is None:

            return []

        return list(definition.required_parameters)

    # =====================================================
    # VALIDATE PARAMETERS
    # =====================================================

    def validate_parameters(
        self,
        action_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate parameters for a registered action.

        Validation is generic and driven by the
        ActionDefinition.

        Returns
        -------

        {
            "valid": True,
            "missing_parameters": [],
            "unexpected_parameters": []
        }

        or:

        {
            "valid": False,
            "missing_parameters": ["subject"],
            "unexpected_parameters": []
        }
        """

        definition = self.get_action_definition(action_name)

        if definition is None:

            return {
                "valid": False,
                "missing_parameters": [],
                "unexpected_parameters": [],
                "error": (f"Unsupported business action: " f"{action_name}"),
            }

        if not isinstance(
            parameters,
            dict,
        ):

            return {
                "valid": False,
                "missing_parameters": list(definition.required_parameters),
                "unexpected_parameters": [],
                "error": ("Action parameters must " "be a dictionary."),
            }

        # -------------------------------------------------
        # Missing required parameters
        # -------------------------------------------------

        missing_parameters = []

        for parameter in definition.required_parameters:

            if parameter not in parameters:

                missing_parameters.append(parameter)
                continue

            value = parameters.get(parameter)

            # Treat None / empty strings as missing.

            if value is None:

                missing_parameters.append(parameter)

            elif (
                isinstance(
                    value,
                    str,
                )
                and not value.strip()
            ):

                missing_parameters.append(parameter)

        # -------------------------------------------------
        # Allowed parameters
        # -------------------------------------------------

        allowed_parameters = set(definition.required_parameters) | set(
            definition.optional_parameters
        )

        unexpected_parameters = [
            parameter
            for parameter in parameters.keys()
            if parameter not in allowed_parameters
        ]

        # -------------------------------------------------
        # Validation result
        # -------------------------------------------------

        valid = not missing_parameters

        return {
            "valid": valid,
            "missing_parameters": (sorted(set(missing_parameters))),
            "unexpected_parameters": (sorted(set(unexpected_parameters))),
            "error": ("" if valid else ("Required action " "parameters are missing.")),
        }

    # =====================================================
    # EXECUTE ACTION
    # =====================================================

    def execute(
        self,
        action_name: str,
        parameters: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Execute a registered business action.

        Approval is intentionally NOT handled here.

        ActionAgent / AgentWorkflow must ensure
        that the action is authorized before calling
        this method.

        Parameter validation is performed here because
        BusinessActionTool owns the action definition.
        """

        # =================================================
        # VALIDATE ACTION NAME
        # =================================================

        if not isinstance(
            action_name,
            str,
        ):

            return {
                "success": False,
                "action": "",
                "status": "failed",
                "error": ("Action name must " "be a string."),
            }

        normalized_action = self._normalize_action_name(action_name)

        if not normalized_action:

            return {
                "success": False,
                "action": "",
                "status": "failed",
                "error": ("Action name cannot " "be empty."),
            }

        # =================================================
        # FIND ACTION
        # =================================================

        definition = self.get_action_definition(normalized_action)

        if definition is None:

            return {
                "success": False,
                "action": normalized_action,
                "status": "unsupported",
                "error": ("Unsupported business " f"action: {normalized_action}"),
                "available_actions": (self.available_actions()),
            }

        # =================================================
        # VALIDATE PARAMETERS TYPE
        # =================================================

        if parameters is None:

            parameters = {}

        if not isinstance(
            parameters,
            dict,
        ):

            return {
                "success": False,
                "action": normalized_action,
                "status": "validation_failed",
                "error": ("Action parameters must " "be a dictionary."),
            }

        # =================================================
        # VALIDATE PARAMETERS
        # =================================================

        validation = self.validate_parameters(
            action_name=normalized_action,
            parameters=parameters,
        )

        if not validation["valid"]:

            return {
                "success": False,
                "action": normalized_action,
                "status": "validation_failed",
                "error": (
                    validation.get(
                        "error",
                        "Action parameter " "validation failed.",
                    )
                ),
                "missing_parameters": (validation["missing_parameters"]),
                "unexpected_parameters": (validation["unexpected_parameters"]),
                "required_parameters": (self.required_parameters(normalized_action)),
            }

        # =================================================
        # EXECUTE HANDLER
        # =================================================

        try:

            result = definition.handler(parameters)

        except Exception as e:

            return {
                "success": False,
                "action": normalized_action,
                "status": "failed",
                "error": str(e),
            }

        # =================================================
        # DETERMINE RESULT STATUS
        # =================================================

        if isinstance(
            result,
            dict,
        ):

            handler_status = (
                str(
                    result.get(
                        "status",
                        "completed",
                    )
                )
                .strip()
                .lower()
            )

        else:

            handler_status = "completed"

        # =================================================
        # RETURN STRUCTURED RESULT
        # =================================================

        return {
            "success": True,
            "action": normalized_action,
            "status": handler_status,
            "result": result,
        }

    # =====================================================
    # DEFAULT ACTIONS
    # =====================================================

    def _register_default_actions(
        self,
    ) -> None:
        """
        Register generic demonstration actions.

        These are safe demonstration handlers.

        Real enterprise adapters can later replace
        these handlers without modifying ActionAgent.
        """

        # -------------------------------------------------
        # Generic compose
        # -------------------------------------------------

        self.register(
            action_name="compose",
            handler=self._compose,
            description=("Compose generic content."),
        )

        # -------------------------------------------------
        # Generic write
        # -------------------------------------------------

        self.register(
            action_name="write",
            handler=self._write,
            required_parameters={
                "resource",
                "data",
            },
            description=("Write data to a business resource."),
        )

        # -------------------------------------------------
        # Generic duplicate
        # -------------------------------------------------

        self.register(
            action_name="duplicate",
            handler=self._duplicate,
            required_parameters={
                "resource",
            },
            description=("Duplicate a business resource."),
        )

        # -------------------------------------------------
        # Generic delete
        # -------------------------------------------------

        self.register(
            action_name="delete",
            handler=self._delete,
            required_parameters={
                "resource",
            },
            description=("Delete a business resource."),
        )

        # -------------------------------------------------
        # Compose email
        # -------------------------------------------------

        self.register(
            action_name="compose_email",
            handler=self._compose_email,
            required_parameters={
                "to",
                "body",
            },
            optional_parameters={
                "subject",
            },
            description=("Compose an email without sending it."),
        )

        # -------------------------------------------------
        # Send email
        # -------------------------------------------------

        self.register(
            action_name="send_email",
            handler=self._send_email,
            required_parameters={
                "to",
                "subject",
                "body",
            },
            optional_parameters={
                "cc",
                "bcc",
                "attachments",
            },
            description=("Send an email through a configured " "email adapter."),
        )

    # =====================================================
    # COMPOSE
    # =====================================================

    @staticmethod
    def _compose(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic compose operation.

        Does not communicate with an external system.
        """

        return {
            "operation": "compose",
            "status": "completed",
            "message": ("Content was composed successfully."),
            "parameters": parameters,
        }

    # =====================================================
    # WRITE
    # =====================================================

    @staticmethod
    def _write(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic write operation.

        This demonstration implementation does not
        write to an external system.
        """

        return {
            "operation": "write",
            "status": "completed",
            "message": (
                "Write operation was validated "
                "and completed by the generic "
                "business-action layer."
            ),
            "parameters": parameters,
        }

    # =====================================================
    # DUPLICATE
    # =====================================================

    @staticmethod
    def _duplicate(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic duplicate operation.

        This demonstration implementation does not
        duplicate a real resource.
        """

        return {
            "operation": "duplicate",
            "status": "completed",
            "message": (
                "Duplicate operation was validated "
                "and completed by the generic "
                "business-action layer."
            ),
            "parameters": parameters,
        }

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def _delete(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic delete operation.

        IMPORTANT
        ---------

        This is currently a safe demonstration handler.

        It does NOT delete a real resource.

        Human approval must still be enforced by
        ActionAgent / AgentWorkflow before this handler
        is called.
        """

        return {
            "operation": "delete",
            "status": "completed",
            "message": (
                "Delete operation was validated "
                "and completed by the generic "
                "business-action layer."
            ),
            "parameters": parameters,
        }

    # =====================================================
    # COMPOSE EMAIL
    # =====================================================

    @staticmethod
    def _compose_email(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic email composition operation.

        This does NOT send an email.
        """

        return {
            "operation": "compose_email",
            "status": "completed",
            "message": ("Email composition was validated " "and completed."),
            "parameters": parameters,
        }

    # =====================================================
    # SEND EMAIL
    # =====================================================

    @staticmethod
    def _send_email(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic email sending operation.

        IMPORTANT
        ---------

        This is currently a SAFE SIMULATION.

        It does NOT send a real email.

        A real email provider can later be connected
        by replacing this handler with a production
        email adapter.

        Human approval must be enforced by
        ActionAgent / AgentWorkflow before this
        handler is called.
        """

        return {
            "operation": "send_email",
            "status": "simulated",
            "message": (
                "Email send operation was "
                "approved and simulated successfully. "
                "No real email was sent."
            ),
            "parameters": parameters,
        }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    tool = BusinessActionTool()

    # =====================================================
    # AVAILABLE ACTIONS
    # =====================================================

    print("\n" + "=" * 80)
    print("BUSINESS ACTION TOOL")
    print("=" * 80)

    print("\nAvailable Actions:")

    for action in tool.available_actions():

        definition = tool.get_action_definition(action)

        print(f"  - {action}")

        if definition:

            print(f"      Required: " f"{list(definition.required_parameters)}")

            print(f"      Optional: " f"{list(definition.optional_parameters)}")

    # =====================================================
    # TEST 1: VALID SEND EMAIL
    # =====================================================

    print("\n" + "=" * 80)
    print("TEST 1: VALID SEND EMAIL")
    print("=" * 80)

    result = tool.execute(
        action_name="send_email",
        parameters={
            "to": "manager@example.com",
            "subject": "Leave Request",
            "body": ("I would like to request " "leave for one day."),
        },
    )

    print(result)

    # =====================================================
    # TEST 2: MISSING EMAIL PARAMETERS
    # =====================================================

    print("\n" + "=" * 80)
    print("TEST 2: MISSING EMAIL PARAMETERS")
    print("=" * 80)

    result = tool.execute(
        action_name="send_email",
        parameters={
            "to": "manager@example.com",
        },
    )

    print(result)

    # =====================================================
    # TEST 3: EMPTY EMAIL PARAMETERS
    # =====================================================

    print("\n" + "=" * 80)
    print("TEST 3: EMPTY EMAIL PARAMETERS")
    print("=" * 80)

    result = tool.execute(
        action_name="send_email",
        parameters={},
    )

    print(result)

    # =====================================================
    # TEST 4: VALID DELETE
    # =====================================================

    print("\n" + "=" * 80)
    print("TEST 4: VALID DELETE")
    print("=" * 80)

    result = tool.execute(
        action_name="delete",
        parameters={
            "resource": "example",
        },
    )

    print(result)

    # =====================================================
    # TEST 5: UNSUPPORTED ACTION
    # =====================================================

    print("\n" + "=" * 80)
    print("TEST 5: UNSUPPORTED ACTION")
    print("=" * 80)

    result = tool.execute(
        action_name="send_money",
        parameters={},
    )

    print(result)
