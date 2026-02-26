# -*- coding: utf-8 -*-
"""
通知模板渲染器
支持变量: {total} {success} {already} {failed} {skipped}
          {all_success} {has_failure} {total_balance}
          {success_names} {failed_names} {already_names}
          {detail_list}
"""

from ..core.models import SummaryResult


DEFAULT_TITLE = "AnyRouter 签到提醒"

DEFAULT_TEMPLATE = """\
📋 AnyRouter 签到完成

总计: {total} 个账号
✅ 成功: {success}  🔁 已签: {already}  ❌ 失败: {failed}

{detail_list}
总余额: {total_balance}
"""


def _build_detail_list(summary: SummaryResult, show_sensitive: bool = False) -> str:
    lines = []
    for r in summary.results:
        status_icon = {
        }.get(r.status.value, "❓")
        from ..core.models import CheckInStatus
        icon_map = {
            CheckInStatus.SUCCESS: "✅",
            CheckInStatus.ALREADY: "🔁",
            CheckInStatus.FAILED:  "❌",
            CheckInStatus.SKIPPED: "⏭️",
        }
        icon = icon_map.get(r.status, "❓")
        name = r.account.display_name()

        bal = ""
        if r.balance_after is not None:
            bal = f"  余额: ${r.balance_after:.4f}"
            if r.balance_delta and abs(r.balance_delta) > 1e-8:
                sign = "+" if r.balance_delta > 0 else ""
                bal += f" ({sign}{r.balance_delta:.4f})"

        lines.append(f"{icon} {name}{bal}  — {r.message}")
    return "\n".join(lines) if lines else "（无）"


def render(template: str, summary: SummaryResult, show_sensitive: bool = False) -> str:
    """将模板字符串渲染为通知内容"""
    s = summary

    def names(lst):
        return "、".join(r.account.display_name() for r in lst) or "无"

    total_balance = f"${s.total_balance:.4f}" if s.total_balance is not None else "N/A"

    variables = {
        "total":         str(s.total),
        "success":       str(len(s.success_list)),
        "already":       str(len(s.already_list)),
        "failed":        str(len(s.failed_list)),
        "skipped":       str(len(s.skipped_list)),
        "all_success":   "是" if s.all_success else "否",
        "has_failure":   "是" if s.has_failure else "否",
        "total_balance": total_balance,
        "success_names": names(s.success_list),
        "already_names": names(s.already_list),
        "failed_names":  names(s.failed_list),
        "detail_list":   _build_detail_list(s, show_sensitive),
    }

    try:
        return template.format(**variables)
    except KeyError as e:
        return f"模板变量错误: {e}\n\n" + DEFAULT_TEMPLATE.format(**variables)
