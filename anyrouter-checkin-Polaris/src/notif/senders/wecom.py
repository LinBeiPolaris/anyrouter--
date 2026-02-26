# -*- coding: utf-8 -*-
"""企业微信 Webhook 通知"""

import requests


def send(config: dict, title: str, content: str) -> bool:
    """
    config 字段:
      webhook : 企业微信 Webhook 地址
    """
    webhook = config.get("webhook", "")
    if not webhook:
        print("  [企业微信] ⚠️  缺少 webhook，跳过")
        return False

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"## {title}\n{content}",
        },
    }
    try:
        resp = requests.post(webhook, json=payload, timeout=15)
        ok   = resp.json().get("errcode", -1) == 0
        if ok:
            print("  [企业微信] ✅ 发送成功")
        else:
            print(f"  [企业微信] ❌ 发送失败: {resp.text}")
        return ok
    except Exception as e:
        print(f"  [企业微信] ❌ 异常: {e}")
        return False
