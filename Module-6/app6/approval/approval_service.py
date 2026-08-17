"""
Human Approval Service

Determines whether an action requires human approval
based on action criticality and confidence.

This service does NOT make the human decision.

It only prepares the approval requirement.

The actual human decision is handled by the
LangGraph workflow through interrupt/resume.
"""

import os
from typing import Any, Dict


class ApprovalService:
    """
    Centralized approval policy.

    Approval can be required when:

    1. The action is marked as critical.
    2. The confidence is below the configured threshold.
    """

    DEFAULT_CONFIDENCE_THRESHOLD = 0.80

    def __init__(self):

        configured_threshold = os.getenv("APPROVAL_CONFIDENCE_THRESHOLD")

        if configured_threshold:

            try:

                self.confidence_threshold = float(configured_threshold)

            except ValueError:

                self.confidence_threshold = self.DEFAULT_CONFIDENCE_THRESHOLD

        else:

            self.confidence_threshold = self.DEFAULT_CONFIDENCE_THRESHOLD

        # Keep threshold within a valid range.
        self.confidence_threshold = max(
            0.0,
            min(
                1.0,
                self.confidence_threshold,
            ),
        )

    # =====================================================
    # EVALUATE APPROVAL
    # =====================================================

    def evaluate(
        self,
        action: Dict[str, Any],
        confidence: float,
    ) -> Dict[str, Any]:
        """
        Evaluate whether human approval is required.

        Parameters
        ----------
        action:
            Structured action returned by ActionAgent.

        confidence:
            Confidence associated with the request.

        Returns
        -------
        dict
            Approval decision metadata.
        """

        if not isinstance(
            action,
            dict,
        ):

            action = {}

        try:

            confidence = float(confidence)

        except (
            TypeError,
            ValueError,
        ):

            confidence = 0.0

        action_name = (
            str(
                action.get(
                    "action",
                    "unknown",
                )
            )
            .strip()
            .lower()
        )

        # -------------------------------------------------
        # Critical action
        # -------------------------------------------------

        critical = bool(
            action.get(
                "requires_approval",
                False,
            )
        )

        # -------------------------------------------------
        # Low confidence
        # -------------------------------------------------

        low_confidence = confidence < self.confidence_threshold

        # -------------------------------------------------
        # Final decision
        # -------------------------------------------------

        approval_required = critical or low_confidence

        reasons = []

        if critical:

            reasons.append("critical_action")

        if low_confidence:

            reasons.append("low_confidence")

        if not reasons:

            reasons.append("no_approval_required")

        return {
            "approval_required": (approval_required),
            "approval_reason": (", ".join(reasons)),
            "confidence": confidence,
            "confidence_threshold": (self.confidence_threshold),
            "action": action_name,
        }
