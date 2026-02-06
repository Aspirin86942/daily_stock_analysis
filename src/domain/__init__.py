# -*- coding: utf-8 -*-
"""
===================================
Domain 层 - 核心实体定义
===================================

设计原则：
- 纯数据结构，无外部依赖
- 所有业务实体的单一来源
- 可被其他层安全导入
"""

from src.domain.stock import StockCode, StockInfo, STANDARD_COLUMNS
from src.domain.analysis import AnalysisResult, TrendAnalysisResult
from src.domain.realtime import UnifiedRealtimeQuote, ChipDistribution, RealtimeSource
from src.domain.enums import (
    ReportType,
    TrendStatus,
    VolumeStatus,
    BuySignal,
    MACDStatus,
    RSIStatus,
    NotificationChannel,
)

__all__ = [
    # stock.py
    "StockCode",
    "StockInfo",
    "STANDARD_COLUMNS",
    # analysis.py
    "AnalysisResult",
    "TrendAnalysisResult",
    # realtime.py
    "UnifiedRealtimeQuote",
    "ChipDistribution",
    "RealtimeSource",
    # enums.py
    "ReportType",
    "TrendStatus",
    "VolumeStatus",
    "BuySignal",
    "MACDStatus",
    "RSIStatus",
    "NotificationChannel",
]
