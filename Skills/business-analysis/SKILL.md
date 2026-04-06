---
name: business-analysis
description: |
  PRISM 商业数据分析框架。五阶段自适应分析：Probe（数据探针）→ Recognize（格局识别）→ Investigate（深度解剖）→ Synthesize（洞察合成）→ Mobilize（决策动员）。
  触发：/analyze、/prism、「帮我分析这份数据」「看看这个表格」「数据分析」「这些数字说明什么」「分析一下」。当用户提供 .csv/.xlsx/.tsv 文件并想获得商业洞察时触发。即使只说「帮我看看」也应触发。
  PRISM business data analysis. Five adaptive stages: Probe → Recognize → Investigate → Synthesize → Mobilize. Trigger on data analysis requests, spreadsheet files, or "analyze this data." Outputs structured Analysis Manifest for /dashboard skill.
---

## PRISM — 商业数据分析框架

棱镜将白光折射为光谱——PRISM 将原始数据折射为多维度商业洞察。

### 五阶段流程

**P — Probe（数据探针）**
执行 `Skills/business-analysis/scripts/data_profiler.py <文件路径>`，生成 `profile.json`。**`profile.json` 输出到数据文件所在目录**（即与数据文件同一文件夹）。模型通过 profile.json 理解数据，不直接读原始数据。原因：企业数据常有数万行，直接载入会溢出 context 或拖慢分析。
- profile.json 包含：形状、每列语义分类（Time/Subject/Object/Value/Quantity/Identifier/Status/Metric）、质量问题、分布统计、样本行、复杂度评分
- 复杂度 ≤2 → standard（2 透镜）；3-4 → deep（3 透镜）；≥5 → comprehensive（4-5 透镜）
- 生成一句话「第一印象假设」
- 质量分 <80 时询问用户是否先清洗

**R — Recognize（格局识别）**
基于 profile.json 识别全局格局：
- 时序模式（趋势、拐点、季节性、增长率）
- 分布与集中度（帕累托检验、基尼系数）
- 相关性 Top 5
- 自动生成 4-6 个 headline KPIs（数字 + 方向 + 上下文）
- 提出 3-5 个可验证假设
- 简要展示给用户，询问是否有特别关注的角度

**I — Investigate（深度解剖）**
基于语义类型和假设选择分析透镜。读 `Skills/business-analysis/references/methodology-catalog.md` 获取方法论指引。
- 每个透镜生成 pandas 分析代码，通过 `Skills/business-analysis/scripts/analysis_worker.py` 本地执行
- 只把聚合结果传回模型——模型不看原始数据行
- 透镜选择参考 `Skills/business-analysis/references/chart-selection-guide.md` 规划可视化
- 每个透镜输出：洞察标题（可证伪声明 + 数字）+ 数据点 + 图表规格 + 结论

**S — Synthesize（洞察合成）**
跨透镜按业务主题（增长/效率/风险/客户/运营）聚类，不按透镜分组。
- 为每个主题构建叙事弧：背景 → 张力 → 洞察 → 启示
- 规划看板：确定 hero chart、KPI 卡片、章节顺序
- 矛盾调和：不同透镜结论矛盾时显式呈现张力

**M — Mobilize（决策动员）**
3-5 条行动建议，格式：

```
行动：[一句话摘要]
WHO：[负责角色]
WHAT：[具体动作]
WHEN：[时间线]
IMPACT：[量化预期]
不行动的风险：[后果]
```

按影响力排序。至少一个「本周快赢」+ 一个「本季度战略行动」。

### 咨询语气
- 图表标题是可证伪声明（BAD:「各品类收入」→ GOOD:「品类 A 贡献 62% 收入但仅占 34% 利润」）
- 结论前置，数字领衔，主动语态，零含糊词
- 量化一切：建议包含金额影响

### 输出
终端展示 Markdown 格式的分析摘要。同时生成结构化 Analysis Manifest（JSON），供 `/dashboard` 技能消费生成交互式看板。

**Analysis Manifest 最小 Schema（必须包含以下字段，LENS 依赖这些字段）：**

```json
{
  "title": "看板标题（数据集名称 + 分析时间）",
  "data_file": "数据文件的绝对路径（供 LENS 读取原始行）",
  "summary": "一句话总结（30字以内，直接可用于看板 Narrative Strip）",
  "kpis": [
    { "label": "指标名", "value": "数值（字符串）", "trend": "+12%", "context": "上下文说明" }
  ],
  "charts": [
    {
      "id": "chart_1",
      "type": "bar|line|pie|waterfall|scatter|heatmap",
      "title": "可证伪声明（含数字）",
      "x_field": "列名",
      "y_field": "列名",
      "insight": "一句话结论",
      "is_hero": true
    }
  ],
  "themes": [
    {
      "name": "主题名（增长/效率/风险/客户/运营）",
      "narrative": "2-3句叙事段落",
      "chart_ids": ["chart_1", "chart_2"]
    }
  ],
  "actions": [
    {
      "who": "角色",
      "what": "具体动作",
      "when": "时间线",
      "impact": "量化预期"
    }
  ],
  "filters": ["可用作筛选器的分类列名列表"]
}
```

Analysis Manifest 以 `analysis_manifest.json` 文件名保存到数据文件同目录，供 LENS 直接读取。

### 独立使用
用户未提看板需求时，终端输出即为完整交付物。分析完成后自然提及「可用 /dashboard 生成交互式看板」，不强推。

### 行业基准
当 Probe 检测到特定行业数据模式时，读 `Skills/business-analysis/references/industry-benchmarks.md` 获取行业 KPI 基准。
