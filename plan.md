## 🚀 多智能体 SEO 内容编排系统：开发里程碑

### 📅 阶段 1：环境搭建与核心状态机（Day 1）
**目标：** 建立项目骨架，定义 Agent 之间共享的“黑板”（State）。

| 步骤 | 任务名称 | 技术重点 | Coding Agent 提示词方向 |
| :--- | :--- | :--- | :--- |
| 1.1 | **项目初始化** | WSL2, Poetry/Pipenv | "创建一个 Python 项目，配置 LangGraph, LangChain 和 Pydantic 环境。" |
| 1.2 | **定义 GraphState** | TypedDict, Pydantic | "定义一个 GraphState 类，包含 topic, keywords, draft, check_result 等字段。" |
| 1.3 | **基础图结构构建** | LangGraph StateGraph | "搭建一个包含 Start -> Node_A -> End 的最小化 LangGraph 工作流。" |

---

### 📅 阶段 2：单体智能体“原子化”开发（Day 2-3）
**目标：** 让每个 Agent 能够独立工作，并严格输出 **JSON**。

* **[Node 1] SEO 专家**：集成 **Tavily/Serper API**，根据主题搜索关键词。
* **[Node 2] 本地化文案**：使用系统提示词（System Prompt）确保日语表达的地道性。
* **[Node 3] 结构化输出控制**：使用 `.with_structured_output(PydanticModel)`。

> **Definition of Done (DoDone):** 每个 Node 都能接收 State 并返回更新后的 JSON 字典，不报错。

---

### 📅 阶段 3：编排“反馈循环”（Day 4）—— **核心攻坚**
**目标：** 实现图片的“编辑打回重写”逻辑，这是磨练多智能体开发的关键。

* **逻辑实现**：编写一个 `should_continue` 函数。
* **判断准则**：
    * 如果 `is_approved == True` ➡️ 结束流。
    * 如果 `is_approved == False` ➡️ 回到 **Writer Node**，并带上 `feedback` 意见。
* **防止死循环**：在 State 中加入 `revision_count`，超过 3 次强制结束。

---

### 📅 阶段 4：工具集成与本地化增强（Day 5）
**目标：** 给智能体配上“手脚”。

* **SEO 检查工具**：编写一个 Python 函数，检查生成的 Markdown 里是否包含指定的关键词。
* **本地化术语库**：挂载一个本地 JSON 文件（如 Coohom 相关的日语专业术语），让 Agent 在生成前先检索。

---

### 📅 阶段 5：前端展示与持久化（Day 6-7）
**目标：** 让项目看起来像一个成品。

* **UI 开发**：使用 **Streamlit** 创建一个简单的输入框和过程展示（可以使用 `langgraph` 的内置绘图功能显示当前进度）。
* **持久化 (Checkpointer)**：学习 LangGraph 的 `MemorySaver`，实现可以“断点续传”的对话任务。

---

### 🛠️ 建议使用的工具组合
* **Orchestration**: `langgraph` (必须)
* **LLM Interface**: `langchain-openai` 或 `langchain-anthropic`
* **Search Engine**: `tavily-python` (对 AI 极其友好)
* **Visualizer**: `grandalf` (用于在终端打印 Graph 图)
。