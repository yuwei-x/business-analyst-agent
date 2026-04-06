# HTML 邮件模板规范

## 核心约束

HTML 邮件的渲染引擎与浏览器不同——Outlook 使用 Word 引擎，Gmail 会剥离 `<style>` 标签，移动端宽度受限。以下规范确保邮件在所有主流客户端正常显示。

---

## 布局原则

### 整体结构
- 最大宽度 **600px**，居中显示
- 全部使用 `<table>` 布局——Outlook 不支持 `flexbox` / `grid` / `float`（float 仅用于移动端 @media 降级）
- 每个视觉区块 = 一个独立的 `<table>`，嵌套而非合并
- 所有样式写在行内 `style=""`（Gmail 剥离 `<head>` 中的 `<style>` 标签）

### 响应式适配
```html
<!-- 仅在支持 @media 的客户端生效（iOS Mail、Gmail app 等） -->
<style>
@media screen and (max-width: 600px) {
  .kpi-cell { width: 50% !important; display: block !important; float: left !important; }
  .full-width { width: 100% !important; }
}
</style>
```
- 不使用 `flex` / `grid`，降级方案用 `float: left` + `width: 50%`
- KPI 4 格在桌面端一行排列，移动端 2 列 × 2 行

---

## 区块规范

### 1. Header（顶部横幅）
```html
<table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #E8637A, #C9A86C); border-radius: 8px 8px 0 0;">
  <tr>
    <td style="padding: 24px 20px; text-align: center;">
      <h1 style="color: #fff; font-size: 20px; margin: 0;">经营分析日报</h1>
      <p style="color: rgba(255,255,255,0.85); font-size: 13px; margin: 8px 0 0;">数据区间：{date_range} | 生成时间：{timestamp}</p>
    </td>
  </tr>
</table>
```
- 渐变背景：品牌粉 `#E8637A` → 品牌金 `#C9A86C`
- Outlook 不支持 `linear-gradient`，自动降级为第一个色值的纯色背景（可接受）

### 2. KPI 卡片区
```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td class="kpi-cell" width="25%" style="padding: 8px;">
      <table width="100%" style="background: #fff; border-radius: 8px; border: 1px solid #eee;">
        <tr><td style="padding: 16px; text-align: center;">
          <p style="color: #888; font-size: 12px; margin: 0;">总 GMV</p>
          <p style="color: #E8637A; font-size: 24px; font-weight: bold; margin: 8px 0 4px;">¥{gmv}</p>
          <p style="color: {trend_color}; font-size: 12px; margin: 0;">{trend_arrow} {trend_pct} 环比</p>
        </td></tr>
      </table>
    </td>
    <!-- 重复 3 次，分别展示毛利率/客单价/退款率 -->
  </tr>
</table>
```
- 4 张 KPI 卡片一行排列
- 核心数字用品牌粉 `#E8637A`，趋势向上用绿色 `#6BAE8A`，向下用红色 `#E8637A`
- 趋势箭头：▲（上升）/ ▼（下降）/ ─（持平，变化 <1%）

### 3. 近 7 日动态
```html
<table width="100%" style="background: #FAFAFA; border-radius: 8px; margin-top: 16px;">
  <tr><td style="padding: 16px 20px;">
    <h2 style="font-size: 15px; color: #333; margin: 0 0 12px;">近 7 日动态</h2>
    <table width="100%">
      <tr>
        <td width="50%">
          <p style="color: #888; font-size: 12px; margin: 0;">7日 GMV</p>
          <p style="font-size: 18px; font-weight: bold; margin: 4px 0;">¥{weekly_gmv}</p>
          <p style="color: {color}; font-size: 12px;">{arrow} {pct} 环比上周</p>
        </td>
        <td width="50%"><!-- 订单数 / 综合评分 --></td>
      </tr>
    </table>
  </td></tr>
</table>
```

### 4. 今日实时数据
- 来自数据源中最新一行的日报数据
- 展示：当日 GMV / 订单数 / 广告 ROI / 毛利率
- 布局同 KPI 卡片区，4 格一行

### 5. 渠道分布
- 纯 `<div>` 进度条（不用 SVG/Canvas，邮件客户端不支持）
- 背景 `#eee`，前景色按渠道区分，高度 12px，border-radius: 6px

```html
<table width="100%">
  <tr>
    <td width="30%" style="font-size: 13px; color: #555;">{channel_name}</td>
    <td width="50%">
      <div style="background: #eee; border-radius: 6px; height: 12px;">
        <div style="background: #E8637A; width: {pct}%; height: 12px; border-radius: 6px;"></div>
      </div>
    </td>
    <td width="20%" style="font-size: 13px; color: #888; text-align: right;">¥{amount}</td>
  </tr>
</table>
```

### 6. TOP3 热销商品
```
🥇 {product_1}    ¥{amount_1}
🥈 {product_2}    ¥{amount_2}
🥉 {product_3}    ¥{amount_3}
```

### 7. CTA 按钮
```html
<table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
  <tr><td align="center">
    <a href="{vercel_url}" target="_blank"
       style="display: inline-block; padding: 12px 32px; background: #E8637A;
              color: #fff; text-decoration: none; border-radius: 6px; font-size: 14px;">
      查看完整交互看板 &rarr;
    </a>
  </td></tr>
</table>
```
- 无 Vercel URL 时隐藏此按钮（不显示空链接）

### 8. Footer
```html
<table width="100%" style="margin-top: 24px; border-top: 1px solid #eee;">
  <tr><td style="padding: 16px 20px; text-align: center;">
    <p style="color: #aaa; font-size: 11px;">此邮件由 BEAM 自动生成 | 数据来源：{data_source}</p>
  </td></tr>
</table>
```

---

## 色彩系统

与 LENS 看板保持一致：

| 用途 | 色值 | 说明 |
|------|------|------|
| 品牌粉 | `#E8637A` | Header 渐变起点、KPI 核心数字、CTA 按钮 |
| 品牌金 | `#C9A86C` | Header 渐变终点、次级强调 |
| 正向趋势 | `#6BAE8A` | 指标上升 |
| 负向趋势 | `#E8637A` | 指标下降（复用品牌粉） |
| 持平 | `#888888` | 变化 <1% |
| 背景 | `#F5F5F5` | 邮件整体背景 |
| 卡片背景 | `#FFFFFF` | KPI 卡片、内容区块 |
| 辅助文字 | `#888888` | 标签文字、日期 |

---

## Outlook 兼容性检查清单

- [ ] 所有样式行内 `style=""`，不依赖 `<style>` 标签
- [ ] 布局全用 `<table>`，不用 `div` 做结构定位
- [ ] 不使用 `flex` / `grid` / `position: absolute`
- [ ] 图片用 `<img>` + 固定 `width` / `height`
- [ ] `border-radius` 在 Outlook 中不生效但不影响阅读
- [ ] `linear-gradient` 在 Outlook 中降级为纯色
- [ ] `@media` 查询在 Outlook 桌面版中不生效（可接受，600px 宽本身适配桌面）
