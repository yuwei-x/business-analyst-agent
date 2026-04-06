# LENS Layout Templates Reference

本文件定义 LENS 看板的完整 HTML/CSS/JS 骨架。生成看板时，LENS 以本模板为基础，
注入数据、图表函数和风格变量，输出一个自包含、零依赖、双击即开的 HTML 文件。

---

## 1. 完整 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{REPORT_TITLE}}</title>
  <style>
    /* ========================================
       0. CSS 变量（由 style-catalog.md 注入）
       ======================================== */
    :root {
      /* 色板 — 以下为默认值，各风格覆盖这些变量即可切换外观 */
      --bg-primary:       #ffffff;
      --bg-secondary:     #f8f9fa;
      --bg-card:          #ffffff;
      --bg-kpi:           #ffffff;
      --bg-insight:       #f4f5f7;
      --bg-action:        #fafbfc;
      --bg-tooltip:       #1a1a2e;
      --bg-header:        transparent;
      --bg-filter:        #f0f2f5;
      --bg-hover:         #f0f2f5;

      --text-primary:     #1a1a2e;
      --text-secondary:   #4a5568;
      --text-muted:       #a0aec0;
      --text-inverse:     #ffffff;
      --text-accent:      #2563eb;
      --text-kpi-value:   #1a1a2e;
      --text-kpi-label:   #4a5568;

      --border-color:     #e2e8f0;
      --border-light:     #edf2f7;

      --accent-primary:   #2563eb;
      --accent-secondary: #7c3aed;

      /* KPI 趋势色 */
      --kpi-up:           #16a34a;
      --kpi-down:         #dc2626;
      --kpi-flat:         #9ca3af;

      /* 图表调色板 — 最多 8 色，依次使用 */
      --chart-1: #2563eb;
      --chart-2: #7c3aed;
      --chart-3: #0891b2;
      --chart-4: #059669;
      --chart-5: #d97706;
      --chart-6: #dc2626;
      --chart-7: #6366f1;
      --chart-8: #ec4899;

      /* 阴影 */
      --shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
      --shadow-md:  0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
      --shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);

      /* 圆角 */
      --radius-sm:  4px;
      --radius-md:  8px;
      --radius-lg:  12px;

      /* 字体 — 系统字体栈，无需 @font-face */
      --font-body:    -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                      "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue",
                      Helvetica, Arial, sans-serif;
      --font-heading: var(--font-body);
      --font-mono:    "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono",
                      "Courier New", Courier, monospace;

      /* 字号 */
      --size-xs:     11px;
      --size-sm:     12px;
      --size-base:   14px;
      --size-md:     16px;
      --size-lg:     20px;
      --size-xl:     24px;
      --size-2xl:    32px;
      --size-3xl:    40px;
      --size-kpi:    36px;

      /* 间距 */
      --space-xs:    4px;
      --space-sm:    8px;
      --space-md:    16px;
      --space-lg:    24px;
      --space-xl:    32px;
      --space-2xl:   48px;

      /* 过渡 */
      --transition-fast:  0.15s ease;
      --transition-base:  0.25s ease;
      --transition-slow:  0.35s ease;

      /* 布局 */
      --max-width:   1200px;
      --grid-gap:    var(--space-lg);
    }

    /* ========================================
       1. 全局重置与基础样式
       ======================================== */
    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      background: var(--bg-primary);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    body {
      max-width: var(--max-width);
      margin: 0 auto;
      padding: 40px 48px 60px;
      font-family: var(--font-body);
      font-size: var(--size-base);
      color: var(--text-primary);
      background: var(--bg-primary);
      line-height: 1.6;
    }

    h1, h2, h3, h4 {
      font-family: var(--font-heading);
      line-height: 1.3;
      color: var(--text-primary);
    }

    a { color: var(--accent-primary); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* ========================================
       2. Dashboard Header（报告标题区域）
       ======================================== */
    .dashboard-header {
      background: var(--bg-header);
      padding: 0 0 var(--space-lg);
      margin-bottom: var(--space-xl);
      border-bottom: 2px solid var(--border-color);
    }

    .dashboard-header h1 {
      font-size: var(--size-2xl);
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: var(--space-xs);
    }

    .dashboard-header .meta {
      font-size: var(--size-sm);
      color: var(--text-muted);
      letter-spacing: 0.02em;
    }

    /* ========================================
       3. Narrative Strip（一句话全局概要）
       ======================================== */
    .narrative-strip {
      background: var(--bg-insight);
      border-left: 4px solid var(--accent-primary);
      padding: var(--space-md) var(--space-lg);
      margin-bottom: var(--space-xl);
      font-size: var(--size-md);
      color: var(--text-secondary);
      line-height: 1.7;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }

    /* ========================================
       4. KPI Strip（指标卡片行）
       ======================================== */
    .kpi-strip {
      display: flex;
      gap: var(--space-md);
      margin-bottom: var(--space-xl);
      flex-wrap: wrap;
    }

    .kpi-card {
      flex: 1;
      min-width: 150px;
      background: var(--bg-kpi);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: var(--space-lg) var(--space-md);
      display: flex;
      flex-direction: column;
      gap: var(--space-xs);
      box-shadow: var(--shadow-sm);
      transition: box-shadow var(--transition-fast), transform var(--transition-fast);
    }

    .kpi-card:hover {
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }

    /* 数值：大号粗体 */
    .kpi-value {
      font-size: var(--size-kpi);
      font-weight: 700;
      color: var(--text-kpi-value);
      line-height: 1.1;
      letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
    }

    /* 趋势指示器 */
    .kpi-trend {
      font-size: var(--size-sm);
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: var(--space-xs);
    }

    .kpi-trend-up   { color: var(--kpi-up); }
    .kpi-trend-down { color: var(--kpi-down); }
    .kpi-trend-flat { color: var(--kpi-flat); }

    /* 标签 */
    .kpi-label {
      font-size: var(--size-sm);
      color: var(--text-kpi-label);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* 上下文说明 */
    .kpi-context {
      font-size: var(--size-xs);
      color: var(--text-muted);
      line-height: 1.4;
    }

    /* ========================================
       5. Filter Bar（筛选栏）
       ======================================== */
    .filter-bar {
      display: flex;
      align-items: center;
      gap: var(--space-md);
      padding: var(--space-sm) var(--space-md);
      background: var(--bg-filter);
      border-radius: var(--radius-md);
      margin-bottom: var(--space-xl);
      flex-wrap: wrap;
    }

    .filter-bar label {
      font-size: var(--size-sm);
      color: var(--text-secondary);
      font-weight: 500;
      white-space: nowrap;
    }

    .filter-bar select {
      font-family: var(--font-body);
      font-size: var(--size-sm);
      padding: 6px 28px 6px 10px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background: var(--bg-card);
      color: var(--text-primary);
      cursor: pointer;
      appearance: none;
      -webkit-appearance: none;
      /* 自定义下拉箭头 */
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%234a5568'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 8px center;
      background-size: 10px 6px;
      outline: none;
      transition: border-color var(--transition-fast);
    }

    .filter-bar select:hover {
      border-color: var(--accent-primary);
    }

    .filter-bar select:focus {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }

    /* 时间范围按钮组 */
    .time-range-group {
      display: flex;
      gap: 0;
      margin-left: auto;
    }

    .time-range-btn {
      font-family: var(--font-body);
      font-size: var(--size-xs);
      padding: 5px 12px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .time-range-btn:first-child { border-radius: var(--radius-sm) 0 0 var(--radius-sm); }
    .time-range-btn:last-child  { border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
    .time-range-btn:not(:last-child) { border-right: none; }

    .time-range-btn:hover {
      background: var(--bg-hover);
    }

    .time-range-btn.active {
      background: var(--accent-primary);
      color: var(--text-inverse);
      border-color: var(--accent-primary);
    }

    /* ========================================
       6. Hero Chart（全宽主图表）
       ======================================== */
    .hero-chart {
      margin-bottom: var(--space-xl);
    }

    .hero-chart .chart-container {
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: var(--space-xl) var(--space-lg);
      background: var(--bg-card);
      box-shadow: var(--shadow-md);
    }

    /* ========================================
       7. Chart Grid（支撑图表 2 列网格）
       ======================================== */
    .chart-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--grid-gap);
      margin-bottom: var(--space-xl);
    }

    /* 当图表数为奇数时，最后一张跨两列 */
    .chart-grid > .chart-container:last-child:nth-child(odd) {
      grid-column: 1 / -1;
    }

    /* ========================================
       8. Chart Container（单图表容器）
       ======================================== */
    .chart-container {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: var(--space-lg);
      display: flex;
      flex-direction: column;
      gap: var(--space-sm);
      box-shadow: var(--shadow-sm);
      transition: box-shadow var(--transition-fast);
      position: relative;  /* 为 .chart-save-btn 绝对定位提供锚点 */
    }

    .chart-container:hover {
      box-shadow: var(--shadow-md);
    }

    /* PNG 保存按钮（悬浮时显示，绝对定位于右上角） */
    .chart-save-btn {
      position: absolute;
      top: var(--space-sm);
      right: var(--space-sm);
      padding: 3px 8px;
      font-size: var(--size-xs);
      font-family: var(--font-body);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      cursor: pointer;
      opacity: 0;
      transition: opacity var(--transition-fast), background var(--transition-fast), color var(--transition-fast);
      z-index: 10;
      line-height: 1.5;
      user-select: none;
    }

    .chart-container:hover .chart-save-btn {
      opacity: 1;
    }

    .chart-save-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
      border-color: var(--accent-primary);
    }

    @media print {
      .chart-save-btn { display: none !important; }
    }

    /* 图表标题 = 洞察声明 */
    .chart-title {
      font-size: var(--size-md);
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.4;
    }

    .chart-subtitle {
      font-size: var(--size-sm);
      color: var(--text-muted);
      margin-top: -2px;
    }

    /* SVG 图表区域 */
    .chart-area {
      width: 100%;
      min-height: 240px;
      position: relative;
    }

    .chart-area svg {
      width: 100%;
      height: 100%;
      overflow: visible;
    }

    /* 图表内嵌洞察 */
    .chart-insight {
      font-size: var(--size-sm);
      color: var(--text-secondary);
      background: var(--bg-insight);
      padding: var(--space-sm) var(--space-md);
      border-radius: var(--radius-sm);
      line-height: 1.5;
    }

    /* 数据来源标注 */
    .chart-source {
      font-size: var(--size-xs);
      color: var(--text-muted);
      text-align: right;
    }

    /* 图例 */
    .chart-legend {
      display: flex;
      flex-wrap: wrap;
      gap: var(--space-md);
      padding: var(--space-sm) 0;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: var(--space-xs);
      font-size: var(--size-sm);
      color: var(--text-secondary);
      cursor: default;
    }

    .legend-swatch {
      width: 12px;
      height: 12px;
      border-radius: 2px;
      flex-shrink: 0;
    }

    /* ========================================
       9. Theme Section（主题段落，可折叠）
       ======================================== */
    .theme-section {
      margin-bottom: var(--space-xl);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      overflow: hidden;
      background: var(--bg-card);
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--space-md) var(--space-lg);
      background: var(--bg-secondary);
      cursor: pointer;
      user-select: none;
      transition: background var(--transition-fast);
    }

    .section-header:hover {
      background: var(--bg-hover);
    }

    .section-header h2 {
      font-size: var(--size-lg);
      font-weight: 600;
    }

    .toggle-icon {
      font-size: var(--size-sm);
      color: var(--text-muted);
      transition: transform var(--transition-base);
    }

    .theme-section.expanded .toggle-icon {
      transform: rotate(180deg);
    }

    .section-content {
      max-height: 0;
      overflow: hidden;
      transition: max-height var(--transition-slow);
    }

    .theme-section.expanded .section-content {
      /* JS 会动态设置 max-height，此处给一个足够大的值作为回退 */
      max-height: 8000px;
    }

    .section-content-inner {
      padding: var(--space-lg);
    }

    .section-narrative {
      font-size: var(--size-base);
      color: var(--text-secondary);
      line-height: 1.7;
      margin-bottom: var(--space-lg);
    }

    /* ========================================
       10. Actions Panel（行动建议）
       ======================================== */
    .actions-panel {
      margin-bottom: var(--space-xl);
    }

    .actions-panel > h2 {
      font-size: var(--size-xl);
      font-weight: 700;
      margin-bottom: var(--space-lg);
      padding-bottom: var(--space-sm);
      border-bottom: 2px solid var(--accent-primary);
      display: inline-block;
    }

    .actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: var(--space-md);
    }

    .action-card {
      background: var(--bg-action);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: var(--space-lg);
      display: flex;
      flex-direction: column;
      gap: var(--space-sm);
      position: relative;
      transition: box-shadow var(--transition-fast), transform var(--transition-fast);
    }

    .action-card:hover {
      box-shadow: var(--shadow-md);
      transform: translateY(-1px);
    }

    /* 优先级标签 */
    .action-priority {
      font-size: var(--size-xs);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      display: inline-block;
      width: fit-content;
    }

    .action-priority.p1 {
      background: #fef2f2;
      color: #dc2626;
      border: 1px solid #fecaca;
    }

    .action-priority.p2 {
      background: #fffbeb;
      color: #d97706;
      border: 1px solid #fed7aa;
    }

    .action-priority.p3 {
      background: #eff6ff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
    }

    .action-summary {
      font-size: var(--size-md);
      font-weight: 600;
      color: var(--text-primary);
      line-height: 1.4;
    }

    .action-details {
      display: flex;
      flex-direction: column;
      gap: var(--space-xs);
      margin-top: var(--space-xs);
    }

    .action-details .detail {
      font-size: var(--size-sm);
      color: var(--text-secondary);
      line-height: 1.5;
    }

    .action-details .detail strong {
      display: inline-block;
      min-width: 56px;
      color: var(--text-primary);
      font-weight: 600;
      font-size: var(--size-xs);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .action-details .detail.risk {
      margin-top: var(--space-xs);
      padding-top: var(--space-sm);
      border-top: 1px dashed var(--border-light);
      color: var(--kpi-down);
    }

    .action-details .detail.risk strong {
      color: var(--kpi-down);
      min-width: auto;
    }

    /* ========================================
       11. Dashboard Footer
       ======================================== */
    .dashboard-footer {
      margin-top: var(--space-2xl);
      padding-top: var(--space-lg);
      border-top: 1px solid var(--border-color);
      text-align: center;
    }

    .dashboard-footer p {
      font-size: var(--size-xs);
      color: var(--text-muted);
      line-height: 1.6;
    }

    .dashboard-footer .print-hint {
      font-size: 10px;
      color: var(--text-muted);
      opacity: 0.6;
      margin-top: var(--space-xs);
    }

    /* ========================================
       12. Tooltip（悬浮提示）
       ======================================== */
    .tooltip {
      position: fixed;
      background: var(--bg-tooltip);
      color: var(--text-inverse);
      padding: var(--space-sm) var(--space-md);
      border-radius: var(--radius-sm);
      font-size: var(--size-sm);
      line-height: 1.5;
      pointer-events: none;
      z-index: 1000;
      opacity: 0;
      transition: opacity var(--transition-fast);
      box-shadow: var(--shadow-lg);
      max-width: 280px;
      word-wrap: break-word;
    }

    .tooltip.visible {
      opacity: 1;
    }

    .tooltip .tooltip-title {
      font-weight: 600;
      margin-bottom: 2px;
    }

    .tooltip .tooltip-row {
      display: flex;
      justify-content: space-between;
      gap: var(--space-md);
    }

    .tooltip .tooltip-label {
      opacity: 0.7;
    }

    .tooltip .tooltip-value {
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }

    /* ========================================
       13. 图表 SVG 通用样式
       ======================================== */

    /* 坐标轴 */
    .axis line, .axis path {
      stroke: var(--border-color);
      stroke-width: 1;
      shape-rendering: crispEdges;
    }

    .axis text {
      fill: var(--text-muted);
      font-family: var(--font-body);
      font-size: var(--size-xs);
    }

    /* 网格线 */
    .grid-line {
      stroke: var(--border-light);
      stroke-width: 1;
      stroke-dasharray: 3,3;
    }

    /* 数据标签 */
    .data-label {
      fill: var(--text-secondary);
      font-family: var(--font-body);
      font-size: var(--size-xs);
      font-variant-numeric: tabular-nums;
    }

    /* 高亮效果：图表元素鼠标悬浮 */
    .chart-element {
      transition: opacity var(--transition-fast);
    }

    .chart-area.has-hover .chart-element:not(.highlighted) {
      opacity: 0.3;
    }

    .chart-element.highlighted {
      opacity: 1;
    }

    /* 标注箭头和标记 */
    .annotation-line {
      stroke: var(--text-muted);
      stroke-width: 1;
      stroke-dasharray: 4,3;
    }

    .annotation-text {
      fill: var(--text-secondary);
      font-family: var(--font-body);
      font-size: var(--size-xs);
      font-style: italic;
    }

    /* 参考线（均值线、目标线等） */
    .reference-line {
      stroke: var(--kpi-down);
      stroke-width: 1.5;
      stroke-dasharray: 6,4;
    }

    .reference-label {
      fill: var(--kpi-down);
      font-family: var(--font-body);
      font-size: var(--size-xs);
      font-weight: 600;
    }

    /* ========================================
       14. 工具类（辅助样式）
       ======================================== */
    .text-up   { color: var(--kpi-up); }
    .text-down { color: var(--kpi-down); }
    .text-flat { color: var(--kpi-flat); }

    .text-muted    { color: var(--text-muted); }
    .text-accent   { color: var(--accent-primary); }
    .font-mono     { font-family: var(--font-mono); }
    .font-tabular  { font-variant-numeric: tabular-nums; }

    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    /* ========================================
       15. 响应式断点
       ======================================== */

    /* 平板（<= 1024px） */
    @media (max-width: 1024px) {
      body {
        padding: 32px 32px 48px;
      }

      .dashboard-header h1 {
        font-size: var(--size-xl);
      }

      .kpi-value {
        font-size: 28px;
      }
    }

    /* 手机横屏 / 小平板（<= 768px） */
    @media (max-width: 768px) {
      body {
        padding: 16px 16px 32px;
      }

      .dashboard-header h1 {
        font-size: var(--size-lg);
      }

      .kpi-strip {
        flex-direction: column;
      }

      .kpi-card {
        min-width: 100%;
      }

      .kpi-value {
        font-size: var(--size-xl);
      }

      .chart-grid {
        grid-template-columns: 1fr;
      }

      .chart-grid > .chart-container:last-child:nth-child(odd) {
        grid-column: auto;
      }

      .actions-grid {
        grid-template-columns: 1fr;
      }

      .filter-bar {
        flex-direction: column;
        align-items: stretch;
      }

      .time-range-group {
        margin-left: 0;
        justify-content: stretch;
      }

      .time-range-btn {
        flex: 1;
        text-align: center;
      }

      .hero-chart .chart-container {
        padding: var(--space-md);
      }

      .chart-container {
        padding: var(--space-md);
      }
    }

    /* 手机竖屏（<= 480px） */
    @media (max-width: 480px) {
      body {
        padding: 12px 12px 24px;
      }

      .kpi-value {
        font-size: var(--size-lg);
      }

      .chart-area {
        min-height: 180px;
      }

      .narrative-strip {
        font-size: var(--size-base);
        padding: var(--space-sm) var(--space-md);
      }
    }

    /* ========================================
       16. 打印样式
       ======================================== */
    @media print {
      /* 隐藏交互元素 */
      .filter-bar,
      .time-range-group,
      .toggle-icon,
      .tooltip,
      .print-hint {
        display: none !important;
      }

      /* 强制展开所有折叠区域 */
      .theme-section .section-content {
        max-height: none !important;
        overflow: visible !important;
      }

      /* 去掉阴影和悬浮效果 */
      .kpi-card,
      .chart-container,
      .action-card {
        box-shadow: none !important;
        transform: none !important;
      }

      /* 收窄内边距 */
      body {
        padding: 20px;
        max-width: 100%;
        font-size: 12px;
      }

      /* 确保分页友好 */
      .chart-container,
      .action-card,
      .theme-section {
        break-inside: avoid;
        page-break-inside: avoid;
      }

      .dashboard-header {
        break-after: avoid;
      }

      .actions-panel > h2 {
        break-after: avoid;
      }

      /* 打印背景色 */
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
      }

      /* 链接显示 URL */
      a[href]::after {
        content: " (" attr(href) ")";
        font-size: 10px;
        color: var(--text-muted);
      }
    }
  </style>
</head>
```

---

## 2. HTML Body 结构

```html
<body>
  <!-- ====== Header ====== -->
  <header class="dashboard-header">
    <h1>{{REPORT_TITLE}}</h1>
    <p class="meta">{{DATE}} · 数据来源: {{DATA_SOURCE}}</p>
  </header>

  <!-- ====== 全局叙事横幅 ====== -->
  <div class="narrative-strip">{{OVERALL_NARRATIVE}}</div>

  <!-- ====== KPI 卡片行 ====== -->
  <div class="kpi-strip">
    <!-- {{KPI_CARDS}} — 4-6 张卡片，由组件模板填充 -->
  </div>

  <!-- ====== 筛选栏 ====== -->
  <div class="filter-bar">
    <!-- {{FILTER_DROPDOWNS}} — 自动检测分类列生成 -->
    <div class="time-range-group">
      <!-- {{TIME_RANGE_BUTTONS}} — 如数据含时间列则生成 -->
    </div>
  </div>

  <!-- ====== 主图表 ====== -->
  <div class="hero-chart">
    <div class="chart-container" id="hero">
      <h2 class="chart-title">{{HERO_TITLE}}</h2>
      <p class="chart-subtitle">{{HERO_SUBTITLE}}</p>
      <div class="chart-legend" id="hero-legend">
        <!-- {{HERO_LEGEND}} -->
      </div>
      <div class="chart-area" id="hero-chart"></div>
      <p class="chart-insight">{{HERO_INSIGHT}}</p>
      <p class="chart-source">{{HERO_SOURCE}}</p>
    </div>
  </div>

  <!-- ====== 支撑图表网格 ====== -->
  <div class="chart-grid">
    <!-- {{SUPPORTING_CHARTS}} — 2-6 张支撑图，由组件模板填充 -->
  </div>

  <!-- ====== 主题段落 ====== -->
  <!-- {{THEME_SECTIONS}} — 0-N 个可折叠段落，由组件模板填充 -->

  <!-- ====== 行动建议 ====== -->
  <div class="actions-panel">
    <h2>行动建议</h2>
    <div class="actions-grid">
      <!-- {{ACTION_CARDS}} — 由组件模板填充 -->
    </div>
  </div>

  <!-- ====== 页脚 ====== -->
  <footer class="dashboard-footer">
    <p>{{QUALITY_NOTE}} · 生成于 {{TIMESTAMP}}</p>
    <p class="print-hint">Ctrl/Cmd + P 导出 PDF</p>
  </footer>

  <!-- ====== Tooltip 容器（全局唯一） ====== -->
  <div class="tooltip" id="tooltip"></div>

  <!-- ====== JavaScript ====== -->
  <script>
    /* 数据注入（LENS 生成时填入 JSON） */
    const dashboardData = {{DASHBOARD_DATA_JSON}};

    /* 图表渲染函数（从 chart-patterns.md 注入） */
    {{CHART_FUNCTIONS}}

    /* 筛选逻辑 */
    {{FILTER_LOGIC}}

    /* 初始化脚本 */
    {{INIT_SCRIPT}}
  </script>
</body>
</html>
```

---

## 3. 组件模板（Component Templates）

LENS 在构建看板时，按以下模板逐个拼装组件，替换占位符后插入 Body 结构中。

### 3.1 KPI 卡片

每张 KPI 卡片展示一个核心指标的数值、趋势方向、标签和上下文说明。

```html
<div class="kpi-card" data-kpi="{{KPI_KEY}}">
  <span class="kpi-value font-tabular">{{VALUE}}</span>
  <span class="kpi-trend kpi-trend-{{DIRECTION}}">{{TREND_ICON}} {{TREND_TEXT}}</span>
  <span class="kpi-label">{{LABEL}}</span>
  <span class="kpi-context">{{CONTEXT}}</span>
</div>
```

**占位符说明：**

| 占位符 | 类型 | 示例 |
|--------|------|------|
| `{{KPI_KEY}}` | string | `revenue`, `conversion_rate` |
| `{{VALUE}}` | string（已格式化） | `$1.2M`, `68.3%`, `2,451` |
| `{{DIRECTION}}` | enum | `up`, `down`, `flat` |
| `{{TREND_ICON}}` | HTML 实体 | `&#9650;`(上), `&#9660;`(下), `&#8212;`(平) |
| `{{TREND_TEXT}}` | string | `+12.3% vs 上月`, `-5.1% YoY`, `持平` |
| `{{LABEL}}` | string | `总收入`, `转化率` |
| `{{CONTEXT}}` | string | `环比增长连续 3 个月`, `低于行业均值 2pp` |

**趋势图标 HTML 实体参考：**
- 上升：`&#9650;`（实心上三角）或 `&#8593;`（箭头）
- 下降：`&#9660;`（实心下三角）或 `&#8595;`（箭头）
- 持平：`&#8212;`（长破折号）

### 3.2 图表容器

包裹每一张图表。标题必须是洞察声明（可证伪、含数字），而非描述性标题。

```html
<div class="chart-container" id="chart-{{ID}}">
  <h3 class="chart-title">{{TITLE}}</h3>
  <p class="chart-subtitle">{{SUBTITLE}}</p>
  <div class="chart-legend" id="legend-{{ID}}">
    <!-- 图例由 JS 渲染函数动态填充 -->
  </div>
  <div class="chart-area" id="chart-area-{{ID}}"></div>
  <p class="chart-insight">{{INSIGHT}}</p>
  <p class="chart-source">{{SOURCE}}</p>
  <!-- PNG 保存按钮：悬浮图表时显示，点击将图表导出为本地 PNG 文件 -->
  <button class="chart-save-btn"
          onclick="saveChartAsPNG('chart-area-{{ID}}', '{{TITLE}}')"
          title="保存为 PNG">↓ PNG</button>
</div>
```

**占位符说明：**

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{ID}}` | 唯一标识符（用于 JS 定位） | `revenue-trend`, `channel-mix` |
| `{{TITLE}}` | 洞察声明式标题（非描述性） | `Q1 线上收入同比增长 34%，线下持平` |
| `{{SUBTITLE}}` | 补充说明（可选） | `2024 年 1 月 - 2024 年 12 月 · 单位: 万元` |
| `{{INSIGHT}}` | 1-2 句叙事结论 | `线上渠道增长主要由社交电商驱动，占增量的 62%` |
| `{{SOURCE}}` | 数据来源标注（可选） | `来源: 内部 CRM 系统` |

**标题撰写规则：**
- 好：`华东区 Q3 客单价下降 18%，低于全国均值`
- 差：`各区域客单价趋势图`

### 3.3 主题段落（可折叠）

将相关图表组织在一个叙事主题下，支持展开/收起。

```html
<section class="theme-section" id="theme-{{ID}}">
  <div class="section-header" onclick="toggleSection('theme-{{ID}}')">
    <h2>{{THEME_NAME}}</h2>
    <span class="toggle-icon">&#9660;</span>
  </div>
  <div class="section-content">
    <div class="section-content-inner">
      <p class="section-narrative">{{NARRATIVE}}</p>
      <div class="chart-grid">
        {{CHARTS}}
      </div>
    </div>
  </div>
</section>
```

**占位符说明：**

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{ID}}` | 段落唯一 ID | `growth-drivers`, `risk-factors` |
| `{{THEME_NAME}}` | 段落标题 | `增长驱动因素`, `风险与预警` |
| `{{NARRATIVE}}` | 2-3 句叙事段落 | `本季度增长主要由两个因素驱动：...` |
| `{{CHARTS}}` | 嵌套的图表容器 HTML | 1-4 个 chart-container 组件 |

### 3.4 行动建议卡片

每张卡片对应一条具体的行动建议，包含执行要素。

```html
<div class="action-card">
  <div class="action-priority {{PRIORITY_CLASS}}">{{PRIORITY}}</div>
  <h3 class="action-summary">{{SUMMARY}}</h3>
  <div class="action-details">
    <div class="detail"><strong>WHO</strong> {{WHO}}</div>
    <div class="detail"><strong>WHAT</strong> {{WHAT}}</div>
    <div class="detail"><strong>WHEN</strong> {{WHEN}}</div>
    <div class="detail"><strong>IMPACT</strong> {{IMPACT}}</div>
    <div class="detail risk"><strong>不行动的风险</strong> {{RISK}}</div>
  </div>
</div>
```

**占位符说明：**

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{PRIORITY_CLASS}}` | CSS 类 | `p1`, `p2`, `p3` |
| `{{PRIORITY}}` | 显示文本 | `P1 紧急`, `P2 重要`, `P3 建议` |
| `{{SUMMARY}}` | 一句话行动摘要 | `将华南区促销预算从 15% 上调至 25%` |
| `{{WHO}}` | 责任人/团队 | `市场部 · 区域负责人` |
| `{{WHAT}}` | 具体动作 | `重新分配 Q2 促销预算，增加华南区线上投放` |
| `{{WHEN}}` | 时间节点 | `2024 年 4 月 15 日前完成` |
| `{{IMPACT}}` | 预期效果 | `预计提升华南区 GMV 12-18%` |
| `{{RISK}}` | 不行动的风险 | `华南区市场份额可能继续被竞品蚕食` |

### 3.5 筛选下拉框

每个分类列生成一个下拉。全部选项在前。

```html
<label for="filter-{{COL_KEY}}">{{COL_LABEL}}</label>
<select id="filter-{{COL_KEY}}" onchange="applyFilters()">
  <option value="__all__">全部</option>
  {{OPTIONS}}
</select>
```

单个选项：
```html
<option value="{{OPTION_VALUE}}">{{OPTION_LABEL}}</option>
```

### 3.6 时间范围按钮

当数据包含日期列时生成。

```html
<div class="time-range-group">
  <button class="time-range-btn active" onclick="setTimeRange('all')">全部</button>
  <button class="time-range-btn" onclick="setTimeRange('ytd')">年初至今</button>
  <button class="time-range-btn" onclick="setTimeRange('quarter')">本季度</button>
  <button class="time-range-btn" onclick="setTimeRange('month')">近 30 天</button>
</div>
```

### 3.7 图例项

图例由 JS 动态构建，但 HTML 结构如下：

```html
<div class="legend-item" data-series="{{SERIES_KEY}}">
  <span class="legend-swatch" style="background: {{COLOR}}"></span>
  <span>{{SERIES_LABEL}}</span>
</div>
```

---

## 4. JavaScript 模板

以下 JS 函数在生成时内联到 `<script>` 标签中。所有函数使用 Vanilla JS，零依赖。

### 4.1 筛选逻辑

```javascript
/**
 * 初始化筛选器：自动检测分类列并创建下拉框
 * @param {Object} data - dashboardData 对象
 * @param {Array<string>} categoricalCols - 分类列名列表
 */
function initFilters(data, categoricalCols) {
  const filterBar = document.querySelector('.filter-bar');
  if (!filterBar || !categoricalCols.length) return;

  categoricalCols.forEach(col => {
    // 提取去重值并排序
    const uniqueValues = [...new Set(data.rows.map(r => r[col]))]
      .filter(v => v != null)
      .sort();

    if (uniqueValues.length < 2 || uniqueValues.length > 50) return; // 跳过不适合筛选的列

    const label = document.createElement('label');
    label.setAttribute('for', 'filter-' + col);
    label.textContent = data.columnLabels?.[col] || col;

    const select = document.createElement('select');
    select.id = 'filter-' + col;
    select.addEventListener('change', applyFilters);

    // "全部"选项
    const allOpt = document.createElement('option');
    allOpt.value = '__all__';
    allOpt.textContent = '全部';
    select.appendChild(allOpt);

    uniqueValues.forEach(val => {
      const opt = document.createElement('option');
      opt.value = val;
      opt.textContent = val;
      select.appendChild(opt);
    });

    // 在时间范围按钮之前插入
    const timeGroup = filterBar.querySelector('.time-range-group');
    if (timeGroup) {
      filterBar.insertBefore(select, timeGroup);
      filterBar.insertBefore(label, select);
    } else {
      filterBar.appendChild(label);
      filterBar.appendChild(select);
    }
  });
}

/**
 * 读取所有筛选器的当前值，过滤数据，重新渲染所有图表和 KPI
 */
function applyFilters() {
  const selects = document.querySelectorAll('.filter-bar select');
  const activeFilters = {};

  selects.forEach(sel => {
    if (sel.value !== '__all__') {
      const col = sel.id.replace('filter-', '');
      activeFilters[col] = sel.value;
    }
  });

  // 过滤数据
  const filtered = dashboardData.rows.filter(row => {
    return Object.entries(activeFilters).every(([col, val]) => row[col] === val);
  });

  // 重新渲染（调用各图表的 render 函数）
  if (typeof renderAllCharts === 'function') {
    renderAllCharts(filtered);
  }
  if (typeof updateKPIs === 'function') {
    updateKPIs(filtered);
  }
}
```

### 4.2 段落折叠切换

```javascript
/**
 * 切换主题段落的展开/收起状态
 * @param {string} sectionId - 段落 DOM ID
 */
function toggleSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (!section) return;

  section.classList.toggle('expanded');

  // 展开时动态计算 max-height，避免固定值带来的截断问题
  const content = section.querySelector('.section-content');
  if (section.classList.contains('expanded')) {
    content.style.maxHeight = content.scrollHeight + 'px';
  } else {
    content.style.maxHeight = '0px';
  }
}

/**
 * 默认展开第一个 theme-section
 */
function initSections() {
  const firstSection = document.querySelector('.theme-section');
  if (firstSection) {
    firstSection.classList.add('expanded');
    const content = firstSection.querySelector('.section-content');
    if (content) {
      content.style.maxHeight = content.scrollHeight + 'px';
    }
  }
}
```

### 4.3 Tooltip 管理

```javascript
const tooltipEl = document.getElementById('tooltip');

/**
 * 显示 tooltip
 * @param {MouseEvent} e - 鼠标事件
 * @param {string} html - tooltip 内容 HTML
 */
function showTooltip(e, html) {
  tooltipEl.innerHTML = html;
  tooltipEl.classList.add('visible');

  // 定位逻辑：防止超出视口
  const rect = tooltipEl.getBoundingClientRect();
  const viewW = window.innerWidth;
  const viewH = window.innerHeight;

  let left = e.clientX + 12;
  let top  = e.clientY - 8;

  // 右侧溢出则移到鼠标左侧
  if (left + rect.width + 8 > viewW) {
    left = e.clientX - rect.width - 12;
  }
  // 底部溢出则上移
  if (top + rect.height + 8 > viewH) {
    top = viewH - rect.height - 8;
  }
  // 防止负值
  if (left < 4) left = 4;
  if (top < 4) top = 4;

  tooltipEl.style.left = left + 'px';
  tooltipEl.style.top  = top  + 'px';
}

/**
 * 隐藏 tooltip
 */
function hideTooltip() {
  tooltipEl.classList.remove('visible');
}
```

### 4.4 时间范围选择器

```javascript
/**
 * 按时间范围过滤数据并重新渲染
 * @param {string} range - 'all' | 'ytd' | 'quarter' | 'month'
 */
function setTimeRange(range) {
  // 更新按钮激活状态
  document.querySelectorAll('.time-range-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('onclick').includes("'" + range + "'"));
  });

  const dateCol = dashboardData.dateColumn;  // LENS 在数据对象中指定日期列名
  if (!dateCol) return;

  const now = new Date();
  let cutoff = null;

  switch (range) {
    case 'month':
      cutoff = new Date(now);
      cutoff.setDate(cutoff.getDate() - 30);
      break;
    case 'quarter':
      cutoff = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1);
      break;
    case 'ytd':
      cutoff = new Date(now.getFullYear(), 0, 1);
      break;
    case 'all':
    default:
      cutoff = null;
  }

  let filtered;
  if (cutoff) {
    filtered = dashboardData.rows.filter(row => {
      const d = new Date(row[dateCol]);
      return d >= cutoff;
    });
  } else {
    filtered = dashboardData.rows;
  }

  // 同时尊重下拉筛选器
  const selects = document.querySelectorAll('.filter-bar select');
  selects.forEach(sel => {
    if (sel.value !== '__all__') {
      const col = sel.id.replace('filter-', '');
      filtered = filtered.filter(row => row[col] === sel.value);
    }
  });

  if (typeof renderAllCharts === 'function') {
    renderAllCharts(filtered);
  }
  if (typeof updateKPIs === 'function') {
    updateKPIs(filtered);
  }
}
```

### 4.5 跨图高亮

```javascript
/**
 * 跨图表高亮：鼠标悬浮某数据实体时，所有图表的同实体元素同步高亮
 * @param {string} entityKey - 实体标识（如分类名、系列名）
 */
function highlightEntity(entityKey) {
  document.querySelectorAll('.chart-area').forEach(area => {
    area.classList.add('has-hover');
  });
  document.querySelectorAll('.chart-element').forEach(el => {
    if (el.dataset.entity === entityKey) {
      el.classList.add('highlighted');
    }
  });
}

/**
 * 清除所有跨图高亮
 */
function clearHighlight() {
  document.querySelectorAll('.chart-area').forEach(area => {
    area.classList.remove('has-hover');
  });
  document.querySelectorAll('.chart-element').forEach(el => {
    el.classList.remove('highlighted');
  });
}
```

### 4.6 KPI 动态更新

```javascript
/**
 * 根据过滤后的数据重新计算并更新 KPI 卡片
 * @param {Array<Object>} filteredRows - 过滤后的数据行
 */
function updateKPIs(filteredRows) {
  if (!dashboardData.kpiDefinitions) return;

  dashboardData.kpiDefinitions.forEach(kpi => {
    const cardEl = document.querySelector('[data-kpi="' + kpi.key + '"]');
    if (!cardEl) return;

    // 计算当前值
    const currentValue = kpi.compute(filteredRows);
    const formattedValue = kpi.format(currentValue);

    // 计算趋势（对比基线）
    const baselineValue = kpi.baseline;
    let direction = 'flat';
    let trendText = '持平';

    if (baselineValue != null && baselineValue !== 0) {
      const pctChange = ((currentValue - baselineValue) / Math.abs(baselineValue)) * 100;
      if (Math.abs(pctChange) >= 0.5) {  // 变化不足 0.5% 视为持平
        direction = pctChange > 0 ? 'up' : 'down';
        const sign = pctChange > 0 ? '+' : '';
        trendText = sign + pctChange.toFixed(1) + '% vs ' + kpi.baselinePeriod;
      }
    }

    // 趋势方向可能需要反转（如成本降低是好事）
    const displayDirection = kpi.invertTrend
      ? (direction === 'up' ? 'down' : direction === 'down' ? 'up' : 'flat')
      : direction;

    // 图标
    const icons = { up: '&#9650;', down: '&#9660;', flat: '&#8212;' };

    // 更新 DOM
    cardEl.querySelector('.kpi-value').textContent = formattedValue;
    const trendEl = cardEl.querySelector('.kpi-trend');
    trendEl.className = 'kpi-trend kpi-trend-' + displayDirection;
    trendEl.innerHTML = icons[direction] + ' ' + trendText;
  });
}
```

### 4.7 PNG 图表导出

```javascript
/**
 * 将指定图表区域内的 SVG 导出为本地 PNG 文件（2× DPI，带背景色）
 * @param {string} areaId   - .chart-area 的 DOM id（如 "chart-area-revenue-trend"）
 * @param {string} [chartTitle] - 图表标题，用于生成文件名；省略则使用 "chart"
 */
function saveChartAsPNG(areaId, chartTitle) {
  const area = document.getElementById(areaId);
  if (!area) return;
  const svg = area.querySelector('svg');
  if (!svg) { alert('此图表暂不支持导出'); return; }

  // 获取实际渲染尺寸（getBoundingClientRect 在部分机型上更可靠）
  const rect = svg.getBoundingClientRect();
  const W = Math.round(rect.width)  || parseInt(svg.getAttribute('width'))  || 600;
  const H = Math.round(rect.height) || parseInt(svg.getAttribute('height')) || 300;

  // 克隆 SVG 并内联计算后的 fill / stroke（化解 CSS 变量对 canvas 的不兼容）
  const clone = svg.cloneNode(true);
  _inlineStyles(svg, clone);

  // 注入背景色矩形（最底层），避免透明背景导出为黑色
  const bgColor = (getComputedStyle(document.documentElement)
    .getPropertyValue('--bg-card') || '#ffffff').trim();
  const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  bgRect.setAttribute('width', W);
  bgRect.setAttribute('height', H);
  bgRect.setAttribute('fill', bgColor);
  clone.insertBefore(bgRect, clone.firstChild);

  clone.setAttribute('width',  W);
  clone.setAttribute('height', H);
  clone.removeAttribute('style'); // 去掉可能干扰渲染的 width:100% 内联样式

  const svgStr = new XMLSerializer().serializeToString(clone);
  const blob   = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
  const url    = URL.createObjectURL(blob);

  const dpr    = window.devicePixelRatio || 1;
  const canvas = document.createElement('canvas');
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const img = new Image();
  img.onload = function () {
    ctx.drawImage(img, 0, 0, W, H);
    URL.revokeObjectURL(url);

    // 生成安全文件名（中文+字母数字，截断 40 字符）
    const name = (chartTitle || 'chart')
      .replace(/[^\w\u4e00-\u9fa5]/g, '_')
      .replace(/_+/g, '_')
      .substring(0, 40)
      .replace(/^_|_$/g, '') || 'chart';

    const a = document.createElement('a');
    a.download = name + '.png';
    a.href = canvas.toDataURL('image/png');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.onerror = function () {
    URL.revokeObjectURL(url);
    console.error('[saveChartAsPNG] SVG → canvas 转换失败', areaId);
  };
  img.src = url;
}

/**
 * 递归地将 sourceEl 中通过 CSS 类/变量设置的 fill/stroke
 * 内联到对应的 cloneEl，保证 canvas 能正确渲染颜色。
 * （chart-patterns.md 中的图表元素已通过 JS 设置 inline style，
 *  此函数主要处理少数依赖 CSS class 的 SVG 元素。）
 */
function _inlineStyles(sourceEl, cloneEl) {
  if (sourceEl.nodeType !== Node.ELEMENT_NODE) return;
  const computed = window.getComputedStyle(sourceEl);
  const fill   = computed.fill;
  const stroke = computed.stroke;
  // 只在值不为"none"且与 inline 不重复时写入，避免覆盖已有值
  if (fill   && fill   !== 'none' && !sourceEl.style.fill)   cloneEl.style.fill   = fill;
  if (stroke && stroke !== 'none' && !sourceEl.style.stroke) cloneEl.style.stroke = stroke;

  const sc = [...sourceEl.children];
  const cc = [...cloneEl.children];
  sc.forEach((child, i) => { if (cc[i]) _inlineStyles(child, cc[i]); });
}
```

### 4.8 初始化入口

```javascript
/**
 * 看板初始化函数 — 在页面加载完成后执行
 * 按顺序：渲染图表 → 初始化筛选 → 展开首段 → 绑定事件
 */
function initDashboard() {
  // 1. 渲染所有图表（使用完整数据）
  if (typeof renderAllCharts === 'function') {
    renderAllCharts(dashboardData.rows);
  }

  // 2. 初始化筛选器
  if (dashboardData.categoricalColumns) {
    initFilters(dashboardData, dashboardData.categoricalColumns);
  }

  // 3. 初始化 KPI
  if (typeof updateKPIs === 'function') {
    updateKPIs(dashboardData.rows);
  }

  // 4. 展开第一个主题段落
  initSections();

  // 5. 全局鼠标移出时清除高亮和 tooltip
  document.addEventListener('mouseleave', function() {
    hideTooltip();
    clearHighlight();
  });

  // 6. 窗口 resize 时重新渲染图表以适配新宽度
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      if (typeof renderAllCharts === 'function') {
        applyFilters();  // 会使用当前筛选状态重新渲染
      }
    }, 250);
  });
}

// 启动
document.addEventListener('DOMContentLoaded', initDashboard);
```

---

## 5. `dashboardData` 数据对象规范

LENS 在生成时将分析结果序列化为 JSON，注入到 `dashboardData` 变量中。
结构如下：

```javascript
const dashboardData = {
  // 元信息
  title: "Q1 2024 华东区销售分析看板",
  date: "2024-04-15",
  dataSource: "内部 CRM + ERP 系统",
  timestamp: "2024-04-15T14:30:00+08:00",
  qualityNote: "数据截至 2024-04-14，部分退货数据有 T+3 延迟",

  // 全局叙事
  overallNarrative: "Q1 华东区总收入 1.2 亿元，同比增长 15%，但毛利率下降 2pp，主要受促销力度加大影响。",

  // 日期列标识（用于时间范围筛选）
  dateColumn: "order_date",

  // 分类列标识（用于自动生成筛选器）
  categoricalColumns: ["region", "channel", "product_category"],

  // 列标签映射（用于筛选器 label 显示）
  columnLabels: {
    "region": "区域",
    "channel": "渠道",
    "product_category": "品类"
  },

  // 原始数据行
  rows: [
    { order_date: "2024-01-05", region: "上海", channel: "线上", product_category: "电子", revenue: 150000, cost: 90000 },
    // ...
  ],

  // KPI 定义
  kpiDefinitions: [
    {
      key: "total_revenue",
      label: "总收入",
      format: (v) => "¥" + (v / 10000).toFixed(1) + "万",
      compute: (rows) => rows.reduce((s, r) => s + r.revenue, 0),
      baseline: 10400000,
      baselinePeriod: "上季度",
      invertTrend: false
    }
    // ...
  ],

  // 图表规格（由 PRISM 的 dashboard_plan 预计算或 LENS 独立模式生成）
  charts: [
    {
      id: "revenue-trend",
      type: "line",           // bar | line | horizontal-bar | pie | donut | stacked-bar | scatter | waterfall | funnel | heatmap
      title: "Q1 月度收入持续攀升，3 月环比增长 22%",
      subtitle: "2024 年 1-3 月 · 单位: 万元",
      insight: "增长主要由上海地区线上渠道驱动。",
      source: "来源: ERP 系统",
      isHero: true,
      config: { /* 图表特定配置，参见 chart-patterns.md */ }
    }
    // ...
  ],

  // 主题段落
  themes: [
    {
      id: "growth-drivers",
      name: "增长驱动因素",
      narrative: "本季度增长由两个核心因素驱动：...",
      chartIds: ["channel-breakdown", "top-products"]
    }
    // ...
  ],

  // 行动建议
  actions: [
    {
      priority: "P1",
      priorityClass: "p1",
      summary: "将华南区促销预算从 15% 上调至 25%",
      who: "市场部 · 区域负责人",
      what: "重新分配 Q2 促销预算",
      when: "2024 年 4 月 15 日前",
      impact: "预计提升华南区 GMV 12-18%",
      risk: "华南区市场份额可能继续被竞品蚕食"
    }
    // ...
  ]
};
```

---

## 6. 生成流程指引

LENS 在组装最终 HTML 时，按以下顺序执行：

1. **选择风格** — 从 `style-catalog.md` 加载对应风格的 CSS 变量，覆盖 `:root` 中的默认值
2. **注入数据** — 将分析结果序列化为 `dashboardData` JSON
3. **构建 KPI 行** — 遍历 `kpiDefinitions`，用 3.1 模板生成 HTML
4. **构建主图表** — 取 `charts` 中 `isHero: true` 的图表，填入 hero-chart 区域
5. **构建支撑图表** — 取剩余图表，用 3.2 模板生成 HTML，放入 chart-grid
6. **构建主题段落** — 遍历 `themes`，用 3.3 模板生成 HTML，按顺序插入
7. **构建行动建议** — 遍历 `actions`，用 3.4 模板生成 HTML
8. **注入图表渲染函数** — 从 `chart-patterns.md` 加载对应图表类型的 SVG 渲染函数
9. **注入筛选和交互 JS** — 加载本文件第 4 节的所有 JS 函数
10. **替换 Body 占位符** — 将 Header、Footer 的文本占位符替换为实际值
11. **输出最终 HTML** — 写入 `dashboard.html`，打印路径提示用户

**硬性规则：**
- 生成的 HTML 文件必须 **完全自包含**：零外部 CSS/JS/字体请求
- 所有 SVG 图表内联，不使用 `<img>` 引用
- 文件大小上限 2MB（超出时减少数据精度或合并小分类）
- 必须能在 Chrome、Safari、Firefox 的最新版本中正确渲染
- 必须能通过 Ctrl/Cmd + P 输出可读的 PDF
