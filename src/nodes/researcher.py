import os
import time
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import PromptTemplate
from src.schemas.state import GraphState
from src.schemas.output import ResearchOutput

def researcher_node(state: GraphState) -> dict:
    """
    SEO Researcher 节点
    基于 Tavily 搜索和 LLM 生成初步关键词和竞品洞察
    """
    topic = state.get("topic", "")
    target_audience = state.get("target_audience", "")
    keywords_preference = state.get("keywords_preference", [])

    # 初始化 LLM (通过带有 openai 接口兼容的代理)
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "dummy"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model=os.getenv("DEFAULT_MODEL", "qwen3-coder-30b"),
        temperature=0.2,
    )
    
    # 绑定结构化输出
    structured_llm = llm.with_structured_output(ResearchOutput)
    
    # 获取搜索结果
    search_results = ""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key != "tvly-...":
        try:
            search_tool = TavilySearchResults(max_results=3)
            query = f"{topic} {target_audience} {' '.join(keywords_preference)} 日語 SEO"
            results = search_tool.invoke({"query": query})
            search_results = str(results)
        except Exception as e:
            print(f"[SEO_Researcher] Tavily API Error: {e}")
            search_results = "搜索失败，无竞品信息。"
    else:
        search_results = "TAVILY_API_KEY 未配置，跳过在线搜索。"
        
    # 构建 Prompt
    prompt = PromptTemplate.from_template(
        "你是一个专业的日语 SEO 研究员。\n"
        "用户提供的主题：{topic}\n"
        "目标受众：{target_audience}\n"
        "已有关键词偏好：{keywords_preference}\n"
        "搜索引擎返回的相关竞品与背景信息：\n{search_results}\n\n"
        "请根据上述信息，提取并生成高相关性的 SEO 关键词列表（包含相关度打分和搜索意图），"
        "并用『日语』总结竞品洞察与内容建议。"
    )
    
    chain = prompt | structured_llm
    
    # 调用 LLM 返回结构化数据
    # 如果遇到解析错误或异常，需要兜底 (带3次重试)
    last_exception = None
    for attempt in range(3):
        try:
            result: ResearchOutput = chain.invoke({
                "topic": topic,
                "target_audience": target_audience,
                "keywords_preference": keywords_preference,
                "search_results": search_results
            })
            
            return {
                "keywords": [kw.term for kw in result.keywords],
                "competitor_insights": result.competitor_insights
            }
        except Exception as e:
            last_exception = e
            print(f"[SEO_Researcher] 生成尝试 {attempt + 1}/3 失败: {e}")
            if attempt < 2:
                time.sleep(2)

    print(f"[SEO_Researcher] 3次尝试均失败，执行兜底。最后错误: {last_exception}")
    # 兜底返回，避免图流转崩溃
    return {
        "keywords": keywords_preference if keywords_preference else [topic],
        "competitor_insights": "搜索agent结构化数据异常，请检查模型输出格式。"
    }
