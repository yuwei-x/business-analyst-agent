# 商业数据分析师 — Agent 系统

三个 Skills 构成数据分析流水线，将原始数据转化为每天自动送达的商业洞察。

---

## 工作方式

```
PRISM（数据分析）  →  LENS（可视化看板）  →  BEAM（自动推送）
    ↑ 入口                ↑ 依赖 PRISM           ↑ 依赖 PRISM + LENS
    可独立终止             必须先完成 PRISM        必须先完成 PRISM + LENS
```

**注意：后置 Skill 不能跳过前置 Skill。** 

---

## Skill 路由规则

**核心逻辑：识别用户意图的「终点」，自动补全前置链路。**

| 用户说的话（示例） | 终点 | 实际执行链 |
|-------------------|------|-----------|
| 「帮我分析一下这份数据」「看看这些数字说明什么」「分析一下」 | PRISM | PRISM |
| 「做个看板」「可视化一下」「做个报表给老板看」 | LENS | PRISM → LENS |
| 「每天推送到我邮箱」「自动发报告」「每天早上 8 点发给我」 | BEAM | PRISM → LENS → BEAM |
| 「深度分析我的业务数据，做个看板，每天推送到邮箱」 | BEAM | PRISM → LENS → BEAM |

**边界处理：**
- 用户说「做个看板」但未提分析 → 自动从 PRISM 开始，不跳过
- 用户说「推送报告」但项目中无看板 → 提示需先完成分析和看板，确认后从 PRISM 开始
- 上一轮对话已完成 PRISM → 可直接从 LENS 继续，无需重跑分析

---

## 各 Skill 简介

### 1. PRISM — 数据分析（`Skills/business-analysis/SKILL.md`）

棱镜将白光折射为光谱——PRISM 将原始数据折射为多维度商业洞察。

五阶段：**P**robe（数据探针）→ **R**ecognize（格局识别）→ **I**nvestigate（深度解剖）→ **S**ynthesize（洞察合成）→ **M**obilize（决策动员）

触发词：`/analyze`、`/prism`、「分析」「数据」「看看这个表格」「这些数字说明什么」

输出：终端 Markdown 分析摘要 + Analysis Manifest（JSON），后者供 LENS 消费。

### 2. LENS — 可视化看板（`Skills/dashboard-viz/SKILL.md`）

透镜将 PRISM 折射出的光谱聚焦成清晰画面。

四阶段：**L**ayout（布局）→ **E**ncode（编码）→ **N**arrate（叙事）→ **S**tyle（风格）

触发词：`/dashboard`、`/lens`、「看板」「可视化」「报表」「图表」

输出：自包含 HTML 看板（双击打开，零 CDN 依赖，离线可用）。11 种专业视觉风格可选。

### 3. BEAM — 自动推送（`Skills/daily-report/SKILL.md`）

BEAM 将看板投射到决策者手中。

四阶段：**B**uild（构建内容）→ **E**mit（发送邮件）→ **A**utomate（定时任务）→ **M**onitor（验证监控）

触发词：`/beam`、`/report`、「推送」「邮件」「每天发给我」「定时报告」

输出：定时推送系统（macOS LaunchAgent + Resend 邮件 + Vercel 部署）。

---

## 目录结构

```
工作目录/
├── CLAUDE.md                     # 本文件：路由与全局约定
├── Skills/
│   ├── business-analysis/        # PRISM — 详见内部 SKILL.md
│   ├── dashboard-viz/            # LENS — 详见内部 SKILL.md
│   └── daily-report/             # BEAM — 详见内部 SKILL.md
└── Data/                         # 测试数据集（待补充）
```

---

## 沟通风格

- **语言**：所有输出使用中文
- **咨询语气**：结论先行，数字领衔，主动语态，零模糊词
- **图表标题**：必须是可证伪声明（BAD:「各品类收入」→ GOOD:「品类 A 贡献 62% 收入但仅占 34% 利润」）
- **建议格式**：每条必须包含 WHO + WHAT + WHEN + 量化 IMPACT

---

## 约束

- **不直接读原始数据行**：通过 `scripts/data_profiler.py` 生成 `profile.json`，模型读 profile 理解数据
- **适配新项目**：需定制 `extract_kpis.py` 的 `compute_kpis()` 和 `refresh_pipeline.sh` 头部配置
- **修改 Script 前**：先运行一次确认当前行为，改完后再次运行验证
- **环境变量**：`RESEND_API_KEY` 和 `RESEND_FROM` 不得出现在代码或输出中
