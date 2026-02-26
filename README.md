# AnyRouter 签到助手

> 多账号自动签到 · 余额追踪 · 多渠道通知 · 支持 GitHub Actions
> anyrouter自动签到脚本

基于  [millylee/anyrouter-check-in](https://github.com/millylee/anyrouter-check-in) 二次开发，感谢原作者。

---

## 功能介绍

- 支持同时管理多个 AnyRouter 账号，一键签到
- 签到前后自动对比余额，清晰显示奖励变化
- 内置 Telegram、钉钉、企业微信、邮件四种通知渠道
- 支持自定义通知触发时机（总是推送 / 仅失败 / 仅成功）
- 支持自定义通知内容模板
- 同时兼容 AnyRouter 和 AgentRouter，也可自行扩展其他平台
- 配置简单，只需一个 `.env` 文件
- 支持 GitHub Actions 定时自动运行，无需服务器

---

## 运行效果

```
╔══════════════════════════════════════════════════════╗
║   AnyRouter  多账号自动签到                          ║
║   2026-02-26 17:06:35                                ║
╚══════════════════════════════════════════════════════╝

[1/2]  主账号
────────────────────────────────────────────────────────
  状态: ✅ 签到成功  每日签到成功
  User: 43851  Session: sess****5e7d
  余额: $124.8000 → $125.0000  (+0.2000)

[2/2]  备用账号
────────────────────────────────────────────────────────
  状态: 🔁 今日已签  already checked in
  User: 140883  Session: MTc3****4bbc
  余额: $125.0000 → $125.0000

════════════════════════════════════════════════════════
  📊 签到汇总
────────────────────────────────────────────────────────
  总计: 2  成功: 1  已签: 1  失败: 0  跳过: 0
  总余额: $250.0000
════════════════════════════════════════════════════════
```

---

## 目录结构

```
anyrouter-checkin/
├── main.py                        # 程序入口
├── requirements.txt               # 依赖列表
├── .env.example                   # 配置模板（复制为 .env 使用）
├── .github/
│   └── workflows/
│       └── checkin.yml            # GitHub Actions 定时任务
└── src/
    ├── core/
    │   ├── models.py              # 数据模型
    │   ├── providers.py           # 服务商配置
    │   └── checkin_service.py     # 签到核心逻辑
    ├── notif/
    │   ├── template.py            # 通知模板渲染
    │   ├── notification_kit.py    # 通知编排器
    │   └── senders/
    │       ├── telegram.py        # Telegram Bot 通知
    │       ├── dingtalk.py        # 钉钉 Webhook 通知
    │       ├── wecom.py           # 企业微信 Webhook 通知
    │       └── email_sender.py    # SMTP 邮件通知
    └── tools/
        ├── printer.py             # 终端彩色输出
        └── config_loader.py       # 配置加载器
```

---

## 快速开始

### 方式一：本地运行

**第一步：安装依赖**

```bash
pip install requests
```

**第二步：创建配置文件**

```bash
cp .env.example .env
```

**第三步：编辑 `.env`，填写账号信息**

```bash
ANYROUTER_ACCOUNTS=[{"name":"主账号","cookies":{"session":"你的session值"},"api_user":"你的用户ID"}]
```

**第四步：运行**

```bash
python main.py
```

---

### 方式二：GitHub Actions 自动运行（推荐）

不需要自己的服务器，利用 GitHub 免费的自动化功能每天定时签到。

**第一步：Fork 本仓库**

点击右上角 `Fork` 按钮，将项目复制到自己的 GitHub 账号下。

**第二步：创建环境**

进入你 Fork 后的仓库，点击顶部 `Settings` → 左侧 `Environments` → 点击 `New environment`，名称填写 `production`，点击 `Configure environment`。

**第三步：添加账号密钥**

在 `Environment secrets` 区域点击 `Add secret`，添加以下内容：

| Secret 名称 | 值 |
|---|---|
| `ANYROUTER_ACCOUNTS` | 账号 JSON（见下方格式） |

**第四步：启用 Actions**

点击顶部 `Actions` → 找到 `AnyRouter 自动签到` → 点击 `Enable workflow`。

之后每 6 小时会自动运行一次，也可以点击 `Run workflow` 手动触发。

---

## 账号配置说明

### 账号 JSON 格式

```json
[
  {
    "name": "主账号",
    "cookies": {"session": "你的session值"},
    "api_user": "你的用户ID"
  },
  {
    "name": "备用账号",
    "cookies": {"session": "你的session值"},
    "api_user": "你的用户ID"
  }
]
```

**注意：写入 `.env` 或 GitHub Secrets 时，JSON 必须压缩为一行。**

### 如何获取 session 和 api_user

1. 用浏览器登录 [anyrouter.top](https://anyrouter.top)
2. 按 `F12` 打开开发者工具
3. 获取 `session`：点击 `Application（应用程序）` → `Cookies` → `https://anyrouter.top` → 找到 `session` 字段，复制其值
4. 获取 `api_user`：点击 `Network（网络）` → 随意点开一个请求 → 查看 `Request Headers（请求标头）` → 找到 `new-api-user` 的值

> Cookie 大约一个月后失效，失效后需要重新登录获取并更新配置。

---

## 通知配置说明

通知渠道均为可选项，不配置则自动跳过，可同时开启多个渠道。

### Telegram

1. 向 [@BotFather](https://t.me/BotFather) 发送 `/newbot` 创建机器人，获取 `bot_token`
2. 向 [@userinfobot](https://t.me/userinfobot) 发送任意消息获取你的 `chat_id`

```bash
TELEGRAM_NOTIF_CONFIG={"trigger":"always","config":{"bot_token":"你的BotToken","chat_id":"你的ChatID"}}
```

### 钉钉

在钉钉群中添加「自定义 Webhook」机器人，获取 Webhook 地址和签名密钥。

```bash
DINGTALK_NOTIF_CONFIG={"trigger":"on_failure","config":{"webhook":"Webhook地址","secret":"签名密钥"}}
```

### 企业微信

在企业微信群中添加「群机器人」，获取 Webhook 地址。

```bash
WECOM_NOTIF_CONFIG={"trigger":"always","config":{"webhook":"Webhook地址"}}
```

### 邮件（SMTP）

```bash
EMAIL_NOTIF_CONFIG={"trigger":"on_failure","config":{"smtp_host":"smtp.163.com","smtp_port":465,"sender":"发件邮箱","password":"授权码","receiver":"收件邮箱"}}
```

### trigger 触发时机说明

| 值 | 说明 |
|---|---|
| `always` | 每次运行后都推送（默认） |
| `on_failure` | 只在有账号签到失败时推送 |
| `on_success` | 只在全部成功时推送 |

---

## 自定义通知模板

在任意通知渠道配置中加入 `title` 和 `template` 字段，即可自定义通知内容。

```bash
TELEGRAM_NOTIF_CONFIG={"trigger":"always","config":{"bot_token":"...","chat_id":"..."},"title":"每日签到播报","template":"签到完成 ✅{success} 🔁{already} ❌{failed}\n\n{detail_list}\n\n💰总余额：{total_balance}"}
```

**可用模板变量：**

| 变量 | 说明 |
|---|---|
| `{total}` | 账号总数 |
| `{success}` | 签到成功数 |
| `{already}` | 今日已签数 |
| `{failed}` | 失败数 |
| `{skipped}` | 跳过数 |
| `{all_success}` | 是否全部成功（是 / 否） |
| `{has_failure}` | 是否有失败（是 / 否） |
| `{total_balance}` | 全账号总余额 |
| `{success_names}` | 签到成功的账号名列表 |
| `{already_names}` | 今日已签的账号名列表 |
| `{failed_names}` | 签到失败的账号名列表 |
| `{detail_list}` | 每个账号的签到详情（含余额） |

---

## 扩展其他平台

默认支持 AnyRouter 和 AgentRouter。如果你使用的是基于 OneAPI 搭建的其他平台，可以通过以下方式扩展：

```bash
PROVIDERS={"我的平台":{"domain":"https://my.example.com","sign_in_path":"/api/user/sign_in","user_info_path":"/api/user/self"}}
```

然后在账号配置中指定 `"provider": "我的平台"` 即可。

---

## 常见问题

**Q：签到失败，提示 `HTTP 401`？**  
A：Session 已过期，请重新登录网站获取新的 Cookie。

**Q：GitHub Actions 没有自动运行？**  
A：请确认已在 Actions 页面手动启用了工作流，同时检查 `production` 环境的 Secrets 是否正确填写。

**Q：支持哪个版本的 Python？**  
A：Python 3.8 及以上版本均可。

**Q：JSON 怎么压缩成一行？**  
A：可以访问 [bejson.com](https://www.bejson.com) 粘贴后点击「压缩」即可。

---

> 作者：Polaris &nbsp;|&nbsp; 基于 [rakuyoMo/autocheck-anyrouter](https://github.com/rakuyoMo/autocheck-anyrouter) 二次开发
