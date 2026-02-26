# -*- coding: utf-8 -*-
"""签到核心服务"""

import time
import requests
from typing import Optional

from .models import AccountConfig, CheckInResult, CheckInStatus, SummaryResult
from .providers import ProviderConfig, get_provider


class CheckInService:
    def __init__(
        self,
        request_delay: float = 1.5,
        timeout: int = 15,
        custom_providers: Optional[dict] = None,
    ):
        self.request_delay    = request_delay
        self.timeout          = timeout
        self.custom_providers = custom_providers or {}

    # ── HTTP helpers ────────────────────────────────────────────

    def _headers(self, account: AccountConfig, provider: ProviderConfig) -> dict:
        return {
            "Cookie": f"session={account.session}",
            provider.api_user_key: str(account.api_user),
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer": provider.domain,
            "Origin":  provider.domain,
        }

    def _get_balance(self, account: AccountConfig, provider: ProviderConfig) -> Optional[float]:
        try:
            url  = provider.domain + provider.user_info_path
            resp = requests.get(
                url,
                headers=self._headers(account, provider),
                timeout=self.timeout,
            )
            data  = resp.json()
            quota = data.get("data", {}).get("quota")
            if quota is not None:
                return round(float(quota) / 500000, 6)   # OneAPI 单位 → 美元
        except Exception:
            pass
        return None

    def _do_sign_in(self, account: AccountConfig, provider: ProviderConfig) -> dict:
        """
        返回 {"status": CheckInStatus, "message": str}
        """
        url = provider.domain + provider.sign_in_path
        try:
            resp = requests.post(
                url,
                headers=self._headers(account, provider),
                timeout=self.timeout,
            )

            # 尝试解析 JSON
            try:
                data = resp.json()
            except Exception:
                return {"status": CheckInStatus.FAILED, "message": f"响应解析失败 (HTTP {resp.status_code})"}

            success = data.get("success", False)
            # message 优先取 data 字段内容，再取 message，最后降级为完整 JSON
            message = (
                data.get("message")
                or data.get("data")
                or data.get("msg")
                or f"HTTP {resp.status_code}"
            )
            if not isinstance(message, str):
                message = str(message)

            if success:
                return {"status": CheckInStatus.SUCCESS, "message": message or "签到成功"}

            # 识别"今日已签到"
            already_keywords = ["already", "今日", "重复", "signed", "checkin"]
            if any(k in message.lower() for k in already_keywords):
                return {"status": CheckInStatus.ALREADY, "message": message}

            return {"status": CheckInStatus.FAILED, "message": message or "未知错误"}

        except requests.exceptions.Timeout:
            return {"status": CheckInStatus.FAILED, "message": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"status": CheckInStatus.FAILED, "message": "网络连接失败"}
        except Exception as e:
            return {"status": CheckInStatus.FAILED, "message": f"异常: {e}"}

    # ── Public API ───────────────────────────────────────────────

    def check_in_one(self, account: AccountConfig) -> CheckInResult:
        provider = get_provider(account.provider, self.custom_providers)

        # 签到前余额（所有账号都查）
        balance_before = self._get_balance(account, provider)

        # 执行签到
        result  = self._do_sign_in(account, provider)
        status  = result["status"]
        message = result["message"]

        # 签到后余额（所有账号都查，用于对比）
        balance_after = self._get_balance(account, provider)

        return CheckInResult(
            account=account,
            status=status,
            message=message,
            balance_before=balance_before,
            balance_after=balance_after,
        )

    def check_in_all(self, accounts: list) -> SummaryResult:
        summary = SummaryResult()
        for i, account in enumerate(accounts):
            result = self.check_in_one(account)
            summary.results.append(result)
            if i < len(accounts) - 1:
                time.sleep(self.request_delay)
        return summary
