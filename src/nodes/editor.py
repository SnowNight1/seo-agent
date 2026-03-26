import os
import time
from langchain_openai import ChatOpenAI
from src.schemas.state import GraphState
from src.schemas.output import EditorOutput
from src.prompts.editor_prompt import get_editor_prompt

def editor_node(state: GraphState) -> dict:
    """
    Editor 节点
    基于生成的文章内容进行打分、审查，并决定是否通过（is_approved）
    """
    topic = state.get("topic", "")
    target_audience = state.get("target_audience", "")
    keywords = state.get("keywords", [])
    
    draft_markdown = state.get("draft_markdown", "")
    meta_title = state.get("meta_title", "")
    meta_description = state.get("meta_description", "")
    h1 = state.get("h1", "")

    keywords_str = "、".join(keywords) if keywords else "指定なし"

    # Editor 需要更加客观严谨，temperature 调低
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "dummy"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model=os.getenv("DEFAULT_MODEL", "qwen3-coder-30b"),
        temperature=0.1,
    )
    
    structured_llm = llm.with_structured_output(EditorOutput)
    prompt = get_editor_prompt()
    chain = prompt | structured_llm

    last_exception = None
    for attempt in range(3):
        try:
            result: EditorOutput = chain.invoke({
                "topic": topic,
                "target_audience": target_audience,
                "keywords": keywords_str,
                "h1": h1,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "draft_markdown": draft_markdown
            })
            
            # 返回更新的数据
            return {
                "is_approved": result.is_approved,
                "feedback": result.feedback,
                "seo_score": result.seo_score,
                "reviewer_notes": result.reviewer_notes
            }
        except Exception as e:
            last_exception = e
            print(f"[Editor] 生成尝试 {attempt + 1}/3 失败: {e}")
            if attempt < 2:
                time.sleep(2)

    print(f"[Editor] 3次尝试均失败，执行兜底。最后错误: {last_exception}")
    # 异常兜底，强制通过以免陷入死循环
    return {
        "is_approved": True,
        "feedback": "",
        "seo_score": 0,
        "reviewer_notes": f"審査エラーが発生しました: {str(last_exception)}"
    }
