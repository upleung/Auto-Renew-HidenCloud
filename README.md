# 🚀 Auto-Renew-HidenCloud Pro

本项目基于 [eooce](https://github.com/eooce/Auto-Renew-HidenCloud) 的优秀开源代码进行深度重构与二次开发。同步升级更新 HidenCloud Renew 保活续期与推送通知功能，支持 Telegram 和 Wechat 续期实况通知推送。

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
