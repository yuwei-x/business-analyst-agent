# BEAM 首次配置指南

## 目录
1. [Resend 邮件服务配置](#1-resend-邮件服务配置)
2. [Vercel 部署服务配置](#2-vercel-部署服务配置)
3. [环境变量文件](#3-环境变量文件)
4. [LaunchAgent 定时任务](#4-launchagent-定时任务)
5. [常见问题排查](#5-常见问题排查)

---

## 1. Resend 邮件服务配置

### 注册与获取 API Key
1. 访问 [resend.com](https://resend.com) 注册账号
2. 进入 Dashboard → API Keys → Create API Key
3. 权限选择 `Sending access`，限定域名（或 Full access 用于测试）
4. 复制生成的 `re_` 开头的 Key，妥善保存

### 发件域名验证
Resend 要求发件地址所在域名完成 DNS 验证（DKIM + SPF），否则 API 返回 422 错误。

**快速测试**：Resend 提供 `onboarding@resend.dev` 作为免费测试发件地址，无需域名验证，但每天限额 100 封。

**正式使用**：
1. Dashboard → Domains → Add Domain
2. 添加域名后，按指引在 DNS 中添加 3 条记录（2 条 DKIM + 1 条 SPF）
3. 点击 Verify，等待 DNS 生效（通常几分钟到几小时）
4. 验证成功后，可使用该域名下任意地址作为发件人

### 收件注意
- 首次收件可能进入垃圾邮件文件夹（Outlook/Gmail 均可能）
- 域名验证完成 + SPF/DKIM 正确后，后续邮件会进入正常收件箱
- Resend Dashboard → Emails 可查看发送状态和退信原因

---

## 2. Vercel 部署服务配置

### 获取 Token
1. 访问 [vercel.com](https://vercel.com) 注册/登录
2. 进入 Account Settings → Tokens → Create Token
3. Scope 选择 Full Account，Expiration 建议选 No Expiration
4. 复制 Token 保存

### 首次项目关联（仅一次）
Vercel 部署前需要先关联项目，之后每次部署才能覆盖同一个生产 URL：
```bash
cd "<看板 HTML 所在目录>"
VERCEL_TOKEN=<你的Token> npx vercel link --yes
```

### Node.js 依赖
Vercel CLI 通过 npx 运行，需要 Node.js 环境：
```bash
node --version  # 检查是否已安装
brew install node  # 未安装时通过 Homebrew 安装
```

### 静态托管配置
看板目录下需要 `vercel.json`：
```json
{
  "version": 2,
  "builds": [{ "src": "dashboard.html", "use": "@vercel/static" }],
  "routes": [{ "src": "/(.*)", "dest": "/dashboard.html" }]
}
```

---

## 3. 环境变量文件

创建 `~/.env_dashboard`，权限设为 600（仅本人可读写）：

```bash
cat > ~/.env_dashboard << 'EOF'
RESEND_API_KEY=re_你的API密钥
RESEND_FROM=noreply@你的域名.com
VERCEL_TOKEN=你的Vercel_Token
EOF
chmod 600 ~/.env_dashboard
```

**安全提醒**：
- 此文件不要提交到 git（已在 .gitignore 排除 `~` 路径）
- API Key 等同密码，泄露后立即在对应平台重新生成
- 演示录屏时注意遮挡

---

## 4. LaunchAgent 定时任务

### 生成 plist
使用 `assets/launchagent-template.plist` 模板，替换占位符后保存到：
```
~/Library/LaunchAgents/com.yuwei.<项目标识>.plist
```

### 安装与管理
```bash
# 加载（安装）
launchctl load ~/Library/LaunchAgents/com.yuwei.<项目标识>.plist

# 立即触发一次（不等到 8:00）
launchctl start com.yuwei.<项目标识>

# 查看是否已加载
launchctl list | grep <项目标识>

# 卸载
launchctl unload ~/Library/LaunchAgents/com.yuwei.<项目标识>.plist
```

### LaunchAgent 行为说明
- `StartCalendarInterval` 使用本地时区（Mac 系统设置为 Asia/Shanghai 即北京时间）
- Mac 合盖睡眠时不会触发，唤醒后如果错过了触发时间会立即补执行一次
- `RunAtLoad: false` 表示加载时不自动执行，仅在到达指定时间时执行
- 日志输出到项目目录下的 `logs/` 文件夹

---

## 5. 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Resend 返回 422 | 发件域名未验证 DKIM/SPF | 完成 DNS 验证，或先用 `onboarding@resend.dev` 测试 |
| Resend 返回 401 | API Key 无效或过期 | 重新创建 API Key |
| 邮件进入垃圾箱 | 新域名信誉度低 | 持续发送正常邮件积累信誉，或手动标记「非垃圾邮件」|
| Vercel 部署失败 | Token 过期或项目未关联 | 重新 `vercel link`，检查 Token |
| LaunchAgent 未触发 | plist 未加载或路径错误 | `launchctl list` 检查，确认 plist 中路径使用绝对路径 |
| Python 找不到 | LaunchAgent 的 PATH 不含 Homebrew | 确认 plist 中 EnvironmentVariables.PATH 包含 `/opt/homebrew/bin` |
| 数据文件未更新 | Excel 文件还是旧的 | 自动化仅在数据文件已手动更新时才有新内容 |
