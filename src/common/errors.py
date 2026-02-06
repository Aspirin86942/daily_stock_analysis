# -*- coding: utf-8 -*-
"""
===================================
统一错误类型定义
===================================

集中管理系统中使用的异常类型，提供清晰的错���层次结构。
"""


class StockAnalysisError(Exception):
    """股票分析系统基础异常"""

    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ============================================
# 数据获取相关异常
# ============================================

class DataFetchError(StockAnalysisError):
    """数据获取异常基类"""

    def __init__(self, message: str, source: str = "unknown"):
        self.source = source
        super().__init__(message, code="DATA_FETCH_ERROR")


class RateLimitError(DataFetchError):
    """API 速率限制异常"""

    def __init__(self, message: str, source: str = "unknown", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, source)
        self.code = "RATE_LIMIT_ERROR"


class DataSourceUnavailableError(DataFetchError):
    """数据源不可用异常"""

    def __init__(self, message: str, source: str = "unknown"):
        super().__init__(message, source)
        self.code = "DATA_SOURCE_UNAVAILABLE"


# ============================================
# 分析相关异常
# ============================================

class AnalysisError(StockAnalysisError):
    """分析异常基类"""

    def __init__(self, message: str, stock_code: str = ""):
        self.stock_code = stock_code
        super().__init__(message, code="ANALYSIS_ERROR")


class AIAnalysisError(AnalysisError):
    """AI 分析异常"""

    def __init__(self, message: str, stock_code: str = "", model: str = ""):
        self.model = model
        super().__init__(message, stock_code)
        self.code = "AI_ANALYSIS_ERROR"


class TrendAnalysisError(AnalysisError):
    """趋势分析异常"""

    def __init__(self, message: str, stock_code: str = ""):
        super().__init__(message, stock_code)
        self.code = "TREND_ANALYSIS_ERROR"


# ============================================
# 通知相关异常
# ============================================

class NotificationError(StockAnalysisError):
    """通知异常基类"""

    def __init__(self, message: str, channel: str = "unknown"):
        self.channel = channel
        super().__init__(message, code="NOTIFICATION_ERROR")


class NotificationConfigError(NotificationError):
    """通知配置异常"""

    def __init__(self, message: str, channel: str = "unknown"):
        super().__init__(message, channel)
        self.code = "NOTIFICATION_CONFIG_ERROR"


class NotificationSendError(NotificationError):
    """通知发送异常"""

    def __init__(self, message: str, channel: str = "unknown"):
        super().__init__(message, channel)
        self.code = "NOTIFICATION_SEND_ERROR"
