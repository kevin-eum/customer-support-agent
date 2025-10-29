"""
Output guardrails for customer support agents.

This module implements output guardrails to ensure agents only provide
information appropriate to their domain (e.g., technical agents shouldn't
discuss billing).
"""

from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from models import TechnicalOutputGuardRailOutput, UserAccountContext
from logging_config import get_logger

logger = get_logger(__name__)


technical_output_guardrail_agent = Agent(
    name="Technical Support Guardrail",
    instructions="""
    Analyze the technical support response to check if it inappropriately contains:
    
    - Billing information (payments, refunds, charges, subscriptions)
    - Order information (shipping, tracking, delivery, returns)
    - Account management info (passwords, email changes, account settings)
    
    Technical agents should ONLY provide technical troubleshooting, diagnostics, and product support.
    Return true for any field that contains inappropriate content for a technical support response.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    output: str,
) -> GuardrailFunctionOutput:
    logger.debug(f"Running output guardrail for agent '{agent.name}'")

    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
    )

    if triggered:
        logger.warning(
            f"Output guardrail triggered for agent '{agent.name}' - "
            f"Off-topic: {validation.contains_off_topic}, "
            f"Billing: {validation.contains_billing_data}, "
            f"Account: {validation.contains_account_data}"
        )
    else:
        logger.debug(f"Output guardrail passed for agent '{agent.name}'")

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )