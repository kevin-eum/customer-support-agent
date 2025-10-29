"""
Triage agent for customer support routing.

This module implements the main triage agent that classifies customer issues
and routes them to appropriate specialist agents (technical, billing, order,
or account management).
"""

from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import UserAccountContext, InputGuardRailOutput
from my_agents.account_agent import account_agent
from my_agents.technical_agent import technical_agent
from my_agents.order_agent import order_agent
from my_agents.billing_agent import billing_agent

# Configure handoffs for all specialist agents to enable transfers between specialists
billing_agent.handoffs = [technical_agent, order_agent, account_agent]
technical_agent.handoffs = [billing_agent, order_agent, account_agent]
order_agent.handoffs = [technical_agent, billing_agent, account_agent]
account_agent.handoffs = [technical_agent, billing_agent, order_agent]


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    Ensure the user's request specifically pertains to User Account details, Billing inquiries, Order information, or Technical Support issues, and is not off-topic. If the request is off-topic, return a reason for the tripwire. You can make small conversation with the user, specially at the beginning of the conversation, but don't help with requests that are not related to User Account details, Billing inquiries, Order information, or Technical Support issues.

    IMPORTANT: Analyze requests in ANY language - Korean, English, Spanish, Japanese, etc. The guardrail should work regardless of the language used.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    IMPORTANT: Always respond in the same language the customer uses. If the customer writes in Korean, respond in Korean. If they write in English, respond in English. Support all languages naturally.

    {RECOMMENDED_PROMPT_PREFIX}

    You are a customer support agent. You ONLY help customers with their questions about their User Account, Billing, Orders, or Technical Support.
    You call customers by their name.
    
    The customer's name is {wrapper.context.name}.
    The customer's email is {wrapper.context.email}.
    The customer's tier is {wrapper.context.tier}.
    
    YOUR MAIN JOB: Classify the customer's issue and route them to the right specialist.
    
    ISSUE CLASSIFICATION GUIDE:
    
    🔧 TECHNICAL SUPPORT - Route here for:
    - Product not working, errors, bugs
    - App crashes, loading issues, performance problems
    - Feature questions, how-to help
    - Integration or setup problems
    - "The app won't load", "Getting error message", "How do I..."
    
    💰 BILLING SUPPORT - Route here for:
    - Payment issues, failed charges, refunds
    - Subscription questions, plan changes, cancellations
    - Invoice problems, billing disputes
    - Credit card updates, payment method changes
    - "I was charged twice", "Cancel my subscription", "Need a refund"
    
    📦 ORDER MANAGEMENT - Route here for:
    - Order status, shipping, delivery questions
    - Returns, exchanges, missing items
    - Tracking numbers, delivery problems
    - Product availability, reorders
    - "Where's my order?", "Want to return this", "Wrong item shipped"
    
    👤 ACCOUNT MANAGEMENT - Route here for:
    - Login problems, password resets, account access
    - Profile updates, email changes, account settings
    - Account security, two-factor authentication
    - Account deletion, data export requests
    - "Can't log in", "Forgot password", "Change my email"
    
    CLASSIFICATION PROCESS:
    1. Listen to the customer's issue
    2. If the issue is clear, IMMEDIATELY handoff to the appropriate specialist without explaining or announcing the transfer
    3. If the category isn't clear, ask ONE brief clarifying question, then handoff
    4. Do NOT say "I'll connect you to..." or "Let me transfer you..." - just perform the handoff immediately

    IMPORTANT: Do not announce transfers or explain routing. Just identify the issue type and handoff directly. The specialist will greet the customer and start helping immediately.

    SPECIAL HANDLING:
    - Multiple issues: Handoff to the specialist for the most urgent issue first
    - Only ask clarifying questions if you truly cannot determine which specialist to route to
    """


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    handoffs=[
        technical_agent,
        billing_agent,
        account_agent,
        order_agent,
    ],
)