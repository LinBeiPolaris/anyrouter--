# -*- coding: utf-8 -*-
"""SMTP 邮件通知"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send(config: dict, title: str, content: str) -> bool:
    """
    config 字段:
      smtp_host : SMTP 服务器
      smtp_port : 端口（默认 465）
      sender    : 发件人邮箱
      password  : 授权码
      receiver  : 收件人邮箱（多个用逗号分隔）
    """
    host     = config.get("smtp_host", "")
    port     = int(config.get("smtp_port", 465))
    sender   = config.get("sender", "")
    password = config.get("password", "")
    receiver = config.get("receiver", "")

    if not all([host, sender, password, receiver]):
        print("  [邮件] ⚠️  配置不完整，跳过")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"]    = sender
    msg["To"]      = receiver

    # 纯文本
    msg.attach(MIMEText(content, "plain", "utf-8"))
    # HTML 版
    html_content = content.replace("\n", "<br>")
    html = f"""
    <html><body style="font-family:monospace;background:#1a1a2e;color:#e0e0e0;padding:20px">
    <h2 style="color:#00d4ff">{title}</h2>
    <pre style="background:#16213e;padding:15px;border-radius:8px;line-height:1.6">{html_content}</pre>
    </body></html>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver.split(","), msg.as_string())
        print("  [邮件] ✅ 发送成功")
        return True
    except Exception as e:
        print(f"  [邮件] ❌ 发送失败: {e}")
        return False
