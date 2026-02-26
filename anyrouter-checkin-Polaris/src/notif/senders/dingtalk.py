# -*- coding: utf-8 -*-
"""钉钉 Webhook 通知"""

import hmac
import hashlib
import base64
import time
import urllib.parse
import requests


def send(config: dict, title: str, content: str) -> bool:
    """
    config 字段:
      webhook : 钉钉 Webhook 地址
      secret  : 签名密钥（可选，加签安全模式）
    """
    webhook = config.get("webhook", "")
    secret  = config.get("secret", "")
    if not webhook:
        print("  [钉钉] ⚠️  缺少 webhook，跳过")
        return False

    url = webhook
    if secret:
        timestamp  = str(round(time.time() * 1000))
        sign_str   = f"{timestamp}\n{secret}"
        sign       = base64.b64encode(
            hmac.new(secret.encode(), sign_str.encode(), digestmod=hashlib.sha256).digest()
        ).decode()
        url += f"&timestamp={timestamp}&sign={urllib.parse.quote_plus(sign)}"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text":  f"## {title}\n\n{content}",
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        ok   = resp.json().get("errcode", -1) == 0
        if ok:
            print("  [钉钉] ✅ 发送成功")
        else:
            print(f"  [钉钉] ❌ 发送失败: {resp.text}")
        return ok
    except Exception as e:
        print(f"  [钉钉] ❌ 异常: {e}")
        return False
