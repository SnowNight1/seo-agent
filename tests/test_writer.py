import pytest
from src.schemas.state import GraphState
from src.nodes.writer import writer_node

def test_writer_node_signature():
    """验证 Writer 节点结构签名"""
    assert callable(writer_node)

def test_writer_node_mocked(monkeypatch):
    """验证 Writer 逻辑状态更新及修正计数功能"""
    initial_state = {
        "topic": "テスト",
        "target_audience": "一般",
        "keywords": ["SEO", "ライティング"],
        "feedback": "文字数を増やしてください",
        "revision_count": 0
    }
    
    # 我们仅 mock 掉 API Key 来触发它的兜底返回就可以通过我们的 State 更新逻辑测试
    # 因为兜底返回也会带有我们想要检测的 Draft 和 revision_count 加 1 的结构。
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    
    result = writer_node(initial_state)
    
    assert isinstance(result, dict)
    assert "draft_markdown" in result
    assert "meta_title" in result
    assert "meta_description" in result
    assert "h1" in result
    # 重要：检测是否自增了
    assert result["revision_count"] == 1
