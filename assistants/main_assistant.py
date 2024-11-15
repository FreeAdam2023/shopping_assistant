"""
@Time ： 2024-10-28
@Auth ： Adam Lyu
"""
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.utilities.serpapi import SerpAPIWrapper
from tools.product_tools import search_products
from tools.policy_tools import query_policy
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量
llm = ChatOpenAI(model="gpt-4-turbo", temperature=1, api_key=os.getenv('OPENAI_API_KEY'))


class MainAssistant:
    """
    The primary shopping assistant that handles product searches, general queries, and policy-related queries.
    """

    def __init__(self):
        # 定义助手的系统提示模板
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a shopping assistant capable of handling product searches, "
                    "general knowledge queries, and policy queries. "
                    "Provide product recommendations based on user input, assist with general knowledge queries, "
                    "and respond to queries about company policies such as shipping, return, and privacy policies."
                ),
                ("placeholder", "{messages}"),
            ]
        )
        # 定义工具分组
        self.safe_tools = [
            SerpAPIWrapper(),  # 一般知识查询工具（如 Google 搜索）
            search_products,  # 产品搜索工具
            query_policy,  # 政策查询工具
        ]

    def __call__(self, state, config):
        """
        Executes the assistant logic by processing the current state and configuration.

        Args:
            state (dict): The current state of the conversation.
            config (dict): Configuration options for the assistant.

        Returns:
            dict: The response from the assistant.
        """
        # 将工具绑定到提示模板
        runnable_safe = self.prompt | llm.bind_tools(self.safe_tools)

        # 调用安全工具处理用户请求
        return self._handle_tool_execution(state, runnable_safe)

    def _handle_tool_execution(self, state, runnable_safe):
        """
        Handle the execution of safe tools.

        Args:
            state (dict): The current state of the conversation.
            runnable_safe: The runnable for safe tools.

        Returns:
            dict: The response after executing the tool.
        """
        try:
            response = runnable_safe.invoke(state)
            return response
        except Exception as e:
            # 捕获执行中的异常并返回错误消息
            return {"error": f"An error occurred during tool execution: {str(e)}"}

