# -*- coding: utf-8 -*-
"""终端美化输出"""

from datetime import datetime
from ..core.models import CheckInStatus, CheckInResult, SummaryResult


class C:
    """ANSI 颜色"""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    GRAY    = "\033[90m"
    WHITE   = "\033[97m"

def c(text: str, color: str, bold: bool = False) -> str:
    b = C.BOLD if bold else ""
    return f"{b}{color}{text}{C.RESET}"

def divider(char: str = "─", width: int = 56) -> str:
    return c(char * width, C.GRAY)


class PrettyPrinter:

    def banner(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print()
        print(c("╔══════════════════════════════════════════════════════╗", C.CYAN))
        print(c("║", C.CYAN) + f"   {c('AnyRouter  多账号自动签到', C.WHITE, bold=True)}                     " + c("║", C.CYAN))
        print(c("║", C.CYAN) + f"   {c(now, C.GRAY)}                       " + c("║", C.CYAN))
        print(c("╚══════════════════════════════════════════════════════╝", C.CYAN))
        print()

    def account_header(self, index: int, total: int, name: str):
        tag = c(f"[{index}/{total}]", C.MAGENTA, bold=True)
        print(f"{tag}  {c(name, C.WHITE, bold=True)}")
        print(divider())

    def checkin_result(self, result: CheckInResult, show_sensitive: bool = False):
        status_map = {
            CheckInStatus.SUCCESS: (c("✅ 签到成功", C.GREEN), C.GREEN),
            CheckInStatus.ALREADY: (c("🔁 今日已签", C.YELLOW), C.YELLOW),
            CheckInStatus.FAILED:  (c("❌ 签到失败", C.RED),   C.RED),
            CheckInStatus.SKIPPED: (c("⏭️  已跳过",  C.GRAY),  C.GRAY),
        }
        status_label, msg_color = status_map[result.status]

        print(f"  状态: {status_label}  {c(result.message, msg_color)}")

        # 账号信息（脱敏控制）
        session_display = result.account.session if show_sensitive else result.account.masked_session()
        print(f"  {c('User:', C.GRAY)} {result.account.api_user}  "
              f"{c('Session:', C.GRAY)} {c(session_display, C.DIM)}")

        # 余额
        ba = result.balance_after
        bb = result.balance_before
        if ba is not None or bb is not None:
            delta_str = ""
            if ba is not None and bb is not None:
                delta = ba - bb
                if abs(delta) > 1e-8:
                    sign      = "+" if delta > 0 else ""
                    clr       = C.GREEN if delta > 0 else C.RED
                    delta_str = c(f"  ({sign}{delta:.4f})", clr)
                before_str = c(f"${bb:.4f}", C.GRAY)
                after_str  = c(f"${ba:.4f}", C.YELLOW, bold=True)
                print(f"  {c('余额:', C.GRAY)} {before_str} → {after_str}{delta_str}")
            elif ba is not None:
                print(f"  {c('余额:', C.GRAY)} {c(f'${ba:.4f}', C.YELLOW, bold=True)}")
            elif bb is not None:
                print(f"  {c('余额:', C.GRAY)} {c(f'${bb:.4f}', C.GRAY)} (签到后查询失败)")
        print()

    def summary(self, summary: SummaryResult):
        print(c("═" * 56, C.CYAN))
        print(f"  {c('📊 签到汇总', C.WHITE, bold=True)}")
        print(divider())

        s = len(summary.success_list)
        a = len(summary.already_list)
        f = len(summary.failed_list)
        k = len(summary.skipped_list)

        print(f"  总计: {c(str(summary.total), C.WHITE, bold=True)}  "
              f"成功: {c(str(s), C.GREEN, bold=True)}  "
              f"已签: {c(str(a), C.YELLOW, bold=True)}  "
              f"失败: {c(str(f), C.RED, bold=True)}  "
              f"跳过: {c(str(k), C.GRAY)}")

        if summary.total_balance is not None:
            print(f"  总余额: {c(f'${summary.total_balance:.4f}', C.YELLOW, bold=True)}")

        for group, label, color in [
            (summary.failed_list,  "❌ 失败账号", C.RED),
            (summary.skipped_list, "⏭️  跳过账号", C.GRAY),
        ]:
            if group:
                print(f"\n  {c(label + ':', color)}")
                for r in group:
                    print(f"     • {c(r.account.display_name(), C.WHITE)}  {c(r.message, C.GRAY)}")

        print(c("═" * 56, C.CYAN))
        print()
