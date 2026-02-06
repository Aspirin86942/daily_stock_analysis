# -*- coding: utf-8 -*-
"""
===================================
大盘复盘服务
===================================

从 src/core/market_review.py 和 src/market_analyzer.py 提取。
提供大盘复盘功能。
"""

import logging
from typing import Optional, Dict, Any

from src.config import Config, get_config

logger = logging.getLogger(__name__)


class MarketReviewService:
    """
    大盘复盘服务

    职责：
    1. 获取大盘涨跌统计
    2. 获取板块涨跌榜
    3. 生成大盘复盘报告
    """

    def __init__(self, config: Optional[Config] = None):
        """
        初始化大盘复盘服务

        Args:
            config: 配置对象（可选，默认使用全局配置）
        """
        self._config = config or get_config()
        self._initialized = False

    def _ensure_initialized(self):
        """确保依赖已初始化"""
        if self._initialized:
            return
        self._initialized = True

    def run_market_review(self) -> Optional[str]:
        """
        执行大盘复盘

        Returns:
            复盘报告内容，失败返回 None
        """
        self._ensure_initialized()

        try:
            # 延迟导入，避免循环依赖
            from src.market_analyzer import MarketAnalyzer

            analyzer = MarketAnalyzer()
            report = analyzer.generate_market_review()
            return report

        except Exception as e:
            logger.error(f"大盘复盘失败: {e}")
            return None

    def get_market_stats(self) -> Dict[str, Any]:
        """
        获取大盘统计数据

        Returns:
            统计数据字典
        """
        self._ensure_initialized()

        try:
            from src.market_analyzer import MarketAnalyzer

            analyzer = MarketAnalyzer()
            return analyzer.get_market_stats()

        except Exception as e:
            logger.error(f"获取大盘统计失败: {e}")
            return {}

    def get_sector_ranking(self, top_n: int = 10) -> Dict[str, Any]:
        """
        获取板块涨跌榜

        Args:
            top_n: 返回前 N 个板块

        Returns:
            板块涨跌榜数据
        """
        self._ensure_initialized()

        try:
            from src.market_analyzer import MarketAnalyzer

            analyzer = MarketAnalyzer()
            return analyzer.get_sector_ranking(top_n)

        except Exception as e:
            logger.error(f"获取板块涨跌榜失败: {e}")
            return {}
