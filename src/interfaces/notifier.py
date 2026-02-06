# -*- coding: utf-8 -*-
"""
===================================
通知器接口定义
===================================

定义通知渠道和报告渲染的统一接口。
"""

from typing import Protocol, List, Optional

from src.domain.analysis import AnalysisResult


class INotifier(Protocol):
    """
    通知渠道接口

    定义发送通知的统一接口。
    各渠道（企业微信/飞书/Telegram 等）需实现此接口。
    """

    @property
    def name(self) -> str:
        """渠道名称"""
        ...

    @property
    def is_available(self) -> bool:
        """渠道是否可用（配置是否完整）"""
        ...

    def send(self, content: str, title: Optional[str] = None) -> bool:
        """
        发送文本消息

        Args:
            content: 消息内容
            title: 消息标题（可选）

        Returns:
            是否发送成功
        """
        ...

    def send_markdown(self, content: str, title: Optional[str] = None) -> bool:
        """
        发送 Markdown 格式消息

        Args:
            content: Markdown 内容
            title: 消息标题（可选）

        Returns:
            是否发送成功
        """
        ...


class IReportRenderer(Protocol):
    """
    报告渲染器接口

    定义将分析结果渲染为报告的统一接口。
    """

    def render_dashboard(self, results: List[AnalysisResult]) -> str:
        """
        渲染决策仪表盘报告

        Args:
            results: 分析结果列表

        Returns:
            Markdown 格式的报告
        """
        ...

    def render_single_stock(self, result: AnalysisResult) -> str:
        """
        渲染单股报告

        Args:
            result: 单只股票的分析结果

        Returns:
            Markdown 格式的报告
        """
        ...

    def render_wechat_dashboard(self, results: List[AnalysisResult]) -> str:
        """
        渲染企业微信专用精简版报告

        Args:
            results: 分析结果列表

        Returns:
            精简版 Markdown 报告（适配 4KB 限制）
        """
        ...
