#!/bin/bash
# BEAM — deploy.sh
# 将看板 HTML 部署到 Vercel，返回生产 URL。
#
# 环境变量（必须）：
#   VERCEL_TOKEN — Vercel Access Token
#
# 用法：
#   bash deploy.sh <看板所在目录> [输出文件路径]
#
# 输出：
#   将 Vercel URL 写入 <输出文件路径>（默认 .tmp/vercel_url.txt）
#   部署失败时写入空字符串并 exit(0)（不中断整体流程）

set -euo pipefail

SRC_DIR="${1:?用法: deploy.sh <看板目录> [输出文件]}"
OUTPUT_FILE="${2:-.tmp/vercel_url.txt}"

# 确保输出目录存在
mkdir -p "$(dirname "$OUTPUT_FILE")"

if [ -z "${VERCEL_TOKEN:-}" ]; then
    echo "WARN: 缺少 VERCEL_TOKEN，跳过 Vercel 部署"
    echo "" > "$OUTPUT_FILE"
    exit 0
fi

echo "开始部署看板到 Vercel..."
echo "  源目录: $SRC_DIR"

# 部署并提取 URL
DEPLOY_OUTPUT=$(npx vercel "$SRC_DIR" \
    --token="$VERCEL_TOKEN" \
    --prod \
    --yes \
    --name=data-dashboard \
    2>&1) || {
    echo "WARN: Vercel 部署失败，邮件将不含在线链接"
    echo "  错误输出: $DEPLOY_OUTPUT"
    echo "" > "$OUTPUT_FILE"
    exit 0
}

# 从输出中提取 https:// URL
URL=$(echo "$DEPLOY_OUTPUT" | grep -oE 'https://[^ ]+' | tail -1)

if [ -n "$URL" ]; then
    echo "$URL" > "$OUTPUT_FILE"
    echo "部署成功 → $URL"
else
    echo "WARN: 未从 Vercel 输出中提取到 URL"
    echo "" > "$OUTPUT_FILE"
fi

exit 0
