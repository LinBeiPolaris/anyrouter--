#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════╗
║       AnyRouter 多账号自动签到  v2.0              ║
║  支持: 多账号 · 多服务商 · 多通知渠道 · 余额追踪  ║
╚═══════════════════════════════════════════════════╝
"""

import sys

# ── 依赖检查 ────────────────────────────────────────
try:
    import requests
except ImportError:
    print("❌ 缺少依赖，请先运行: pip install requests")
    sys.exit(1)

from src.tools.config_loader import (
    load_settings,
    load_accounts,
    load_custom_providers,
    load_notif_configs,
)
from src.core.checkin_service import CheckInService
from src.notif.notification_kit import NotificationKit
from src.tools.printer import PrettyPrinter


def main():
    printer  = PrettyPrinter()
    settings = load_settings()

    printer.banner()

    # ── 加载账号 ────────────────────────────────────
    accounts = load_accounts()
    if not accounts:
        print("  ⚠️  未找到有效账号配置！")
        print()
        print("  请在 .env 文件中配置 ANYROUTER_ACCOUNTS，格式：")
        print('  ANYROUTER_ACCOUNTS=[{"name":"账号1","cookies":{"session":"..."},"api_user":"12345"}]')
        print()
        return

    # ── 执行签到 ────────────────────────────────────
    service = CheckInService(
        request_delay    = settings["request_delay"],
        custom_providers = load_custom_providers(),
    )

    show = settings["show_sensitive"]
    total = len(accounts)

    results_list = []
    for i, account in enumerate(accounts, 1):
        printer.account_header(i, total, account.display_name())
        result = service.check_in_one(account)
        results_list.append(result)
        printer.checkin_result(result, show_sensitive=show)

        # 非最后一个账号时等待
        if i < total:
            import time
            time.sleep(settings["request_delay"])

    # ── 汇总输出 ────────────────────────────────────
    from src.core.models import SummaryResult
    summary = SummaryResult(results=results_list)
    printer.summary(summary)

    # ── 推送通知 ────────────────────────────────────
    notif_configs = load_notif_configs()
    if notif_configs:
        kit = NotificationKit(notif_configs, show_sensitive=show)
        kit.dispatch(summary)
    else:
        print("  ℹ️  未配置通知渠道，跳过推送")
        print()


if __name__ == "__main__":
    main()
