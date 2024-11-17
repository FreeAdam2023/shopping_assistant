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

# "有哪些类别产品我可以选择？"
# "今天渥太华天气怎么样"
# "我喜欢电子产品"
# "我想看下最新的手机产品"
# "Apple iPhone 15 Pro Max"
# "帮我把这个产品添加到购物车"
# "我的购物车里面有哪些商品"

if __name__ == "__main__":
    _printed = set()
    while True:
        question = input("input question please\n\n")
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
