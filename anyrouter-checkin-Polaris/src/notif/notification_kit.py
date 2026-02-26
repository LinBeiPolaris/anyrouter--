# -*- coding: utf-8 -*-
"""
通知编排器
支持通知渠道: telegram | dingtalk | wecom | email
触发时机: always | on_failure | on_success
"""

import json
from ..core.models import SummaryResult
from .template import render, DEFAULT_TITLE, DEFAULT_TEMPLATE
from .senders.telegram import send as telegram_send
from .senders.dingtalk import send as dingtalk_send
from .senders.wecom import send as wecom_send
from .senders.email_sender import send as email_send


SENDER_MAP = {
    "telegram": telegram_send,
    "dingtalk":  dingtalk_send,
    "wecom":     wecom_send,
    "email":     email_send,
}


class NotificationKit:
    def __init__(self, configs: dict, show_sensitive: bool = False):
        """
        configs 格式:
        {
            "telegram": {
                "trigger": "always",   # always | on_failure | on_success
                "config": { "bot_token": "...", "chat_id": "..." },
                "title":    "可选自定义标题",
                "template": "可选自定义模板，支持 {变量}"
            },
            "dingtalk": { ... },
            ...
        }
        """
        self.configs        = configs or {}
        self.show_sensitive = show_sensitive

    def dispatch(self, summary: SummaryResult):
        if not self.configs:
            return

        print("\n─── 通知推送 ─────────────────────────────────────────")
        for channel, cfg in self.configs.items():
            sender = SENDER_MAP.get(channel)
            if sender is None:
                print(f"  [未知渠道] {channel}，跳过")
                continue

            trigger = cfg.get("trigger", "always")
            if trigger == "on_failure" and not summary.has_failure:
                print(f"  [{channel}] ℹ️  无失败，跳过")
                continue
            if trigger == "on_success" and summary.has_failure:
                print(f"  [{channel}] ℹ️  有失败，跳过（trigger=on_success）")
                continue

            title    = cfg.get("title",    DEFAULT_TITLE)
            template = cfg.get("template", DEFAULT_TEMPLATE)
            content  = render(template, summary, self.show_sensitive)

            sender(cfg.get("config", {}), title, content)
