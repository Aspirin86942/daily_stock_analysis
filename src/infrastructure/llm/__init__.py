# -*- coding: utf-8 -*-
"""
===================================
LLM 模块 - AI 分析器实现
===================================

从 src/analyzer.py 拆分而来。

包含：
- base: 基础类和 Prompt 模板
- gemini_client: Gemini API 封装
- openai_client: OpenAI 兼容 API 封装
- factory: 工厂函数

注意：完整的 GeminiAnalyzer 仍在 src/analyzer.py 中。
此模块提供新架构的入口点，后续版本将逐步完成迁移。
"""

# 重导出原模块内容，保持兼容性
from src.analyzer import GeminiAnalyzer, AnalysisResult, STOCK_NAME_MAP

__all__ = [
    "GeminiAnalyzer",
    "AnalysisResult",
    "STOCK_NAME_MAP",
]


def create_analyzer(analyzer_type: str = "gemini"):
    """
    工厂函数：根据类型创建分析器

    Args:
        analyzer_type: 分析器类型 ("gemini" 或 "openai")

    Returns:
        分析器实例
    """
    if analyzer_type == "gemini":
        return GeminiAnalyzer()
    elif analyzer_type == "openai":
        # OpenAI 兼容模式也使用 GeminiAnalyzer（内部支持 OpenAI API）
        return GeminiAnalyzer()
    else:
        raise ValueError(f"不支持的分析器类型: {analyzer_type}")
