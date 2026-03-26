import pytest
from src.graph.graph import graph
from src.schemas.output import ResearchOutput, WriterOutput, EditorOutput, Keyword

# 模拟用于 Researcher 的数据
dummy_keyword = Keyword(term="テスト", relevance_score=10, search_intent="informational")
dummy_research = ResearchOutput(keywords=[dummy_keyword], competitor_insights="Test Insight")

# 模拟用于 Writer 的数据
dummy_writer = WriterOutput(
    meta_title="Test Title",
    meta_description="Test Desc",
    h1="Test H1",
    draft_markdown="This is a test document."
)

class MockStructuredChain:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        
    def __call__(self, *args, **kwargs):
        res = self.responses[self.call_count]
        if self.call_count < len(self.responses) - 1:
            self.call_count += 1
        return res
        
    def invoke(self, *args, **kwargs):
        return self(*args, **kwargs)

from langchain_openai import ChatOpenAI

def make_mock_structured_output(editor_responses):
    editor_chain = MockStructuredChain(editor_responses)
    researcher_chain = MockStructuredChain([dummy_research])
    writer_chain = MockStructuredChain([dummy_writer] * 10)
    
    def mocker(self, schema, *args, **kwargs):
        if schema.__name__ == "ResearchOutput":
            return researcher_chain
        elif schema.__name__ == "WriterOutput":
            return writer_chain
        elif schema.__name__ == "EditorOutput":
            return editor_chain
        return MockStructuredChain([])
    return mocker

def test_path_a_once_approved(monkeypatch):
    """路径 A：Editor 首次便返回 is_approved=True"""
    monkeypatch.setenv("TAVILY_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    
    editor_responses = [EditorOutput(is_approved=True, feedback="", seo_score=90, reviewer_notes="Perfect!")]
    monkeypatch.setattr(ChatOpenAI, "with_structured_output", make_mock_structured_output(editor_responses))

    result = graph.invoke({"topic": "テスト"})
    
    assert result["is_approved"] is True
    assert result["revision_count"] == 1 


def test_path_b_approved_after_2_retries(monkeypatch):
    """路径 B：Editor 前2次打回 (False)，第3次返回 True"""
    monkeypatch.setenv("TAVILY_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
                        
    editor_responses = [
        EditorOutput(is_approved=False, feedback="Fix 1", seo_score=50, reviewer_notes="Bad"),
        EditorOutput(is_approved=False, feedback="Fix 2", seo_score=60, reviewer_notes="Better"),
        EditorOutput(is_approved=True, feedback="", seo_score=85, reviewer_notes="Good"),
    ]
    monkeypatch.setattr(ChatOpenAI, "with_structured_output", make_mock_structured_output(editor_responses))

    result = graph.invoke({"topic": "テスト"})
    
    assert result["is_approved"] is True
    assert result["revision_count"] == 3


def test_path_c_human_review_exceeds_max_retries(monkeypatch):
    """路径 C：Editor 连续 3 次打回，触发 human_review 跳转"""
    monkeypatch.setenv("TAVILY_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
                        
    editor_responses = [
        EditorOutput(is_approved=False, feedback="Fix 1", seo_score=50, reviewer_notes="Bad"),
        EditorOutput(is_approved=False, feedback="Fix 2", seo_score=55, reviewer_notes="Bad"),
        EditorOutput(is_approved=False, feedback="Fix 3", seo_score=60, reviewer_notes="Bad"),
    ]
    monkeypatch.setattr(ChatOpenAI, "with_structured_output", make_mock_structured_output(editor_responses))

    result = graph.invoke({"topic": "テスト", "target_audience": "一般"})
    
    assert result["is_approved"] is False
    assert result["revision_count"] == 3 
    assert result["feedback"] == "Fix 3"
