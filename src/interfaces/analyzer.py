# -*- coding: utf-8 -*-
"""
===================================
分析器接口定义
===================================

定义 AI 分析器和趋势分析器的统一接口。
"""

from typing import Protocol, Optional, Dict, Any
import pandas as pd

from src.domain.analysis import AnalysisResult, TrendAnalysisResult


class IAnalyzer(Protocol):
    """
    AI 分析器接口

    定义 AI 模型分析股票的统一接口。
    与现有 GeminiAnalyzer 保持一致：输入为上下文字典。
    """

    def analyze(
        self,
        context: Dict[str, Any],
        news_context: Optional[str] = None,
    ) -> AnalysisResult:
        """
        执行 AI 分析

        Args:
            context: 技术面与增强数据上下文（含 today/yesterday/trend 等）
            news_context: 新闻/消息面上下文（可选）

        Returns:
            AI 分析结果
        """
        ...


class ITrendAnalyzer(Protocol):
    """
    趋势分析器接口

    定义基于技术指标的趋势分析接口。
    """

    def analyze(
        self,
        df: pd.DataFrame,
        stock_code: str,
    ) -> TrendAnalysisResult:
        """
        执行趋势分析

        Args:
            df: 包含技术指标的 DataFrame
            stock_code: 股票代码

        Returns:
            趋势分析结果
        """
        ...
