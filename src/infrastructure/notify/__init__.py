# -*- coding: utf-8 -*-
"""
===================================
Notify 模块 - 通知渠道实现
===================================

从 src/notification.py 拆分而来。

包含：
- base: 基础类和枚举
- wechat_mp: 微信公众号草稿箱客户端

注意：完整的 NotificationService 仍在 src/notification.py 中。
此模块提供新架构的入口点，后续版本将逐步完成迁移。
"""

from src.infrastructure.notify.base import (
    SMTP_CONFIGS,
    ChannelDetector,
)
from src.infrastructure.notify.wechat_mp import WechatMPDraftClient

__all__ = [
    "SMTP_CONFIGS",
    "ChannelDetector",
    "WechatMPDraftClient",
]


def get_notification_service():
    """
    获取 NotificationService 实例

    兼容层：返回原 src.notification.NotificationService
    """
    from src.notification import NotificationService
    return NotificationService
