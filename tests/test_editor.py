import pytest
from src.schemas.state import GraphState
from src.nodes.editor import editor_node

def test_editor_node_signature():
    """验证 Editor 节点签名"""
    assert callable(editor_node)

def test_editor_node_mocked(monkeypatch):
    """验证 Editor 节点状态流转"""
    initial_state = {
        "topic": "テスト",
        "target_audience": "一般",
        "keywords": ["SEO"],
        "draft_markdown": "これはテスト記事です。",
        "meta_title": "テスト",
        "meta_description": "テストの説明",
        "h1": "テスト見出し"
    }
    
    # Mock api key 产生异常并触发兜底返回值，用以验证结构流转
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    
    result = editor_node(initial_state)
    
    assert isinstance(result, dict)
    assert "is_approved" in result
    assert "feedback" in result
    assert "seo_score" in result
    assert "reviewer_notes" in result
