"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""

from typing import Literal
from langchain_core.messages import ToolMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from utils.utilities import create_tool_node_with_fallback, create_entry_node
from assistants.product_assistant import ProductAssistant
from assistants.cart_assistant import CartAssistant
from assistants.order_assistant import OrderAssistant
from tools.product_tools import search_products
from tools.cart_tools import add_to_cart, view_cart, remove_from_cart
from tools.order_tools import checkout, get_order_status
from state.state import State

# 初始化状态图
builder = StateGraph(State)

# 工具到助手的映射配置
ASSISTANT_CONFIGS = {
    "product_search": {
        "entry_name": "Product Search Assistant",
        "node_name": "product_search",
        "assistant_class": ProductAssistant,
        "tools": [search_products],
    },
    "cart_management": {
        "entry_name": "Cart Management Assistant",
        "node_name": "cart_management",
        "assistant_class": CartAssistant,
        "safe_tools": [view_cart],
        "sensitive_tools": [add_to_cart, remove_from_cart],
    },
    "order_query": {
        "entry_name": "Order Query Assistant",
        "node_name": "order_query",
        "assistant_class": OrderAssistant,
        "tools": [checkout, get_order_status],
    },
}

# 动态添加助手逻辑到状态图
for key, config in ASSISTANT_CONFIGS.items():
    # 添加入口节点
    builder.add_node(
        f"enter_{key}",
        create_entry_node(config["entry_name"], key),
    )

    # 检查并实例化助手类
    assistant_instance = config["assistant_class"]()
    if not callable(assistant_instance):
        raise TypeError(
            f"Expected {config['assistant_class']} to return a callable, but got {type(assistant_instance)}"
        )

    # 添加助手节点
    builder.add_node(config["node_name"], assistant_instance)
    builder.add_edge(f"enter_{key}", config["node_name"])

    # 动态添加工具节点（安全和敏感工具）
    for tool_type in ["safe_tools", "sensitive_tools"]:
        if tool_type in config:
            node_name = f"{key}_{tool_type}"
            tools_node = create_tool_node_with_fallback(config[tool_type])
            builder.add_node(node_name, tools_node)
            builder.add_edge(config["node_name"], node_name)

    # 定义动态路由逻辑
    def route(state: State, key=key):
        """Route logic for the specific assistant."""
        route_result = tools_condition(state)
        if route_result == END:
            return END
        tool_calls = state["messages"][-1].get("tool_calls", [{}])
        if tool_calls:
            called_tool = tool_calls[0].get("name")
            sensitive_tool_names = [
                tool.__name__ for tool in config.get("sensitive_tools", [])
            ]
            return (
                f"{key}_sensitive_tools"
                if called_tool in sensitive_tool_names
                else f"{key}_safe_tools"
            )
        return END

    # 添加条件路由
    builder.add_conditional_edges(
        config["node_name"],
        route,
        [
            f"{key}_safe_tools" if "safe_tools" in config else None,
            f"{key}_sensitive_tools" if "sensitive_tools" in config else None,
            END,
        ],
    )

# 主助手逻辑节点
builder.add_node("primary_assistant", create_entry_node("Main Assistant", "primary"))
builder.add_edge(START, "primary_assistant")

# 工具到助手的映射
TOOL_TO_ASSISTANT_MAP = {
    "search_products": "enter_product_search",
    "add_to_cart": "enter_cart_management",
    "view_cart": "enter_cart_management",
    "remove_from_cart": "enter_cart_management",
    "checkout": "enter_order_query",
    "get_order_status": "enter_order_query",
}


# 主助手路由逻辑
def route_primary_assistant(state: State):
    """Route to the appropriate sub-assistants."""
    tool_calls = state["messages"][-1].get("tool_calls", []) if state.get("messages") else []
    if tool_calls:
        tool_name = tool_calls[0].get("name")
        return TOOL_TO_ASSISTANT_MAP.get(tool_name, END)
    return END


builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    list(TOOL_TO_ASSISTANT_MAP.values()) + [END],
)

# 编译状态图
graph = builder.compile()
