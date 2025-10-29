"""
Customer data management.

This module provides functions to load and manage customer data from
the customers.json file.
"""

import json
from pathlib import Path
from typing import Optional
from models import UserAccountContext
from logging_config import get_logger

logger = get_logger(__name__)

# Path to customers data file
CUSTOMERS_FILE = Path(__file__).parent / "customers.json"


def load_customers() -> list[dict]:
    """
    Load all customers from the customers.json file.

    Returns:
        List of customer dictionaries

    Raises:
        FileNotFoundError: If customers.json doesn't exist
        json.JSONDecodeError: If customers.json is invalid
    """
    try:
        with open(CUSTOMERS_FILE, "r") as f:
            customers = json.load(f)
        logger.debug(f"Loaded {len(customers)} customers from {CUSTOMERS_FILE}")
        return customers
    except FileNotFoundError:
        logger.error(f"Customers file not found: {CUSTOMERS_FILE}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in customers file: {e}")
        raise


def get_customer_by_id(customer_id: int) -> Optional[dict]:
    """
    Get a customer by their ID.

    Args:
        customer_id: Customer ID to look up

    Returns:
        Customer dictionary or None if not found
    """
    customers = load_customers()
    for customer in customers:
        if customer["customer_id"] == customer_id:
            logger.debug(f"Found customer {customer_id}: {customer['name']}")
            return customer
    logger.warning(f"Customer {customer_id} not found")
    return None


def get_customer_by_name(name: str) -> Optional[dict]:
    """
    Get a customer by their name.

    Args:
        name: Customer name to look up

    Returns:
        Customer dictionary or None if not found
    """
    customers = load_customers()
    for customer in customers:
        if customer["name"] == name:
            logger.debug(f"Found customer by name: {name}")
            return customer
    logger.warning(f"Customer with name '{name}' not found")
    return None


def get_all_customer_names() -> list[str]:
    """
    Get a list of all customer names.

    Returns:
        List of customer names sorted alphabetically
    """
    customers = load_customers()
    names = [c["name"] for c in customers]
    return sorted(names)


def customer_dict_to_context(customer_dict: dict) -> UserAccountContext:
    """
    Convert a customer dictionary to a UserAccountContext object.

    Args:
        customer_dict: Customer dictionary from JSON

    Returns:
        UserAccountContext instance
    """
    return UserAccountContext(
        customer_id=customer_dict["customer_id"],
        name=customer_dict["name"],
        email=customer_dict.get("email"),
        tier=customer_dict.get("tier", "basic"),
    )


def get_customer_context(identifier: str | int) -> Optional[UserAccountContext]:
    """
    Get a UserAccountContext by customer ID or name.

    Args:
        identifier: Customer ID (int) or name (str)

    Returns:
        UserAccountContext instance or None if not found
    """
    if isinstance(identifier, int):
        customer_dict = get_customer_by_id(identifier)
    else:
        customer_dict = get_customer_by_name(identifier)

    if customer_dict:
        return customer_dict_to_context(customer_dict)

    return None


def get_default_customer() -> UserAccountContext:
    """
    Get the default customer (first customer in the list).

    Returns:
        UserAccountContext instance

    Raises:
        ValueError: If no customers exist
    """
    customers = load_customers()
    if not customers:
        logger.error("No customers found in customers.json")
        raise ValueError("No customers available")

    default = customers[0]
    logger.info(f"Using default customer: {default['name']} (ID: {default['customer_id']})")
    return customer_dict_to_context(default)
