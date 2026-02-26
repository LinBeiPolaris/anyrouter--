# -*- coding: utf-8 -*-
"""
配置加载器
优先级: .env 文件 < 环境变量

环境变量说明:
  ANYROUTER_ACCOUNTS  : JSON 数组，账号列表（必填）
  PROVIDERS           : JSON 对象，自定义服务商（可选）
  SHOW_SENSITIVE_INFO : true/false，是否显示敏感信息（默认 false）
  REQUEST_DELAY       : 请求间隔秒数（默认 1.5）
  NOTIF_CONFIG        : JSON 对象，通知渠道配置（可选）

通知渠道也可以单独配置（与 NOTIF_CONFIG 合并）:
  TELEGRAM_NOTIF_CONFIG  : JSON 对象
  DINGTALK_NOTIF_CONFIG  : JSON 对象
  WECOM_NOTIF_CONFIG     : JSON 对象
  EMAIL_NOTIF_CONFIG     : JSON 对象
"""

import os
import json
from pathlib import Path
from ..core.models import AccountConfig


def _load_dotenv(path: str = ".env"):
    """手动解析 .env 文件（不依赖 python-dotenv）"""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _parse_json_env(key: str, default=None):
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  ⚠️  环境变量 {key} JSON 解析失败: {e}")
        return default


def load_accounts() -> list:
    raw_list = _parse_json_env("ANYROUTER_ACCOUNTS", [])
    accounts = []
    for i, item in enumerate(raw_list):
        session  = item.get("cookies", {}).get("session") or item.get("session", "")
        api_user = str(item.get("api_user", ""))
        if not session or not api_user:
            print(f"  ⚠️  账号 #{i+1} 缺少 session 或 api_user，跳过")
            continue
        accounts.append(AccountConfig(
            session  = session,
            api_user = api_user,
            name     = item.get("name", f"账号{i+1}"),
            provider = item.get("provider", "anyrouter"),
        ))
    return accounts


def load_custom_providers() -> dict:
    return _parse_json_env("PROVIDERS", {})


def load_notif_configs() -> dict:
    """合并 NOTIF_CONFIG 与各渠道独立配置"""
    merged = _parse_json_env("NOTIF_CONFIG", {})

    channel_envs = {
        "telegram": "TELEGRAM_NOTIF_CONFIG",
        "dingtalk":  "DINGTALK_NOTIF_CONFIG",
        "wecom":     "WECOM_NOTIF_CONFIG",
        "email":     "EMAIL_NOTIF_CONFIG",
    }
    for channel, env_key in channel_envs.items():
        cfg = _parse_json_env(env_key)
        if cfg:
            merged[channel] = cfg

    return merged


def load_settings() -> dict:
    _load_dotenv(".env")
    return {
        "show_sensitive": os.environ.get("SHOW_SENSITIVE_INFO", "false").lower() == "true",
        "request_delay":  float(os.environ.get("REQUEST_DELAY", "1.5")),
    }
