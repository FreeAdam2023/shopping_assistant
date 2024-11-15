"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
from langgraph.constants import END

from state.state_graph import graph
from state.state import State

if __name__ == "__main__":
    # 初始化状态
    state = State()

    # 运行状态图
    while True:
        try:
            result = graph.execute(state)
            if result == END:
                print("Session ended.")
                break
        except Exception as e:
            print(f"Error: {e}")
