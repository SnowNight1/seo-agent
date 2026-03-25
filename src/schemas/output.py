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
