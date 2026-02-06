# -*- coding: utf-8 -*-
"""
===================================
Services 层 - 业务服务
===================================

包含：
- AnalysisService: 股票分析服务
- MarketReviewService: 大盘复盘服务

设计原则：
- 依赖注入（通过接口依赖）
- 单一职责
- 可测试性
"""

from src.services.analysis_service import AnalysisService
from src.services.market_review_service import MarketReviewService

__all__ = [
    "AnalysisService",
    "MarketReviewService",
]
