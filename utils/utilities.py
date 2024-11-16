"""
@Time ： 2024-10-27
@Auth ： Adam Lyu
"""

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from typing import List, Callable
from state.state import State


def _print_event(event: dict, _printed: set, max_length=1500):
    """
    Print current state and message for debugging.

    Args:
        event (dict): Current event in the state machine.
        _printed (set): Set of already printed message IDs to avoid duplicates.
        max_length (int): Max length of the message to print.
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def handle_tool_error(state: dict) -> dict:
    """
    Handle errors occurring during tool execution.

    Args:
        state (dict): Current state containing error information.

    Returns:
        dict: A dictionary with error messages for each tool call.
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\nPlease fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(
    tools: List[Callable],
    fallback_handler: Callable = None,
    exception_key: str = "error"
) -> ToolNode:
    """
    Create a ToolNode with fallback logic for handling tool errors.

    Args:
        tools (List[Callable]): A list of tools to include in the node.
        fallback_handler (Callable): A fallback function to handle tool errors (default: `handle_tool_error`).
        exception_key (str): The key to store exceptions in fallback handling.

    Returns:
        ToolNode: A configured ToolNode with fallbacks.
    """
    if fallback_handler is None:
        fallback_handler = handle_tool_error

    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(fallback_handler)], exception_key=exception_key
    )


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    """
    Create an entry node for an assistant.

    Args:
        assistant_name (str): The name of the assistant (e.g., 'Product Search Assistant').
        new_dialog_state (str): The new dialog state for the assistant.

    Returns:
        Callable: A function that generates the entry node data.
    """
    def entry_node(state: State) -> dict:
        """
        Generate the entry node's initial message and dialog state.

        Args:
            state (State): The current state containing messages and tool calls.

        Returns:
            dict: A dictionary with the assistant's messages and dialog state.
        """
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]

        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the add, update, other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node
