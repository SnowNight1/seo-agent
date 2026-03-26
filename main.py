import os
from dotenv import load_dotenv
from src.graph.graph import graph

def main():
    # 加载环境变量 (.env) 并覆盖同名的系统变量
    load_dotenv(override=True)
    
    print("🚀 SEO Agent 启动中...")

    # 1. 导出图拓扑可视化结构
    os.makedirs("outputs", exist_ok=True)
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        with open("outputs/graph.png", "wb") as f:
            f.write(png_bytes)
        print("🗺️  已在 outputs/graph.png 导出工作流可视化图表。")
    except Exception as e:
        print(f"⚠️ 无法导出拓扑图 (可能缺少必要的依赖或网络限制): {e}")

    # 2. 构造真是的测试输入状态
    initial_state = {
        "topic": "2026年インテリアデザイントレンド",
        "target_audience": "30代の日本人女性、インテリアに関心が高い",
        "keywords_preference": ["北欧", "サステナブル", "カラートレンド"]
    }
    
    print(f"📦 测试输入: {initial_state}")
    print("=" * 50)
    
    # 3. 真正调用执行
    result = graph.invoke(initial_state)
    
    print("=" * 50)
    print("✅ 执行完成！")
    print("\n--- 🏁 最终判决 ---")
    print(f"通过状态    : {result.get('is_approved')}")
    print(f"打回重写次数: {result.get('revision_count')}")
    print(f"SEO  得分   : {result.get('seo_score')}")
    print(f"最终反馈    : {result.get('feedback')}")
    print(f"审查者备注  : {result.get('reviewer_notes')}")
    
    print("\n--- 📝 提取的关键词 ---")
    print(", ".join(result.get("keywords", [])))
    
    print("\n--- 📖 生成正文 Markdown (预览前500字) ---")
    draft = result.get("draft_markdown", "")
    print(draft[:500] + ("..." if len(draft) > 500 else ""))
    
    # 输出完整文件
    with open("outputs/final_article.md", "w") as f:
        f.write(f"# {result.get('h1', '')}\n\n")
        f.write(f"**Meta Title:** {result.get('meta_title', '')}\n")
        f.write(f"**Meta Description:** {result.get('meta_description', '')}\n\n")
        f.write(draft)
    print("\n📄 完整文章已保存至 outputs/final_article.md")

if __name__ == "__main__":
    main()
