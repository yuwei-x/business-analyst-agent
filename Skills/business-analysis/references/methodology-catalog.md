# PRISM 方法论目录
> Investigate 阶段参考手册 — 透镜选择 · 代码模板 · 输出规范

---

## 1. 分析透镜选择指南

根据 Probe 阶段 `semantic_map` 中识别的数据类型，选择对应透镜：

| 数据包含 | 推荐透镜 | 分析深度 |
|----------|---------|---------|
| Value + Time | 收入趋势分析、增长拆解 | standard |
| Subject + Value + Time | RFM 分层、客户 Cohort | deep |
| Value + Object | 产品组合分析、帕累托 | standard |
| Value + Object + Quantity | 利润率分析、SKU 贡献度 | deep |
| Status / Metric | 漏斗分析、转化优化 | standard |
| Multiple Value columns | 单位经济模型 | deep |
| Time + Category | 趋势分解、季节性检测 | standard |
| Single numeric column | 异常检测、分布分析 | standard |

**深度选择原则：**
- `standard` — 单维切片，输出 1-2 个 insight，适合快速概览
- `deep` — 多维交叉，输出完整分层/矩阵，适合决策支撑

---

## 2. 收入与增长分析

### 增长率计算

- **MoM**（月环比）：`df['revenue'].pct_change()`
- **YoY**（年同比）：`df['revenue'].pct_change(12)`（月度数据）
- **CAGR**：`(end_value / start_value) ** (1 / n_years) - 1`

**输出格式规范：** 数字 + 方向 + 上下文
> "收入 ¥4.2M，YoY +23%，较上期的 +15% 加速增长"

```python
# 增长率模板
import pandas as pd

monthly = df.resample('M', on='order_date')['revenue'].sum()
growth = pd.DataFrame({
    'revenue': monthly,
    'mom': monthly.pct_change(),
    'yoy': monthly.pct_change(12)
})
result = {"growth_summary": growth.tail(12).round(4).to_dict('records')}
```

### 增长拆解（新老客贡献）

将增长来源拆分为：新增客户贡献 vs 存量客户增长。

```python
# 新老客贡献拆解
current = df[df['period'] == 'current'].groupby('customer_id')['revenue'].sum()
prior = df[df['period'] == 'prior'].groupby('customer_id')['revenue'].sum()

new_customers = current[~current.index.isin(prior.index)]
retained = current[current.index.isin(prior.index)]
churned = prior[~prior.index.isin(current.index)]

result = {
    "new_revenue": new_customers.sum(),
    "retained_revenue": retained.sum(),
    "churned_revenue": churned.sum(),
    "net_change": current.sum() - prior.sum()
}
```

### 收入驱动分析（Price × Volume）

```python
# Price × Volume 拆解
current_avg_price = current_df['revenue'].sum() / current_df['quantity'].sum()
prior_avg_price = prior_df['revenue'].sum() / prior_df['quantity'].sum()
current_vol = current_df['quantity'].sum()
prior_vol = prior_df['quantity'].sum()

price_effect = (current_avg_price - prior_avg_price) * current_vol
volume_effect = (current_vol - prior_vol) * prior_avg_price
result = {"price_effect": price_effect, "volume_effect": volume_effect}
```

---

## 3. 客户分析

### RFM 分层

三个维度：**R**ecency（距今天数）、**F**requency（购买次数）、**M**onetary（总金额）

```python
from datetime import timedelta
import pandas as pd

snapshot_date = df['order_date'].max() + timedelta(days=1)
rfm = df.groupby('customer_id').agg(
    Recency=('order_date', lambda x: (snapshot_date - x.max()).days),
    Frequency=('order_id', 'nunique'),
    Monetary=('revenue', 'sum')
)
rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['M'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
result = {"rfm_summary": rfm.groupby('RFM_Score').size().reset_index().to_dict('records')}
```

**分层映射：**

| 标签 | RFM 特征 | 策略 |
|------|---------|------|
| Champions | R≥4, F≥4, M≥4 | 维护关系，激励转介绍 |
| Loyal | F≥4 | 升单，提升 AOV |
| At Risk | R=2, 曾高F/M | 立即挽留，定向优惠 |
| Lost | R=1, F=1 | 低成本再激活或放弃 |
| New | R=5, F=1 | 引导复购，建立习惯 |

### Cohort 留存分析

按首次购买月分组，追踪各月留存率：

```python
from operator import attrgetter

df['cohort_month'] = df.groupby('customer_id')['order_date'].transform('min').dt.to_period('M')
df['order_month'] = df['order_date'].dt.to_period('M')
df['period_number'] = (df['order_month'] - df['cohort_month']).apply(attrgetter('n'))
cohort_pivot = df.groupby(['cohort_month', 'period_number'])['customer_id'].nunique().unstack()
retention = cohort_pivot.divide(cohort_pivot[0], axis=0)
result = {"cohort_retention": retention.round(3).to_dict()}
```

**关键指标：**
- Month 1 留存率 < 20%：产品/服务体验问题
- Month 3 留存率 > 40%：核心用户群健康

### CLV 估算（简化版）

```python
# CLV = AOV × 购买频率 × 平均生命周期（月）
aov = df.groupby('customer_id')['revenue'].mean()
freq = df.groupby('customer_id')['order_id'].nunique() / active_months
clv = aov * freq * avg_lifetime_months

clv_segments = pd.cut(clv, bins=3, labels=['Low', 'Mid', 'High'])
result = {"clv_distribution": clv_segments.value_counts().to_dict()}
```

---

## 4. 产品与组合分析

### 帕累托分析（80/20）

```python
product_rev = df.groupby('product')['revenue'].sum().sort_values(ascending=False)
product_rev_df = product_rev.reset_index()
product_rev_df['cumulative_pct'] = (
    product_rev_df['revenue'].cumsum() / product_rev_df['revenue'].sum() * 100
)
pareto_80 = (product_rev_df['cumulative_pct'] <= 80).sum()
result = {
    "top_products": product_rev_df.head(20).to_dict('records'),
    "pareto_insight": f"前 {pareto_80} 个产品贡献 80% 收入（共 {len(product_rev_df)} 个产品）"
}
```

### 利润率分析

```python
df['gross_margin'] = (df['revenue'] - df['cost']) / df['revenue']
margin_by_category = df.groupby('category').agg(
    revenue=('revenue', 'sum'),
    gross_margin=('gross_margin', 'mean')
).sort_values('revenue', ascending=False)

# 识别"利润陷阱"：收入高但利润率低于均值 20%+
avg_margin = margin_by_category['gross_margin'].mean()
traps = margin_by_category[margin_by_category['gross_margin'] < avg_margin * 0.8]
result = {
    "margin_by_category": margin_by_category.to_dict('records'),
    "profit_traps": traps.index.tolist()
}
```

### SKU 贡献度矩阵

按收入贡献 × 利润率四象限分类：
- 高收入 + 高利润：**明星品**，优先保量
- 高收入 + 低利润：**现金牛**，优化成本
- 低收入 + 高利润：**潜力品**，加大推广
- 低收入 + 低利润：**拖累品**，考虑下架

---

## 5. 单位经济模型

### SaaS 核心指标

| 指标 | 公式 | 健康基准 |
|------|------|---------|
| MRR | sum(月费用) | — |
| ARR | MRR × 12 | — |
| Churn Rate | 流失客户数 / 期初客户数 | <2%/月（SMB） |
| NRR | (期末ARR - 流失 + 扩展) / 期初ARR | >120%（企业级） |
| LTV | ARPU / Churn Rate | — |
| CAC | 总获客成本 / 新客数 | — |
| LTV/CAC | LTV / CAC | >3 |
| Payback Period | CAC / (ARPU × 毛利率) | <18 个月 |

```python
# SaaS 指标计算模板
mrr = df[df['period'] == 'current']['mrr'].sum()
churned_arr = df[df['status'] == 'churned']['arr'].sum()
expansion_arr = df[df['status'] == 'expanded']['arr_delta'].sum()
prior_arr = df[df['period'] == 'prior']['arr'].sum()

nrr = (mrr * 12 - churned_arr + expansion_arr) / prior_arr
churn_rate = len(df[df['status'] == 'churned']) / len(df[df['period'] == 'prior'])
result = {"mrr": mrr, "arr": mrr * 12, "nrr": round(nrr, 3), "churn_rate": round(churn_rate, 4)}
```

### 电商核心指标

| 指标 | 公式 | 参考基准 |
|------|------|---------|
| AOV | GMV / 订单数 | 行业差异大 |
| 转化率 | 订单数 / 访客数 | >2% |
| 退货率 | 退货数 / 订单数 | <30%（美妆类目） |
| ROI | GMV / 广告费 | >3.0（自播） |
| 复购率 | 有复购客户数 / 总客户数 | >30%（成熟品牌） |

---

## 6. 漏斗与转化分析

```python
# 漏斗分析模板
stages = ['访问', '注册', '首单', '复购']  # 替换为实际阶段名
funnel_counts = [df[df['stage'] == s]['user_id'].nunique() for s in stages]

funnel_df = pd.DataFrame({'stage': stages, 'count': funnel_counts})
funnel_df['overall_cvr'] = funnel_df['count'] / funnel_df['count'].iloc[0]
funnel_df['step_cvr'] = funnel_df['count'] / funnel_df['count'].shift(1)
funnel_df['drop_off_abs'] = funnel_df['count'].diff().abs()

# 识别最大漏损环节
max_drop_idx = funnel_df['drop_off_abs'].idxmax()
result = {
    "funnel": funnel_df.to_dict('records'),
    "biggest_drop": funnel_df.loc[max_drop_idx, 'stage']
}
```

**漏损诊断参考：**
- 访问→注册 < 5%：落地页/注册流程问题
- 注册→首单 < 20%：激活策略缺失
- 首单→复购 < 30%：产品/体验问题

---

## 7. 统计方法

### 趋势分解（时序数据）

```python
from statsmodels.tsa.seasonal import seasonal_decompose

ts = df.set_index('date')['value']
decomp = seasonal_decompose(ts, model='additive', period=12)
result = {
    "trend": decomp.trend.dropna().to_dict(),
    "seasonal": decomp.seasonal.to_dict(),
    "residual_std": decomp.resid.dropna().std()
}
```

### 相关性分析

```python
numeric_cols = df.select_dtypes(include='number').columns.tolist()
corr = df[numeric_cols].corr()

# 提取 Top 5 强相关对（排除自相关）
corr_pairs = (corr.where(~pd.eye(len(corr), dtype=bool))
              .stack()
              .abs()
              .sort_values(ascending=False)
              .head(5))
result = {"top_correlations": corr_pairs.to_dict()}
```

### 异常检测（±2σ）

```python
def detect_outliers(df, col):
    mean, std = df[col].mean(), df[col].std()
    df['is_outlier'] = (df[col] - mean).abs() > 2 * std
    outliers = df[df['is_outlier']][['date', col]].to_dict('records')
    return {
        "outlier_count": len(outliers),
        "outlier_records": outliers,
        "threshold_upper": mean + 2 * std,
        "threshold_lower": mean - 2 * std
    }
```

### 移动平均（平滑噪音）

```python
df['ma_7'] = df['value'].rolling(7).mean()   # 7日移动均线
df['ma_30'] = df['value'].rolling(30).mean() # 30日移动均线
```

---

## 8. 输出规范

### Finding 标准格式

每个透镜的分析结果统一结构化为：

```json
{
  "id": "lens_rfm_01",
  "theme": "customer",
  "narrative_title": "前 20% 客户贡献 73% 收入，但高价值客户 30 天流失率达 18%",
  "chart_specs": [
    {
      "type": "bar",
      "title": "RFM 分层客户价值分布",
      "x": "rfm_segment",
      "y": "revenue_contribution"
    }
  ],
  "data_snapshot": {},
  "conclusion": "立即启动高价值客户挽留计划，优先触达 RFM 评分 ≥4 的 At-Risk 客户"
}
```

### Narrative Title 写法规范

好的 narrative_title = **具体数字** + **问题或机会**
- 正确："前 3 个 SKU 贡献 61% 收入，但库存周转率仅行业均值 40%"
- 避免："产品集中度较高，存在库存风险"

### 结论强度标准

| 强度 | 触发条件 | 表达方式 |
|------|---------|---------|
| 观察 | 数据描述，无显著异常 | "数据显示……" |
| 洞察 | 存在明显规律或对比 | "值得注意的是……" |
| 建议 | 有明确可行动方向 | "建议立即……" |
| 警报 | 指标超出健康基准 20%+ | "需紧急关注……" |

---

## 9. 快速参考：透镜与图表类型对照

| 分析透镜 | 首选图表 | 备选图表 |
|---------|---------|---------|
| 增长趋势 | 折线图 | 面积图 |
| 增长拆解 | 堆叠柱状图 | 瀑布图 |
| RFM 分层 | 气泡图（R×F，气泡=M） | 热力图 |
| Cohort 留存 | 热力表格 | 折线图（各 Cohort） |
| 帕累托 | 柱状图 + 累计折线 | — |
| 漏斗 | 漏斗图 | 横向柱状图 |
| 利润矩阵 | 四象限散点图 | — |
| 相关性 | 热力图 | 散点矩阵 |
| 异常检测 | 折线图 + 阈值线 | 箱线图 |
