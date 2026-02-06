# -*- coding: utf-8 -*-
"""
===================================
通知服务聚合类
===================================

兼容层：重导出原 NotificationService。

完整实现仍在 src/notification.py 中。
后续版本将逐步迁移到此模块。
"""

import warnings

# 重导出原 NotificationService
from src.notification import NotificationService

__all__ = ["NotificationService"]

# 添加弃用提示（仅在直接导入此模块时显示）
warnings.warn(
    "src.infrastructure.notify.service 模块正在开发中，"
    "当前版本重导出 src.notification.NotificationService。"
    "建议直接使用 from src.notification import NotificationService",
    FutureWarning,
    stacklevel=2
)
