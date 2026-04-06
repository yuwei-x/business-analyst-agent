#!/bin/bash
# BEAM — refresh_pipeline.sh
# 每日自动化编排脚本。LaunchAgent 或手动触发时执行。
# 串行执行：数据刷新 → KPI 提取 → 看板部署 → 邮件生成 → 邮件发送
#
# 环境变量（从 ~/.env_dashboard 加载）：
#   RESEND_API_KEY, RESEND_FROM, VERCEL_TOKEN
#
# 用法：
#   bash refresh_pipeline.sh
#
# 需要在项目根目录下运行，或由 LaunchAgent 设置 WorkingDirectory

set -uo pipefail

# ── 配置 ──────────────────────────────────────────────────────────────

# 项目根目录（脚本所在目录的上一级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 加载环境变量
ENV_FILE="$HOME/.env_dashboard"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "WARN: 环境变量文件 $ENV_FILE 不存在"
fi

# Python 解释器（优先 uv 管理的，fallback 到系统）
PYTHON=""
for candidate in \
    "$HOME/.local/bin/python3" \
    "/opt/homebrew/bin/python3" \
    "/usr/local/bin/python3" \
    "/usr/bin/python3"; do
    if [ -x "$candidate" ]; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "ERROR: 未找到 Python3 解释器"
    exit 1
fi

# 日志
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run_daily_$(date +%Y-%m-%d).log"

SKILLS_DIR="$PROJECT_DIR/Skills/daily-report/scripts"
TMP_DIR="$PROJECT_DIR/.tmp"
mkdir -p "$TMP_DIR"

# ── 配置项（按项目定制）──────────────────────────────────────────────
# >>> 修改以下变量以适配你的项目 <<<

DATA_FILE="$PROJECT_DIR/data/经营数据.xlsx"        # 数据文件路径
DASHBOARD_DIR="$PROJECT_DIR"                       # 看板 HTML 所在目录（LENS 输出到项目根目录）
RECIPIENT="yuwei.x.2026@outlook.com"                # 收件人邮箱
SUBJECT="经营分析日报 | $(date +%Y-%m-%d)"          # 邮件主题
EMAIL_THEME="swiss"                                  # 邮件主题风格（与 LENS 看板风格对齐）

# ── 工具函数 ──────────────────────────────────────────────────────────

log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

step() {
    local step_name="$1"
    shift
    log "▶ 开始: $step_name"
    local start=$(date +%s)
    if "$@" >> "$LOG_FILE" 2>&1; then
        local end=$(date +%s)
        log "✓ 完成: $step_name ($(( end - start ))s)"
        return 0
    else
        local code=$?
        local end=$(date +%s)
        log "✗ 失败: $step_name (exit $code, $(( end - start ))s)"
        return $code
    fi
}

# ── 执行流水线 ────────────────────────────────────────────────────────

log "═══════════════════════════════════════════"
log "BEAM 每日流水线启动"
log "  项目: $PROJECT_DIR"
log "  数据: $DATA_FILE"
log "═══════════════════════════════════════════"

# Step 1: 检查数据文件
if [ ! -f "$DATA_FILE" ]; then
    log "ERROR: 数据文件不存在: $DATA_FILE"
    exit 1
fi

# Step 2: 提取 KPI
if ! step "KPI 提取" "$PYTHON" "$SKILLS_DIR/extract_kpis.py" "$DATA_FILE" --output "$TMP_DIR/kpis.json"; then
    log "ABORT: KPI 提取失败，中止流水线"
    exit 1
fi

# Step 3: 部署看板到 Vercel（失败不中断）
step "Vercel 部署" bash "$SKILLS_DIR/deploy.sh" "$DASHBOARD_DIR" "$TMP_DIR/vercel_url.txt" || true

# Step 4: 生成邮件 HTML
VERCEL_URL=""
if [ -f "$TMP_DIR/vercel_url.txt" ]; then
    VERCEL_URL="$(cat "$TMP_DIR/vercel_url.txt")"
fi

BUILD_CMD=("$PYTHON" "$SKILLS_DIR/build_email.py"
    --kpis "$TMP_DIR/kpis.json"
    --theme "$EMAIL_THEME"
    --output "$TMP_DIR/email.html")
if [ -n "$VERCEL_URL" ]; then
    BUILD_CMD+=(--vercel-url "$VERCEL_URL")
fi

if ! step "邮件生成" "${BUILD_CMD[@]}"; then
    log "ABORT: 邮件生成失败，中止流水线"
    exit 1
fi

# Step 5: 发送邮件
if ! step "邮件发送" "$PYTHON" "$SKILLS_DIR/send_email.py" \
    --to "$RECIPIENT" \
    --subject "$SUBJECT" \
    --html-file "$TMP_DIR/email.html"; then
    log "ERROR: 邮件发送失败（前序步骤已完成，可手动重发）"
    exit 1
fi

log "═══════════════════════════════════════════"
log "BEAM 流水线完成"
log "═══════════════════════════════════════════"
