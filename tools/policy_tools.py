"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
@Desc ： Provides tools to query company policies and payment methods.
"""

from typing import Literal
from langchain_core.tools import tool


def query_policy(policy_type: Literal["shipping", "return", "privacy"]) -> str:
    """
    A tool for fetching the content of company policies.

    Args:
        policy_type (Literal): The type of policy to query. Options are 'shipping', 'return', or 'privacy'.

    Returns:
        str: The content of the requested policy.
    """
    # Define policy content
    policies = {
        "shipping": "Our shipping policy includes free shipping on orders over $50. Delivery times vary by location, usually 15 days to shipping.",
        "return": "Our return policy allows returns within 30 days of receipt. Items must be unused and in original packaging.",
        "privacy": "Our privacy policy ensures that your personal data is protected. We do not share your information with third parties without consent.",
    }

    # Return policy content
    return policies.get(policy_type, "Policy not found.")


@tool
def query_policy_tool(policy_type: Literal["shipping", "return", "privacy"]) -> str:
    """
    A tool for fetching the content of company policies.

    Args:
        policy_type (Literal): The type of policy to query. Options are 'shipping', 'return', or 'privacy'.

    Returns:
        str: The content of the requested policy.
    """
    return query_policy(policy_type)


def query_payment_methods() -> str:
    """
    A tool for retrieving available payment methods.

    Returns:
        str: A list of supported payment methods.
    """
    # Define available payment methods
    payment_methods = """
    We support the following payment methods:
    - Credit/Debit Cards (Visa, MasterCard, American Express)
    - PayPal
    - Apple Pay
    - Google Pay
    - Bank Transfer (for orders over $100)
    """
    return payment_methods


@tool
def query_payment_methods_tool() -> str:
    """
    A tool for retrieving available payment methods.

    Returns:
        str: A list of supported payment methods.
    """
    return query_payment_methods()
