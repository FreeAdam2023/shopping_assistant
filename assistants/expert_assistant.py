"""
@Time ： 2024-10-28
@Auth ： Adam Lyu
"""
import os
from datetime import datetime

# from langchain.utilities.serpapi import SerpAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

from state.state import State
from pydantic import BaseModel, Field

from tools.policy_tools import query_policy_tool
from tools.product_tools import search_and_recommend_products_tool, list_categories_tool
from tools.order_tools import (search_orders_tool, checkout_order_tool, update_delivery_address_tool, cancel_order_tool,
                               get_recent_orders_tool)
from tools.cart_tools import add_to_cart_tool, view_cart_tool, remove_from_cart_tool

from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量

llm = ChatOpenAI(model="gpt-4-turbo", temperature=1, api_key=os.getenv('OPENAI_API_KEY'))  # gpt-4-turbo  gpt-3.5-turbo


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            print(f"state -> {state}")
            # print(json.dumps(state, indent=4, ensure_ascii=False))
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }


# product assistant

product_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a product assistant specializing in helping users search for products, provice categories options, "
            "If the user does not provide a specific query but asks about product categories, always call `list_categories_tool`."
            "Don’t make up products or categories that don’t exist"
            "\n\nCurrent user information:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}."
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            "\n\nIf the user needs help, and none of your tools are appropriate for it, then"
            ' "CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

product_safe_tools = [search_and_recommend_products_tool, list_categories_tool]
product_sensitive_tools = []
product_tools = product_safe_tools + product_sensitive_tools
product_runnable = product_assistant_prompt | llm.bind_tools(
    product_tools + [CompleteOrEscalate]
)

# order  Assistant

order_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for managing customer order queries and checkout processes. "
            "Help users by providing detailed information about their orders based on their input. "
            "If the user provides an order ID, retrieve details about that order. "
            "If no order ID is provided, retrieve all orders for the given user. "
            "For sensitive actions like checkout order, cancel order, change order address, "
            "confirm with the user before proceeding."
            "\n\nCurrent user information:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}."
            '\n\nIf the user needs help, and none of your tools are appropriate for it, '
            'then "CompleteOrEscalate" the dialog to the host assistant.'
            " Do not waste the user's time. Do not make up invalid tools or functions."
            "\n\nSome examples for which you should CompleteOrEscalate:\n"
            " - 'what's the weather like this time of year?'\n"
            " - 'never mind i think I'll add more products'\n"
            " - 'order confirmed'",
        ),
        ("placeholder", "{messages}"),
    ]

).partial(time=datetime.now)

order_safe_tools = [search_orders_tool, get_recent_orders_tool]
order_sensitive_tools = [checkout_order_tool, update_delivery_address_tool, cancel_order_tool]
order_tools = order_safe_tools + order_sensitive_tools
order_runnable = order_assistant_prompt | llm.bind_tools(
    order_tools + [CompleteOrEscalate]
)

# Cart Assistant
cart_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a cart assistant that helps users manage their shopping cart. "
            "You can assist with adding items to the cart, removing items from the cart, or viewing the cart's contents. "
            "Provide clear feedback to the user about the actions you perform. For sensitive actions like adding or removing items, "
            "confirm with the user before proceeding."
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant."
            " Remember that a task isn't completed until after the relevant tool has successfully been used."
            "\n\nCurrent user information:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}."
            "\n\nIf the user needs help, and none of your tools are appropriate for it, then "
            '"CompleteOrEscalate" the dialog to the host assistant. Do not waste the user\'s time. Do not make up invalid tools or functions.'
            "\n\nSome examples for which you should CompleteOrEscalate:\n"
            " - 'what's the weather like this time of year?'\n"
            " - 'What products are available?'\n"
            " - 'never mind i think I'll change order'\n"
            " - 'Oh wait i haven't find my product yet i'll do that first'\n"
            " - 'add product confirmed'",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

cart_safe_tools = [view_cart_tool]
cart_sensitive_tools = [
    add_to_cart_tool,
    remove_from_cart_tool,
]
cart_tools = cart_safe_tools + cart_sensitive_tools
cart_runnable = cart_assistant_prompt | llm.bind_tools(
    cart_tools + [CompleteOrEscalate]
)


# Primary Assistant
class ToProductAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle product-related queries."""
    name: str = Field(description="The name of the product. Optional, can be empty.")
    category: str = Field(description="The category of the product. Optional, can be empty.")
    price_range: str = Field(description="The price range of the product. Optional, can be empty.")
    request: str = Field(
        description="Any additional information or requests from the user regarding products or categories"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "",
                "category": "",
                "price_range": "",
                "request": "Show me the product categories available.",
            }
        }


class ToOrderAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle car rental bookings."""

    new_address: str = Field(description="The new_address of the order.")

    request: str = Field(
        description="Any additional information or requests from the user regarding the order"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "new_address": "2023-07-01",
                "request": "change to new address",
            }
        }


class ToCartAssistant(BaseModel):
    """Transfer work to a specialized assistant to handle hotel bookings."""

    product_id: int = Field(description="The id of the product which related to cart.")
    quantity: int = Field(description="The count of product which will add to cart.")

    request: str = Field(
        description="Any additional information or requests from the user regarding the cart"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 3,
                "request": "...",
            }
        }


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a shopping assistant handling general queries about shopping, company policies, and products. "
            "You can delegate specific tasks to specialized assistants for managing orders, carts, or product queries. "
            "For example:\n"
            "- If the query involves adding or removing products to/from the cart or viewing the cart, "
            "delegate the task to the `ToCartAssistant`.\n"
            "- If the query involves searching for products or viewing product categories, "
            "delegate the task to the `ToProductAssistant`.\n"
            "- If the query involves managing orders (e.g., checking orders, updating delivery addresses, canceling orders), "
            "delegate the task to the `ToOrderAssistant`.\n"
            "\nAlways double-check the database before concluding that information is unavailable. "
            "Do not make up invalid categories, product names, or order details. "
            "Provide clear instructions to specialized assistants and ensure seamless task completion.\n"
            "\n\nCurrent user information:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

primary_assistant_tools = [
    TavilySearchResults(max_results=1, tavily_api_key=os.getenv('TAVILY_API_KEY')),
    query_policy_tool,
]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToProductAssistant,
        ToOrderAssistant,
        ToCartAssistant,
    ]
)
