"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""

from typing import Literal
from langchain_core.tools import tool


@tool
def query_policy(policy_type: Literal["shipping", "return", "privacy"]) -> str:
    """
    A tool for fetching the content of company policies.

    Args:
        policy_type (Literal): The type of policy to query. Options are 'shipping', 'return', or 'privacy'.

    Returns:
        str: The content of the requested policy.
    """
    # 定义政策内容
    policies = {
        "shipping": "Our shipping policy includes free shipping on orders over $50. Delivery times vary by location. usually 15 days to shipping",
        "return": "Our return policy allows returns within 30 days of receipt. Items must be unused and in original packaging.",
        "privacy": "Our privacy policy ensures that your personal data is protected. We do not share your information with third parties without consent.",
    }

    # 返回政策内容
    return policies.get(policy_type, "Policy not found.")
