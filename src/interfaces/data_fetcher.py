# -*- coding: utf-8 -*-
"""
===================================
数据源接口定义
===================================

定义数据获取器的统一接口，供各数据源实现。
"""

from typing import Protocol, Optional, List, Tuple
import pandas as pd

from src.domain.realtime import UnifiedRealtimeQuote, ChipDistribution


class IDataFetcher(Protocol):
    """
    数据源接口

    定义获取股票历史数据的统一接口。
    各数据源（Efinance/Akshare/Tushare 等）需实现此接口。
    """

    @property
    def name(self) -> str:
        """数据源名称"""
        ...

    @property
    def priority(self) -> int:
        """优先级（数字越小越优先）"""
        ...

    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 30
    ) -> Tuple[pd.DataFrame, str]:
        """
        获取日线数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选，默认今天）
            days: 获取天数（当 start_date 未指定时使用）

        Returns:
            Tuple[DataFrame, str]:
                - 标准化的 DataFrame，包含技术指标
                - 数据源名称
            列名：['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        """
        ...


class IRealtimeFetcher(Protocol):
    """
    实时行情接口

    定义获取实时行情和筹码分布的统一接口。
    """

    def get_realtime_quote(self, stock_code: str) -> Optional[UnifiedRealtimeQuote]:
        """
        获取实时行情

        Args:
            stock_code: 股票代码

        Returns:
            统一格式的实时行情数据
        """
        ...

    def get_realtime_quotes_batch(
        self,
        stock_codes: List[str]
    ) -> dict[str, UnifiedRealtimeQuote]:
        """
        批量获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            股票代码 -> 实时行情的映射
        """
        ...

    def get_chip_distribution(self, stock_code: str) -> Optional[ChipDistribution]:
        """
        获取筹码分布

        Args:
            stock_code: 股票代码

        Returns:
            筹码分布数据
        """
        ...
