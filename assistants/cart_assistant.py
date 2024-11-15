"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools.cart_tools import add_to_cart, view_cart, remove_from_cart
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量
llm = ChatOpenAI(model="gpt-4-turbo", temperature=1, api_key=os.getenv('OPENAI_API_KEY'))


class CartAssistant:
    """Specialized assistant for managing the shopping cart."""

    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a shopping assistant that helps users manage their shopping cart. "
                    "You can assist with adding items to the cart, removing items from the cart, or viewing the cart's contents. "
                    "Provide clear feedback to the user about the actions you perform. For sensitive actions like adding or removing items, "
                    "confirm with the user before proceeding."
                ),
                ("placeholder", "{messages}"),
            ]
        )
        # 定义工具分组
        self.safe_tools = [view_cart]
        self.sensitive_tools = [add_to_cart, remove_from_cart]

    def __call__(self, state: dict):
        """
        Makes the CartAssistant class callable.

        Args:
            state (dict): The current state, including the user's action and parameters.

        Returns:
            dict: The response after processing the action.
        """
        action = state.get("action")
        product_id = state.get("product_id")
        user_id = state.get("user_id", 1)

        return self.handle(action, product_id=product_id, user_id=user_id)

    def handle(self, action: str, product_id: int = None, user_id: int = 1):
        """
        Handle user actions such as viewing the cart, adding items, or removing items.

        Args:
            action (str): The user action. Options are 'add', 'remove', or 'view'.
            product_id (int, optional): The product ID for cart actions (default: None).
            user_id (int): The user ID (default: 1).

        Returns:
            dict: The response after executing the action.
        """
        # 操作映射到工具
        tool_mapping = {
            "view": (view_cart, False),
            "add": (add_to_cart, True),
            "remove": (remove_from_cart, True),
        }

        # 确认操作是否支持
        if action not in tool_mapping:
            return {"error": f"Unsupported action: {action}"}

        tool, is_sensitive = tool_mapping[action]

        # 检查必需参数
        if action in ["add", "remove"] and not product_id:
            return {"error": f"Product ID is required for '{action}' action."}

        # 执行工具
        params = {"user_id": user_id}
        if product_id:
            params["product_id"] = product_id

        return self._execute_tool(tool, params, is_sensitive)

    def _execute_tool(self, tool, params: dict, is_sensitive: bool):
        """
        Execute a tool (safe or sensitive).

        Args:
            tool (Callable): The tool to execute.
            params (dict): Parameters to pass to the tool.
            is_sensitive (bool): Whether the tool requires confirmation.

        Returns:
            dict: The response after executing the tool.
        """
        state = {"messages": []}

        if is_sensitive:
            # 添加确认消息
            state["messages"].append(
                {
                    "role": "assistant",
                    "content": f"Are you sure you want to execute: {tool.__name__} with parameters {params}? Please confirm."
                }
            )
        else:
            # 添加直接操作消息
            state["messages"].append(
                {
                    "role": "user",
                    "content": f"Executing: {tool.__name__} with parameters {params}."
                }
            )

        # 将工具绑定到提示模板并执行
        runnable = self.prompt | llm.bind_tools([tool])
        return runnable.invoke(state)
