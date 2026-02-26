# -*- coding: utf-8 -*-
"""Telegram Bot 通知"""

import requests


def send(config: dict, title: str, content: str) -> bool:
    """
    config 字段:
      bot_token  : Telegram Bot Token
      chat_id    : 目标 Chat ID
    """
    bot_token = config.get("bot_token", "")
    chat_id   = config.get("chat_id", "")
    if not bot_token or not chat_id:
        print("  [Telegram] ⚠️  缺少 bot_token 或 chat_id，跳过")
        return False

    text = f"*{title}*\n\n{content}"
    url  = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id":    chat_id,
            "text":       text,
            "parse_mode": "Markdown",
        }, timeout=15)
        ok = resp.json().get("ok", False)
        if ok:
            print("  [Telegram] ✅ 发送成功")
        else:
            print(f"  [Telegram] ❌ 发送失败: {resp.text}")
        return ok
    except Exception as e:
        print(f"  [Telegram] ❌ 异常: {e}")
        return False
