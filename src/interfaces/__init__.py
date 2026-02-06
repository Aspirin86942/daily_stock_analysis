# -*- coding: utf-8 -*-
"""
===================================
Interfaces 层 - 接口协议定义
===================================

设计原则：
- 使用 Protocol 定义接口（结构化子类型）
- 仅依赖 domain 层
- 供 services 层和 infrastructure 层实现
"""

from src.interfaces.data_fetcher import IDataFetcher, IRealtimeFetcher
from src.interfaces.analyzer import IAnalyzer, ITrendAnalyzer
from src.interfaces.notifier import INotifier, IReportRenderer

__all__ = [
    "IDataFetcher",
    "IRealtimeFetcher",
    "IAnalyzer",
    "ITrendAnalyzer",
    "INotifier",
    "IReportRenderer",
]
