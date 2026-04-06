# PRISM 图表选择指南

> 本文件在 Investigate 阶段加载，用于为每条洞察选择最合适的可视化方式。
> 此处定义的 `chart_spec` 格式由 LENS 技能消费，渲染为内联 SVG（HTML）。

---

## 1. 图表选择决策矩阵

| 要回答的问题 | 推荐图表 | 避免使用 | 选择理由 |
|---|---|---|---|
| 大小 / 数量比较 | 柱状图 / 水平条形图 | 饼图（>5 类） | 人眼对长度差异的感知精度远高于面积和角度 |
| 时间趋势 | 折线图 | 柱状图（>12 个时间点） | 折线图强调连续变化方向，柱状图在密集时间点下视觉拥挤 |
| 组成 / 占比 | 饼图（≤5 类）/ 堆叠柱状图 | 折线图 | 占比信息需要「部分与整体」的视觉隐喻 |
| 双变量关系 | 散点图 | 柱状图 | 散点图是唯一能同时编码两个连续变量位置的图表 |
| 排名 | 水平条形图 | 折线图 | 水平方向给标签留出足够空间，阅读顺序自然 |
| 分布 | 直方图 / 箱线图 | 饼图 | 分布关注频率密度，饼图无法表达 |
| 变化拆解 | 瀑布图 | 堆叠柱状图 | 瀑布图逐项展示增减贡献，因果链清晰 |
| 漏斗转化 | 漏斗图 | 折线图 | 漏斗的渐缩形态直觉映射「流失」概念 |
| 矩阵数据 | 热力图 | 散点图 | 热力图用颜色深浅编码二维矩阵中的数值大小 |

**快速判断流程：**
1. 先确定你要回答的业务问题属于上表哪一行
2. 检查数据形态是否满足该图表的「数据要求」（见第 3 节）
3. 如果不满足，沿同一行寻找替代图表
4. 应用「通用规则」（第 4 节）做最终校验

---

## 2. Chart Spec 格式定义

PRISM 输出、LENS 消费的标准 JSON 格式：

```json
{
  "chart_type": "bar | line | scatter | pie | horizontal_bar | stacked_bar | waterfall | funnel | heatmap",
  "title": "洞察声明标题（可证伪、含数字）",
  "subtitle": "上下文补充（时间范围、数据口径等）",
  "data": [
    { "category": "A", "value": 120 },
    { "category": "B", "value": 85 }
  ],
  "x_field": "字段名（映射到 X 轴或主分类轴）",
  "y_field": "字段名（映射到 Y 轴或数值轴）",
  "color_field": "分组字段（可选，用于多系列 / 堆叠 / 散点着色）",
  "annotations": [
    {
      "type": "highlight | arrow | line | label",
      "target": "数据点标识或坐标",
      "text": "标注文字"
    }
  ],
  "insight": "一句话结论（与 title 一致或更精炼）",
  "source": "数据来源说明（表名、时间范围、筛选条件）"
}
```

**字段规则：**
- `chart_type`：必填，必须为上述 9 种之一
- `title`：必填，必须是可证伪的洞察声明（含数字），不是描述性标题
- `data`：必填，数组，每个元素是一个数据点对象
- `x_field` / `y_field`：必填，指向 `data` 中对象的 key
- `color_field`：可选，用于多系列分组
- `annotations`：可选，数组，用于标注关键数据点
- `insight`：必填，一句话结论
- `source`：必填，数据溯源信息

---

## 3. 各图表类型详细规格

### 3.1 柱状图（Bar - Vertical）

**适用场景：**
- 比较不同类别的数值大小
- 类别数量 ≤8 个
- 类别之间无天然顺序（有顺序时考虑折线图）

**数据要求：**
- 1 个分类字段（x_field）+ 1 个数值字段（y_field）
- 可选 1 个分组字段（color_field），此时变为分组柱状图（grouped bar）
- 分组柱状图中每组内的系列数 ≤4

**必须规则：**
- Y 轴必须从 0 开始（截断 Y 轴会夸大差异）
- 柱宽 ≥12pt，柱间距 = 柱宽的 50%-100%
- 类别 >8 个时，尾部合并为「其他」
- 柱子按数值降序排列（除非类别有天然顺序，如月份）
- 每根柱子顶部标注具体数值

**标注建议：**
- 最大值 / 最小值用 `highlight` 标注
- 如果存在均值参考线，用 `line` 标注
- 异常值（偏离均值 ±2σ）用 `arrow` 标注并说明原因

**chart_spec 示例：**

```json
{
  "chart_type": "bar",
  "title": "华东区 Q1 销售额领跑全国，超出第二名 37%",
  "subtitle": "2026 年 Q1 各区域销售额（万元）",
  "data": [
    { "region": "华东", "sales": 4820 },
    { "region": "华南", "sales": 3520 },
    { "region": "华北", "sales": 2910 },
    { "region": "西南", "sales": 1870 },
    { "region": "其他", "sales": 1450 }
  ],
  "x_field": "region",
  "y_field": "sales",
  "annotations": [
    { "type": "highlight", "target": "华东", "text": "4,820 万" },
    { "type": "line", "target": "y=2914", "text": "全国均值 2,914 万" }
  ],
  "insight": "华东区 Q1 销售额 4,820 万元，超出第二名华南区 37%，显著领先",
  "source": "sales_regional 表，2026-01-01 至 2026-03-31"
}
```

---

### 3.2 水平条形图（Horizontal Bar）

**适用场景：**
- 排名展示（Top N）
- 类别名称较长（中文 >4 个字）
- 类别数量 5-15 个

**数据要求：**
- 1 个分类字段（y_field，映射到纵轴）+ 1 个数值字段（x_field，映射到横轴）
- 数据必须已按数值排序

**必须规则：**
- X 轴（数值轴）必须从 0 开始
- 按数值从上到下降序排列（最大值在最上方）
- 条形高度 ≥12pt
- 每条末端标注具体数值
- 类别 >15 个时，只展示 Top 10 + 合并「其他」

**标注建议：**
- Top 1 用 `highlight` 强调
- 如果存在显著断层（第 N 名与第 N+1 名差距 >50%），用 `arrow` 标注断层位置

**chart_spec 示例：**

```json
{
  "chart_type": "horizontal_bar",
  "title": "Claude Code 以 42% 使用率成为团队最高频 AI 工具",
  "subtitle": "2026 年 3 月团队 AI 工具使用率排名",
  "data": [
    { "tool": "Claude Code", "usage_rate": 0.42 },
    { "tool": "Cursor", "usage_rate": 0.28 },
    { "tool": "ChatGPT", "usage_rate": 0.15 },
    { "tool": "Copilot", "usage_rate": 0.10 },
    { "tool": "其他", "usage_rate": 0.05 }
  ],
  "x_field": "usage_rate",
  "y_field": "tool",
  "annotations": [
    { "type": "highlight", "target": "Claude Code", "text": "42%" }
  ],
  "insight": "Claude Code 使用率 42%，是第二名 Cursor（28%）的 1.5 倍",
  "source": "tool_usage_log 表，2026-03"
}
```

---

### 3.3 折线图（Line）

**适用场景：**
- 展示时间序列趋势
- 对比多个系列的趋势变化（≤5 条线）
- 时间点 ≥5 个

**数据要求：**
- 1 个时间字段（x_field）+ 1 个数值字段（y_field）
- 可选 1 个系列字段（color_field），用于多线对比
- 多系列时，系列数 ≤5（超过则只保留最关键的 + 合并其余为「其他」）

**必须规则：**
- X 轴时间间隔必须等距
- Y 轴起点可以不从 0 开始（趋势图关注变化幅度而非绝对量）
- 如果 Y 轴不从 0 开始，必须在 subtitle 中注明「Y 轴起点非零」
- 数据点 >20 个时隐藏数据点标记，只保留线
- 多系列时每条线用不同颜色 + 直接标签（不依赖图例）

**标注建议：**
- 峰值 / 谷值用 `label` 标注具体数值
- 拐点（趋势方向改变）用 `arrow` 标注
- 关键事件（产品发布、政策变化等）用 `line`（垂直参考线）标注

**chart_spec 示例：**

```json
{
  "chart_type": "line",
  "title": "付费用户在 3 月第 2 周出现拐点，周环比增长从 -5% 翻转为 +12%",
  "subtitle": "2026 年 Q1 周度付费用户数变化",
  "data": [
    { "week": "W1", "paid_users": 1200 },
    { "week": "W2", "paid_users": 1180 },
    { "week": "W3", "paid_users": 1150 },
    { "week": "W4", "paid_users": 1120 },
    { "week": "W5", "paid_users": 1065 },
    { "week": "W6", "paid_users": 1040 },
    { "week": "W7", "paid_users": 1020 },
    { "week": "W8", "paid_users": 990 },
    { "week": "W9", "paid_users": 1110 },
    { "week": "W10", "paid_users": 1250 },
    { "week": "W11", "paid_users": 1380 },
    { "week": "W12", "paid_users": 1520 }
  ],
  "x_field": "week",
  "y_field": "paid_users",
  "annotations": [
    { "type": "arrow", "target": "W9", "text": "拐点：新定价策略上线" },
    { "type": "label", "target": "W12", "text": "1,520（季度峰值）" },
    { "type": "label", "target": "W8", "text": "990（季度谷值）" }
  ],
  "insight": "付费用户在 W9 出现拐点，与新定价策略上线时间吻合，后续 4 周持续增长",
  "source": "user_subscriptions 表，按周聚合，2026-01 至 2026-03"
}
```

---

### 3.4 堆叠柱状图（Stacked Bar）

**适用场景：**
- 展示「整体中各部分的构成」随类别或时间的变化
- 既关心总量，又关心内部结构
- 类别数 ≤10，堆叠层数 ≤5

**数据要求：**
- 1 个分类字段（x_field）+ 1 个数值字段（y_field）+ 1 个堆叠分组字段（color_field）
- 堆叠层数 ≤5（超过则合并为「其他」）

**必须规则：**
- Y 轴必须从 0 开始
- 每个堆叠段标注百分比或数值（段太小时省略，合并到 tooltip）
- 堆叠顺序保持一致（所有柱子中同一类别在相同位置）
- 使用 100% 堆叠柱状图时必须在 subtitle 中标明「百分比堆叠」
- 颜色分配按系列重要性递减，最重要的系列放在底部

**标注建议：**
- 总量变化显著时，在柱顶标注总数
- 某一层占比发生剧烈变化时，用 `arrow` 指向该段

**chart_spec 示例：**

```json
{
  "chart_type": "stacked_bar",
  "title": "企业客户收入占比从 Q1 的 35% 增长至 Q4 的 52%",
  "subtitle": "2025 年各季度收入构成（万元）",
  "data": [
    { "quarter": "Q1", "segment": "企业客户", "revenue": 350 },
    { "quarter": "Q1", "segment": "中小商户", "revenue": 420 },
    { "quarter": "Q1", "segment": "个人用户", "revenue": 230 },
    { "quarter": "Q2", "segment": "企业客户", "revenue": 410 },
    { "quarter": "Q2", "segment": "中小商户", "revenue": 390 },
    { "quarter": "Q2", "segment": "个人用户", "revenue": 210 },
    { "quarter": "Q3", "segment": "企业客户", "revenue": 480 },
    { "quarter": "Q3", "segment": "中小商户", "revenue": 370 },
    { "quarter": "Q3", "segment": "个人用户", "revenue": 190 },
    { "quarter": "Q4", "segment": "企业客户", "revenue": 560 },
    { "quarter": "Q4", "segment": "中小商户", "revenue": 350 },
    { "quarter": "Q4", "segment": "个人用户", "revenue": 170 }
  ],
  "x_field": "quarter",
  "y_field": "revenue",
  "color_field": "segment",
  "annotations": [
    { "type": "arrow", "target": "Q4-企业客户", "text": "占比升至 52%" }
  ],
  "insight": "企业客户收入占比持续走高，从 Q1 的 35% 增至 Q4 的 52%，成为第一大收入来源",
  "source": "revenue_by_segment 表，2025 全年"
}
```

---

### 3.5 饼图 / 环图（Pie / Donut）

**适用场景：**
- 展示单一维度的占比构成
- 类别数 ≤5
- 读者需要快速感知「谁是最大的一块」

**数据要求：**
- 1 个分类字段 + 1 个数值字段
- 所有数值之和代表 100% 整体
- 类别数严格 ≤5（含「其他」）

**必须规则：**
- 类别 >5 个时**禁止使用**饼图，改用水平条形图
- 占比 <3% 的类别合并为「其他」
- 每个扇区标注类别名 + 百分比
- 最大扇区从 12 点钟方向顺时针开始
- 环图内圆可放置总数或核心指标
- 禁止使用 3D 饼图

**标注建议：**
- 最大占比类别用 `highlight` 强调
- 如果某类别占比出乎预料（与行业基准差异 >10pp），用 `label` 说明

**chart_spec 示例：**

```json
{
  "chart_type": "pie",
  "title": "自然搜索贡献 61% 流量，付费渠道 ROI 需重新评估",
  "subtitle": "2026 年 3 月网站流量来源构成",
  "data": [
    { "channel": "自然搜索", "traffic_pct": 61 },
    { "channel": "社交媒体", "traffic_pct": 18 },
    { "channel": "付费广告", "traffic_pct": 12 },
    { "channel": "直接访问", "traffic_pct": 6 },
    { "channel": "其他", "traffic_pct": 3 }
  ],
  "x_field": "channel",
  "y_field": "traffic_pct",
  "annotations": [
    { "type": "highlight", "target": "自然搜索", "text": "61% — 绝对主导渠道" }
  ],
  "insight": "自然搜索贡献 61% 流量，是付费广告的 5 倍；付费渠道投入产出比需重新评估",
  "source": "ga_traffic_sources 表，2026-03"
}
```

---

### 3.6 散点图（Scatter）

**适用场景：**
- 探索两个连续变量之间的关系（相关性、聚类、异常值）
- 数据点 ≥15 个
- 需要发现模式而非精确读数

**数据要求：**
- 2 个数值字段（x_field + y_field）
- 可选 1 个分类字段（color_field）用于分组着色
- 可选 1 个数值字段映射到点的大小（气泡图变体）

**必须规则：**
- 必须绘制象限线（通常为均值线或业务阈值线）
- 每个象限必须有标签说明其含义
- 异常点（远离主体分布的点）必须标注具体名称和数值
- 数据点 >50 时降低不透明度（opacity: 0.6）防止遮挡
- 如果存在明显线性关系，绘制趋势线并标注 R^2

**标注建议：**
- 每个象限一个标签（如「高增长高利润」「低增长高利润」等）
- 异常值用 `arrow` 标注
- 趋势线用 `line` 标注并附 R^2 值

**chart_spec 示例：**

```json
{
  "chart_type": "scatter",
  "title": "产品 C 增速最快但利润率仅 3%，存在规模不经济风险",
  "subtitle": "各产品线收入增速 vs 利润率（气泡大小 = 收入规模）",
  "data": [
    { "product": "产品 A", "growth_rate": 0.05, "margin": 0.22, "revenue": 5000 },
    { "product": "产品 B", "growth_rate": 0.12, "margin": 0.18, "revenue": 3200 },
    { "product": "产品 C", "growth_rate": 0.35, "margin": 0.03, "revenue": 1800 },
    { "product": "产品 D", "growth_rate": -0.02, "margin": 0.31, "revenue": 4100 },
    { "product": "产品 E", "growth_rate": 0.08, "margin": 0.15, "revenue": 2700 }
  ],
  "x_field": "growth_rate",
  "y_field": "margin",
  "color_field": "product",
  "annotations": [
    { "type": "line", "target": "x=0.10", "text": "增速均值 10%" },
    { "type": "line", "target": "y=0.15", "text": "利润率均值 15%" },
    { "type": "label", "target": "top-right", "text": "明星象限：高增长 + 高利润" },
    { "type": "label", "target": "top-left", "text": "现金牛：低增长 + 高利润" },
    { "type": "label", "target": "bottom-right", "text": "问题象限：高增长 + 低利润" },
    { "type": "label", "target": "bottom-left", "text": "瘦狗象限：低增长 + 低利润" },
    { "type": "arrow", "target": "产品 C", "text": "增速 35% 但利润率仅 3%" }
  ],
  "insight": "产品 C 增速最快（35%）但利润率仅 3%，处于「问题象限」，需评估规模不经济风险",
  "source": "product_financials 表，2025 全年"
}
```

---

### 3.7 瀑布图（Waterfall）

**适用场景：**
- 拆解从起点到终点的增减因素（如利润桥、收入变动拆解）
- 需要展示「哪些因素贡献了增长，哪些拖累了表现」
- 步骤数 3-10 个

**数据要求：**
- 每个数据点包含：名称、数值、类型（increase / decrease / total）
- 第一项和最后一项通常是 `total` 类型
- 中间各项是 `increase` 或 `decrease`

**必须规则：**
- 增加项用绿色系（Green #2A9D8F），减少项用红色系（Red #E63946）
- 起点和终点用中性色（Dark #2E4057）
- 每个段标注数值（正数带 +，负数带 -）
- 段之间用连接线串联
- Y 轴从 0 开始

**标注建议：**
- 最大增幅和最大降幅用 `highlight` 强调
- 净变化在终点柱旁用 `label` 标注

**chart_spec 示例：**

```json
{
  "chart_type": "waterfall",
  "title": "Q1 利润同比下降 18%，人力成本上升是最大拖累因素（-320 万）",
  "subtitle": "2026 Q1 vs 2025 Q1 利润变动桥（万元）",
  "data": [
    { "item": "2025 Q1 利润", "value": 1800, "type": "total" },
    { "item": "收入增长", "value": 420, "type": "increase" },
    { "item": "毛利率改善", "value": 85, "type": "increase" },
    { "item": "人力成本上升", "value": -320, "type": "decrease" },
    { "item": "营销费用增加", "value": -210, "type": "decrease" },
    { "item": "运营效率提升", "value": 60, "type": "increase" },
    { "item": "其他", "value": -55, "type": "decrease" },
    { "item": "2026 Q1 利润", "value": 1780, "type": "total" }
  ],
  "x_field": "item",
  "y_field": "value",
  "annotations": [
    { "type": "highlight", "target": "人力成本上升", "text": "-320 万（最大拖累）" },
    { "type": "label", "target": "2026 Q1 利润", "text": "净变化 -20 万（-1.1%）" }
  ],
  "insight": "利润同比微降 1.1%，但人力成本上升（-320 万）吃掉了收入增长（+420 万）的大部分红利",
  "source": "pnl_bridge 表，2025 Q1 vs 2026 Q1"
}
```

---

### 3.8 漏斗图（Funnel）

**适用场景：**
- 展示转化漏斗中各环节的流失情况
- 步骤数 3-7 个
- 核心关注「哪一步流失最大」

**数据要求：**
- 每个数据点包含：步骤名称、数值（绝对数或百分比）
- 数据按漏斗顺序排列（从大到小）
- 每步的值 ≤ 上一步的值

**必须规则：**
- 每层标注绝对数 + 转化率（相对上一步）
- 宽度按数值等比缩放
- 流失最大的环节用红色高亮
- 首尾层之间标注总转化率

**标注建议：**
- 流失率最高的环节用 `arrow` 标注
- 总转化率用 `label` 标注

**chart_spec 示例：**

```json
{
  "chart_type": "funnel",
  "title": "「加购→支付」环节流失 68%，是转化链最大瓶颈",
  "subtitle": "2026 年 3 月电商转化漏斗",
  "data": [
    { "stage": "浏览商品", "count": 50000, "rate": 1.00 },
    { "stage": "商品详情页", "count": 22000, "rate": 0.44 },
    { "stage": "加入购物车", "count": 8500, "rate": 0.386 },
    { "stage": "提交订单", "count": 2700, "rate": 0.318 },
    { "stage": "完成支付", "count": 2150, "rate": 0.796 }
  ],
  "x_field": "stage",
  "y_field": "count",
  "annotations": [
    { "type": "arrow", "target": "加入购物车→提交订单", "text": "流失 68%（5,800 人）" },
    { "type": "label", "target": "完成支付", "text": "总转化率 4.3%" }
  ],
  "insight": "加购到提交订单环节流失 68%，是整个转化链最大瓶颈，优先优化结算流程",
  "source": "funnel_events 表，2026-03"
}
```

---

### 3.9 热力图（Heatmap）

**适用场景：**
- 在二维矩阵中发现模式（如时间 × 类别、产品 × 指标）
- 快速识别高值区和低值区
- 数据点密集（行数 × 列数 ≥ 20）

**数据要求：**
- 2 个分类字段（x_field + y_field）+ 1 个数值字段（color 映射）
- 数值字段用于颜色深浅编码

**必须规则：**
- 颜色映射使用单色渐变（浅 → 深）或发散色（低值蓝 → 高值红）
- 每个单元格标注数值（单元格过多时省略，依赖颜色）
- 行列排序要有逻辑（时间顺序、数值排序等），不要随机排
- 必须有颜色图例（色阶条）

**标注建议：**
- 最高值和最低值单元格用 `highlight` 边框强调
- 异常集中区域用 `label` 圈出

**chart_spec 示例：**

```json
{
  "chart_type": "heatmap",
  "title": "周三下午 14:00-16:00 是客服工单高峰，响应时长超标 2.3 倍",
  "subtitle": "每周各时段平均工单量（按小时 × 星期聚合）",
  "data": [
    { "day": "周一", "hour": "09:00", "ticket_count": 12 },
    { "day": "周一", "hour": "10:00", "ticket_count": 18 },
    { "day": "周三", "hour": "14:00", "ticket_count": 47 },
    { "day": "周三", "hour": "15:00", "ticket_count": 52 },
    { "day": "周三", "hour": "16:00", "ticket_count": 43 },
    { "day": "周五", "hour": "17:00", "ticket_count": 8 }
  ],
  "x_field": "hour",
  "y_field": "day",
  "annotations": [
    { "type": "highlight", "target": "周三-15:00", "text": "峰值 52 单/小时" },
    { "type": "label", "target": "周三-14:00~16:00", "text": "高峰区间：平均 47 单/小时" }
  ],
  "insight": "周三 14:00-16:00 是工单高峰，平均 47 单/小时，超出日常均值 2.3 倍",
  "source": "support_tickets 表，按小时×星期聚合，近 4 周均值"
}
```

---

## 4. 通用规则

以下规则适用于所有图表类型，PRISM 在生成 `chart_spec` 时必须逐条校验：

### 标题规则
- **图表标题 = 洞察声明**，不是描述性标题
  - 正确：「华东区 Q1 销售额领跑全国，超出第二名 37%」
  - 错误：「各区域 Q1 销售额对比」
- 标题必须**可证伪**（读者能用数据验证真假）
- 标题必须**含数字**（百分比、金额、倍数等）

### 一图一洞察
- 每张图表传达且仅传达一个核心洞察
- 如果发现需要展示多个洞察，拆成多张图

### 数据标注
- 关键数字必须标注在图内（不依赖鼠标悬停）
- 异常值（偏离均值 ±2σ）必须用 `arrow` 标注并简要说明原因
- 参考线（均值、目标值、基准线）用 `line` 标注

### 视觉规范
- 所有文字 ≥10pt（含轴标签、标注文字）
- 最小柱宽 / 条形高度 ≥12pt
- 不使用 3D 效果、阴影、渐变填充等装饰性元素
- 网格线使用 Light gray #CCCCCC，辅助定位但不喧宾夺主

### 数据处理
- 占比 <3% 的段合并为「其他」
- 类别 >8 个时，尾部合并为「其他」（保留 Top 7 + 其他）
- 散点图必须有象限线 + 四象限标签
- 时间轴数据点必须等间距

### 排序原则
- 柱状图 / 条形图：默认按数值降序（除非有天然顺序）
- 堆叠图：堆叠层按全局总量降序，最大层在底部
- 饼图：最大扇区从 12 点钟方向开始，顺时针递减

---

## 5. 色彩语义系统

### 系列色板（Series Palette）

用于区分不同数据系列，按优先级顺序使用：

| 顺序 | 名称 | 色值 | 用途 |
|------|------|------|------|
| 1 | Coral | `#E17055` | 主系列 / 第一分类 |
| 2 | Mint | `#45B7AA` | 第二系列 |
| 3 | Olive | `#5B8C5A` | 第三系列 |
| 4 | Gold | `#FFD700` | 第四系列 |
| 5 | Lavender | `#9B7EDE` | 第五系列 |

**使用规则：**
- 单系列图表统一使用 Coral `#E17055`
- 多系列按上表顺序分配，不跳号
- 需要强调某一系列时，该系列用原色，其他系列降低不透明度至 0.3

### 语义色（Semantic Colors）

用于传达固定含义，**不可用作普通系列色**：

| 语义 | 名称 | 色值 | 使用场景 |
|------|------|------|---------|
| 危险 / 下降 | Red | `#E63946` | 负增长、流失、超支、异常 |
| 成功 / 增长 | Green | `#2A9D8F` | 正增长、达标、盈利 |
| 警告 / 关注 | Orange | `#F4A261` | 接近阈值、需关注但未告警 |

**使用规则：**
- 瀑布图中 increase 用 Green，decrease 用 Red
- 漏斗图中流失最大环节用 Red 高亮
- KPI 卡片中达标用 Green，未达标用 Red，接近阈值用 Orange
- 绝对不要用 Red 表示正面含义，或 Green 表示负面含义

### 中性色（Neutral Colors）

| 用途 | 名称 | 色值 |
|------|------|------|
| 主要文字 / 标题 / 总计柱 | Dark | `#2E4057` |
| 网格线 / 参考线 / 次要元素 | Light Gray | `#CCCCCC` |
| 背景 | White | `#FFFFFF` |

### 色彩无障碍

- 不依赖颜色作为唯一的信息编码手段（同时使用形状、标签或纹理）
- 相邻系列色的亮度差 ≥30%（确保灰度打印下可区分）
- 语义色（Red / Green）配合方向箭头（ / ）或 +/- 符号使用

---

## 附录：chart_type 速查表

| chart_type 值 | 中文名 | 最少数据点 | 最多类别 | Y 轴从 0 |
|---|---|---|---|---|
| `bar` | 柱状图 | 2 | 8 | 必须 |
| `horizontal_bar` | 水平条形图 | 2 | 15 | 必须 |
| `line` | 折线图 | 5 | N/A | 非必须 |
| `stacked_bar` | 堆叠柱状图 | 2 | 10 | 必须 |
| `pie` | 饼图/环图 | 2 | 5 | N/A |
| `scatter` | 散点图 | 15 | N/A | 视数据 |
| `waterfall` | 瀑布图 | 3 | 10 | 必须 |
| `funnel` | 漏斗图 | 3 | 7 | N/A |
| `heatmap` | 热力图 | 20 (cells) | N/A | N/A |
