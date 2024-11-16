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
    logger.info("Current stack (left): %s", ", ".join(left) if left else "Empty stack")
    logger.info("Operation (right): %s", right or "No operation")

    # Perform stack operations
    if right is None:
        logger.info("Stack unchanged: %s", ", ".join(left) if left else "Empty stack")
        return left
    if right == "pop":
        logger.info("Stack after pop: %s", ", ".join(left[:-1]) if left[:-1] else "Empty stack")
        return left[:-1]
    updated_stack = left + [right]
    logger.info("Stack after push: %s", ", ".join(updated_stack))
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
