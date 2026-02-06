# -*- coding: utf-8 -*-
"""
===================================
Providers 模块 - 数据源实现
===================================

从 data_provider/ 目录迁移而来。

包含：
- base: 基础类和管理器
- efinance: Efinance 数据源
- akshare: Akshare 数据源
- tushare: Tushare 数据源
- baostock: Baostock 数据源
- yfinance: YFinance 数据源
- realtime: 实时行情类型

注意：完整实现仍在 data_provider/ 目录中。
此模块提供新架构的入口点，后续版本将逐步完成迁移。
"""

# 重导出原模块内容，保持兼容性
from data_provider import (
    DataFetcherManager,
    BaseFetcher,
    DataFetchError,
    RateLimitError,
    DataSourceUnavailableError,
    STANDARD_COLUMNS,
)

__all__ = [
    "DataFetcherManager",
    "BaseFetcher",
    "DataFetchError",
    "RateLimitError",
    "DataSourceUnavailableError",
    "STANDARD_COLUMNS",
]
