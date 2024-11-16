"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""

from typing import Annotated, Literal, Optional, List
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from utils.logger import logger


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
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "product",
                "cart",
                "order",
            ]
        ],
        update_dialog_stack,
    ]
