from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    """多智能体 SEO 内容编排系统的全局状态。

    所有字段均为 Optional（total=False），避免图启动时因字段缺失报错。
    字段按职责分为三组：用户输入、节点间中间态、循环控制。
    """

    # ── 用户输入（图启动时由调用方传入） ──────────────────────────────
    topic: str
    """文章主题，例如「2026年インテリアデザイントレンド」"""

    target_audience: str
    """目标读者，例如「30代の日本人女性、インテリアに関心が高い」"""

    keywords_preference: list[str]
    """用户指定的关键词偏好列表，SEO_Researcher 可将其作为搜索种子"""

    # ── 节点间中间态（由各节点写入，传递给下游节点） ──────────────────
    keywords: list[str]
    """SEO_Researcher 输出的目标关键词列表（按相关度排序）"""

    competitor_insights: str
    """SEO_Researcher 从 Tavily 搜索结果中提炼的竞品内容摘要"""

    draft_markdown: str
    """Writer 输出的文章正文草稿（Markdown 格式）"""

    meta_title: str
    """Writer 输出的 SEO 页面标题（≤60 字符）"""

    meta_description: str
    """Writer 输出的 Meta 描述（70-160 字符）"""

    h1: str
    """Writer 输出的 H1 主标题"""

    feedback: str
    """Editor 反馈给 Writer 的修改意见（打回重写时传入）"""

    # ── 循环控制（由 Editor 写入，驱动路由函数决策） ──────────────────
    is_approved: bool
    """Editor 的审查结论：True 表示通过，False 表示打回重写"""

    revision_count: int
    """Writer 已执行的重写次数；初始为 0，每次重写时自增 1"""

    seo_score: int
    """Editor 评定的 SEO 综合评分（0-100）"""

    reviewer_notes: str
    """Editor 的最终审查备注，写入最终输出报告"""
