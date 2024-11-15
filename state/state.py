"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""

from typing import Annotated, Literal, Optional, List
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
import logging

# 初始化日志记录器
logger = logging.getLogger("StateLogger")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def update_dialog_stack(left: List[str], right: Optional[str]) -> List[str]:
    """
    Push or pop the state stack based on the given operation.

    Args:
        left (List[str]): Current state stack.
        right (Optional[str]): Operation ("pop" to remove the last state, or a new state to push).

    Returns:
        List[str]: Updated state stack.
    """
    logger.info("Current stack (left): %s", left)
    logger.info("Operation (right): %s", right)

    # Perform stack operations
    if right is None:
        logger.info("Updated stack: %s", left)
        return left
    if right == "pop":
        logger.info("Updated stack: %s", left[:-1])
        return left[:-1]
    updated_stack = left + [right]
    logger.info("Updated stack: %s", updated_stack)
    return updated_stack


class State(TypedDict):
    """
    Represents the state of the assistants's dialog and context.
    """
    messages: Annotated[List[AnyMessage], add_messages]
    user_info: Optional[str]  # Optional user information
    dialog_state: Annotated[
        List[str],  # Support flexible states, not limited to predefined ones
        update_dialog_stack,
    ]
