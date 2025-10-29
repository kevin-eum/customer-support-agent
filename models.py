"""
Data models for customer support agent system.

This module defines Pydantic models for user context, guardrail outputs,
and handoff data structures used throughout the application.
"""

from pydantic import BaseModel
from typing import Optional


class UserAccountContext(BaseModel):

    customer_id: int
    name: str
    tier: str = "basic"
    email: Optional[str] = None  # premium entreprise

    def is_premium_customer(self) -> bool:
        """Check if customer has premium or enterprise tier."""
        return self.tier in ["premium", "enterprise"]

    def add_troubleshooting_step(self, step: str) -> None:
        """Log a troubleshooting step (for future tracking implementation)."""
        # Placeholder for future implementation
        # Could log to database, file, or monitoring system
        pass


class InputGuardRailOutput(BaseModel):

    is_off_topic: bool
    reason: str


class TechnicalOutputGuardRailOutput(BaseModel):

    contains_off_topic: bool
    contains_billing_data: bool
    contains_account_data: bool
    reason: str


class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str