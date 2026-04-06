# LENS Style Catalog — 完整视觉风格参考

> **用途**：LENS 生成仪表盘时，读取本文件获取所选风格的 CSS 变量定义。
> 所有风格共享统一的 CSS 变量命名规范，切换风格只需替换 `:root` 块。
> **默认风格**：Swiss/NZZ（风格 5）

---

## 通用图表色板（全局默认）

以下色板适用于所有风格，除非风格内部显式覆盖：

```css
/* 通用图表色板 */
--chart-1: #E17055; /* coral 珊瑚 */
--chart-2: #45B7AA; /* mint 薄荷 */
--chart-3: #5B8C5A; /* olive 橄榄 */
--chart-4: #FFD700; /* gold 金 */
--chart-5: #9B7EDE; /* lavender 薰衣草 */

/* 语义色 */
--kpi-down:  #E63946; /* negative / danger */
--kpi-up:    #2A9D8F; /* positive / growth */
--warning:   #F4A261; /* warning */
--grid-ref:  #CCCCCC; /* grid / reference lines */
```

---

## CSS 变量命名规范

每个风格的 `:root` 块严格遵循以下变量名：

| 类别 | 变量名 | 说明 |
|------|--------|------|
| 背景 | `--bg-primary` | 页面主背景 |
| 背景 | `--bg-secondary` | 次级背景（分区/侧栏） |
| 背景 | `--bg-card` | 卡片/面板背景 |
| 文字 | `--text-primary` | 主文本色 |
| 文字 | `--text-secondary` | 副文本色 |
| 文字 | `--text-muted` | 弱化文本/标注 |
| 强调 | `--accent` | 主强调色 |
| 强调 | `--accent-light` | 轻量强调色（悬停/背景） |
| 图表 | `--chart-1` ~ `--chart-5` | 图表系列色 |
| 语义 | `--kpi-up` | 正面/增长 |
| 语义 | `--kpi-down` | 负面/下降 |
| 语义 | `--kpi-flat` | 持平/中性 |
| 语义 | `--warning` | 警告 |
| 字体 | `--font-display` | 标题/展示字体 |
| 字体 | `--font-body` | 正文字体 |
| 字体 | `--font-mono` | 等宽字体 |
| 字号 | `--font-size-kpi` | KPI 大数字 |
| 字号 | `--font-size-title` | 区块标题 |
| 字号 | `--font-size-body` | 正文 |
| 字号 | `--font-size-caption` | 说明文字/脚注 |
| 结构 | `--border` | 边框定义 |
| 结构 | `--border-radius` | 圆角 |
| 结构 | `--shadow` | 默认阴影 |
| 结构 | `--shadow-hover` | 悬停阴影 |

---

## 风格 1：Financial Times — 三文鱼粉温暖权威

**English Name**: Financial Times

**适用场景**：财务分析、投资者报告、营收归因拆解、季度财务回顾

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FFF1E5;
  --bg-secondary: #F2DFCE;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #33302E;
  --text-secondary: #66605C;
  --text-muted: #9E9893;

  /* Accent */
  --accent: #0F5499;
  --accent-light: #CCE0F5;

  /* Charts */
  --chart-1: #0F5499;
  --chart-2: #990F3D;
  --chart-3: #FF7FAA;
  --chart-4: #00A0AF;
  --chart-5: #593380;

  /* Semantic */
  --kpi-up: #0A7B3E;
  --kpi-down: #CC0000;
  --kpi-flat: #9E9893;
  --warning: #F2A900;

  /* Typography */
  --font-display: 'Georgia', 'Times New Roman', serif;
  --font-body: 'Segoe UI', system-ui, -apple-system, sans-serif;
  --font-mono: 'Consolas', 'Menlo', monospace;
  --font-size-kpi: 36px;
  --font-size-title: 20px;
  --font-size-body: 15px;
  --font-size-caption: 12px;

  /* Structure */
  --border: 1px solid #E0D5CA;
  --border-radius: 2px;
  --shadow: 0 1px 3px rgba(51, 48, 46, 0.08);
  --shadow-hover: 0 2px 8px rgba(51, 48, 46, 0.12);
}
```

### 核心视觉规则

- **标志性蓝色顶线**：每个仪表盘顶部添加 `border-top: 4px solid #0F5499`，这是 FT 最强的视觉锚点。
- **温暖底色叙事感**：三文鱼粉底色（`#FFF1E5`）传递"深度阅读"的信号，卡片使用白色浮出。
- **Georgia 标题 + 无衬线正文**：标题用 Georgia 建立权威叙事感，数据标签和正文用 Segoe UI 保持清晰可读。

### 图表配置覆盖

```
- 网格线：#E0D5CA（暖灰，与底色协调）
- 坐标轴文字：#66605C
- 图表背景：transparent（继承三文鱼粉底色）
- 工具提示：白底 + 1px #E0D5CA 边框，无阴影
- 折线图线宽：2.5px
```

---

## 风格 2：McKinsey — 深蓝结构化说服力

**English Name**: McKinsey

**适用场景**：战略分析、咨询类演示、管理层汇报、竞争格局分析

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F4F6F9;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1A1A2E;
  --text-secondary: #4A4A68;
  --text-muted: #8C8CA1;

  /* Accent */
  --accent: #003366;
  --accent-light: #E8EFF7;

  /* Charts */
  --chart-1: #003366;
  --chart-2: #1A73E8;
  --chart-3: #5CA0D3;
  --chart-4: #A3C4E7;
  --chart-5: #162D50;

  /* Semantic */
  --kpi-up: #0D7C3F;
  --kpi-down: #D32F2F;
  --kpi-flat: #8C8CA1;
  --warning: #F9A825;

  /* Typography */
  --font-display: 'Arial', 'Helvetica Neue', sans-serif;
  --font-body: 'Arial', 'Helvetica Neue', sans-serif;
  --font-mono: 'Consolas', 'Menlo', monospace;
  --font-size-kpi: 40px;
  --font-size-title: 18px;
  --font-size-body: 14px;
  --font-size-caption: 11px;

  /* Structure */
  --border: 1px solid #D9E0EA;
  --border-radius: 2px;
  --shadow: 0 1px 4px rgba(0, 51, 102, 0.06);
  --shadow-hover: 0 3px 10px rgba(0, 51, 102, 0.10);
}
```

### 核心视觉规则

- **Exhibit 编号系统**：每个图表区域左上角标注 `Exhibit 1`、`Exhibit 2`... 使用 11px 大写字母，色值 `#8C8CA1`，增加咨询报告的仪式感。
- **核心洞察框**：每个图表下方可附一个要点框——白底 + `border-left: 4px solid #003366` + `padding: 12px 16px`，写一句结论（如"核心发现：..."）。
- **蓝色渐变层级**：图表色从深蓝到浅蓝形成一致的单色调渐变，避免多色跳跃，强化结构化感知。

### 图表配置覆盖

```
- 网格线：#E8EFF7（极浅蓝灰）
- 坐标轴文字：#4A4A68
- 柱状图间距：barPercentage 0.6（留白多，呼吸感强）
- 图例位置：图表正下方，水平居中
- 图表标题：加粗 + 左对齐，14px
```

---

## 风格 3：The Economist — 红线点睛杂志感

**English Name**: The Economist

**适用场景**：行业洞察、社论风格分析、带观点的数据叙事、市场趋势评论

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F7F7F7;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1D1D1B;
  --text-secondary: #525252;
  --text-muted: #8B8B8B;

  /* Accent */
  --accent: #E3120B;
  --accent-light: #FDECEA;

  /* Charts */
  --chart-1: #E3120B;
  --chart-2: #0D5C91;
  --chart-3: #3F9C8E;
  --chart-4: #C75B12;
  --chart-5: #6B3FA0;

  /* Semantic */
  --kpi-up: #006837;
  --kpi-down: #E3120B;
  --kpi-flat: #8B8B8B;
  --warning: #DC8605;

  /* Typography */
  --font-display: 'Georgia', 'Times New Roman', serif;
  --font-body: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
  --font-mono: 'Menlo', 'Consolas', monospace;
  --font-size-kpi: 38px;
  --font-size-title: 22px;
  --font-size-body: 15px;
  --font-size-caption: 11px;

  /* Structure */
  --border: 1px solid #DCDCDC;
  --border-radius: 0px;
  --shadow: none;
  --shadow-hover: none;
}
```

### 核心视觉规则

- **6px 红色顶线签名**：仪表盘顶部 `border-top: 6px solid #E3120B`，这是经济学人最核心的视觉识别，比 FT 的蓝线更粗更醒目。
- **零圆角 + 零阴影**：所有元素使用 `border-radius: 0`，杂志排版风格拒绝"app 感"，干净利落。
- **观点型标题**：标题不是中性描述（如"Q3 营收趋势"），而是带立场的判断（如"增长引擎熄火：Q3 营收增速跌至三年最低"）。Georgia 斜体用于副标题/注释。

### 图表配置覆盖

```
- 网格线：#DCDCDC（标准灰，极细 0.5px）
- 坐标轴线：#1D1D1B（黑色底轴线，1px）
- 图表区域顶部：添加 2px #E3120B 红线分隔
- 折线图：圆点标记 pointRadius: 3
- 注释/来源文字：右下角，11px 斜体灰色
```

---

## 风格 4：Goldman Sachs — 投行表格信息密度

**English Name**: Goldman Sachs

**适用场景**：财务建模、详细数值分析、估值对比、投资备忘录

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #F8F9FA;
  --bg-secondary: #EBEDF0;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1C2028;
  --text-secondary: #4B5563;
  --text-muted: #8993A4;

  /* Accent */
  --accent: #00338D;
  --accent-light: #E3EBF7;

  /* Charts */
  --chart-1: #00338D;
  --chart-2: #D4AF37;
  --chart-3: #5B7FA5;
  --chart-4: #8B6914;
  --chart-5: #2C3E6B;

  /* Semantic */
  --kpi-up: #056B3A;
  --kpi-down: #C62828;
  --kpi-flat: #8993A4;
  --warning: #E6930A;

  /* Typography */
  --font-display: 'Arial', 'Helvetica', sans-serif;
  --font-body: 'Arial', 'Helvetica', sans-serif;
  --font-mono: 'Consolas', 'Monaco', monospace;
  --font-size-kpi: 32px;
  --font-size-title: 16px;
  --font-size-body: 13px;
  --font-size-caption: 10px;

  /* Structure */
  --border: 1px solid #D1D5DB;
  --border-radius: 0px;
  --shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-hover: 0 2px 6px rgba(0, 0, 0, 0.08);
}
```

### 核心视觉规则

- **表格为王**：这个风格的核心是信息密度极高的表格。使用斑马纹（`#F8F9FA` / `#FFFFFF` 交替），行高压缩至 28-32px，表头深蓝底白字（`#00338D`）。
- **评级徽章系统**：使用内联小圆角标签（`border-radius: 3px`，`padding: 2px 8px`，`font-size: 10px`）标注评级/状态，如 "Buy"（绿底白字）、"Sell"（红底白字）、"Hold"（灰底白字）。
- **金色点缀**：`#D4AF37` 仅用于高亮关键数字或分隔线，传递投行的精密和克制。

### 图表配置覆盖

```
- 字号全局缩小 1-2px（高密度排版）
- 表格单元格 padding: 6px 10px
- 数字右对齐，负数红色，正数深蓝
- 图表高度压缩（max-height: 200px），为表格让出空间
- 工具提示：深色背景（#1C2028），白字，紧凑
```

---

## 风格 5：Swiss / NZZ — 瑞士极简数据纯粹 [DEFAULT]

**English Name**: Swiss / NZZ

**适用场景**：通用专业场景、数据展览、产品仪表盘、任何需要"让数据自己说话"的场景

> 这是 LENS 的默认风格。当用户未指定风格时，使用此风格。

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F5F5F5;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #000000;
  --text-secondary: #333333;
  --text-muted: #767676;

  /* Accent */
  --accent: #FF0000;
  --accent-light: #FFE5E5;

  /* Charts — 严格限色：黑/灰/红 */
  --chart-1: #000000;
  --chart-2: #767676;
  --chart-3: #FF0000;
  --chart-4: #AAAAAA;
  --chart-5: #333333;

  /* Semantic */
  --kpi-up: #000000;
  --kpi-down: #FF0000;
  --kpi-flat: #767676;
  --warning: #FF0000;

  /* Typography */
  --font-display: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
  --font-body: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
  --font-mono: 'Menlo', 'Consolas', monospace;
  --font-size-kpi: 72px;
  --font-size-title: 28px;
  --font-size-body: 15px;
  --font-size-caption: 11px;

  /* Structure */
  --border: 1px solid #000000;
  --border-radius: 0px;
  --shadow: none;
  --shadow-hover: none;
}
```

### 核心视觉规则

- **仅黑、白、灰、红四色**：零彩色、零渐变、零装饰阴影。红色（`#FF0000`）仅用于标注异常/危险/关键强调，使用频率 < 5%。
- **极端字号对比**：KPI 数字 72px vs 标注文字 11px，通过字号落差创造视觉层级，而非颜色或装饰。标题 28px，中间无过渡字号。
- **Helvetica 唯一**：不混用任何其他字体。轻重量（300-700）的变化替代字体种类的变化。

### 图表配置覆盖

```
- 网格线：#E5E5E5（极浅灰，几乎隐形）
- 坐标轴线：#000000（纯黑，1px）
- 折线图线宽：2px，无圆点（pointRadius: 0）
- 柱状图：纯黑填充，无边框
- 高亮数据点：红色（唯一允许用红色的场景）
- 零边框圆角（borderRadius: 0 everywhere）
```

---

## 风格 6：Stamen Design — 数据诗学

**English Name**: Stamen Design

**适用场景**：地理/社会数据可视化、艺术展示、人文类报告、面向设计师群体的演示

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FAF6F1;
  --bg-secondary: #F0EAE0;
  --bg-card: #FFFDF9;

  /* Text */
  --text-primary: #2E2A25;
  --text-secondary: #5C554E;
  --text-muted: #9C9488;

  /* Accent */
  --accent: #C07850;
  --accent-light: #F5E6DB;

  /* Charts */
  --chart-1: #C07850;
  --chart-2: #7A9E7E;
  --chart-3: #2E5266;
  --chart-4: #D4A574;
  --chart-5: #5A7D7C;

  /* Semantic */
  --kpi-up: #4A7C59;
  --kpi-down: #B5493A;
  --kpi-flat: #9C9488;
  --warning: #C99537;

  /* Typography */
  --font-display: 'Georgia', 'Palatino', serif;
  --font-body: 'Georgia', 'Palatino', serif;
  --font-mono: 'Courier New', 'Courier', monospace;
  --font-size-kpi: 42px;
  --font-size-title: 24px;
  --font-size-body: 16px;
  --font-size-caption: 12px;

  /* Structure */
  --border: 1px solid #E0D8CE;
  --border-radius: 12px;
  --shadow: 0 2px 12px rgba(46, 42, 37, 0.06);
  --shadow-hover: 0 4px 20px rgba(46, 42, 37, 0.10);
}
```

### 核心视觉规则

- **羊皮纸质感底色**：`#FAF6F1` 底色传递手工、有机的感觉，卡片用 `#FFFDF9`（几乎白但带暖意）浮出。
- **有机圆角 + 柔和阴影**：`border-radius: 12px`（可在重点区域提至 16px），阴影使用暖色调（`rgba(46, 42, 37, ...)`），避免冷灰阴影。
- **衬线斜体注释**：图表注释和来源文字使用 Georgia italic，12px，模拟手写旁注感。色值 `#9C9488`。

### 图表配置覆盖

```
- 网格线：#E0D8CE（暖灰，与底色融合）
- 坐标轴文字：#5C554E，Georgia 14px
- 折线图：线宽 3px，大圆点（pointRadius: 5），线条末端 round
- 区域图：半透明填充 opacity: 0.15
- 图例：衬线体，斜体
```

---

## 风格 7：Fathom — 科学叙事

**English Name**: Fathom

**适用场景**：研究报告、运营分析、异常检测报告、需要严谨归因的数据叙事

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #F7F8FA;
  --bg-secondary: #ECEEF2;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1B2A3D;
  --text-secondary: #4A5568;
  --text-muted: #8794A7;

  /* Accent */
  --accent: #1B3A5C;
  --accent-light: #E1EAF4;

  /* Charts */
  --chart-1: #1B3A5C;
  --chart-2: #4A7FB5;
  --chart-3: #7BA7CC;
  --chart-4: #A8C4DD;
  --chart-5: #0F2440;

  /* Semantic */
  --kpi-up: #1A7F5A;
  --kpi-down: #C0392B;
  --kpi-flat: #8794A7;
  --warning: #E8724A;

  /* Typography */
  --font-display: 'Helvetica Neue', 'Arial', sans-serif;
  --font-body: 'Helvetica Neue', 'Arial', sans-serif;
  --font-mono: 'SF Mono', 'Menlo', monospace;
  --font-size-kpi: 36px;
  --font-size-title: 18px;
  --font-size-body: 14px;
  --font-size-caption: 11px;

  /* Structure */
  --border: 1px solid #D6DAE2;
  --border-radius: 4px;
  --shadow: 0 1px 4px rgba(27, 58, 92, 0.05);
  --shadow-hover: 0 3px 10px rgba(27, 58, 92, 0.08);
}
```

### 核心视觉规则

- **信号橙仅限真异常**：`#E8724A`（signal orange）是全仪表盘唯一的暖色，严格限定仅用于标注真正的数据异常、偏差超阈值的指标。日常数据一律用蓝灰色系。
- **脚注系统**：图表中使用上标数字（`<sup>1</sup>`）链接到底部脚注区域，写明数据来源、计算口径、采样方法。脚注区域 11px，`#8794A7`。
- **Figure 编号（学术风格）**：每个图表标注"Figure 1"、"Figure 2"...，位于图表左上方，`font-size: 11px`，`font-weight: 600`，`color: #8794A7`，`text-transform: uppercase`，`letter-spacing: 1px`。

### 图表配置覆盖

```
- 网格线：#ECEEF2（冷灰，实验室白板感）
- 主色系：单色蓝渐变（深蓝 → 浅蓝），避免多色
- 异常数据点：#E8724A 实心圆 + 虚线引注
- 置信区间：浅蓝带 opacity: 0.1 填充
- 工具提示：包含数据来源标注
```

---

## 风格 8：Sagmeister & Walsh — 快乐极简

**English Name**: Sagmeister & Walsh

**适用场景**：增长回顾、正面基调报告、创业里程碑、市场营销数据、团队汇报

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FAFAFA;
  --bg-secondary: #F0F0F0;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1A1A1A;
  --text-secondary: #4D4D4D;
  --text-muted: #999999;

  /* Accent — 每个 section 选一种 color burst */
  --accent: #FF6B6B;
  --accent-light: #FFE0E0;

  /* Charts — 色彩爆发色板 */
  --chart-1: #FF6B6B;
  --chart-2: #FFD93D;
  --chart-3: #6BCB77;
  --chart-4: #4D96FF;
  --chart-5: #9B7EDE;

  /* Semantic */
  --kpi-up: #6BCB77;
  --kpi-down: #FF6B6B;
  --kpi-flat: #999999;
  --warning: #FFD93D;

  /* Typography */
  --font-display: 'Helvetica Neue', 'Arial', sans-serif;
  --font-body: 'Helvetica Neue', 'Arial', sans-serif;
  --font-mono: 'SF Mono', 'Menlo', monospace;
  --font-size-kpi: 56px;
  --font-size-title: 22px;
  --font-size-body: 15px;
  --font-size-caption: 12px;

  /* Structure */
  --border: 1px solid #E5E5E5;
  --border-radius: 16px;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  --shadow-hover: 0 6px 24px rgba(0, 0, 0, 0.08);
}
```

### 核心视觉规则

- **90% 黑白灰 + 每区一色爆发**：页面主体严格黑白灰，但每个 section 允许使用一种明亮色彩（coral / yellow / mint / blue 四选一）。色彩爆发仅出现在 KPI 数字和关键图表元素上。
- **超大 KPI 数字**：KPI 数字 48-64px（变量设为 56px），使用该 section 的色彩爆发色。数字本身就是视觉焦点，不需要额外装饰。
- **大圆角 + 柔软阴影**：`border-radius: 16px`，阴影柔和扩散，传递"友好""轻松"的情绪基调。

### 图表配置覆盖

```
- 网格线：#F0F0F0（几乎隐形）
- 柱状图：圆角顶部（borderRadius: 8）
- 每个图表使用单一色彩爆发色 + 灰色对比
- 甜甜圈图优先于饼图（cutout: 65%）
- 动画：入场时数字从 0 滚动到目标值
```

**色彩爆发分配规则**：

| Section 顺序 | 色彩爆发 | 色值 |
|:---:|:---:|:---:|
| 第 1 区 | Coral 珊瑚 | `#FF6B6B` |
| 第 2 区 | Yellow 明黄 | `#FFD93D` |
| 第 3 区 | Mint 薄荷 | `#6BCB77` |
| 第 4 区 | Blue 天蓝 | `#4D96FF` |
| 第 5+ 区 | 循环以上 | — |

---

## 风格 9：Takram — 日式轻量温柔科技感

**English Name**: Takram

**适用场景**：产品分析、设计导向受众、用户体验数据、面向日本/东亚审美的报告

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #F5F2ED;
  --bg-secondary: #ECE8E1;
  --bg-card: #FDFCF9;

  /* Text */
  --text-primary: #2C2C2C;
  --text-secondary: #5A5A5A;
  --text-muted: #9B9B9B;

  /* Accent */
  --accent: #6B8CAE;
  --accent-light: #E4ECF3;

  /* Charts */
  --chart-1: #6B8CAE;
  --chart-2: #7FA87F;
  --chart-3: #B8A9C9;
  --chart-4: #D4B896;
  --chart-5: #8EACAC;

  /* Semantic */
  --kpi-up: #7FA87F;
  --kpi-down: #C47D5A;
  --kpi-flat: #9B9B9B;
  --warning: #C47D5A;

  /* Typography */
  --font-display: 'Helvetica Neue', system-ui, sans-serif;
  --font-body: 'Helvetica Neue', system-ui, sans-serif;
  --font-mono: 'SF Mono', 'Menlo', monospace;
  --font-size-kpi: 40px;
  --font-size-title: 18px;
  --font-size-body: 14px;
  --font-size-caption: 11px;

  /* Structure */
  --border: none;
  --border-radius: 8px;
  --shadow: 0 1px 6px rgba(44, 44, 44, 0.03);
  --shadow-hover: 0 2px 12px rgba(44, 44, 44, 0.06);
}
```

### 核心视觉规则

- **font-weight: 300（轻量优先）**：所有正文和标签使用 300 字重（light），仅标题允许 400-500。这是 Takram 风格最核心的视觉特征——"轻"到几乎消融。
- **零分隔线 + 呼吸留白**：section 之间不使用 `<hr>` 或边框分隔，而是通过 56-64px 的纵向间距（`margin-bottom: 56px`）实现自然分区。`--border: none`。
- **茶红仅限警告**：`#C47D5A`（tea red / 茶红）在整个仪表盘中仅用于 caution/warning 场景，日常数据使用柔蓝（`#6B8CAE`）和草绿（`#7FA87F`）。

### 图表配置覆盖

```
- 网格线：#ECE8E1（暖灰，与底色几乎融合）
- 坐标轴线：隐藏（display: false）
- 折线图线宽：1.5px（轻量感），tension: 0.3（微弧度）
- 图例文字：font-weight 300，11px
- 图表区域上下 padding: 24px
- 所有数字使用 tabular-nums（等宽数字，对齐优雅）
```

---

## 风格 10：Irma Boom — 编辑叙事

**English Name**: Irma Boom

**适用场景**：年度报告、品牌叙事、需要"翻页感"的深度报告、设计师/创意行业受众

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FAF7F4;
  --bg-secondary: #4A3728;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #2A2118;
  --text-secondary: #5E4D3B;
  --text-muted: #A0917F;

  /* Accent */
  --accent: #C75B3A;
  --accent-light: #F5DDD5;

  /* Charts */
  --chart-1: #C75B3A;
  --chart-2: #D4898F;
  --chart-3: #8B7355;
  --chart-4: #4A3728;
  --chart-5: #B8A08E;

  /* Semantic */
  --kpi-up: #5B7F4E;
  --kpi-down: #C75B3A;
  --kpi-flat: #A0917F;
  --warning: #D4A043;

  /* Typography */
  --font-display: 'Georgia', 'Palatino Linotype', serif;
  --font-body: 'Georgia', 'Palatino Linotype', serif;
  --font-mono: 'Courier New', monospace;
  --font-size-kpi: 44px;
  --font-size-title: 26px;
  --font-size-body: 16px;
  --font-size-caption: 11px;

  /* Structure */
  --border: 1px solid #D9CEBF;
  --border-radius: 0px;
  --shadow: none;
  --shadow-hover: 0 2px 8px rgba(42, 33, 24, 0.10);
}
```

### 核心视觉规则

- **不对称布局 + 深色反转区**：仪表盘中有 1-2 个 section 使用深色背景（`#4A3728` dark tea），白色文字（`#FAF7F4`）。这打破单调节奏，创造"翻页"的叙事感。普通 section 用浅底色。
- **Georgia 衬线斜体标题**：标题使用 Georgia italic，传递"作者感"和"编辑策划感"。26px，`font-style: italic`，`letter-spacing: -0.3px`。
- **铁锈色、暮粉色、橄榄棕三主色**：`#C75B3A`（rust）、`#D4898F`（twilight pink）、`#8B7355`（olive brown）组成温暖而有深度的色彩组合，避免冷调。

### 图表配置覆盖

```
- 深色 section 内图表：白色文字、浅色网格线（rgba(255,255,255,0.15)）
- 浅色 section 内图表：标准暗文字
- 柱状图：无边框圆角，相邻柱间距极窄（barPercentage: 0.85）
- 注释文字：Georgia italic 11px，#A0917F
- 图表与文字穿插排列（非传统网格对齐）
```

**深色反转区 CSS 补充**：

```css
.section--inverted {
  background: #4A3728;
  color: #FAF7F4;
  padding: 48px 40px;
}
.section--inverted .text-secondary {
  color: #D9CEBF;
}
.section--inverted .text-muted {
  color: #A0917F;
}
```

---

## 风格 11：Build — 奢侈极简

**English Name**: Build

**适用场景**：董事会演示、高端品牌报告、奢侈品行业数据、需要"安静的高级感"的场景

### 完整 CSS 变量

```css
:root {
  /* Backgrounds */
  --bg-primary: #FAFAF8;
  --bg-secondary: #F2F2EE;
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #1A1A18;
  --text-secondary: #4A4A46;
  --text-muted: #9A9A94;

  /* Accent — 唯一强调色 */
  --accent: #2D5F4A;
  --accent-light: #E0EDE6;

  /* Charts — 深鼠尾草绿单色系 */
  --chart-1: #2D5F4A;
  --chart-2: #5A8A73;
  --chart-3: #87B49C;
  --chart-4: #B4D4C3;
  --chart-5: #1A3D2E;

  /* Semantic */
  --kpi-up: #2D5F4A;
  --kpi-down: #8B3A3A;
  --kpi-flat: #9A9A94;
  --warning: #A07D3A;

  /* Typography */
  --font-display: 'Helvetica Neue', 'Helvetica', sans-serif;
  --font-body: 'Helvetica Neue', 'Helvetica', sans-serif;
  --font-mono: 'SF Mono', 'Menlo', monospace;
  --font-size-kpi: 48px;
  --font-size-title: 16px;
  --font-size-body: 14px;
  --font-size-caption: 10px;

  /* Structure */
  --border: 1px solid #E5E5E0;
  --border-radius: 2px;
  --shadow: none;
  --shadow-hover: 0 1px 4px rgba(0, 0, 0, 0.04);
}
```

### 核心视觉规则

- **70% 留白**：页面内容仅占约 30% 面积，其余全部是呼吸空间。section 间距 80px+，卡片内 padding 40px+。"奢侈就是空间"。
- **font-weight: 200-300（超轻）**：标题 200，正文 300。标签使用 `text-transform: uppercase` + `letter-spacing: 1.5px` + `font-size: 10px` 替代加粗——永远不用 bold。
- **单一强调色**：整个仪表盘只有 `#2D5F4A`（deep sage green）一种彩色，所有图表都是其明暗变体。需要强调时用色值深浅对比，而非引入新色。

### 图表配置覆盖

```
- 网格线：#F2F2EE（与 bg-secondary 同色，近乎隐形）
- 坐标轴线：#E5E5E0（极淡，不抢注意力）
- 坐标轴文字：10px，uppercase，letter-spacing: 1px，#9A9A94
- 折线图线宽：1.5px（纤细），tension: 0.4
- 柱状图：barPercentage: 0.4（极窄柱，大量留白）
- 图例：隐藏或极小化（10px，#9A9A94）
- KPI 数字：font-weight: 200，48px，#2D5F4A
```

**标签样式补充**：

```css
.label-uppercase {
  font-size: 10px;
  font-weight: 300;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #9A9A94;
}
```

---

## 风格速查表

| # | 风格名 | 核心关键词 | 底色 | 主强调色 | 圆角 | 字体 |
|:-:|:------:|:---------:|:----:|:-------:|:----:|:----:|
| 1 | Financial Times | 温暖权威 | `#FFF1E5` | `#0F5499` | 2px | Georgia + Segoe UI |
| 2 | McKinsey | 结构说服 | `#FFFFFF` | `#003366` | 2px | Arial |
| 3 | The Economist | 红线杂志 | `#FFFFFF` | `#E3120B` | 0px | Georgia + Helvetica |
| 4 | Goldman Sachs | 投行密度 | `#F8F9FA` | `#00338D` | 0px | Arial |
| 5 | **Swiss/NZZ** | **极简纯粹** | `#FFFFFF` | `#FF0000` | **0px** | **Helvetica** |
| 6 | Stamen Design | 数据诗学 | `#FAF6F1` | `#C07850` | 12px | Georgia |
| 7 | Fathom | 科学叙事 | `#F7F8FA` | `#1B3A5C` | 4px | Helvetica |
| 8 | Sagmeister & Walsh | 快乐极简 | `#FAFAFA` | `#FF6B6B` | 16px | Helvetica |
| 9 | Takram | 温柔科技 | `#F5F2ED` | `#6B8CAE` | 8px | Helvetica light |
| 10 | Irma Boom | 编辑叙事 | `#FAF7F4` | `#C75B3A` | 0px | Georgia italic |
| 11 | Build | 奢侈极简 | `#FAFAF8` | `#2D5F4A` | 2px | Helvetica ultralight |

---

## 使用说明

### LENS 如何消费本文件

1. 用户指定风格名（中文或英文均可匹配）。
2. LENS 从本文件提取对应风格的 `:root` CSS 变量块，完整插入生成的 HTML `<style>` 标签中。
3. HTML 模板中的所有颜色、字号、圆角、阴影均通过 `var(--xxx)` 引用，无硬编码色值。
4. 切换风格 = 替换 `:root` 块，零模板修改。

### 自定义风格

如需新增风格，复制任一现有风格的 `:root` 块，修改色值和字体，确保所有 24 个 CSS 变量完整定义即可。模板无需任何改动。

### 变量依赖关系

```
--bg-primary     → 页面 body 背景
--bg-secondary   → section 交替背景 / 侧栏
--bg-card        → .card / .panel 背景
--text-primary   → h1, h2, p, td
--text-secondary → h3, .subtitle, .axis-label
--text-muted     → .caption, .footnote, .legend
--accent         → 按钮、链接、活跃状态、关键线条
--accent-light   → 按钮 hover 背景、标签背景
--chart-1~5      → Chart.js / D3 系列色
--kpi-up/down/flat → KPI 箭头和变化值颜色
--warning        → 警告标识、阈值超限
--font-display   → h1, h2, .kpi-value
--font-body      → p, td, .label
--font-mono      → 代码块、精确数值
--font-size-*    → 对应元素字号
--border         → .card, table, .divider 边框
--border-radius  → 全局圆角
--shadow         → .card 默认阴影
--shadow-hover   → .card:hover 阴影
```
