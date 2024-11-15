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
        # 安全操作处理
        if action == "view":
            return self._execute_safe_tool(view_cart, {"user_id": user_id})

        # 敏感操作处理
        elif action in ["add", "remove"]:
            if not product_id:
                return {"error": "Product ID is required for 'add' or 'remove' actions."}
            tool = add_to_cart if action == "add" else remove_from_cart
            return self._execute_sensitive_tool(tool, {"user_id": user_id, "product_id": product_id})

        # 未知操作
        else:
            return {"error": f"Unsupported action: {action}"}

    def _execute_safe_tool(self, tool, params: dict):
        """
        Execute a safe tool (no confirmation required).

        Args:
            tool (Callable): The tool to execute.
            params (dict): Parameters to pass to the tool.

        Returns:
            dict: The response from the tool.
        """
        runnable = self.prompt | llm.bind_tools([tool])
        state = {"messages": [{"role": "user", "content": f"Safe action: {tool.__name__} with params {params}"}]}
        return runnable.invoke(state)

    def _execute_sensitive_tool(self, tool, params: dict):
        """
        Execute a sensitive tool (requires user confirmation).

        Args:
            tool (Callable): The tool to execute.
            params (dict): Parameters to pass to the tool.

        Returns:
            dict: The response after user confirmation.
        """
        # 模拟确认步骤
        confirmation_prompt = {
            "role": "assistant",
            "content": f"Are you sure you want to proceed with this action: {tool.__name__} with params {params}? Please confirm.",
        }
        state = {"messages": [confirmation_prompt]}

        # 将工具绑定到提示模板
        runnable = self.prompt | llm.bind_tools([tool])
        return runnable.invoke(state)
