#!/usr/bin/env python3
"""
BEAM — build_email.py
读取 kpis.json，生成 600px 宽的 HTML 邮件，兼容 Outlook/Gmail/移动端。

邮件布局规范详见 references/email-template-guide.md。
核心约束：全 <table> 布局、行内样式、无 CDN 依赖。

用法：
  python build_email.py [--kpis .tmp/kpis.json] [--vercel-url https://...] \
                        [--theme swiss] [--output .tmp/email.html]
"""

import argparse
import json
import os
import sys
from datetime import datetime


# ── 主题色字典（与 LENS style-catalog.md 对齐）─────────────────────────────
# 邮件使用固体背景色（不用渐变），字号适配 email 客户端，与 LENS 同主题保持视觉一致。
EMAIL_THEMES = {
    # Swiss/NZZ — LENS 默认主题：黑白灰 + 红色警示
    "swiss": {
        "header_bg":    "#1A1A1A",   # 深灰黑（Swiss 纯黑的邮件友好版）
        "header_text":  "#FFFFFF",
        "accent":       "#1A1A1A",
        "kpi_value":    "#000000",
        "bar_color":    "#1A1A1A",
        "positive":     "#2A9D8F",   # 全局 --kpi-up（Swiss 用黑表示正增长，邮件用绿更直观）
        "negative":     "#CC0000",   # Swiss --kpi-down
        "neutral":      "#767676",   # Swiss --text-muted
        "bg_section":   "#F5F5F5",
        "border":       "#E5E5E5",
    },
    # Financial Times — 三文鱼粉 + 深蓝
    "financial_times": {
        "header_bg":    "#0F5499",
        "header_text":  "#FFFFFF",
        "accent":       "#0F5499",
        "kpi_value":    "#0F5499",
        "bar_color":    "#0F5499",
        "positive":     "#0A7B3E",
        "negative":     "#CC0000",
        "neutral":      "#9E9893",
        "bg_section":   "#FFF1E5",
        "border":       "#E0D5CA",
    },
    # McKinsey — 深蓝 + 金
    "mckinsey": {
        "header_bg":    "#00338D",
        "header_text":  "#FFFFFF",
        "accent":       "#00338D",
        "kpi_value":    "#00338D",
        "bar_color":    "#00338D",
        "positive":     "#056B3A",
        "negative":     "#C62828",
        "neutral":      "#8993A4",
        "bg_section":   "#F4F6F9",
        "border":       "#D1D5DB",
    },
    # Fathom — 温暖深蓝 + 薄荷绿
    "fathom": {
        "header_bg":    "#1D3557",
        "header_text":  "#FFFFFF",
        "accent":       "#457B9D",
        "kpi_value":    "#1D3557",
        "bar_color":    "#457B9D",
        "positive":     "#2A9D8F",
        "negative":     "#E63946",
        "neutral":      "#A8DADC",
        "bg_section":   "#F8F9FA",
        "border":       "#DEE2E6",
    },
    # 兜底 default（未指定主题时使用）
    "default": {
        "header_bg":    "#1F2937",
        "header_text":  "#FFFFFF",
        "accent":       "#2563EB",
        "kpi_value":    "#1A1A2E",
        "bar_color":    "#2563EB",
        "positive":     "#16A34A",
        "negative":     "#DC2626",
        "neutral":      "#6B7280",
        "bg_section":   "#F8F9FA",
        "border":       "#E5E7EB",
    },
}

BG_LIGHT = "#F5F5F5"
BG_WHITE  = "#FFFFFF"


def trend_arrow(pct, tc):
    """根据环比百分比返回箭头和颜色"""
    if pct > 1:
        return "▲", tc["positive"]
    elif pct < -1:
        return "▼", tc["negative"]
    else:
        return "─", tc["neutral"]


def fmt_money(val):
    """格式化金额"""
    if val >= 10000:
        return f"¥{val/10000:.1f}万"
    return f"¥{val:,.0f}"


def build_kpi_cell(label, value, tc, trend_pct=None, is_pct=False):
    """生成单个 KPI 卡片 HTML"""
    display_val = f"{value}%" if is_pct else fmt_money(value)
    trend_html = ""
    if trend_pct is not None:
        arrow, color = trend_arrow(trend_pct, tc)
        trend_html = f'<p style="color:{color};font-size:12px;margin:0;">{arrow} {abs(trend_pct):.1f}% 环比</p>'

    return f'''<td class="kpi-cell" width="25%" style="padding:6px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:{BG_WHITE};border-radius:6px;border:1px solid {tc["border"]};">
        <tr><td style="padding:14px 8px;text-align:center;">
          <p style="color:{tc["neutral"]};font-size:11px;margin:0;line-height:1.4;">{label}</p>
          <p style="color:{tc["kpi_value"]};font-size:22px;font-weight:bold;margin:6px 0 4px;">{display_val}</p>
          {trend_html}
        </td></tr>
      </table>
    </td>'''


def build_channel_bar(name, gmv, max_gmv, tc):
    """生成渠道分布进度条"""
    pct = (gmv / max_gmv * 100) if max_gmv > 0 else 0
    return f'''<tr>
      <td width="28%" style="font-size:13px;color:#555;padding:4px 0;">{name}</td>
      <td width="50%" style="padding:4px 0;">
        <div style="background:{tc["border"]};border-radius:4px;height:10px;">
          <div style="background:{tc["bar_color"]};width:{pct:.0f}%;height:10px;border-radius:4px;min-width:4px;"></div>
        </div>
      </td>
      <td width="22%" style="font-size:12px;color:{tc["neutral"]};text-align:right;padding:4px 0;">{fmt_money(gmv)}</td>
    </tr>'''


def build_email(kpis, vercel_url=None, theme="swiss"):
    """组装完整 HTML 邮件"""
    tc = EMAIL_THEMES.get(theme, EMAIL_THEMES["default"])

    overview   = kpis.get("overview",    {})
    last_7d    = kpis.get("last_7d",     {})
    today      = kpis.get("today",       {})
    channels   = kpis.get("channels",    [])
    top3       = kpis.get("top3_skus",   [])
    reviews    = kpis.get("reviews",     {})
    date_range = kpis.get("date_range",  {})
    meta       = kpis.get("meta",        {})

    report_date = meta.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M"))[:10]

    # ── Header（纯色背景，与 LENS 主题一致；Swiss 无渐变）──
    header = f'''<table width="100%" cellpadding="0" cellspacing="0" style="background:{tc["header_bg"]};border-radius:8px 8px 0 0;">
      <tr><td bgcolor="{tc["header_bg"]}" style="padding:24px 20px;text-align:center;background:{tc["header_bg"]};">
        <h1 style="color:{tc["header_text"]};font-size:20px;margin:0;font-family:Arial,sans-serif;">经营分析日报</h1>
        <p style="color:rgba(255,255,255,0.75);font-size:12px;margin:8px 0 0;">{report_date}</p>
      </td></tr>
    </table>'''

    # ── KPI 卡片 ──
    kpi_cells  = build_kpi_cell("总 GMV",  overview.get("total_gmv",        0), tc)
    kpi_cells += build_kpi_cell("毛利率",  overview.get("gross_margin_pct", 0), tc, is_pct=True)
    kpi_cells += build_kpi_cell("客单价",  overview.get("avg_order_value",  0), tc)
    kpi_cells += build_kpi_cell("退款率",  overview.get("refund_rate_pct",  0), tc, is_pct=True)

    kpi_strip = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:2px;">
      <tr>{kpi_cells}</tr>
    </table>'''

    # ── 近 7 日动态 ──
    weekly_section = ""
    if last_7d:
        arrow, color = trend_arrow(last_7d.get("wow_pct", 0), tc)
        weekly_section = f'''<table width="100%" cellpadding="0" cellspacing="0" style="background:{tc["bg_section"]};border-radius:6px;margin-top:12px;border:1px solid {tc["border"]};">
      <tr><td style="padding:14px 18px;">
        <p style="font-size:14px;font-weight:bold;color:#333;margin:0 0 10px;">近 7 日动态</p>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="33%">
              <p style="color:{tc["neutral"]};font-size:11px;margin:0;">7日 GMV</p>
              <p style="font-size:17px;font-weight:bold;margin:4px 0 2px;">{fmt_money(last_7d.get("gmv", 0))}</p>
              <p style="color:{color};font-size:11px;margin:0;">{arrow} {abs(last_7d.get("wow_pct", 0)):.1f}% 环比上周</p>
            </td>
            <td width="33%">
              <p style="color:{tc["neutral"]};font-size:11px;margin:0;">订单数</p>
              <p style="font-size:17px;font-weight:bold;margin:4px 0 2px;">{overview.get("order_count", "—")}</p>
            </td>
            <td width="33%">
              <p style="color:{tc["neutral"]};font-size:11px;margin:0;">综合评分</p>
              <p style="font-size:17px;font-weight:bold;margin:4px 0 2px;">{reviews.get("avg_score", "—")}</p>
            </td>
          </tr>
        </table>
      </td></tr>
    </table>'''

    # ── 今日实时 ──
    today_section = ""
    if today:
        today_section = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px;">
      <tr><td style="padding:0 0 4px;">
        <p style="font-size:14px;font-weight:bold;color:#333;margin:0 0 8px;padding:0 6px;">今日实时</p>
      </td></tr>
      <tr>
        <td width="25%" style="padding:4px 6px;">
          <table width="100%" style="background:{BG_WHITE};border-radius:6px;border:1px solid {tc["border"]};">
            <tr><td style="padding:10px;text-align:center;">
              <p style="color:{tc["neutral"]};font-size:10px;margin:0;">当日GMV</p>
              <p style="color:{tc["kpi_value"]};font-size:16px;font-weight:bold;margin:4px 0 0;">{fmt_money(today.get("gmv", 0))}</p>
            </td></tr>
          </table>
        </td>
        <td width="25%" style="padding:4px 6px;">
          <table width="100%" style="background:{BG_WHITE};border-radius:6px;border:1px solid {tc["border"]};">
            <tr><td style="padding:10px;text-align:center;">
              <p style="color:{tc["neutral"]};font-size:10px;margin:0;">订单数</p>
              <p style="font-size:16px;font-weight:bold;margin:4px 0 0;">{today.get("orders", "—")}</p>
            </td></tr>
          </table>
        </td>
        <td width="25%" style="padding:4px 6px;">
          <table width="100%" style="background:{BG_WHITE};border-radius:6px;border:1px solid {tc["border"]};">
            <tr><td style="padding:10px;text-align:center;">
              <p style="color:{tc["neutral"]};font-size:10px;margin:0;">广告ROI</p>
              <p style="font-size:16px;font-weight:bold;margin:4px 0 0;">{today.get("ad_roi", "—")}</p>
            </td></tr>
          </table>
        </td>
        <td width="25%" style="padding:4px 6px;">
          <table width="100%" style="background:{BG_WHITE};border-radius:6px;border:1px solid {tc["border"]};">
            <tr><td style="padding:10px;text-align:center;">
              <p style="color:{tc["neutral"]};font-size:10px;margin:0;">毛利率</p>
              <p style="font-size:16px;font-weight:bold;margin:4px 0 0;">{today.get("gross_margin_pct", "—")}%</p>
            </td></tr>
          </table>
        </td>
      </tr>
    </table>'''

    # ── 渠道分布 ──
    channel_section = ""
    if channels:
        max_gmv = channels[0]["gmv"] if channels else 1
        channel_rows = "\n".join(build_channel_bar(c["name"], c["gmv"], max_gmv, tc) for c in channels)
        channel_section = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px;">
      <tr><td style="padding:0 6px 4px;">
        <p style="font-size:14px;font-weight:bold;color:#333;margin:0 0 8px;">渠道分布 TOP5</p>
      </td></tr>
      <tr><td style="padding:0 6px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          {channel_rows}
        </table>
      </td></tr>
    </table>'''

    # ── TOP3 热销 ──
    top3_section = ""
    if top3:
        medals = ["🥇", "🥈", "🥉"]
        rows = ""
        for i, s in enumerate(top3):
            medal = medals[i] if i < 3 else ""
            rows += f'''<tr>
              <td width="8%" style="font-size:16px;padding:4px 0;">{medal}</td>
              <td width="62%" style="font-size:13px;color:#333;padding:4px 0;">{s["name"]}</td>
              <td width="30%" style="font-size:13px;color:{tc["neutral"]};text-align:right;padding:4px 0;">{fmt_money(s["gmv"])}</td>
            </tr>'''
        top3_section = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:12px;">
      <tr><td style="padding:0 6px 4px;">
        <p style="font-size:14px;font-weight:bold;color:#333;margin:0 0 8px;">热销商品 TOP3</p>
      </td></tr>
      <tr><td style="padding:0 6px;">
        <table width="100%" cellpadding="0" cellspacing="0">{rows}</table>
      </td></tr>
    </table>'''

    # ── CTA 按钮 ──
    cta_section = ""
    if vercel_url:
        cta_section = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;">
      <tr><td align="center">
        <a href="{vercel_url}" target="_blank"
           style="display:inline-block;padding:12px 32px;background:{tc["accent"]};
                  color:#fff;text-decoration:none;border-radius:4px;font-size:14px;font-family:Arial,sans-serif;">
          查看完整交互看板 &rarr;
        </a>
      </td></tr>
    </table>'''

    # ── Footer ──
    data_source = meta.get("data_file", "未知")
    footer = f'''<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;border-top:1px solid {tc["border"]};">
      <tr><td style="padding:14px 20px;text-align:center;">
        <p style="color:#aaa;font-size:11px;margin:0;">此邮件由 BEAM 自动生成 | 数据来源：{data_source}</p>
      </td></tr>
    </table>'''

    # ── 组装完整邮件 ──
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>经营分析日报</title>
<style>
  body {{ margin:0; padding:0; background:{BG_LIGHT}; }}
  @media screen and (max-width:600px) {{
    .kpi-cell {{ width:50% !important; display:block !important; float:left !important; }}
    .full-width {{ width:100% !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{BG_LIGHT};font-family:Arial,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{BG_LIGHT};">
  <tr><td align="center" style="padding:20px 10px;">
    <table width="600" cellpadding="0" cellspacing="0" class="full-width" style="background:{BG_WHITE};border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
      <tr><td>
        {header}
        <div style="padding:16px 14px;">
          {kpi_strip}
          {weekly_section}
          {today_section}
          {channel_section}
          {top3_section}
          {cta_section}
        </div>
        {footer}
      </td></tr>
    </table>
  </td></tr>
</table>
</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description="BEAM: 生成 HTML 邮件")
    parser.add_argument("--kpis",       default=".tmp/kpis.json",  help="KPI JSON 文件路径")
    parser.add_argument("--vercel-url", default=None,              help="Vercel 在线看板 URL（可选）")
    parser.add_argument("--theme",      default="swiss",
                        choices=list(EMAIL_THEMES.keys()),
                        help="邮件视觉主题，需与 LENS 看板主题一致（默认 swiss）")
    parser.add_argument("--output",     default=".tmp/email.html", help="输出 HTML 路径")
    args = parser.parse_args()

    # 读取 Vercel URL（优先命令行参数，其次文件）
    vercel_url = args.vercel_url
    if not vercel_url:
        url_file = ".tmp/vercel_url.txt"
        if os.path.exists(url_file):
            with open(url_file, "r") as f:
                vercel_url = f.read().strip() or None

    # 读取 KPI
    if not os.path.exists(args.kpis):
        print(f"ERROR: KPI 文件不存在: {args.kpis}", file=sys.stderr)
        sys.exit(1)

    with open(args.kpis, "r", encoding="utf-8") as f:
        kpis = json.load(f)

    # 生成邮件
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    html = build_email(kpis, vercel_url, theme=args.theme)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"邮件 HTML 生成完成 → {args.output}（主题：{args.theme}）")
    if vercel_url:
        print(f"  含看板链接: {vercel_url}")
    else:
        print("  未含看板链接（无 Vercel URL）")


if __name__ == "__main__":
    main()
