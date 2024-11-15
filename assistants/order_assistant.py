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
        # 安全操作处理
        if action == "query":
            if order_id:
                params = {"order_id": order_id, "user_id": user_id}
                return self._execute_safe_tool(get_order_status, params)
            else:
                params = {"user_id": user_id}
                return self._execute_safe_tool(get_order_status, params)

        # 敏感操作处理
        elif action == "checkout":
            params = {"user_id": user_id}
            return self._execute_sensitive_tool(checkout, params)

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
