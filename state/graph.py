"""
@Time ： 2024-10-28
@Auth ： Adam Lyu
"""
from typing import Literal

from langchain_core.messages import ToolMessage
from langgraph.constants import START, END

from assistants.expert_assistant import CompleteOrEscalate, cart_safe_tools, cart_sensitive_tools, \
    cart_runnable, Assistant, product_safe_tools, product_sensitive_tools, \
    product_runnable, order_safe_tools, order_sensitive_tools, order_runnable, \
    ToProductAssistant, \
    ToCartAssistant, ToOrderAssistant, primary_assistant_tools, assistant_runnable
from state.state import State
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from utils.utilities import create_tool_node_with_fallback, create_entry_node

builder = StateGraph(State)


def user_info(state: State):
    return {"user_info": {"user_id": 1,  "gender": 'Female', "age": 25, "name": 'Annie',
                          "address": "1375 Baseline Rd, Ottawa, ON K2C 3G1 Canada",}}


builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")

# Product assistant
builder.add_node(
    "enter_product",
    create_entry_node("Product Searching and Recommendation Assistant", "product"),
)
builder.add_node("product", Assistant(product_runnable))
builder.add_edge("enter_product", "product")
builder.add_node(
    "product_sensitive_tools",
    create_tool_node_with_fallback(product_sensitive_tools),
)
builder.add_node(
    "product_safe_tools",
    create_tool_node_with_fallback(product_safe_tools),
)


def route_product(
        state: State,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    safe_toolnames = [t.name for t in product_safe_tools]
    if all(tc["name"] in safe_toolnames for tc in tool_calls):
        return "product_safe_tools"
    return "product_sensitive_tools"


builder.add_edge("product_sensitive_tools", "product")
builder.add_edge("product_safe_tools", "product")
builder.add_conditional_edges(
    "product",
    route_product,
    ["product_sensitive_tools", "product_safe_tools", "leave_skill", END],
)


# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the main assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. "
                        "Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }


builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")

# Cart assistant

builder.add_node(
    "enter_cart",
    create_entry_node("Cart Assistant", "cart"),
)
builder.add_node("cart", Assistant(cart_runnable))
builder.add_edge("enter_cart", "cart")
builder.add_node(
    "cart_safe_tools",
    create_tool_node_with_fallback(cart_safe_tools),
)
builder.add_node(
    "cart_sensitive_tools",
    create_tool_node_with_fallback(cart_sensitive_tools),
)


def route_cart(
        state: State,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    safe_toolnames = [t.name for t in cart_safe_tools]
    if all(tc["name"] in safe_toolnames for tc in tool_calls):
        return "cart_safe_tools"
    return "cart_sensitive_tools"


builder.add_edge("cart_sensitive_tools", "cart")
builder.add_edge("cart_safe_tools", "cart")
builder.add_conditional_edges(
    "cart",
    route_cart,
    [
        "cart_safe_tools",
        "cart_sensitive_tools",
        "leave_skill",
        END,
    ],
)

# Order assistant
builder.add_node(
    "enter_order", create_entry_node("Order Assistant", "order")
)
builder.add_node("order", Assistant(order_runnable))
builder.add_edge("enter_order", "order")
builder.add_node(
    "order_safe_tools",
    create_tool_node_with_fallback(order_safe_tools),
)
builder.add_node(
    "order_sensitive_tools",
    create_tool_node_with_fallback(order_sensitive_tools),
)


def route_order(
        state: State,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    tool_names = [t.name for t in order_safe_tools]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "order_safe_tools"
    return "order_sensitive_tools"


builder.add_edge("order_sensitive_tools", "order")
builder.add_edge("order_safe_tools", "order")
builder.add_conditional_edges(
    "order",
    route_order,
    ["leave_skill", "order_safe_tools", "order_sensitive_tools", END],
)

# Primary assistant
builder.add_node("primary_assistant", Assistant(assistant_runnable))
builder.add_node(
    "primary_assistant_tools", create_tool_node_with_fallback(primary_assistant_tools)
)


def route_primary_assistant(
        state: State,
):
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToProductAssistant.__name__:
            return "enter_product"
        elif tool_calls[0]["name"] == ToCartAssistant.__name__:
            return "enter_cart"
        elif tool_calls[0]["name"] == ToOrderAssistant.__name__:
            return "enter_order"
        return "primary_assistant_tools"
    raise ValueError("Invalid route")


# The assistant can route to one of the delegated assistants,
# directly use a tool, or directly respond to the user
builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    [
        "enter_product",
        "enter_cart",
        "enter_order",
        "primary_assistant_tools",
        END,
    ],
)
builder.add_edge("primary_assistant_tools", "primary_assistant")


# Each delegated workflow can directly respond to the user
# When the user responds, we want to return to the currently active workflow
def route_to_workflow(
        state: State,
) -> Literal[
    "primary_assistant",
    "product",
    "cart",
    "order",
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]


builder.add_conditional_edges("fetch_user_info", route_to_workflow)

# Compile graph
memory = MemorySaver()
part_graph = builder.compile(
    checkpointer=memory,
    # Let the user approve or deny the use of sensitive tools
    interrupt_before=[
        "product_sensitive_tools",
        "cart_sensitive_tools",
        "order_sensitive_tools",
    ],
)
