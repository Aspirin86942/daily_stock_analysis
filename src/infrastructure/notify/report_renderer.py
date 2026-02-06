# -*- coding: utf-8 -*-
"""
===================================
报告渲染器
===================================

负责将分析结果渲染为各种格式的报告。

从 src/notification.py 提取的报告生成函数。
为保持兼容性，这里提供函数级别的导出。
实际实现仍在 NotificationService 中。
"""

from typing import List, Optional
from datetime import datetime

# 延迟导入，避免循环依赖
# 实际使用时从 NotificationService 获取方法


def generate_dashboard_report(results: List, report_date: Optional[str] = None) -> str:
    """
    生成决策仪表盘格式的日报（详细版）

    注意：此函数为兼容层，实际实现在 NotificationService 中。
    建议直接使用 NotificationService().generate_dashboard_report()

    Args:
        results: 分析结果列表
        report_date: 报告日期（默认今天）

    Returns:
        Markdown 格式的决策仪表盘日报
    """
    # 延迟导入避免循环依赖
    from src.notification import NotificationService
    service = NotificationService()
    return service.generate_dashboard_report(results, report_date)


def generate_single_stock_report(result) -> str:
    """
    生成单只股票的分析报告

    注意：此函数为兼容层，实际实现在 NotificationService 中。

    Args:
        result: 单只股票的分析结果

    Returns:
        Markdown 格式的单股报告
    """
    from src.notification import NotificationService
    service = NotificationService()
    return service.generate_single_stock_report(result)


def generate_wechat_dashboard(results: List) -> str:
    """
    生成企业微信决策仪表盘精简版

    注意：此函数为兼容层，实际实现在 NotificationService 中。

    Args:
        results: 分析结果列表

    Returns:
        精简版决策仪表盘
    """
    from src.notification import NotificationService
    service = NotificationService()
    return service.generate_wechat_dashboard(results)
