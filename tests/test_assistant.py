"""
@Time ： 2024-10-28
@Auth ： Adam Lyu
"""
import shutil
import uuid
from scripts.main import setup_database
from langchain_core.messages import ToolMessage
from utils.logger import logger
from utils.utilities import _print_event
from state.graph import part_graph

# Update with the backup file so we can restart from the original place in each section
setup_database()
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # fetch the user's information
        "user_id": 1,
        "gender": 'Female',
        "age": 25,
        "name": 'Annie',
        "address": "1375 Baseline Rd, Ottawa, ON K2C 3G1 Canada",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}
#
# tutorial_questions = [
#     "你好，有哪些类别产品我可以选择？",
#     "我喜欢电子产品",
#     "我想看下最新的手机产品",
#     "帮我把最贵的添加到购物车中",
#     "今天天气怎么样？",
#     "我还想买衣服，帮我推荐一些T-shirt",
#     "好的，帮我把最便宜的添加到购物车",
#     "现在我的购物车里有什么商品",
#     "将购物车中的内容加倍",
#     "移除 T-shirt 的产品，我不想要了",
#     "好的可以下单了",
#     "我可以看下订单信息吗",
#     "多久能送到？",
#     "我想修改下发货地址到 169 Rue Galipeau, Thurso, QC J0X 3B0",
#     "我可以取消订单吗",
#     "我改主意了，帮我取消订单",
#     "查看我的订单"
# ]

tutorial_questions = [
    "Hello, what categories of products can I choose from?",
    "I like electronic products.",
    "I want to see the latest mobile products.",
    "Help me add the most expensive one to the shopping cart.",
    "How's the weather today?",
    "I also want to buy clothes, recommend some T-shirts for me.",
    "Alright, help me add the cheapest one to the shopping cart.",
    "What items are currently in my shopping cart?",
    "Double the contents of the shopping cart.",
    "Okay, I’m ready to place the order.",
    "Can I see the order details?",
    "How long will delivery take?",
    "I want to change the shipping address to 169 Rue Galipeau, Thurso, QC J0X 3B0.",
    "Can I cancel the order?",
    "I changed my mind, help me cancel the order.",
    "View my order."
]



def test_assitant():
    _printed = set()
    for question in tutorial_questions:
        # question = input("input question please\n\n")
        events = part_graph.stream(
            {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
            logger.debug(f"Event processed: {event}")
        snapshot = part_graph.get_state(config)
        while snapshot.next:
            # 如果有中断，记录当前调用的 tool_call_id 和事件
            if 'tool_calls' in event["messages"][-1]:
                for tool_call in event["messages"][-1]['tool_calls']:
                    logger.debug(f"Handling tool call: {tool_call['id']} for function {tool_call['name']}")
            # 继续对用户请求的操作
            try:
                user_input = input("Do you approve of the above actions? Type 'y' to continue;"
                                   " otherwise, explain your requested changed.\n\n")
            except:
                user_input = "y"
            if user_input.strip() == "y":
                result = part_graph.invoke(
                    None,
                    config,
                )
                logger.debug(f"Invoke result: {result}")
            else:
                result = part_graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
                logger.debug(f"Invoke result after user denial: {result}")
            snapshot = part_graph.get_state(config)
            logger.debug(f"New snapshot state: {snapshot}")


if __name__ == "__main__":
    test_assitant()
