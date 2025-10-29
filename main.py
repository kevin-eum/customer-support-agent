"""
Customer support agent main application.

This module provides the Streamlit web interface for the customer support
chatbot system, handling user interactions and agent routing.
"""

import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from models import UserAccountContext
from my_agents.triage_agent import triage_agent
import config
from logging_config import get_logger
import customers

# Setup logging
logger = get_logger(__name__)

# Validate environment variables
logger.info("Starting customer support agent application")
try:
    config.validate_environment()
    logger.info("Environment validation successful")
except EnvironmentError as e:
    logger.error(f"Environment validation failed: {e}")
    raise

client = OpenAI()

# =============================================================================
# CUSTOMER SELECTION
# =============================================================================

# Initialize selected customer in session state
if "selected_customer_name" not in st.session_state:
    # Get default customer on first load
    default_customer = customers.get_default_customer()
    st.session_state["selected_customer_name"] = default_customer.name
    logger.info(f"Initialized with default customer: {default_customer.name}")

# Get current customer context
user_account_ctx = customers.get_customer_context(st.session_state["selected_customer_name"])
if user_account_ctx is None:
    # Fallback to default if selected customer not found
    user_account_ctx = customers.get_default_customer()
    st.session_state["selected_customer_name"] = user_account_ctx.name
    logger.warning(f"Selected customer not found, using default: {user_account_ctx.name}")

# =============================================================================
# SESSION MANAGEMENT (per customer)
# =============================================================================

# Create customer-specific session key
customer_session_key = f"{config.SESSION_STATE_SESSION_KEY}_{user_account_ctx.customer_id}"

if customer_session_key not in st.session_state:
    # Create customer-specific database
    customer_db_name = f"customer_{user_account_ctx.customer_id}_support.db"
    logger.info(
        f"Initializing session for customer {user_account_ctx.customer_id} "
        f"({user_account_ctx.name}), DB: {customer_db_name}"
    )
    st.session_state[customer_session_key] = SQLiteSession(
        config.SESSION_ID,
        customer_db_name,
    )

# Use customer-specific session
session = st.session_state[customer_session_key]

# Initialize agent (shared across all customers)
if config.SESSION_STATE_AGENT_KEY not in st.session_state:
    logger.info("Initializing triage agent")
    st.session_state[config.SESSION_STATE_AGENT_KEY] = triage_agent


async def paint_history() -> None:
    """Render chat history messages in the Streamlit interface."""
    logger.debug("Rendering chat history")
    messages = await session.get_items()
    logger.debug(f"Retrieved {len(messages)} messages from history")
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))


try:
    asyncio.run(paint_history())
except Exception as e:
    logger.error(f"Error loading chat history: {e}", exc_info=True)
    st.error(f"Error loading chat history: {e}")


async def run_agent(message: str) -> None:
    """
    Process user message through the agent system and display responses.

    Args:
        message: User's input message to process
    """
    logger.info(f"Processing user message: {message[:50]}...")  # Log first 50 chars
    current_agent = st.session_state[config.SESSION_STATE_AGENT_KEY]
    logger.debug(f"Current agent: {current_agent.name}")

    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        st.session_state[config.SESSION_STATE_TEXT_PLACEHOLDER_KEY] = text_placeholder

        try:
            logger.debug("Starting agent stream")
            stream = Runner.run_streamed(
                st.session_state[config.SESSION_STATE_AGENT_KEY],
                message,
                session=session,
                context=user_account_ctx,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\$"))

                elif event.type == "agent_updated_stream_event":

                    if st.session_state[config.SESSION_STATE_AGENT_KEY].name != event.new_agent.name:
                        old_agent = st.session_state[config.SESSION_STATE_AGENT_KEY].name
                        new_agent = event.new_agent.name
                        logger.info(f"Agent handoff: {old_agent} -> {new_agent}")

                        st.write(f"🤖 Transfered from {old_agent} to {new_agent}")

                        st.session_state[config.SESSION_STATE_AGENT_KEY] = event.new_agent

                        text_placeholder = st.empty()

                        st.session_state[config.SESSION_STATE_TEXT_PLACEHOLDER_KEY] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered:
            logger.warning(f"Input guardrail triggered for message: {message[:50]}...")
            st.write("I can't help you with that.")


        except OutputGuardrailTripwireTriggered:
            logger.warning(f"Output guardrail triggered for agent response")
            st.write("I can't show you that answer.")
            st.session_state[config.SESSION_STATE_TEXT_PLACEHOLDER_KEY].empty()

message = st.chat_input(
    "Write a message for your assistant",
)

if message:
    logger.info(f"Received new user message")
    with st.chat_message("human"):
        st.write(message)
    try:
        asyncio.run(run_agent(message))
        logger.info("Message processing completed successfully")
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        st.error(f"Error processing message: {e}")


with st.sidebar:
    # =============================================================================
    # CS INFORMATION
    # =============================================================================
    st.title("CS Information")

    # =============================================================================
    # CUSTOMER SELECTOR
    # =============================================================================
    st.header("👤 Customer")

    # Get all available customers
    all_customer_names = customers.get_all_customer_names()

    # Customer selector
    selected_name = st.selectbox(
        "Select Customer:",
        options=all_customer_names,
        index=all_customer_names.index(st.session_state["selected_customer_name"])
        if st.session_state["selected_customer_name"] in all_customer_names
        else 0,
        key="customer_selector",
    )

    # Check if customer changed
    if selected_name != st.session_state["selected_customer_name"]:
        logger.info(
            f"Customer changed from {st.session_state['selected_customer_name']} to {selected_name}"
        )
        st.session_state["selected_customer_name"] = selected_name
        # Force page rerun to reload with new customer
        st.rerun()

    # Display current customer info
    st.divider()
    st.write(f"**Name:** {user_account_ctx.name}")
    st.write(f"**ID:** {user_account_ctx.customer_id}")
    st.write(f"**Email:** {user_account_ctx.email or 'Not set'}")
    st.write(f"**Tier:** {user_account_ctx.tier.title()}")

    # =============================================================================
    # MEMORY CONTROLS
    # =============================================================================
    st.divider()
    st.header("💾 Memory")

    reset = st.button("Reset memory")
    if reset:
        logger.info(f"User requested memory reset for customer {user_account_ctx.customer_id}")
        try:
            asyncio.run(session.clear_session())
            logger.info("Memory cleared successfully")
            st.success("Memory cleared successfully!")
        except Exception as e:
            logger.error(f"Error clearing memory: {e}", exc_info=True)
            st.error(f"Error clearing memory: {e}")

    # =============================================================================
    # SESSION DEBUG INFO
    # =============================================================================
    with st.expander("Debug: Session Data"):
        try:
            st.write(asyncio.run(session.get_items()))
        except Exception as e:
            logger.error(f"Error displaying session items: {e}", exc_info=True)
            st.error(f"Error displaying session items: {e}")