#!/usr/bin/env python3
"""
BEAM — send_email.py
通过 Resend API 发送 HTML 邮件。纯标准库实现，零第三方依赖。

环境变量（必须）：
  RESEND_API_KEY  — Resend API 密钥（re_ 开头）
  RESEND_FROM     — 已验证的发件地址（如 noreply@yourdomain.com）

用法：
  python send_email.py --to user@example.com --subject "日报" --html-file .tmp/email.html
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


RESEND_API_URL = "https://api.resend.com/emails"


def send(to: str, subject: str, html: str, api_key: str, from_addr: str) -> dict:
    """调用 Resend API 发送邮件，返回响应 JSON"""
    payload = json.dumps({
        "from": from_addr,
        "to": [to],
        "subject": subject,
        "html": html,
    }).encode("utf-8")

    req = urllib.request.Request(
        RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"ERROR: Resend API 返回 {e.code}", file=sys.stderr)
        print(f"  响应: {error_body}", file=sys.stderr)
        sys.exit(2)
    except urllib.error.URLError as e:
        print(f"ERROR: 网络错误: {e.reason}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description="BEAM: 通过 Resend API 发送 HTML 邮件")
    parser.add_argument("--to", required=True, help="收件人邮箱")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--html-file", required=True, help="HTML 邮件文件路径")
    args = parser.parse_args()

    # 读取环境变量
    api_key = os.environ.get("RESEND_API_KEY")
    from_addr = os.environ.get("RESEND_FROM")

    if not api_key:
        print("ERROR: 缺少环境变量 RESEND_API_KEY", file=sys.stderr)
        print("  请在 ~/.env_dashboard 中配置，或 export RESEND_API_KEY=re_xxx", file=sys.stderr)
        sys.exit(1)

    if not from_addr:
        print("ERROR: 缺少环境变量 RESEND_FROM", file=sys.stderr)
        print("  请在 ~/.env_dashboard 中配置，或 export RESEND_FROM=noreply@yourdomain.com", file=sys.stderr)
        sys.exit(1)

    # 读取 HTML 文件
    if not os.path.exists(args.html_file):
        print(f"ERROR: HTML 文件不存在: {args.html_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.html_file, "r", encoding="utf-8") as f:
        html = f.read()

    # 发送
    result = send(
        to=args.to,
        subject=args.subject,
        html=html,
        api_key=api_key,
        from_addr=from_addr,
    )

    email_id = result.get("id", "unknown")
    print(f"邮件发送成功 id={email_id}")
    print(f"  收件人: {args.to}")
    print(f"  主题: {args.subject}")


if __name__ == "__main__":
    main()
