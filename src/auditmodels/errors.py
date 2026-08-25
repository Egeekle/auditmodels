"""
Exception hierarchy and section status helpers shared by all audit phases.
"""

from typing import Any, Dict, Optional

SECTION_STATUS_OK = "OK"
SECTION_STATUS_SKIPPED = "SKIPPED"
SECTION_STATUS_ERROR = "ERROR"


class AuditModelsError(Exception):
    """Base exception for all AuditModels failures."""


class AuditConfigurationError(AuditModelsError):
    """Raised when the inputs supplied to an audit phase are invalid or inconsistent."""


class AuditExecutionError(AuditModelsError):
    """Raised when an audit phase cannot be completed because an underlying call failed."""


class ReportGenerationError(AuditModelsError):
    """Raised when an audit report cannot be rendered or written to disk."""


def skipped_section(reason: str, **extra: Any) -> Dict[str, Any]:
    """
    Builds a section result for an audit phase that could not be executed.

    Skipped sections carry no score so that they are excluded from the weighted
    overall score instead of being credited with a perfect one.
    """
    return {
        "score": None,
        "status": SECTION_STATUS_SKIPPED,
        "risk_level": "UNKNOWN",
        "skip_reason": reason,
        "warnings": [reason],
        **extra,
    }


def errored_section(reason: str, error: Optional[BaseException] = None, **extra: Any) -> Dict[str, Any]:
    """Builds a section result for an audit phase that raised an unexpected exception."""
    return {
        "score": None,
        "status": SECTION_STATUS_ERROR,
        "risk_level": "UNKNOWN",
        "error": str(error) if error is not None else reason,
        "error_type": type(error).__name__ if error is not None else None,
        "warnings": [reason],
        **extra,
    }
