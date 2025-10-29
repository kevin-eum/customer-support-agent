"""
Application constants and enums.

This module contains constants for ID generation, status values,
and other application-wide constants.
"""

from typing import Final


# =============================================================================
# ID GENERATION RANGES
# =============================================================================

TICKET_ID_MIN: Final[int] = 10000
TICKET_ID_MAX: Final[int] = 99999

REFUND_ID_MIN: Final[int] = 100000
REFUND_ID_MAX: Final[int] = 999999

RETURN_ID_MIN: Final[int] = 100000
RETURN_ID_MAX: Final[int] = 999999

EXPORT_ID_MIN: Final[int] = 100000
EXPORT_ID_MAX: Final[int] = 999999

RESET_TOKEN_MIN: Final[int] = 100000
RESET_TOKEN_MAX: Final[int] = 999999

VERIFICATION_CODE_MIN: Final[int] = 100000
VERIFICATION_CODE_MAX: Final[int] = 999999

TWO_FA_CODE_MIN: Final[int] = 100000
TWO_FA_CODE_MAX: Final[int] = 999999

TRACKING_NUMBER_MIN: Final[int] = 100000
TRACKING_NUMBER_MAX: Final[int] = 999999


# =============================================================================
# ORDER STATUSES
# =============================================================================

ORDER_STATUSES: Final[list[str]] = [
    "processing",
    "shipped",
    "in_transit",
    "delivered",
]


# =============================================================================
# ISSUE TYPES
# =============================================================================

ISSUE_TYPE_TECHNICAL: Final[str] = "technical"
ISSUE_TYPE_BILLING: Final[str] = "billing"
ISSUE_TYPE_ORDER: Final[str] = "order"
ISSUE_TYPE_ACCOUNT: Final[str] = "account"


# =============================================================================
# CUSTOMER TIERS
# =============================================================================

TIER_BASIC: Final[str] = "basic"
TIER_PREMIUM: Final[str] = "premium"
TIER_ENTERPRISE: Final[str] = "enterprise"

PREMIUM_TIERS: Final[list[str]] = [TIER_PREMIUM, TIER_ENTERPRISE]


# =============================================================================
# DATA EXPORT PROCESSING
# =============================================================================

DATA_EXPORT_PROCESSING_MIN_HOURS: Final[int] = 2
DATA_EXPORT_PROCESSING_MAX_HOURS: Final[int] = 4


# =============================================================================
# DELIVERY ESTIMATION
# =============================================================================

DELIVERY_ESTIMATE_MIN_DAYS: Final[int] = 1
DELIVERY_ESTIMATE_MAX_DAYS: Final[int] = 5


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_REFUND_AMOUNT_ZERO: Final[str] = "❌ Error: Refund amount must be greater than zero"
ERROR_REFUND_AMOUNT_MAX: Final[str] = "❌ Error: Refund amount exceeds maximum allowed ($10,000). Please contact supervisor."
ERROR_REFUND_REASON_REQUIRED: Final[str] = "❌ Error: Refund reason is required"

ERROR_CREDIT_AMOUNT_ZERO: Final[str] = "❌ Error: Credit amount must be greater than zero"
ERROR_CREDIT_AMOUNT_MAX: Final[str] = "❌ Error: Credit amount exceeds maximum allowed ($5,000). Please contact supervisor."
ERROR_CREDIT_REASON_REQUIRED: Final[str] = "❌ Error: Credit reason is required"

ERROR_ORDER_NUMBER_REQUIRED: Final[str] = "❌ Error: Order number is required"
ERROR_ORDER_NUMBER_INVALID: Final[str] = "❌ Error: Invalid order number format"

ERROR_EMAIL_REQUIRED: Final[str] = "❌ Error: Both old and new email addresses are required"
ERROR_EMAIL_INVALID: Final[str] = "❌ Error: Invalid email address format"
ERROR_EMAIL_SAME: Final[str] = "❌ Error: New email must be different from current email"

ERROR_PREMIUM_REQUIRED: Final[str] = "❌ Expedited shipping upgrade requires Premium membership"
