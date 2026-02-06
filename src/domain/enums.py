# -*- coding: utf-8 -*-
"""
===================================
枚举类型定义
===================================

集中管理系统中使用的枚举类型，提供类型安全和代码可读性。

合并自：
- src/enums.py
- src/stock_analyzer.py
- src/notification.py
"""

from enum import Enum


class ReportType(str, Enum):
    """
    报告类型枚举

    用于 API 触发分析时选择推送的报告格式。
    继承 str 使其可以直接与字符串比较和序列化。
    """
    SIMPLE = "simple"  # 精简报告：使用 generate_single_stock_report
    FULL = "full"      # 完整报告：使用 generate_dashboard_report

    @classmethod
    def from_str(cls, value: str) -> "ReportType":
        """
        从字符串安全地转换为枚举值

        Args:
            value: 字符串值

        Returns:
            对应的枚举值，无效输入返回默认值 SIMPLE
        """
        try:
            return cls(value.lower().strip())
        except (ValueError, AttributeError):
            return cls.SIMPLE

    @property
    def display_name(self) -> str:
        """获取用于显示的名称"""
        return {
            ReportType.SIMPLE: "精简报告",
            ReportType.FULL: "完整报告",
        }.get(self, "精简报告")


class TrendStatus(Enum):
    """趋势状态枚举"""
    STRONG_BULL = "强势多头"      # MA5 > MA10 > MA20，且间距扩大
    BULL = "多头排列"             # MA5 > MA10 > MA20
    WEAK_BULL = "弱势多头"        # MA5 > MA10，但 MA10 < MA20
    CONSOLIDATION = "盘整"        # 均线缠绕
    WEAK_BEAR = "弱势空头"        # MA5 < MA10，但 MA10 > MA20
    BEAR = "空头排列"             # MA5 < MA10 < MA20
    STRONG_BEAR = "强势空头"      # MA5 < MA10 < MA20，且间距扩大


class VolumeStatus(Enum):
    """量能状态枚举"""
    HEAVY_VOLUME_UP = "放量上涨"       # 量价齐升
    HEAVY_VOLUME_DOWN = "放量下跌"     # 放量杀跌
    SHRINK_VOLUME_UP = "缩量上涨"      # 无量上涨
    SHRINK_VOLUME_DOWN = "缩量回调"    # 缩量回调（好）
    NORMAL = "量能正常"


class BuySignal(Enum):
    """买入信号枚举"""
    STRONG_BUY = "强烈买入"       # 多条件满足
    BUY = "买入"                  # 基本条件满足
    HOLD = "持有"                 # 已持有可继续
    WAIT = "观望"                 # 等待更好时机
    SELL = "卖出"                 # 趋势转弱
    STRONG_SELL = "强烈卖出"      # 趋势破坏


class MACDStatus(Enum):
    """MACD状态枚举"""
    GOLDEN_CROSS_ZERO = "零轴上金叉"      # DIF上穿DEA，且在零轴上方
    GOLDEN_CROSS = "金叉"                # DIF上穿DEA
    BULLISH = "多头"                    # DIF>DEA>0
    CROSSING_UP = "上穿零轴"             # DIF上穿零轴
    CROSSING_DOWN = "下穿零轴"           # DIF下穿零轴
    BEARISH = "空头"                    # DIF<DEA<0
    DEATH_CROSS = "死叉"                # DIF下穿DEA


class RSIStatus(Enum):
    """RSI状态枚举"""
    OVERBOUGHT = "超买"        # RSI > 70
    STRONG_BUY = "强势买入"    # 50 < RSI < 70
    NEUTRAL = "中性"          # 40 <= RSI <= 60
    WEAK = "弱势"             # 30 < RSI < 40
    OVERSOLD = "超卖"         # RSI < 30


class NotificationChannel(Enum):
    """通知渠道类型"""
    WECHAT = "wechat"  # 企业微信
    FEISHU = "feishu"  # 飞书
    TELEGRAM = "telegram"  # Telegram
    EMAIL = "email"  # 邮件
    PUSHOVER = "pushover"  # Pushover（手机/桌面推送）
    PUSHPLUS = "pushplus"  # PushPlus（国内推送服务）
    CUSTOM = "custom"  # 自定义 Webhook
    DISCORD = "discord"  # Discord 机器人 (Bot)
    SHOWDOC = "showdoc"  # ShowDoc推送
    WECHAT_MP_DRAFT = "wechat_mp_draft"  # 微信公众号草稿箱
    UNKNOWN = "unknown"  # 未知
