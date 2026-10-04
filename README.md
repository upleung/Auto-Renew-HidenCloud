# 🚀 Auto-Renew-HidenCloud Pro

本项目基于 [eooce](https://github.com/eooce/Auto-Renew-HidenCloud) 的优秀开源代码进行深度重构与二次开发。专为应对 HidenCloud 日益严苛的 Cloudflare Turnstile (5秒盾) 验证与多账号风控而设计。

核心理念：**“算网分离”** —— 利用 GitHub Actions 的免费强大算力进行高负载的浏览器自动化破盾，同时通过独享代理节点将网络请求完美伪装为您自己的原生 IP。

## ✨ 进阶版核心特性 (Pro Features)

- **🛡️ 极致破盾内核**：全面弃用原生 Playwright，升级至专为反指纹检测打造的 `Patchright` 内核，配合 CDP 底层真实鼠标轨迹模拟，无感绕过最新版 CF 验证盾。
- **🌐 原生 IP 伪装 (算网分离)**：内置 `sing-box` 代理引擎。允许 GitHub 服务器通过您的个人独享节点（如 GCP、Oracle）发起请求，完美规避 GitHub 官方机房 IP 被 HidenCloud 批量拉黑的风险。
- **🔒 日志 IP 安全脱敏**：脚本运行初期自动嗅探出口 IP，并对 GitHub Actions 运行日志中的节点 IP 进行 `***` 脱敏掩码处理，彻底杜绝节点泄露。
- **📱 微信/TG 双通道推送**：除了 Telegram，国内用户现可配置**微信官方测试号**直连推送，告别 Server酱 等第三方平台的数据中转泄露隐患。
- **⏱️ Actions 智能防休眠**：每次运行自动向仓库提交 `time.txt` 时间戳，彻底解决 GitHub Actions 超过 60 天无活动被官方强制挂起的问题。

---

## 🛠️ 环境变量配置 (Secrets)

在仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下 Secrets 变量：

### 🔑 基础认证 (必填)
| Secret 名称 | 说明 | 示例 / 获取方式 |
| :--- | :--- | :--- |
| `COOKIE_VALUE` | Remember_web Cookie 值 | 登录 Dashboard 后，F12 控制台 `Application` -> `Cookies` 提取 |
| `EMAIL` | 登录邮箱 | `your-email@gmail.com` (Cookie 失效时的备用登录方案) |
| `PASSWORD` | 登录密码 | `your-password` |

### 🚀 代理防封配置 (强烈建议配置)
| Secret 名称 | 说明 | 示例格式 |
| :--- | :--- | :--- |
| `NODE_LINK` | 您的独享代理节点链接 | 支持 `vless://`, `vmess://`, `trojan://`, `hysteria2://`, `socks5://` 等常用协议 |

### 🔔 消息推送配置 (可选)
| Secret 名称 | 说明 | 获取方式 |
| :--- | :--- | :--- |
| `TG_BOT_TOKEN` | Telegram 机器人 Token | 找 `@BotFather` 申请 |
| `TG_CHAT_ID` | Telegram 接收者 ID | 找 `@userinfobot` 获取 |
| `WECHAT_APPID` | 微信测试号 appID | [微信公众平台接口测试账号](https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index) |
| `WECHAT_APPSECRET` | 微信测试号 appsecret | 同上 |
| `WECHAT_OPENID` | 您微信扫码后的微信号 id | 同上页面的测试号二维码，扫码后生成的长字符 |
| `WECHAT_TEMPLATE_ID` | 微信消息模板 ID | 新增测试模板，内容见下方说明 |

<details>
<summary>👉 附：微信模板配置内容（点击展开）</summary>

在微信测试号后台新增模板，模板内容填入：
```text
{{title.DATA}}
{{content.DATA}}

```

保存后会生成一个**模板ID**，将其填入 `WECHAT_TEMPLATE_ID` 即可。

</details>

---

## 🚀 使用指南 (Usage)

1. **Fork 本仓库** 到您自己的 GitHub 账号下。
2. 按照上方说明，在仓库 Secrets 中配置相关环境变量。
3. 进入 `Actions` 页面，在左侧点击 `Auto Renew HidenCloud TG WeChat`，然后点击右侧的 **Run workflow** 手动触发一次测试。
4. **定时执行**：默认配置为 **UTC时间 每周六 22:35 和 周日 15:36** 自动探测并续期（对应北京时间周日 06:35 和周日 23:36）。如需修改，请编辑 `.github/workflows/renew.yml` 中的 `cron` 表达式。

---

## ⚠️ 免责声明

本脚本及其拓展功能仅供编程学习与技术交流使用。使用者需严格遵守 [HidenCloud 服务条款](https://hidencloud.com)。由于使用本脚本导致的任何账号封禁、资源回收或法律争议，开发者不承担任何责任。
