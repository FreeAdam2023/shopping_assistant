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
    # 使用自定义日志类记录信息
    logger.info(f"Current stack (left): {', '.join(left) if left else 'Empty stack'}")
    logger.info(f"Operation (right): {right or 'No operation'}")

    # 执行堆栈操作
    if right is None:
        logger.info(f"Stack unchanged: {', '.join(left) if left else 'Empty stack'}")
        return left
    if right == "pop":
        updated_stack = left[:-1]
        logger.info(f"Stack after pop: {', '.join(updated_stack) if updated_stack else 'Empty stack'}")
        return updated_stack
    updated_stack = left + [right]
    logger.info(f"Stack after push: {', '.join(updated_stack)}")
    return updated_stack




class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "primary_assistant",
                "product",
                "cart",
                "order",
            ]
        ],
        update_dialog_stack,
    ]
