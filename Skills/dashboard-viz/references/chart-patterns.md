<!--
  LENS Dashboard — 图表渲染函数库
  内联 SVG 图表的 JavaScript 渲染函数，直接嵌入生成的 HTML 仪表盘。
  无 CDN，无外部依赖。颜色使用 CSS 变量（--chart-1~5, --text-primary 等）。
-->

```javascript
// ── SHARED UTILITIES ────────────────────────────────────────

function getCSSVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

function getChartColors(n) {
  const base = [1,2,3,4,5].map(i => getCSSVar(`--chart-${i}`) || `hsl(${i*60},65%,55%)`);
  return Array.from({length: n}, (_, i) => base[i % 5]);
}

function fmt(n, type = 'auto') {
  if (n == null || isNaN(n)) return '—';
  if (type === 'percent') return (n * 100).toFixed(1) + '%';
  if (type === 'currency') {
    if (Math.abs(n) >= 1e9) return '¥' + (n/1e9).toFixed(1) + 'B';
    if (Math.abs(n) >= 1e6) return '¥' + (n/1e6).toFixed(1) + 'M';
    if (Math.abs(n) >= 1e3) return '¥' + (n/1e3).toFixed(1) + 'K';
    return '¥' + n.toFixed(0);
  }
  if (Math.abs(n) >= 1e9) return (n/1e9).toFixed(1) + 'B';
  if (Math.abs(n) >= 1e6) return (n/1e6).toFixed(1) + 'M';
  if (Math.abs(n) >= 1e3) return (n/1e3).toFixed(1) + 'K';
  return n % 1 === 0 ? String(n) : n.toFixed(2);
}

let _tip = null;
function showTooltip(e, html) {
  if (!_tip) {
    _tip = document.createElement('div');
    _tip.style.cssText = 'position:fixed;background:var(--bg-card,#1e1e2e);color:var(--text-primary,#cdd6f4);' +
      'padding:8px 12px;border-radius:8px;font-size:13px;pointer-events:none;z-index:9999;' +
      'box-shadow:0 4px 16px rgba(0,0,0,.4);border:1px solid var(--border,rgba(255,255,255,.1));max-width:220px;line-height:1.5;';
    document.body.appendChild(_tip);
  }
  _tip.innerHTML = html; _tip.style.display = 'block';
  let x = e.clientX + 12, y = e.clientY + 12;
  if (x + 230 > window.innerWidth) x = e.clientX - 230;
  if (y + 80 > window.innerHeight) y = e.clientY - 80;
  _tip.style.left = x + 'px'; _tip.style.top = y + 'px';
}
function hideTooltip() { if (_tip) _tip.style.display = 'none'; }

const NS = 'http://www.w3.org/2000/svg';
function makeSVG(w, h) {
  const s = document.createElementNS(NS, 'svg');
  s.setAttribute('viewBox', `0 0 ${w} ${h}`); s.setAttribute('width', '100%'); s.setAttribute('height', h);
  s.style.overflow = 'visible'; return s;
}
function makeText(x, y, text, o = {}) {
  const e = document.createElementNS(NS, 'text');
  e.setAttribute('x', x); e.setAttribute('y', y); e.textContent = text;
  e.style.fill = o.fill || getCSSVar('--text-secondary') || '#a6adc8';
  e.style.fontSize = o.fontSize || '12px';
  if (o.anchor) e.setAttribute('text-anchor', o.anchor);
  if (o.weight) e.style.fontWeight = o.weight;
  return e;
}
function makeRect(x, y, w, h, fill, o = {}) {
  const e = document.createElementNS(NS, 'rect');
  e.setAttribute('x', x); e.setAttribute('y', y);
  e.setAttribute('width', Math.max(0, w)); e.setAttribute('height', Math.max(0, h));
  e.style.fill = fill;
  if (o.rx) e.setAttribute('rx', o.rx);
  if (o.opacity) e.style.opacity = o.opacity;
  return e;
}
function makeLine(x1, y1, x2, y2, stroke, o = {}) {
  const e = document.createElementNS(NS, 'line');
  e.setAttribute('x1', x1); e.setAttribute('y1', y1); e.setAttribute('x2', x2); e.setAttribute('y2', y2);
  e.style.stroke = stroke; e.style.strokeWidth = o.width || 1;
  if (o.dash) e.style.strokeDasharray = o.dash;
  if (o.opacity) e.style.opacity = o.opacity;
  return e;
}

function _wrap(container, title, insight, svg) {
  // 注意：_wrap() 开头会清空 container（container.innerHTML = ''），
  // 因此 PNG 导出按钮（.chart-save-btn）必须放在外层 .chart-container 的 HTML 模板中
  // （见 layout-templates.md §3.2），而不是在此函数内添加，
  // 否则每次重渲染时按钮会被清除。
  container.innerHTML = ''; container.style.fontFamily = 'inherit';
  if (title) {
    const t = document.createElement('div');
    t.style.cssText = 'font-size:14px;font-weight:600;margin-bottom:8px;color:var(--text-primary,#cdd6f4);';
    t.textContent = title; container.appendChild(t);
  }
  container.appendChild(svg);
  if (insight) {
    const ins = document.createElement('div');
    ins.style.cssText = 'font-size:12px;color:var(--text-secondary,#a6adc8);margin-top:6px;padding:6px 10px;' +
      'background:var(--bg-surface,rgba(255,255,255,.04));border-radius:6px;border-left:3px solid var(--chart-1,#89b4fa);';
    ins.textContent = insight; container.appendChild(ins);
  }
}

function _yScale(vals, h) {
  const max = Math.max(...vals.map(Math.abs), 0) * 1.15 || 1;
  return { max, scale: v => h - (v / max) * h };
}

function _gridLines(max, n = 4) {
  return Array.from({length: n + 1}, (_, i) => max / n * i);
}

function _legend(g, series, colors, yOff) {
  let lx = 0;
  series.forEach((s, i) => {
    const lg = document.createElementNS(NS, 'g');
    lg.setAttribute('transform', `translate(${lx},${yOff})`);
    lg.appendChild(makeRect(0, -8, 10, 10, colors[i], { rx: 2 }));
    lg.appendChild(makeText(14, 2, s.name));
    g.appendChild(lg); lx += s.name.length * 7 + 30;
  });
}


// ── CHART 1: BAR CHART ──────────────────────────────────────

function renderBarChart(container, data, options = {}) {
  const { title, insight, height = 300, color, showValues = true } = options;
  const isMulti = data.series?.length > 0;
  const labels = data.labels || [];
  const series = isMulti ? data.series : [{ name: '', values: data.values }];
  const colors = color ? [color] : getChartColors(series.length);
  const W = 600, pad = { t: 20, r: 20, b: isMulti ? 60 : 44, l: 55 };
  const chartW = W - pad.l - pad.r, chartH = height - pad.t - pad.b;
  const { max, scale } = _yScale(series.flatMap(s => s.values), chartH);
  const svg = makeSVG(W, height);
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${pad.l},${pad.t})`); svg.appendChild(g);

  _gridLines(max).forEach(v => {
    const y = scale(v);
    g.appendChild(makeLine(0, y, chartW, y, getCSSVar('--border') || 'rgba(255,255,255,.08)', { dash: '4 4' }));
    g.appendChild(makeText(-6, y + 4, fmt(v), { anchor: 'end' }));
  });

  const gW = chartW / labels.length, barW = (gW - 12) / series.length;
  labels.forEach((lbl, i) => {
    series.forEach((s, si) => {
      const v = s.values[i] || 0, x = i * gW + 6 + si * barW, y = scale(v), bh = chartH - y;
      const rect = makeRect(x, y, barW - 2, bh, colors[si], { rx: 3 });
      rect.style.cursor = 'pointer';
      rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${lbl}</strong>${series.length > 1 ? '<br>' + s.name : ''}<br>${fmt(v)}`));
      rect.addEventListener('mouseleave', hideTooltip);
      g.appendChild(rect);
      if (showValues && bh > 16)
        g.appendChild(makeText(x + (barW - 2) / 2, y - 4, fmt(v), { anchor: 'middle', fontSize: '11px', fill: getCSSVar('--text-primary') || '#cdd6f4' }));
    });
    g.appendChild(makeText(i * gW + gW / 2, chartH + 18, lbl, { anchor: 'middle' }));
  });

  if (isMulti) _legend(g, series, colors, chartH + 36);
  _wrap(container, title, insight, svg);
}


// ── CHART 2: HORIZONTAL BAR ──────────────────────────────────

function renderHorizontalBar(container, data, options = {}) {
  const { title, insight } = options;
  const pairs = data.labels.map((l, i) => ({ l, v: data.values[i] })).sort((a, b) => b.v - a.v);
  const barH = 28, gap = 8, labW = 120, W = 580, chartW = W - labW - 60;
  const maxV = Math.max(...pairs.map(p => p.v)) || 1;
  const H = pairs.length * (barH + gap) + 20;
  const color = getChartColors(1)[0];
  const svg = makeSVG(W, H);

  pairs.forEach(({ l, v }, i) => {
    const y = i * (barH + gap), bw = (v / maxV) * chartW;
    svg.appendChild(makeText(labW - 8, y + barH / 2 + 5, l, { anchor: 'end' }));
    const rect = makeRect(labW, y, bw, barH, color, { rx: 3 });
    rect.style.cursor = 'pointer';
    rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${l}</strong><br>${fmt(v)}`));
    rect.addEventListener('mouseleave', hideTooltip);
    svg.appendChild(rect);
    svg.appendChild(makeText(labW + bw + 6, y + barH / 2 + 5, fmt(v), { fill: getCSSVar('--text-primary') || '#cdd6f4', fontSize: '12px' }));
  });

  _wrap(container, title, insight, svg);
}


// ── CHART 3: LINE CHART ──────────────────────────────────────

function renderLineChart(container, data, options = {}) {
  const { title, insight, height = 300, fill = false } = options;
  const isMulti = data.series?.length > 0;
  const series = isMulti ? data.series : [{ name: '', values: data.values }];
  const labels = data.labels || [];
  const colors = getChartColors(series.length);
  const W = 600, pad = { t: 20, r: 20, b: isMulti ? 60 : 44, l: 55 };
  const chartW = W - pad.l - pad.r, chartH = height - pad.t - pad.b;
  const { max, scale } = _yScale(series.flatMap(s => s.values), chartH);
  const svg = makeSVG(W, height);
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${pad.l},${pad.t})`); svg.appendChild(g);

  _gridLines(max).forEach(v => {
    const y = scale(v);
    g.appendChild(makeLine(0, y, chartW, y, getCSSVar('--border') || 'rgba(255,255,255,.08)', { dash: '4 4' }));
    g.appendChild(makeText(-6, y + 4, fmt(v), { anchor: 'end' }));
  });

  const xStep = labels.length > 1 ? chartW / (labels.length - 1) : chartW;
  series.forEach((s, si) => {
    const pts = s.values.map((v, i) => ({ x: i * xStep, y: scale(v), v }));
    const pathD = pts.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' ');
    if (fill) {
      const area = document.createElementNS(NS, 'path');
      area.setAttribute('d', pathD + ` L${pts[pts.length-1].x},${chartH} L0,${chartH} Z`);
      area.style.fill = colors[si]; area.style.opacity = '0.15'; g.appendChild(area);
    }
    const path = document.createElementNS(NS, 'path');
    path.setAttribute('d', pathD); path.style.fill = 'none'; path.style.stroke = colors[si];
    path.style.strokeWidth = '2.5'; path.style.strokeLinecap = 'round'; g.appendChild(path);

    pts.forEach((p, i) => {
      const dot = document.createElementNS(NS, 'circle');
      dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y); dot.setAttribute('r', 4);
      dot.style.fill = colors[si]; dot.style.stroke = getCSSVar('--bg-card') || '#1e1e2e'; dot.style.strokeWidth = '2';
      dot.style.cursor = 'pointer';
      dot.addEventListener('mousemove', e => showTooltip(e, `<strong>${labels[i] || i}</strong>${series.length > 1 ? '<br>' + s.name : ''}<br>${fmt(p.v)}`));
      dot.addEventListener('mouseleave', hideTooltip);
      g.appendChild(dot);
    });
  });

  labels.forEach((lbl, i) => g.appendChild(makeText(i * xStep, chartH + 18, lbl, { anchor: 'middle' })));
  if (isMulti) {
    let lx = 0;
    series.forEach((s, si) => {
      const lg = document.createElementNS(NS, 'g'); lg.setAttribute('transform', `translate(${lx},${chartH + 34})`);
      lg.appendChild(makeLine(0, -3, 16, -3, colors[si], { width: 3 }));
      lg.appendChild(makeText(20, 2, s.name)); g.appendChild(lg); lx += s.name.length * 7 + 36;
    });
  }
  _wrap(container, title, insight, svg);
}


// ── CHART 4: PIE / DONUT ─────────────────────────────────────

function renderPieChart(container, data, options = {}) {
  const { title, insight, donut = false, height = 300 } = options;
  let items = data.labels.map((l, i) => ({ l, v: data.values[i] }));
  const tot = items.reduce((s, x) => s + x.v, 0) || 1;
  const small = items.filter(x => x.v / tot < 0.03);
  items = items.filter(x => x.v / tot >= 0.03);
  if (small.length) items.push({ l: 'Other', v: small.reduce((s, x) => s + x.v, 0) });
  if (items.length > 5) items = [...items.slice(0, 5), { l: 'Other', v: items.slice(5).reduce((s, x) => s + x.v, 0) }];

  const colors = getChartColors(items.length);
  const W = 400, r = 110, cx = W / 2, cy = r + 20, legH = items.length * 22 + 10;
  const svgH = cy + r + legH + 30, ir = donut ? r * 0.55 : 0;
  const svg = makeSVG(W, svgH);
  let angle = -Math.PI / 2;
  const total = items.reduce((s, x) => s + x.v, 0) || 1;

  items.forEach(({ l, v }, i) => {
    const slice = (v / total) * 2 * Math.PI, large = slice > Math.PI ? 1 : 0;
    const [x1, y1] = [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
    const [x2, y2] = [cx + r * Math.cos(angle + slice), cy + r * Math.sin(angle + slice)];
    const [ix1, iy1] = [cx + ir * Math.cos(angle), cy + ir * Math.sin(angle)];
    const [ix2, iy2] = [cx + ir * Math.cos(angle + slice), cy + ir * Math.sin(angle + slice)];
    const d = donut
      ? `M${ix1},${iy1} L${x1},${y1} A${r},${r} 0 ${large} 1 ${x2},${y2} L${ix2},${iy2} A${ir},${ir} 0 ${large} 0 ${ix1},${iy1} Z`
      : `M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${large} 1 ${x2},${y2} Z`;
    const path = document.createElementNS(NS, 'path');
    path.setAttribute('d', d); path.style.fill = colors[i]; path.style.cursor = 'pointer';
    path.addEventListener('mousemove', e => showTooltip(e, `<strong>${l}</strong><br>${fmt(v)} (${(v/total*100).toFixed(1)}%)`));
    path.addEventListener('mouseleave', hideTooltip);
    svg.appendChild(path);
    if (slice > 0.3) {
      const mid = angle + slice / 2, lr = donut ? (r + ir) / 2 : r * 0.65;
      svg.appendChild(makeText(cx + lr * Math.cos(mid), cy + lr * Math.sin(mid) + 4,
        (v / total * 100).toFixed(0) + '%', { anchor: 'middle', fill: '#fff', fontSize: '11px', weight: '600' }));
    }
    angle += slice;
  });

  items.forEach(({ l, v }, i) => {
    const ly = cy + r + 20 + i * 22;
    svg.appendChild(makeRect(W / 2 - 80, ly - 10, 12, 12, colors[i], { rx: 2 }));
    svg.appendChild(makeText(W / 2 - 62, ly + 1, `${l} — ${fmt(v)}`));
  });

  _wrap(container, title, insight, svg);
}


// ── CHART 5: STACKED BAR ─────────────────────────────────────

function renderStackedBar(container, data, options = {}) {
  const { title, insight, height = 300, mode = 'absolute' } = options;
  const { labels, series } = data;
  const colors = getChartColors(series.length);
  const W = 600, pad = { t: 20, r: 20, b: 60, l: 55 };
  const chartW = W - pad.l - pad.r, chartH = height - pad.t - pad.b;
  const isPct = mode === 'percent';
  const totals = labels.map((_, i) => series.reduce((s, sr) => s + (sr.values[i] || 0), 0));
  const maxVal = isPct ? 1 : Math.max(...totals) * 1.1 || 1;
  const colW = chartW / labels.length, barW = colW * 0.7, barOff = colW * 0.15;
  const svg = makeSVG(W, height);
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${pad.l},${pad.t})`); svg.appendChild(g);

  _gridLines(isPct ? 1 : maxVal).forEach(v => {
    const y = chartH - (v / maxVal) * chartH;
    g.appendChild(makeLine(0, y, chartW, y, getCSSVar('--border') || 'rgba(255,255,255,.08)', { dash: '4 4' }));
    g.appendChild(makeText(-6, y + 4, isPct ? fmt(v, 'percent') : fmt(v), { anchor: 'end' }));
  });

  labels.forEach((lbl, i) => {
    const tot = totals[i] || 1; let yOff = chartH;
    series.forEach((s, si) => {
      const raw = s.values[i] || 0, norm = isPct ? raw / tot : raw;
      const bh = (norm / maxVal) * chartH; yOff -= bh;
      const rect = makeRect(i * colW + barOff, yOff, barW, bh, colors[si], { rx: 2 });
      rect.style.cursor = 'pointer';
      rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${lbl}</strong><br>${s.name}: ${isPct ? fmt(norm, 'percent') : fmt(raw)}`));
      rect.addEventListener('mouseleave', hideTooltip);
      g.appendChild(rect);
      if (bh > 18)
        g.appendChild(makeText(i * colW + barOff + barW / 2, yOff + bh / 2 + 4,
          isPct ? fmt(norm, 'percent') : fmt(raw), { anchor: 'middle', fill: '#fff', fontSize: '11px' }));
    });
    g.appendChild(makeText(i * colW + colW / 2, chartH + 18, lbl, { anchor: 'middle' }));
  });

  _legend(g, series, colors, chartH + 36);
  _wrap(container, title, insight, svg);
}


// ── CHART 6: WATERFALL ───────────────────────────────────────

function renderWaterfall(container, data, options = {}) {
  const { title, insight, height = 300 } = options;
  const { labels, values, isTotal = [] } = data;
  let running = 0;
  const bars = values.map((v, i) => {
    if (isTotal[i]) return { start: 0, end: running + v, isTotal: true, v };
    const b = { start: running, end: running + v, v }; running += v; return b;
  });
  const allV = bars.flatMap(b => [b.start, b.end]);
  const minV = Math.min(0, ...allV), maxV = Math.max(...allV);
  const range = (maxV - minV) * 1.15 || 1;
  const W = 600, pad = { t: 20, r: 20, b: 44, l: 60 };
  const chartW = W - pad.l - pad.r, chartH = height - pad.t - pad.b;
  const sy = v => chartH - ((v - minV) / range) * chartH;
  const colW = chartW / labels.length, barW = colW * 0.6;
  const colorPos = getCSSVar('--chart-3') || '#a6e3a1';
  const colorNeg = getCSSVar('--chart-5') || '#f38ba8';
  const colorTot = getCSSVar('--text-secondary') || '#6c7086';
  const svg = makeSVG(W, height);
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${pad.l},${pad.t})`); svg.appendChild(g);
  g.appendChild(makeLine(0, sy(0), chartW, sy(0), getCSSVar('--text-secondary') || '#a6adc8', { opacity: 0.3 }));

  bars.forEach((b, i) => {
    const x = i * colW + colW * 0.2, y = sy(Math.max(b.start, b.end)), bh = Math.abs(sy(b.start) - sy(b.end)) || 2;
    const fill = b.isTotal ? colorTot : b.v >= 0 ? colorPos : colorNeg;
    const rect = makeRect(x, y, barW, bh, fill, { rx: 3 });
    rect.style.cursor = 'pointer';
    rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${labels[i]}</strong><br>${fmt(b.v)}`));
    rect.addEventListener('mouseleave', hideTooltip);
    g.appendChild(rect);
    g.appendChild(makeText(x + barW / 2, b.v >= 0 ? y - 5 : y + bh + 14, fmt(b.v),
      { anchor: 'middle', fill: getCSSVar('--text-primary') || '#cdd6f4', fontSize: '11px' }));
    if (i < bars.length - 1 && !b.isTotal)
      g.appendChild(makeLine(x + barW, sy(b.end), (i + 1) * colW + colW * 0.2, sy(b.end),
        getCSSVar('--border') || 'rgba(255,255,255,.2)', { dash: '3 3' }));
    g.appendChild(makeText(i * colW + colW / 2, chartH + 18, labels[i], { anchor: 'middle' }));
  });

  _wrap(container, title, insight, svg);
}


// ── CHART 7: FUNNEL ──────────────────────────────────────────

function renderFunnel(container, data, options = {}) {
  const { title, insight, height = 300 } = options;
  const stages = data.stages || [];
  const n = stages.length, stageH = Math.min((height - 40) / n, 60);
  const W = 500, maxV = stages[0]?.value || 1;
  const colors = getChartColors(n);
  const svg = makeSVG(W, n * stageH + 40);

  stages.forEach((s, i) => {
    const bw = (s.value / maxV) * (W - 150), x = (W - 150 - bw) / 2 + 10, y = 20 + i * stageH;
    const rect = makeRect(x, y + 2, bw, stageH - 4, colors[i], { rx: 4 });
    rect.style.cursor = 'pointer';
    rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${s.name}</strong><br>${fmt(s.value)}`));
    rect.addEventListener('mouseleave', hideTooltip);
    svg.appendChild(rect);
    svg.appendChild(makeText(x - 6, y + stageH / 2 + 5, s.name, { anchor: 'end', fill: getCSSVar('--text-primary') || '#cdd6f4' }));
    svg.appendChild(makeText(x + bw + 8, y + stageH / 2 + 5, fmt(s.value), { fontSize: '11px' }));
    if (i > 0) {
      const drop = ((stages[i-1].value - s.value) / stages[i-1].value * 100).toFixed(0);
      svg.appendChild(makeText(W - 8, y + stageH / 2 + 5, `-${drop}%`,
        { anchor: 'end', fill: getCSSVar('--chart-5') || '#f38ba8', fontSize: '11px' }));
    }
  });

  _wrap(container, title, insight, svg);
}


// ── CHART 8: SCATTER ─────────────────────────────────────────

function renderScatter(container, data, options = {}) {
  const { title, insight, height = 300, xLabel = '', yLabel = '', quadrants = false } = options;
  const points = data.points || [];
  const W = 580, pad = { t: 20, r: 20, b: 50, l: 60 };
  const chartW = W - pad.l - pad.r, chartH = height - pad.t - pad.b;
  const xs = points.map(p => p.x), ys = points.map(p => p.y);
  const [xMin, xMax] = [Math.min(...xs), Math.max(...xs)];
  const [yMin, yMax] = [Math.min(0, ...ys), Math.max(...ys)];
  const sx = v => (v - xMin) / (xMax - xMin || 1) * chartW;
  const sy = v => chartH - (v - yMin) / (yMax - yMin || 1) * chartH;
  const color = getChartColors(1)[0];
  const svg = makeSVG(W, height);
  const g = document.createElementNS(NS, 'g');
  g.setAttribute('transform', `translate(${pad.l},${pad.t})`); svg.appendChild(g);

  g.appendChild(makeLine(0, chartH, chartW, chartH, getCSSVar('--border') || 'rgba(255,255,255,.2)'));
  g.appendChild(makeLine(0, 0, 0, chartH, getCSSVar('--border') || 'rgba(255,255,255,.2)'));

  if (quadrants) {
    const mx = sx((xMin + xMax) / 2), my = sy((yMin + yMax) / 2);
    g.appendChild(makeLine(mx, 0, mx, chartH, getCSSVar('--border') || 'rgba(255,255,255,.15)', { dash: '4 4' }));
    g.appendChild(makeLine(0, my, chartW, my, getCSSVar('--border') || 'rgba(255,255,255,.15)', { dash: '4 4' }));
  }

  if (points.length > 1) {
    const n = points.length, mx = xs.reduce((a,b) => a+b,0)/n, my = ys.reduce((a,b) => a+b,0)/n;
    const num = xs.reduce((s,x,i) => s + (x-mx)*(ys[i]-my), 0);
    const den = xs.reduce((s,x) => s + (x-mx)**2, 0);
    if (den) {
      const m = num/den, b = my - m*mx;
      g.appendChild(makeLine(sx(xMin), sy(m*xMin+b), sx(xMax), sy(m*xMax+b),
        getCSSVar('--chart-2') || '#cba6f7', { width: 1.5, dash: '5 5', opacity: 0.6 }));
    }
  }

  points.forEach(p => {
    const r = p.size ? Math.sqrt(p.size) * 2 : 5;
    const dot = document.createElementNS(NS, 'circle');
    dot.setAttribute('cx', sx(p.x)); dot.setAttribute('cy', sy(p.y)); dot.setAttribute('r', r);
    dot.style.fill = color; dot.style.opacity = '0.8'; dot.style.cursor = 'pointer';
    dot.addEventListener('mousemove', e => showTooltip(e, `<strong>${p.label || ''}</strong><br>x: ${fmt(p.x)}<br>y: ${fmt(p.y)}`));
    dot.addEventListener('mouseleave', hideTooltip);
    g.appendChild(dot);
  });

  if (xLabel) g.appendChild(makeText(chartW / 2, chartH + 38, xLabel, { anchor: 'middle' }));
  if (yLabel) {
    const yl = makeText(-chartH / 2, -44, yLabel, { anchor: 'middle' });
    yl.setAttribute('transform', 'rotate(-90)'); g.appendChild(yl);
  }
  _wrap(container, title, insight, svg);
}


// ── CHART 9: HEATMAP ─────────────────────────────────────────

function renderHeatmap(container, data, options = {}) {
  const { title, insight } = options;
  const { rows, cols, values } = data;
  const cellW = Math.min(70, Math.floor(480 / cols.length)), cellH = 36;
  const labW = 100, labH = 30;
  const W = labW + cols.length * cellW + 20, H = labH + rows.length * cellH + 10;
  const allV = values.flat().filter(v => v != null);
  const [minV, maxV] = [Math.min(...allV), Math.max(...allV)];
  const range = maxV - minV || 1;
  const base = getCSSVar('--chart-1') || '#89b4fa';
  const cellColor = v => `color-mix(in srgb, ${base} ${Math.round((v-minV)/range*90+10)}%, transparent)`;
  const svg = makeSVG(W, H);

  cols.forEach((c, j) => svg.appendChild(makeText(labW + j * cellW + cellW / 2, labH - 6, c, { anchor: 'middle', fontSize: '11px' })));
  rows.forEach((r, i) => {
    svg.appendChild(makeText(labW - 6, labH + i * cellH + cellH / 2 + 5, r, { anchor: 'end', fontSize: '12px' }));
    cols.forEach((c, j) => {
      const v = values[i]?.[j]; if (v == null) return;
      const x = labW + j * cellW, y = labH + i * cellH;
      const rect = makeRect(x + 1, y + 1, cellW - 2, cellH - 2, cellColor(v), { rx: 3 });
      rect.style.cursor = 'pointer';
      rect.addEventListener('mousemove', e => showTooltip(e, `<strong>${r} × ${c}</strong><br>${fmt(v)}`));
      rect.addEventListener('mouseleave', hideTooltip);
      svg.appendChild(rect);
      svg.appendChild(makeText(x + cellW / 2, y + cellH / 2 + 5, fmt(v), { anchor: 'middle', fill: '#fff', fontSize: '11px' }));
    });
  });

  _wrap(container, title, insight, svg);
}


// ── DISPATCHER ───────────────────────────────────────────────

function renderChart(container, spec) {
  const { chart_type, data, options = {} } = spec;
  switch (chart_type) {
    case 'bar':            return renderBarChart(container, data, options);
    case 'horizontal_bar': return renderHorizontalBar(container, data, options);
    case 'line':           return renderLineChart(container, data, options);
    case 'pie':            return renderPieChart(container, data, options);
    case 'donut':          return renderPieChart(container, data, { ...options, donut: true });
    case 'stacked_bar':    return renderStackedBar(container, data, options);
    case 'waterfall':      return renderWaterfall(container, data, options);
    case 'funnel':         return renderFunnel(container, data, options);
    case 'scatter':        return renderScatter(container, data, options);
    case 'heatmap':        return renderHeatmap(container, data, options);
    default:
      container.innerHTML = `<div style="color:var(--chart-5,#f38ba8);padding:12px;">Unknown chart type: ${chart_type}</div>`;
  }
}
```
