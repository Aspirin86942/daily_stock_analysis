# -*- coding: utf-8 -*-
"""
===================================
股票分析服务
===================================

从 src/core/pipeline.py 提取的核心分析逻辑。
使用依赖注入，便于测试和扩展。

设计原则：
- 依赖接口而非实现
- 单一职责
- 可测试性
"""

import logging
import math
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import Config, get_config
from src.domain.analysis import AnalysisResult, TrendAnalysisResult
from src.interfaces.data_fetcher import IDataFetcher, IRealtimeFetcher
from src.interfaces.analyzer import IAnalyzer, ITrendAnalyzer
from src.interfaces.notifier import INotifier

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    股票分析服务

    职责：
    1. 协调数据获取、分析、通知等模块
    2. 实现并发控制和异常处理
    3. 提供股票分析的核心功能

    使用依赖注入，便于测试和扩展。
    """

    def __init__(
        self,
        data_fetcher: Optional[IDataFetcher] = None,
        realtime_fetcher: Optional[IRealtimeFetcher] = None,
        analyzer: Optional[IAnalyzer] = None,
        trend_analyzer: Optional[ITrendAnalyzer] = None,
        notifier: Optional[INotifier] = None,
        config: Optional[Config] = None,
    ):
        """
        初始化分析服务

        Args:
            data_fetcher: 数据获取器（可选，默认使用 DataFetcherManager）
            realtime_fetcher: 实时行情获取器（可选）
            analyzer: AI 分析器（可选，默认使用 GeminiAnalyzer）
            trend_analyzer: 趋势分析器（可选，默认使用 StockTrendAnalyzer）
            notifier: 通知器（可选，默认使用 NotificationService）
            config: 配置对象（可选，默认使用全局配置）
        """
        self._config = config or get_config()

        # 延迟初始化，避免循环导入
        self._data_fetcher = data_fetcher
        self._realtime_fetcher = realtime_fetcher
        self._analyzer = analyzer
        self._trend_analyzer = trend_analyzer
        self._notifier = notifier

        self._initialized = False

    def _ensure_initialized(self):
        """确保依赖已初始化"""
        if self._initialized:
            return

        # 延迟导入，避免循环依赖
        if self._data_fetcher is None:
            from data_provider import DataFetcherManager
            self._data_fetcher = DataFetcherManager()

        if self._analyzer is None:
            from src.analyzer import GeminiAnalyzer
            self._analyzer = GeminiAnalyzer()

        if self._trend_analyzer is None:
            from src.stock_analyzer import StockTrendAnalyzer
            self._trend_analyzer = StockTrendAnalyzer()

        if self._notifier is None:
            from src.notification import NotificationService
            self._notifier = NotificationService()

        self._initialized = True

    def analyze_stocks(
        self,
        stock_codes: List[str],
        max_workers: Optional[int] = None,
    ) -> List[AnalysisResult]:
        """
        分析多只股票

        Args:
            stock_codes: 股票代码列表
            max_workers: 最大并发线程数（可选）

        Returns:
            分析结果列表
        """
        self._ensure_initialized()

        max_workers = max_workers or self._config.max_workers
        results = []

        logger.info(f"开始分析 {len(stock_codes)} 只股票，最大并发数: {max_workers}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_code = {
                executor.submit(self.analyze_single_stock, code): code
                for code in stock_codes
            }

            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"[{code}] 分析完成: {result.operation_advice}")
                except Exception as e:
                    logger.error(f"[{code}] 分析失败: {e}")

        logger.info(f"分析完成，成功 {len(results)}/{len(stock_codes)} 只")
        return results

    def analyze_single_stock(self, stock_code: str) -> Optional[AnalysisResult]:
        """
        分析单只股票

        Args:
            stock_code: 股票代码

        Returns:
            分析结果，失败返回 None
        """
        self._ensure_initialized()

        try:
            logger.info(f"[{stock_code}] 开始分析...")

            # 1. 获取历史数据
            df, source_name = self._data_fetcher.get_daily_data(stock_code, days=30)
            if df is None or df.empty:
                logger.warning(f"[{stock_code}] 获取数据失败")
                return None

            # 2. 趋势分析
            # 注意：StockTrendAnalyzer.analyze(df, code) 参数顺序是 df 在前
            trend_result = None
            if self._trend_analyzer:
                trend_result = self._trend_analyzer.analyze(df, stock_code)

            # 3. 构建上下文数据（与 GeminiAnalyzer 接口一致）
            from src.domain.stock import get_stock_name
            stock_name = get_stock_name(stock_code)

            context = self._build_context_from_df(
                stock_code=stock_code,
                stock_name=stock_name,
                df=df,
                trend_result=trend_result,
            )

            result = self._analyzer.analyze(context, news_context=None)

            return result

        except Exception as e:
            logger.error(f"[{stock_code}] 分析异常: {e}")
            return None

    def _build_technical_data(
        self,
        df,
        trend_result: Optional[TrendAnalysisResult] = None,
    ) -> Dict[str, Any]:
        """
        构建技术面数据

        Args:
            df: 历史数据 DataFrame
            trend_result: 趋势分析结果

        Returns:
            技术面数据字典
        """
        if df is None or df.empty:
            return {}

        latest = df.iloc[-1]

        data = {
            "current_price": float(latest.get("close", 0)),
            "ma5": float(latest.get("ma5", 0)) if "ma5" in latest else None,
            "ma10": float(latest.get("ma10", 0)) if "ma10" in latest else None,
            "ma20": float(latest.get("ma20", 0)) if "ma20" in latest else None,
            "volume": int(latest.get("volume", 0)),
            "pct_chg": float(latest.get("pct_chg", 0)) if "pct_chg" in latest else None,
        }

        if trend_result:
            data.update({
                "trend_status": trend_result.trend_status.value,
                "ma_alignment": trend_result.ma_alignment,
                "bias_ma5": trend_result.bias_ma5,
                "buy_signal": trend_result.buy_signal.value,
                "signal_score": trend_result.signal_score,
            })

        return data

    def _build_context_from_df(
        self,
        stock_code: str,
        stock_name: str,
        df,
        trend_result: Optional[TrendAnalysisResult] = None,
    ) -> Dict[str, Any]:
        """
        从日线数据构建 GeminiAnalyzer 所需上下文

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            df: 历史数据 DataFrame
            trend_result: 趋势分析结果（可选）

        Returns:
            上下文字典（包含 today/yesterday/trend 等）
        """
        latest = df.iloc[-1]
        today = self._extract_row(latest)

        context: Dict[str, Any] = {
            "code": stock_code,
            "stock_name": stock_name,
            "date": self._format_date(today.get("date")),
            "today": today,
        }

        if len(df) > 1:
            yesterday = self._extract_row(df.iloc[-2])
            context["yesterday"] = yesterday

            # 量价变化
            vol_y = yesterday.get("volume")
            vol_t = today.get("volume")
            if vol_y and vol_t:
                context["volume_change_ratio"] = round(vol_t / vol_y, 2)

            close_y = yesterday.get("close")
            close_t = today.get("close")
            if close_y and close_t:
                context["price_change_ratio"] = round((close_t - close_y) / close_y * 100, 2)

        # 均线形态
        context["ma_status"] = self._calc_ma_status(
            close=today.get("close"),
            ma5=today.get("ma5"),
            ma10=today.get("ma10"),
            ma20=today.get("ma20"),
        )

        # 趋势分析结果
        if trend_result:
            context["trend_analysis"] = trend_result.to_dict()

        return context

    @staticmethod
    def _extract_row(row) -> Dict[str, Any]:
        """抽取关键字段并进行基础清洗"""
        keys = [
            "date", "open", "high", "low", "close",
            "volume", "amount", "pct_chg",
            "ma5", "ma10", "ma20",
        ]
        result: Dict[str, Any] = {}
        for key in keys:
            val = row.get(key) if hasattr(row, "get") else None
            if hasattr(val, "item"):
                try:
                    val = val.item()
                except Exception:
                    pass
            if isinstance(val, float) and math.isnan(val):
                val = None
            result[key] = val
        return result

    @staticmethod
    def _format_date(value: Any) -> str:
        """格式化日期为 ISO 字符串"""
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if value:
            return str(value)
        return date.today().isoformat()

    @staticmethod
    def _calc_ma_status(
        close: Optional[float],
        ma5: Optional[float],
        ma10: Optional[float],
        ma20: Optional[float],
    ) -> str:
        """均线形态判断（简化版）"""
        if not close or not ma5 or not ma10 or not ma20:
            return "未知"
        if close > ma5 > ma10 > ma20:
            return "多头排列 📈"
        if close < ma5 < ma10 < ma20:
            return "空头排列 📉"
        if close > ma5 and ma5 > ma10:
            return "短期向好 🔼"
        if close < ma5 and ma5 < ma10:
            return "短期走弱 🔽"
        return "震荡整理 ↔️"

    def send_report(self, results: List[AnalysisResult]) -> bool:
        """
        发送分析报告

        Args:
            results: 分析结果列表

        Returns:
            是否发送成功
        """
        self._ensure_initialized()

        if not results:
            logger.warning("没有分析结果，跳过发送报告")
            return False

        try:
            # 使用 NotificationService 的现有接口：
            # 1. generate_dashboard_report() 生成报告
            # 2. send() 发送到所有渠道
            report = self._notifier.generate_dashboard_report(results)
            return self._notifier.send(report)
        except Exception as e:
            logger.error(f"发送报告失败: {e}")
            return False
