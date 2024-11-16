"""
@Time ： 2024-10-28
@Auth ： Adam Lyu
"""
import shutil
import uuid
from scripts.main import setup_database
from langchain_core.messages import ToolMessage
from utils.logger import logger
from state.graph import part_graph
from utils.utilities import _print_event

# Update with the backup file so we can restart from the original place in each section
setup_database()
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "user_id": 1,  # ticket no: 7240005432906569	book ref C46E9F	passenger id 3442 587242
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


if __name__ == "__main__":
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
