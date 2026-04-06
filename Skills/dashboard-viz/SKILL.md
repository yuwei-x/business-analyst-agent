---
name: dashboard-viz
description: |
  交互式商业数据看板生成器。LENS 框架：Layout（布局）→ Encode（编码）→ Narrate（叙事）→ Style（风格）。
  生成可双击打开的自包含 HTML 看板，包含筛选、悬浮提示、叙事式分析。11 种专业视觉风格可选。
  触发：/dashboard、/lens、/看板、「帮我做个看板」「生成 dashboard」「可视化这份分析」「做个报表」「数据可视化」。
  两种模式：(1) 接收 /analyze (PRISM) 的 Analysis Manifest 自动生成完整看板；(2) 独立使用，用户提供数据和需求。
  Interactive business dashboard generator. Produces self-contained HTML dashboards with filtering, tooltips, and narrative analysis.
  11 professional visual styles (Financial Times, McKinsey, Swiss, etc.). Works standalone or consumes PRISM Analysis Manifest.
---

## LENS — 交互式商业看板生成器

透镜将 PRISM 折射出的光谱聚焦成清晰画面，呈现给决策者。

### LENS 四维度

**L**ayout · **E**ncode · **N**arrate · **S**tyle

四个平行维度，不存在固定顺序。实践中叙事意图（N）往往最先确定，布局（L）和编码（E）依叙事而定，风格（S）最后收尾。

### 两种输入模式

**模式 1：From PRISM（推荐）**
读取数据文件同目录下的 `analysis_manifest.json`（PRISM 的 Analysis Manifest），使用 `charts`/`kpis`/`themes`/`actions` 字段作为蓝图。所有图表规格、KPI、叙事、行动建议已预计算。

**模式 2：独立使用**
用户提供数据文件 + 描述需求。用 pandas 做轻量数据读取，用户指定要展示的指标、对比、拆分维度。分析深度不如 PRISM，但能生成功能完整的看板。

### 技术架构

生成单一自包含 HTML 文件：
- 双击在任意浏览器打开，无需服务器
- JS/CSS/SVG 全部内联，零 CDN 依赖，离线可用
- Vanilla JS + 内联 SVG 图表渲染（不依赖 D3.js CDN）
- 响应式布局，支持桌面和移动端
- Ctrl+P 输出打印友好版本

原因：CDN 依赖在离线环境下会导致空白页面，自包含 HTML 确保任何环境都能正常展示。

### L — Layout（看板布局）

读 `Skills/dashboard-viz/references/layout-templates.md` 获取详细布局规范。固定结构：

1. **Header**：报告标题 + 日期 + 数据来源
2. **Narrative Strip**：一句话总结（30 秒版本）
3. **KPI Strip**：4-6 张 KPI 卡片（数字 + 趋势箭头 + 上下文）
4. **筛选栏**：基于分类列的下拉筛选（自动检测）
5. **Hero Chart**：最重要的一张图，全宽，标题 = 洞察声明
6. **支撑图表**：2 列网格，每张图含洞察标题 + 1 句结论
7. **Theme Sections**：叙事段落 + 支撑图表，可折叠
8. **Actions Panel**：行动建议卡片（WHO/WHAT/WHEN/IMPACT）
9. **Footer**：数据质量说明 + 生成时间

### 交互功能

全部 Vanilla JS 实现：
- Tooltips（悬浮显示精确数值）
- 筛选联动（选择筛选项时所有图表和 KPI 同步更新）
- 跨图高亮（悬浮某数据点，其他图的同实体同步高亮）
- 可折叠章节（展开/收起 Theme Sections）
- 时间范围选择器（最近30天/季度/YTD/全部）
- 打印模式（隐藏筛选栏，展开所有章节）
- **PNG 导出**（鼠标悬浮图表时右上角出现"↓ PNG"按钮，点击将图表 SVG 保存为本地 PNG）

**筛选响应规范（强制）：**
- `dashboardData.rows` 必须存储最细粒度的原始行数据（按天/单笔订单级别），不得预聚合。
  时间范围选择器和维度筛选均在此层做过滤，再由图表函数实时聚合后渲染。
- `renderAllCharts(filteredRows)` 必须被实现：接收过滤后的行数组，
  在函数内部重新计算每张图表所需的聚合序列（如按月汇总 GMV），
  再调用各图表的渲染函数刷新画布。不得将图表数据硬编码为静态 JS 对象。
- 结论文字（`.chart-insight`、`.section-narrative`）**可以静态**，
  不要求随筛选变化——它们代表对全量数据的洞察判断；
  但所有数值、坐标轴刻度、图形本身**必须**随筛选联动。

### E — Encode（图表编码）

读 `Skills/dashboard-viz/references/chart-patterns.md` 获取每种图表类型的 SVG 渲染模式。支持：柱状图、折线图、水平条形图、饼图/环图、堆叠柱状图、散点图、瀑布图、漏斗图、热力图。

硬性规则：
- 所有图表为内联 SVG
- 柱状图 Y 轴从 0 开始
- 饼图 <3% 合并为「其他」
- 最小柱宽 ≥12pt，文字 ≥10pt
- 图表标题 = 洞察声明（可证伪 + 数字）

### S — Style（视觉风格）

读 `Skills/dashboard-viz/references/style-catalog.md` 获取 11 种风格的完整 CSS 变量。

自动选择逻辑：
- 金融数据 → Goldman Sachs / Financial Times
- 运营/产品数据 → Fathom
- 未指定 → Swiss/NZZ（万能专业风格）
- 用户说 `/style [名称]` 可覆盖

每种风格通过 `:root` CSS 变量切换，不改变 HTML 结构。

### N — Narrate（叙事整合）

区别于图表堆砌——看板本身是一个可读的故事：
- 总叙事横幅：一句话总结全局（扫一眼即知大意）
- 每个主题章节：叙事段落（2-3 句）→ 支撑图表 → 结论
- 图表内嵌标注：拐点箭头、高亮柱、趋势斜率
- 渐进式披露：KPI+Hero=30秒版 → 标题=2分钟版 → 全读=10分钟版

### 输出

在**项目根目录**（即 CLAUDE.md 所在目录）生成 `dashboard.html`，打印文件路径提示用户双击打开。
不论数据文件放在哪个子目录，看板始终输出到项目根目录，以便 BEAM 的部署脚本能用固定路径找到它。
