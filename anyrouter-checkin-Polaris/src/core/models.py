# -*- coding: utf-8 -*-
"""核心数据模型"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class CheckInStatus(Enum):
    SUCCESS = "success"
    ALREADY = "already"       # 今日已签到
    FAILED  = "failed"
    SKIPPED = "skipped"       # 配置不完整跳过


@dataclass
class AccountConfig:
    """账号配置"""
    session:  str
    api_user: str
    name:     str = ""
    provider: str = "anyrouter"   # anyrouter | agentrouter | custom

    def display_name(self) -> str:
        return self.name or f"账号-{self.api_user[:6]}..."

    def masked_session(self) -> str:
        """脱敏 session"""
        if len(self.session) <= 8:
            return "****"
        return self.session[:4] + "****" + self.session[-4:]


@dataclass
class CheckInResult:
    """单个账号签到结果"""
    account:      AccountConfig
    status:       CheckInStatus
    message:      str         = ""
    balance_before: Optional[float] = None
    balance_after:  Optional[float] = None

    @property
    def success(self) -> bool:
        return self.status in (CheckInStatus.SUCCESS, CheckInStatus.ALREADY)

    @property
    def balance_changed(self) -> Optional[bool]:
        if self.balance_before is None or self.balance_after is None:
            return None
        return self.balance_after != self.balance_before

    @property
    def balance_delta(self) -> Optional[float]:
        if self.balance_before is None or self.balance_after is None:
            return None
        return self.balance_after - self.balance_before

    def balance_str(self, value: Optional[float]) -> str:
        if value is None:
            return "N/A"
        return f"${value:.4f}"


@dataclass
class SummaryResult:
    """全部账号汇总结果"""
    results: list = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_list(self) -> list:
        return [r for r in self.results if r.status == CheckInStatus.SUCCESS]

    @property
    def already_list(self) -> list:
        return [r for r in self.results if r.status == CheckInStatus.ALREADY]

    @property
    def failed_list(self) -> list:
        return [r for r in self.results if r.status == CheckInStatus.FAILED]

    @property
    def skipped_list(self) -> list:
        return [r for r in self.results if r.status == CheckInStatus.SKIPPED]

    @property
    def all_success(self) -> bool:
        return len(self.failed_list) == 0 and len(self.skipped_list) == 0

    @property
    def has_failure(self) -> bool:
        return len(self.failed_list) > 0

    @property
    def total_balance(self) -> Optional[float]:
        totals = [r.balance_after for r in self.results if r.balance_after is not None]
        return sum(totals) if totals else None
