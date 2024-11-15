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
        # 工具集合
        self.tools = {
            "search_products": search_products,  # 产品搜索工具
            "query_policy": query_policy,  # 政策查询工具
            "general_query": SerpAPIWrapper(),  # 一般知识查询工具
        }

    def __call__(self, state):
        """
        Makes the MainAssistant class callable.

        Args:
            state (dict): The current state of the conversation.

        Returns:
            dict: The response after processing the user's request.
        """
        action = state.get("action")  # 动作类型
        tool_name = state.get("tool")  # 目标工具名称

        # 检查工具是否支持
        if tool_name not in self.tools:
            return {"error": f"Unsupported tool: {tool_name}"}

        # 获取工具并执行
        tool = self.tools[tool_name]
        return self._execute_tool(state, tool)

    def _execute_tool(self, state, tool):
        """
        Executes the specified tool with the provided state.

        Args:
            state (dict): The current state of the conversation.
            tool (Callable): The tool to execute.

        Returns:
            dict: The response from the tool or an error message.
        """
        try:
            # 将工具绑定到提示模板
            runnable = self.prompt | llm.bind_tools([tool])
            # 执行工具
            return runnable.invoke(state)
        except Exception as e:
            # 捕获执行中的异常并返回详细错误信息
            tool_name = getattr(tool, "__name__", "unknown_tool")
            return {
                "error": f"An error occurred during execution of {tool_name}: {str(e)}"
            }
