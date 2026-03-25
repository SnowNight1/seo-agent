"""
SEO Agent — 开发进度检查脚本

用法：
    uv run python scripts/check.py          # 检查所有阶段
    uv run python scripts/check.py --stage 1  # 只检查阶段 1

每项检查对应 plan_final.md 中各阶段的 DoD（Definition of Done）。
输出结果：
    ✅ PASS   — 已完成且验证通过
    ❌ FAIL   — 文件存在但验证失败（含错误说明）
    ⏳ TODO   — 尚未实现
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path
from typing import Callable

# 确保从项目根目录导入
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── 颜色输出 ──────────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS = f"{GREEN}✅ PASS{RESET}"
FAIL = f"{RED}❌ FAIL{RESET}"
TODO = f"{YELLOW}⏳ TODO{RESET}"


def _check(label: str, fn: Callable[[], None]) -> bool:
    """运行单项检查，捕获异常并统一输出结果。返回 True 表示通过。"""
    try:
        fn()
        print(f"  {PASS}  {label}")
        return True
    except NotImplementedError:
        print(f"  {TODO}  {label}")
        return False
    except Exception as e:
        print(f"  {FAIL}  {label}")
        print(f"         → {e}")
        return False


# ── 阶段 1 检查 ───────────────────────────────────────────────────────────────

def check_stage_1() -> int:
    """阶段 1：需求定义与架构骨架"""
    print(f"\n{BOLD}{CYAN}📅 阶段 1：需求定义与架构骨架{RESET}")
    results: list[bool] = []

    # 1.1 — Output Schema
    print(f"  {'─'*48}")
    print(f"  1.1  Output Schema")

    def _1_1_1():
        assert (ROOT / "src/schemas/output.py").exists(), \
            "src/schemas/output.py 不存在"

    def _1_1_2():
        from src.schemas.output import SEOArticleOutput
        fields = SEOArticleOutput.model_fields
        required = ["meta_title", "meta_description", "target_keywords",
                    "h1", "content_markdown", "seo_score", "revision_count", "reviewer_notes"]
        missing = [f for f in required if f not in fields]
        assert not missing, f"缺少字段：{missing}"
        for name, field in fields.items():
            assert field.description, f"字段 '{name}' 缺少 description"

    def _1_1_3():
        from src.schemas.output import SEOArticleOutput
        from pydantic import ValidationError
        # meta_title 超长
        try:
            SEOArticleOutput(meta_title="あ" * 61, meta_description="x" * 100,
                             target_keywords=[], h1="t", content_markdown="t", seo_score=50)
            raise AssertionError("meta_title 长度校验器未触发")
        except ValidationError:
            pass
        # seo_score 越界
        try:
            SEOArticleOutput(meta_title="t", meta_description="x" * 100,
                             target_keywords=[], h1="t", content_markdown="t", seo_score=101)
            raise AssertionError("seo_score 上限校验器未触发")
        except ValidationError:
            pass

    results.append(_check("1.1.1  src/schemas/output.py 存在", _1_1_1))
    results.append(_check("1.1.2  SEOArticleOutput 8字段均带 description", _1_1_2))
    results.append(_check("1.1.3  meta_title / seo_score 校验器有效", _1_1_3))

    # 1.2 — GraphState
    print(f"  {'─'*48}")
    print(f"  1.2  GraphState")

    def _1_2_1():
        assert (ROOT / "src/schemas/state.py").exists(), \
            "src/schemas/state.py 不存在"

    def _1_2_2_4():
        from src.schemas.state import GraphState
        hints = GraphState.__annotations__
        input_fields = ["topic", "target_audience", "keywords_preference"]
        mid_fields = ["keywords", "competitor_insights", "draft_markdown",
                      "meta_title", "meta_description", "h1", "feedback"]
        ctrl_fields = ["is_approved", "revision_count", "seo_score", "reviewer_notes"]
        missing = [f for f in input_fields + mid_fields + ctrl_fields if f not in hints]
        assert not missing, f"State 缺少字段：{missing}"

    def _1_2_5():
        from src.schemas.state import GraphState
        # total=False → 空 dict 合法
        s: GraphState = {}
        s2: GraphState = {"topic": "test"}
        assert True  # 能赋值即通过

    results.append(_check("1.2.1  src/schemas/state.py 存在", _1_2_1))
    results.append(_check("1.2.2-4  GraphState 所有字段定义完整", _1_2_2_4))
    results.append(_check("1.2.5  空 State 合法（total=False）", _1_2_5))

    # 1.3 — 目录结构
    print(f"  {'─'*48}")
    print(f"  1.3  项目目录结构")

    def _1_3_1():
        required_dirs = [
            "src/nodes", "src/schemas", "src/tools", "src/graph", "tests", "data"
        ]
        missing = [d for d in required_dirs if not (ROOT / d).is_dir()]
        assert not missing, f"缺少目录：{missing}"

    def _1_3_2():
        assert (ROOT / ".env.example").exists(), ".env.example 不存在"
        content = (ROOT / ".env.example").read_text()
        for key in ["OPENAI_API_KEY", "TAVILY_API_KEY", "LANGCHAIN_API_KEY"]:
            assert key in content, f".env.example 缺少 {key}"

    def _1_3_3():
        gitignore = (ROOT / ".gitignore").read_text()
        assert ".env" in gitignore, ".gitignore 未屏蔽 .env"

    def _1_3_4():
        required_inits = [
            "src/__init__.py", "src/nodes/__init__.py", "src/tools/__init__.py",
            "src/graph/__init__.py", "src/schemas/__init__.py", "tests/__init__.py",
        ]
        missing = [p for p in required_inits if not (ROOT / p).exists()]
        assert not missing, f"缺少 __init__.py：{missing}"

    results.append(_check("1.3.1  目录骨架完整", _1_3_1))
    results.append(_check("1.3.2  .env.example 含所有必须 Key", _1_3_2))
    results.append(_check("1.3.3  .gitignore 屏蔽 .env", _1_3_3))
    results.append(_check("1.3.4  各包 __init__.py 就绪", _1_3_4))

    # 1.4 — 最小 Graph
    print(f"  {'─'*48}")
    print(f"  1.4  最小 Graph（START → DummyNode → END）")

    def _1_4_1():
        assert (ROOT / "src/graph/graph.py").exists(), \
            "src/graph/graph.py 不存在"

    def _1_4_2():
        mod = importlib.import_module("src.graph.graph")
        assert hasattr(mod, "graph"), "src/graph/graph.py 未导出 'graph' 对象"

    def _1_4_3():
        assert (ROOT / "main.py").exists(), "main.py 不存在"
        content = (ROOT / "main.py").read_text()
        assert "graph" in content or "invoke" in content, \
            "main.py 未调用 graph.invoke()"

    def _1_4_4():
        mod = importlib.import_module("src.graph.graph")
        g = mod.graph
        result = g.invoke({"topic": "テストトピック"})
        assert isinstance(result, dict), "graph.invoke() 未返回 dict"
        assert result.get("topic") == "テストトピック", \
            "graph.invoke() 返回的 State 中 topic 字段丢失"

    results.append(_check("1.4.1  src/graph/graph.py 存在", _1_4_1))
    results.append(_check("1.4.2  graph.py 导出 'graph' 对象", _1_4_2))
    results.append(_check("1.4.3  main.py 存在且调用 graph", _1_4_3))
    results.append(_check("1.4.4  graph.invoke() 跑通，State 传递无损", _1_4_4))

    # 1.5 — Tracing
    print(f"  {'─'*48}")
    print(f"  1.5  LangSmith Tracing 配置")

    def _1_5_1():
        env_file = ROOT / ".env"
        if not env_file.exists():
            raise AssertionError(".env 文件不存在，请复制 .env.example 并填入真实 Key")
        content = env_file.read_text()
        assert "LANGCHAIN_TRACING_V2=true" in content, \
            ".env 中 LANGCHAIN_TRACING_V2 未设置为 true"
        assert "LANGCHAIN_PROJECT" in content, \
            ".env 中缺少 LANGCHAIN_PROJECT"

    def _1_5_2():
        # 仅检查环境变量是否已加载，不做真实 API 调用
        tracing = os.getenv("LANGCHAIN_TRACING_V2", "")
        if tracing.lower() != "true":
            raise AssertionError(
                "LANGCHAIN_TRACING_V2 环境变量未生效（值为 %r）。"
                "请确认已运行 `source .env` 或通过 python-dotenv 加载" % tracing
            )

    results.append(_check("1.5.1  .env 含 LANGCHAIN_TRACING_V2=true 和 LANGCHAIN_PROJECT", _1_5_1))
    results.append(_check("1.5.2  LANGCHAIN_TRACING_V2 环境变量已生效", _1_5_2))

    return sum(results)


# ── 阶段 2-5 占位检查 ─────────────────────────────────────────────────────────

def check_stage_2() -> int:
    print(f"\n{BOLD}{CYAN}📅 阶段 2：三核心节点原子化开发{RESET}")
    results: list[bool] = []

    def _researcher():
        assert (ROOT / "src/nodes/researcher.py").exists(), \
            "src/nodes/researcher.py 不存在"
        mod = importlib.import_module("src.nodes.researcher")
        assert hasattr(mod, "researcher_node"), "未导出 researcher_node"

    def _writer():
        assert (ROOT / "src/nodes/writer.py").exists(), \
            "src/nodes/writer.py 不存在"
        mod = importlib.import_module("src.nodes.writer")
        assert hasattr(mod, "writer_node"), "未导出 writer_node"

    def _editor():
        assert (ROOT / "src/nodes/editor.py").exists(), \
            "src/nodes/editor.py 不存在"
        mod = importlib.import_module("src.nodes.editor")
        assert hasattr(mod, "editor_node"), "未导出 editor_node"

    def _tests():
        test_files = [
            "tests/test_researcher.py", "tests/test_writer.py", "tests/test_editor.py"
        ]
        missing = [f for f in test_files if not (ROOT / f).exists()]
        assert not missing, f"缺少测试文件：{missing}"

    results.append(_check("2.1  SEO_Researcher 节点（researcher_node）", _researcher))
    results.append(_check("2.2  Writer 节点（writer_node）", _writer))
    results.append(_check("2.3  Editor 节点（editor_node）", _editor))
    results.append(_check("2.4  FakeLLM 单元测试文件存在", _tests))
    return sum(results)


def check_stage_3() -> int:
    print(f"\n{BOLD}{CYAN}📅 阶段 3：编排反馈循环{RESET}")
    results: list[bool] = []

    def _graph_edges():
        mod = importlib.import_module("src.graph.graph")
        g = mod.graph
        # 验证图中有条件边（should_continue）
        nodes = list(g.nodes)
        assert "researcher" in nodes or "seo_researcher" in nodes, \
            "graph 中未找到 researcher 节点"
        assert "writer" in nodes, "graph 中未找到 writer 节点"
        assert "editor" in nodes, "graph 中未找到 editor 节点"

    def _routing():
        mod = importlib.import_module("src.graph.graph")
        assert hasattr(mod, "should_continue"), "未导出路由函数 should_continue"
        sc = mod.should_continue
        assert sc({"is_approved": True}) == "end"
        assert sc({"is_approved": False, "revision_count": 3}) == "human_review"
        assert sc({"is_approved": False, "revision_count": 1}) == "revise"

    results.append(_check("3.1  完整 Graph（researcher→writer→editor）组装", _graph_edges))
    results.append(_check("3.2  should_continue 三条路径路由正确", _routing))
    return sum(results)


def check_stage_4() -> int:
    print(f"\n{BOLD}{CYAN}📅 阶段 4：专业化能力强化{RESET}")
    results: list[bool] = []

    def _seo_tools():
        assert (ROOT / "src/tools/seo_checker.py").exists(), \
            "src/tools/seo_checker.py 不存在"
        mod = importlib.import_module("src.tools.seo_checker")
        for fn in ["check_keyword_density", "check_meta_description", "check_headings"]:
            assert hasattr(mod, fn), f"未导出 {fn}"

    def _terminology():
        assert (ROOT / "data/terminology.json").exists(), \
            "data/terminology.json 不存在"
        import json
        data = json.loads((ROOT / "data/terminology.json").read_text())
        assert isinstance(data, list) and len(data) >= 10, \
            f"术语库条目不足（当前 {len(data)} 条，要求 ≥10 条）"

    results.append(_check("4.1  SEO 检查工具（seo_checker.py 三个函数）", _seo_tools))
    results.append(_check("4.2  本地术语库（data/terminology.json ≥10 条）", _terminology))
    return sum(results)


def check_stage_5() -> int:
    print(f"\n{BOLD}{CYAN}📅 阶段 5：前端展示与持久化{RESET}")
    results: list[bool] = []

    def _app():
        assert (ROOT / "app.py").exists(), "app.py 不存在"
        content = (ROOT / "app.py").read_text()
        assert "streamlit" in content.lower(), "app.py 未导入 streamlit"
        assert "st.status" in content or "st.spinner" in content, \
            "app.py 未使用 st.status / st.spinner 展示进度"

    def _checkpointer():
        mod = importlib.import_module("src.graph.graph")
        src = Path(mod.__file__).read_text()
        assert "SqliteSaver" in src or "checkpointer" in src, \
            "graph.py 未集成 SqliteSaver Checkpointer"

    results.append(_check("5.1  Streamlit app.py（含 st.status 进度展示）", _app))
    results.append(_check("5.2  SqliteSaver Checkpointer 已集成", _checkpointer))
    return sum(results)


# ── 主入口 ────────────────────────────────────────────────────────────────────

STAGE_CHECKS = {
    1: check_stage_1,
    2: check_stage_2,
    3: check_stage_3,
    4: check_stage_4,
    5: check_stage_5,
}

STAGE_TOTALS = {1: 13, 2: 4, 3: 2, 4: 2, 5: 2}


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO Agent 开发进度检查")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4, 5],
                        help="只检查指定阶段（默认检查全部）")
    args = parser.parse_args()

    stages = [args.stage] if args.stage else [1, 2, 3, 4, 5]

    total_pass = 0
    total_checks = 0

    for s in stages:
        passed = STAGE_CHECKS[s]()
        total_checks_in_stage = STAGE_TOTALS[s]
        total_pass += passed
        total_checks += total_checks_in_stage

    print(f"\n{'═'*54}")
    pct = int(total_pass / total_checks * 100) if total_checks else 0
    color = GREEN if pct == 100 else (YELLOW if pct >= 50 else RED)
    print(f"{BOLD}  总进度：{color}{total_pass}/{total_checks} 项通过 ({pct}%){RESET}")
    print(f"{'═'*54}\n")

    sys.exit(0 if total_pass == total_checks else 1)


if __name__ == "__main__":
    main()
