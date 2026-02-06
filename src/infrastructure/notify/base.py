# -*- coding: utf-8 -*-
"""
===================================
通知模块基础类
===================================

包含：
- NotificationChannel 枚举（从 domain 重导出）
- SMTP 服务器配置
- ChannelDetector 渠道检测器
"""

import logging
from typing import Dict, Any

from src.domain.enums import NotificationChannel

logger = logging.getLogger(__name__)


# SMTP 服务器配置（自动识别）
SMTP_CONFIGS: Dict[str, Dict[str, Any]] = {
    # QQ邮箱
    "qq.com": {"server": "smtp.qq.com", "port": 465, "ssl": True},
    "foxmail.com": {"server": "smtp.qq.com", "port": 465, "ssl": True},
    # 网易邮箱
    "163.com": {"server": "smtp.163.com", "port": 465, "ssl": True},
    "126.com": {"server": "smtp.126.com", "port": 465, "ssl": True},
    # Gmail
    "gmail.com": {"server": "smtp.gmail.com", "port": 587, "ssl": False},
    # Outlook
    "outlook.com": {"server": "smtp-mail.outlook.com", "port": 587, "ssl": False},
    "hotmail.com": {"server": "smtp-mail.outlook.com", "port": 587, "ssl": False},
    "live.com": {"server": "smtp-mail.outlook.com", "port": 587, "ssl": False},
    # 新浪
    "sina.com": {"server": "smtp.sina.com", "port": 465, "ssl": True},
    # 搜狐
    "sohu.com": {"server": "smtp.sohu.com", "port": 465, "ssl": True},
    # 阿里云
    "aliyun.com": {"server": "smtp.aliyun.com", "port": 465, "ssl": True},
    # 139邮箱
    "139.com": {"server": "smtp.139.com", "port": 465, "ssl": True},
}


class ChannelDetector:
    """
    渠道检测器 - 简化版

    根据配置直接判断渠道类型（不再需要 URL 解析）
    """

    @staticmethod
    def get_channel_name(channel: NotificationChannel) -> str:
        """获取渠道中文名称"""
        names = {
            NotificationChannel.WECHAT: "企业微信",
            NotificationChannel.FEISHU: "飞书",
            NotificationChannel.TELEGRAM: "Telegram",
            NotificationChannel.EMAIL: "邮件",
            NotificationChannel.PUSHOVER: "Pushover",
            NotificationChannel.PUSHPLUS: "PushPlus",
            NotificationChannel.CUSTOM: "自定义Webhook",
            NotificationChannel.DISCORD: "Discord机器人",
            NotificationChannel.SHOWDOC: "ShowDoc推送",
            NotificationChannel.WECHAT_MP_DRAFT: "微信公众号草稿箱",
            NotificationChannel.UNKNOWN: "未知渠道",
        }
        return names.get(channel, "未知渠道")
