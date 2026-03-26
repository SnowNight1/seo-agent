from langgraph.graph import StateGraph, START, END
from src.schemas.state import GraphState
from src.nodes.researcher import researcher_node
from src.nodes.writer import writer_node
from src.nodes.editor import editor_node


def human_review_node(state: GraphState) -> dict:
    """
    人工审核占位节点
    当多次打回重写仍未通过时，交由人工介入
    """
    print("\n" + "="*50)
    print("⚠️ [Human Review] 文章生成超出最大重写次数，需要人工介入！")
    print(f"当前 revision_count: {state.get('revision_count')}")
    print(f"最后的 Editor 反馈: {state.get('feedback')}")
    print("="*50 + "\n")
    # 可以用 input() 暂停，或者使用 interrupt 功能
    # 目前仅作为占位
    return state


def should_continue(state: GraphState) -> str:
    """
    Editor -> 下一步的路由判断函数
    返回边名称:
    - "end": 若通过，直接结束
    - "human_review": 若未通过且修改次数超过限额(>=3)，转人工
    - "revise": 打回 Writer 重写
    """
    is_approved = state.get("is_approved", False)
    revision_count = state.get("revision_count", 0)

    if is_approved:
        return "end"
    if revision_count >= 3:
        return "human_review"
    return "revise"


# 初始化图，指定状态结构为 GraphState
builder = StateGraph(GraphState)

# 添加核心节点
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)
builder.add_node("editor", editor_node)
builder.add_node("human_review", human_review_node)

# 定义正向流转的固定边
builder.add_edge(START, "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "editor")

# 从 Editor 出发定义条件边（打回重写循环）
builder.add_conditional_edges(
    "editor",
    should_continue,
    {
        "end": END,
        "human_review": "human_review",
        "revise": "writer"
    }
)

# 人工审核节点处理完毕后结束
builder.add_edge("human_review", END)

# 编译生成可执行的 graph 对象
graph = builder.compile()
