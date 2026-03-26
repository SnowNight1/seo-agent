from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SEOArticleOutput(BaseModel):
    """多智能体 SEO 内容编排系统的最终输出结构。

    该模型描述一篇符合 SEO 规范的日语文章的完整产出，
    同时记录系统内部的审查状态信息。
    """

    meta_title: str = Field(
        description="SEO 页面标题，应包含主关键词，长度不超过 60 个字符",
    )
    meta_description: str = Field(
        description="Meta 描述，用于搜索结果摘要展示，长度建议 70-160 个字符，需包含主关键词",
    )
    target_keywords: list[str] = Field(
        description="本文的目标关键词列表，按相关度由高到低排列",
    )
    h1: str = Field(
        description="文章的 H1 主标题，需自然包含核心关键词",
    )
    content_markdown: str = Field(
        description="文章正文内容，Markdown 格式，包含 H2/H3 小节结构",
    )
    seo_score: int = Field(
        ge=0,
        le=100,
        description="SEO 综合评分，0-100 分，由 Editor 节点基于关键词密度、标题规范、Meta 规范等维度评定",
    )
    revision_count: int = Field(
        default=0,
        ge=0,
        description="本稿经历的修订次数，每次 Writer 重写时自增 1",
    )
    reviewer_notes: str = Field(
        default="",
        description="Editor 最终审查备注，说明通过或拒绝的具体原因及改进建议",
    )

    @field_validator("meta_title")
    @classmethod
    def meta_title_max_length(cls, v: str) -> str:
        if len(v) > 60:
            raise ValueError(
                f"meta_title 长度为 {len(v)} 字符，超过上限 60 字符：{v!r}"
            )
        return v

    @field_validator("meta_description")
    @classmethod
    def meta_description_length_range(cls, v: str) -> str:
        length = len(v)
        if length < 70 or length > 160:
            raise ValueError(
                f"meta_description 长度为 {length} 字符，应在 70-160 字符之间"
            )
        return v

class Keyword(BaseModel):
    """提取的单个 SEO 关键词及其属性"""
    term: str = Field(description="关键词文本")
    relevance_score: int = Field(ge=0, le=10, description="关键词与主题的相关性评分(0-10)")
    search_intent: str = Field(description="用户搜索该关键词的意图(如：情報収集、購買意欲等)")

class ResearchOutput(BaseModel):
    """SEO_Researcher 节点的结构化输出"""
    keywords: list[Keyword] = Field(description="提取的目标关键词列表，按相关度由高到低依次排序")
    competitor_insights: str = Field(description="从搜索引擎竞品内容中提取的日语内容建设洞察与建议")

class WriterOutput(BaseModel):
    """Writer 节点的结构化输出"""
    meta_title: str = Field(description="SEO 页面标题，需包含核心关键词，且长度不超过 60 个字符")
    meta_description: str = Field(description="Meta 描述，建议 70-160 个字符，需自然包含关键短语")
    h1: str = Field(description="文章的大标题(H1)，明确清晰且包含最核心关键词")
    draft_markdown: str = Field(description="生成的文章正文草稿（Markdown 格式），请包含 H2、H3 及段落正文")

class EditorOutput(BaseModel):
    """Editor 节点的结构化输出"""
    is_approved: bool = Field(description="文章是否通过审查：如果质量达标则为 true，如果需要重写则为 false")
    feedback: str = Field(description="给 Writer 的日语修改意见。如果通过则可为空；如果不通过，必须详细说明哪里需要修改")
    seo_score: int = Field(ge=0, le=100, description="对文章 SEO 表现的综合评分 (0-100分)")
    reviewer_notes: str = Field(description="Editor 的最终审查备注，可用于最终测试报告。")
