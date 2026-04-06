---
name: daily-report
description: |
  BEAM 每日数据报告自动推送。将 LENS 看板部署上线 + 提取 KPI 摘要 + 生成邮件 + 定时推送到邮箱。
  四阶段：Build（构建内容）→ Emit（发送邮件）→ Automate（定时任务）→ Monitor（验证监控）。
  触发：/beam、/report、/推送、/daily、「帮我设置每天推送」「自动发邮件」「定时发送报告」「每天早上发到我邮箱」「schedule email」「send dashboard」「daily report」。
  两种模式：setup（首次配置 API + 定时任务）和 run（手动触发一次推送）。即使只说「把看板发给我」也应触发。
  BEAM daily report automation. Deploy dashboard + extract KPIs + email summary + schedule delivery. Trigger on email/push/schedule/daily report requests.
---

## BEAM — 每日数据报告自动推送

光学隐喻闭环：PRISM 折射数据为洞察，LENS 聚焦洞察为看板，BEAM 将看板投射到决策者手中。

### 两种模式

**Setup 模式**：首次使用，或需要重新配置。读 `references/setup-guide.md` 引导用户完成 Resend/Vercel 注册、API Key 配置、环境变量创建、LaunchAgent 安装。

**Run 模式**：手动触发一次完整推送流水线，用于测试或按需发送。

### BEAM 四阶段

**B — Build（构建投送内容）**

确认项目中已有看板 HTML（LENS 输出到项目根目录的 `dashboard.html`）和数据文件。如果没有，提示先运行 PRISM + LENS。

执行 `Skills/daily-report/scripts/extract_kpis.py <数据文件>` 提取 KPI 到 `.tmp/kpis.json`。这是模板脚本——首次使用时根据项目数据的实际字段名定制 `compute_kpis()` 函数。需按实际情况修改字段映射。
支持格式：`.xlsx` / `.xls` / `.csv` / `.tsv`。CSV/TSV 为单表文件，文件名含 "订单"/"日报"/"评论" 关键词时自动匹配对应 KPI 逻辑。

执行 `Skills/daily-report/scripts/build_email.py` 读取 KPI 生成 HTML 邮件。邮件设计规范见 `references/email-template-guide.md`：600px table 布局、Outlook 兼容、与 LENS 主题风格一致。

执行时传入 `--theme` 参数，需与该项目 LENS 看板所用视觉风格保持一致：
```
python build_email.py --theme swiss            # LENS 默认风格（Swiss/NZZ）
python build_email.py --theme financial_times  # FT 主题
python build_email.py --theme mckinsey         # McKinsey 主题
python build_email.py --theme fathom           # Fathom 主题
```
未指定时默认 `swiss`，与 LENS 默认风格对齐。主题控制 Header 背景色、KPI 数值色、渠道进度条色等全局色彩，确保邮件预览与正式看板视觉一致。

**E — Emit（发射到目标）**

执行 `Skills/daily-report/scripts/deploy.sh <看板目录>` 部署到 Vercel 获取 URL。部署失败时不中断——邮件降级为不含在线链接。

执行 `Skills/daily-report/scripts/send_email.py --to <邮箱> --subject <主题> --html-file .tmp/email.html` 发送。需要环境变量 `RESEND_API_KEY` 和 `RESEND_FROM`。

**A — Automate（自动化调度）**

仅 Setup 模式执行。使用 `Skills/daily-report/assets/launchagent-template.plist` 生成项目专属 plist，替换占位符（项目路径、Label、触发时间），安装到 `~/Library/LaunchAgents/` 并 `launchctl load`。

`Skills/daily-report/scripts/refresh_pipeline.sh` 是 LaunchAgent 调用入口——串行执行 KPI 提取 → Vercel 部署 → 邮件生成 → 邮件发送，每步记录时间戳日志到 `logs/` 目录。首次使用时根据项目定制脚本头部的配置变量（数据文件路径、收件人、看板目录）。

**M — Monitor（验证与监控）**

`launchctl start <Label>` 立即触发一次（不等到定时时间），检查 `logs/run_daily_<日期>.log` 确认执行状态，检查邮箱确认收件（含垃圾邮件文件夹）。

### 错误处理策略

| 故障点 | 策略 |
|--------|------|
| 数据文件不存在 | 中止，无数据无意义 |
| KPI 提取失败 | 中止，无内容可发 |
| Vercel 部署失败 | 继续，邮件不含链接 |
| 邮件发送失败 | 记录错误，前序步骤已完成可重发 |

### 适配新项目

将此 Skill 用于非美妆电商数据时，需定制两处：
1. `Skills/daily-report/scripts/extract_kpis.py` 中的 `compute_kpis()` — 按数据 schema 修改字段映射
2. `Skills/daily-report/scripts/refresh_pipeline.sh` 头部配置变量 — 数据文件路径、收件人、看板目录
