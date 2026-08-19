# Zeabur 部署指南（⚠️ 已停止推荐）

> ⚠️ **重要更新（2025 起）**：Zeabur 已取消新用户免费额度、转向订阅制，**不再作为本项目免费部署方案**。
> 本文件仅保留供已有 Zeabur 付费订阅的开发者参考。

## 费用现状

- Zeabur 个人免费时代已结束，新注册用户需购买订阅（按服务计费）
- 参考：https://zeabur.com/docs/zh-CN/pricing/pricing-plans

## 推荐替代方案（免费）

- **阿里云函数计算** / **腾讯云 CloudBase**：国内实名账号有免费额度，国内访问最快
- **本机运行 + 内网穿透**（cpolar）：零成本，适合先演示
- 详见 `docs/DEPLOY.md` 与 `docs/DEPLOY-FREE.md`

---

## 原部署步骤（供付费用户参考）

## 一、部署后端

### 第 1 步：登录 Zeabur

打开 https://zeabur.com → 右上角 **Sign in with GitHub** → 授权登录（免费注册）。

### 第 2 步：新建项目

1. 点击 **创建新项目（New Project）**
2. 项目名称填 `xiyuan-xiaozhi`，**区域选择「香港」**（对大陆访问最优）
3. 进入项目后点击 **添加服务（Add Service）**

### 第 3 步：导入 GitHub 仓库

1. 选择 **Deploy from GitHub（从 GitHub 部署）**
2. 首次会要求授权 Zeabur 访问 GitHub，允许并选择仓库 `Atopos-suyu/xiyuan-xiaozhi`
3. Zeabur 会自动检测到**根目录 Dockerfile**，开始构建（约 3-6 分钟）

### 第 4 步：配置环境变量

构建完成后，在服务 **Variables（变量）** 中添加：

| Key | Value | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | `sk-...` | **必填**，填你的 DeepSeek Key |
| `ALLOWED_ORIGINS` | `*` | 允许前端跨域（默认已开，可省略） |

### 第 5 步：获取域名

1. 服务部署完成后，点击 **生成域名（Generate Domain）** → 选择 `*.zeabur.app` 免费域名
2. 得到地址如 `https://xiyuan-xiaozhi-abc123.zeabur.app`
3. **访问 `https://你的域名/api/health` 验证**，应返回：
   ```json
   {"status":"ok","kb_chunks":83,"kb_ready":true}
   ```
   > ⚠️ 首次访问需要 1-2 分钟冷启动（自动下载 embedding 模型），之后保持常驻。

## 二、对接前端（我来完成）

把部署 URL 告诉我（或自行操作）：

1. 修改 `frontend/js/app.js` 顶部：
   ```js
   const DEFAULT_API_BASE = "https://你的域名.zeabur.app";
   ```
2. 重新推送 `gh-pages` 分支（前端更新）
3. 新生访问 https://atopos-suyu.github.io/xiyuan-xiaozhi/ 即可直接对话，**无需任何设置**

## 三、常见问题

| 问题 | 解决 |
|---|---|
| 构建失败 | 查看构建日志；常见为网络拉取 PyPI 失败，重试即可 |
| 首次访问很慢 | 冷启动加载模型，等待 1-2 分钟刷新 |
| 内存不足 OOM | Zeabur 免费实例内存较小，可换 `BAAI/bge-small-zh-v1.5`（已是最小之一）或升级实例 |
| 免费额度用完 | 免费实例会休眠，访问时自动唤醒（较慢）；升级付费计划可常驻 |
| 想换模型 | 在 Variables 加 `EMBED_MODEL=BAAI/bge-small-zh-v1.5`（默认） |

## 四、费用说明

- Zeabur 免费计划：提供基础配额（服务时长/流量），本项目（小型 API + 92MB 模型）在配额内可运行
- 模型调用费：DeepSeek API 按 token 计费（几元可用很久）
- 无隐性费用，超出配额仅会休眠不会扣费
