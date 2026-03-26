import os
import time
from langchain_openai import ChatOpenAI
from src.schemas.state import GraphState
from src.schemas.output import WriterOutput
from src.prompts.writer_prompt import get_writer_prompt, build_feedback_section

def writer_node(state: GraphState) -> dict:
    """
    Writer 节点
    基于 Researcher 提供的关键词和 Editor 提供的反馈，撰写 SEO 优化的日语文章
    每次执行 revision_count 会自增 1。
    """
    topic = state.get("topic", "")
    target_audience = state.get("target_audience", "")
    keywords = state.get("keywords", [])
    feedback = state.get("feedback", "")
    revision_count = state.get("revision_count", 0)

    keywords_str = "、".join(keywords) if keywords else "指定なし"
    feedback_section = build_feedback_section(feedback)

    # Writer 需要一些创造力，所以 temperature 可以适当放宽到 0.7
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "dummy"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model=os.getenv("DEFAULT_MODEL", "qwen3-coder-30b"),
        temperature=0.7,
    )
    
    structured_llm = llm.with_structured_output(WriterOutput)
    prompt = get_writer_prompt()
    chain = prompt | structured_llm

    last_exception = None
    for attempt in range(3):
        try:
            result: WriterOutput = chain.invoke({
                "topic": topic,
                "target_audience": target_audience,
                "keywords": keywords_str,
                "feedback_section": feedback_section
            })
            
            # 返回更新的数据
            return {
                "draft_markdown": result.draft_markdown,
                "meta_title": result.meta_title,
                "meta_description": result.meta_description,
                "h1": result.h1,
                "revision_count": revision_count + 1
            }
        except Exception as e:
            last_exception = e
            print(f"[Writer] 生成尝试 {attempt + 1}/3 失败: {e}")
            if attempt < 2:
                time.sleep(2)

    print(f"[Writer] 3次尝试均失败，执行兜底。最后错误: {last_exception}")
    # 在异常情况下的兜底，主要是为了容错网络断开、Key 失效等问题
    return {
        "draft_markdown": f"記事生成エラーが発生しました。\nエラー詳細: {str(last_exception)}",
        "meta_title": f"エラー: {topic[:10]}",
        "meta_description": "エラーのため生成できませんでした。",
        "h1": topic,
        "revision_count": revision_count + 1
    }
