
import os
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools.product_tools import search_products
from tools.cart_tools import add_to_cart, remove_from_cart, view_cart
from tools.order_tools import checkout

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
llm = ChatOpenAI(model="gpt-4-turbo", temperature=1, api_key=os.getenv('OPENAI_API_KEY'))


class ProductAssistant:
    """Handles product search, cart management, and checkout actions."""


    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a shopping assistant specializing in helping users search for products, "
                    "manage their shopping cart, and handle checkout operations. "
                    "For sensitive actions like adding or removing items from the cart or checking out, "
                    "confirm with the user before proceeding."
                ),
                ("placeholder", "{messages}"),
            ]
        )
        # 定义工具分组
        self.safe_tools = [search_products, view_cart]
        self.sensitive_tools = [add_to_cart, remove_from_cart, checkout]

    def handle(self, action: str, query: Optional[str] = None, product_id: Optional[int] = None, user_id: int = 1):
        """
        Handle user actions such as product search, cart management, and checkout.

        Args:
            action (str): The user action. Options are 'search', 'add', 'remove', 'view', 'checkout'.
            query (str, optional): The search query for products.
            product_id (int, optional): The product ID for cart actions.
            user_id (int): The user ID (default is 1).

        Returns:
            dict: The response after executing the action.
        """
        if action == "search":
            return self._execute_tool(search_products, {"name": query}, is_sensitive=False)

        elif action == "view":
            return self._execute_tool(view_cart, {"user_id": user_id}, is_sensitive=False)

        elif action == "add":
            if not product_id:
                return {"error": "Product ID is required for 'add' action."}
            return self._execute_tool(add_to_cart, {"user_id": user_id, "product_id": product_id}, is_sensitive=True)

        elif action == "remove":
            if not product_id:
                return {"error": "Product ID is required for 'remove' action."}
            return self._execute_tool(remove_from_cart, {"user_id": user_id, "product_id": product_id}, is_sensitive=True)

        elif action == "checkout":
            return self._execute_tool(checkout, {"user_id": user_id}, is_sensitive=True)

        else:
            return {"error": f"Unsupported action: {action}"}

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
