"""
Application configuration and environment management.

This module provides centralized configuration for the customer support agent,
including database settings, session management, and environment validation.
"""

import os
from typing import Final


# =============================================================================
# ENVIRONMENT VALIDATION
# =============================================================================

def validate_environment() -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        EnvironmentError: If any required environment variables are missing
    """
    REQUIRED_ENV_VARS = ["OPENAI_API_KEY"]
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_NAME: Final[str] = os.getenv("DB_NAME", "customer-support-memory.db")
SESSION_ID: Final[str] = "chat-history"


# =============================================================================
# SESSION STATE KEYS
# =============================================================================

SESSION_STATE_SESSION_KEY: Final[str] = "session"
SESSION_STATE_AGENT_KEY: Final[str] = "agent"
SESSION_STATE_TEXT_PLACEHOLDER_KEY: Final[str] = "text_placeholder"


# =============================================================================
# USER DEFAULTS
# =============================================================================

DEFAULT_CUSTOMER_ID: Final[int] = 1
DEFAULT_CUSTOMER_NAME: Final[str] = "nico"
DEFAULT_CUSTOMER_TIER: Final[str] = "basic"


# =============================================================================
# BUSINESS RULES - TIMING
# =============================================================================

REFUND_PROCESSING_DAYS_PREMIUM: Final[int] = 3
REFUND_PROCESSING_DAYS_BASIC: Final[int] = 5

ENGINEERING_RESPONSE_HOURS_PREMIUM: Final[int] = 2
ENGINEERING_RESPONSE_HOURS_BASIC: Final[int] = 4


# =============================================================================
# BUSINESS RULES - LIMITS
# =============================================================================

MAX_REFUND_AMOUNT: Final[float] = 10000.0
MAX_CREDIT_AMOUNT: Final[float] = 5000.0

RETURN_WINDOW_DAYS: Final[int] = 30
PASSWORD_RESET_EXPIRY_HOURS: Final[int] = 1
EMAIL_VERIFICATION_EXPIRY_MINUTES: Final[int] = 30
ACCOUNT_REACTIVATION_DAYS: Final[int] = 30
DATA_EXPORT_LINK_EXPIRY_DAYS: Final[int] = 7


# =============================================================================
# BUSINESS RULES - FEES
# =============================================================================

RETURN_LABEL_FEE_BASIC: Final[float] = 5.99
RETURN_LABEL_FEE_PREMIUM: Final[float] = 0.0
