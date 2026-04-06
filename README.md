# 商业数据分析师 Agent

> 把业务数据变成每天自动送达的商业洞察

三个 Skills 构成一条完整的数据分析流水线：**分析 → 看板 → 自动推送**，使得一个人可以完成过去需要数据团队才能做的事。

---

## 三个 Skills

```
PRISM（数据分析）  →  LENS（可视化看板）  →  BEAM（自动推送）
```

### PRISM — 数据分析

棱镜将白光折射为光谱——PRISM 将原始数据折射为多维度商业洞察。

五阶段分析框架：**P**robe → **R**ecognize → **I**nvestigate → **S**ynthesize → **M**obilize

- 自动识别数据类型、质量、业务场景
- 内置 8 类分析方法论（增长率 / RFM / Cohort / 帕累托 / 漏斗 / SaaS 指标 / 电商指标等）
- 本地沙箱执行，不将原始数据发送到云端
- 输出：Markdown 分析报告 + `analysis_manifest.json`（供 LENS 消费）

### LENS — 可视化看板

透镜将 PRISM 折射出的光谱聚焦成清晰画面。

四阶段：**L**ayout → **E**ncode → **N**arrate → **S**tyle

- 生成自包含 HTML 看板（双击打开，零 CDN 依赖，离线可用）
- 10 种图表类型（柱状 / 折线 / 饼图 / 散点 / 瀑布 / 漏斗 / 热力图等）
- 11 种专业视觉风格（Financial Times / McKinsey / The Economist / Swiss / 日式极简等）
- 支持 Tooltip / 筛选 / 高亮 / PNG 导出交互

### BEAM — 自动推送

BEAM 将看板投射到决策者手中。

四阶段：**B**uild → **E**mit → **A**utomate → **M**onitor

- 生成 Outlook 兼容 HTML 邮件（600px，纯表格布局，移动端自适应）
- 通过 Resend API 发送邮件
- 通过 Vercel 部署在线看板
- macOS LaunchAgent 定时触发，每天早 8 点自动运行

---

## 目录结构

```
.
├── CLAUDE.md                          # Agent 路由与全局约定（放入项目根目录）
├── Skills/
│   ├── business-analysis/             # PRISM
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── data_profiler.py       # 数据质量评分与 Profile 生成
│   │   │   └── analysis_worker.py     # 本地 pandas 沙箱执行引擎
│   │   └── references/
│   │       ├── methodology-catalog.md # 8 类分析方法论 + pandas 代码模板
│   │       ├── chart-selection-guide.md
│   │       └── industry-benchmarks.md
│   ├── dashboard-viz/                 # LENS
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── chart-patterns.md      # SVG 图表渲染库（Vanilla JS）
│   │       ├── layout-templates.md
│   │       └── style-catalog.md       # 11 种视觉风格 CSS 系统
│   └── daily-report/                  # BEAM
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── extract_kpis.py
│       │   ├── build_email.py
│       │   ├── send_email.py
│       │   ├── deploy.sh
│       │   └── refresh_pipeline.sh
│       ├── assets/
│       │   └── launchagent-template.plist
│       └── references/
│           ├── setup-guide.md         # 首次配置指南（Resend / Vercel / LaunchAgent）
│           └── email-template-guide.md
└── README.md
```

---

## 使用方法

### 1. 安装依赖

```bash
pip install pandas numpy openpyxl chardet
```

### 2. 配置到你的项目

将 `CLAUDE.md` 和 `Skills/` 目录复制到你的数据分析工作目录：

```
你的工作目录/
├── CLAUDE.md
├── Skills/          ← 从本 repo 复制
└── Data/            ← 放你的数据文件（CSV / XLSX）
```

### 3. 在 Claude Code 中使用

```
# 只分析数据
帮我分析一下 Data/sales_2025.xlsx

# 分析 + 生成看板
做个看板，数据在 Data/sales_2025.xlsx

# 分析 + 看板 + 每天推送到邮箱
每天早上把 Data/sales_2025.xlsx 的分析推送到我邮箱
```

Claude Code 会自动识别意图、补全前置链路。

### 4. 配置 BEAM 自动推送（可选）

首次使用 BEAM 前，参考 `Skills/daily-report/references/setup-guide.md` 完成：
- [Resend](https://resend.com) 邮件服务配置
- [Vercel](https://vercel.com) 静态托管配置
- macOS LaunchAgent 定时任务配置

---

## 技术约束

- **数据不出本地**：原始数据仅在本地通过 `data_profiler.py` 采样，模型读 Profile，不接触原始行数据
- **零外部依赖**：HTML 看板自包含（无 CDN），邮件纯表格布局（Outlook 兼容）
- **沙箱执行**：分析代码在本地沙箱运行，120 秒超时保护

---

## 配套视频

本套件配套宇微 Vol.3《用 Claude Code 10 分钟搭建你的 AI 数据分析师》

---

## 许可证

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 许可证。

你可以自由分享和改编，但须署名，且不得用于商业目的。
