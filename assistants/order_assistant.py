"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools.order_tools import get_order_status, checkout
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量
llm = ChatOpenAI(model="gpt-4-turbo", temperature=1, api_key=os.getenv('OPENAI_API_KEY'))


class OrderAssistant:
    """Specialized assistant for managing customer order queries and handling checkout."""

    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a specialized assistant for managing customer order queries and checkout processes. "
                    "Help users by providing detailed information about their orders based on their input. "
                    "If the user provides an order ID, retrieve details about that order. "
                    "If no order ID is provided, retrieve all orders for the given user. "
                    "For sensitive actions like checkout, confirm with the user before proceeding."
                ),
                ("placeholder", "{messages}"),
            ]
        )
        # 定义工具分组
        self.safe_tools = [get_order_status]
        self.sensitive_tools = [checkout]

    def __call__(self, state: dict):
        """
        Makes the OrderAssistant class callable.

        Args:
            state (dict): The current state, including the user's action and parameters.

        Returns:
            dict: The response after processing the action.
        """
        action = state.get("action")
        order_id = state.get("order_id")
        user_id = state.get("user_id", 1)

        return self.handle(action, order_id=order_id, user_id=user_id)

    def handle(self, action: str, order_id: int = None, user_id: int = 1):
        """
        Handle user actions such as querying order details or initiating checkout.

        Args:
            action (str): The user action. Options are 'query' or 'checkout'.
            order_id (int, optional): The order ID for queries (default: None).
            user_id (int): The user ID (default: 1).

        Returns:
            dict: The response after executing the action.
        """
        if action == "query":
            params = {"order_id": order_id, "user_id": user_id} if order_id else {"user_id": user_id}
            return self._execute_tool(get_order_status, params, is_sensitive=False)

        elif action == "checkout":
            params = {"user_id": user_id}
            return self._execute_tool(checkout, params, is_sensitive=True)

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
