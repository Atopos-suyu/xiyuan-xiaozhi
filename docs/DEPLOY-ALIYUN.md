# 阿里云函数计算部署指南（免费额度 · 国内访问快）

> 把后端容器部署到阿里云函数计算 FC（自定义容器），使用免费额度，约 1 小时可完成。

## 费用与免费额度（2025 现状）

- 函数计算按"调用次数 + 资源用量（GB·秒）+ 公网流量"计费
- 免费额度（每月）：**100 万次调用 + 40 万 GB·秒 + 公网流量 100GB**（以控制台"免费额度"页为准）
- 本项目（1GB 内存实例）每月可免费运行约 **111 小时**，新生问答场景绰绰有余
- 超出才收费，无强制消费

## 前置条件

- [ ] 阿里云账号（已实名认证）✅ 您已确认有
- [ ] 开通【函数计算 FC】：控制台搜"函数计算"→ 开通服务（免费开通）
- [ ] 开通【容器镜像服务 ACR】个人版：控制台搜"容器镜像服务"→ 免费开通 → 创建**命名空间**（如 `xiaozhi`）

---

## 路线一：ACR 自动构建 + 控制台部署（无需本地 Docker，推荐）

### 第 1 步：ACR 绑定 GitHub 自动构建镜像

1. 容器镜像服务 → 命名空间 `xiaozhi` → 创建镜像仓库：名称 `xiyuan-xiaozhi`，**代码源选 GitHub**，绑定仓库 `Atopos-suyu/xiyuan-xiaozhi`
2. 仓库创建后 → 点 **构建** → **添加规则**：
   - 分支：`main`
   - Dockerfile 路径：`Dockerfile`（仓库根目录）
   - 版本号：`v1`
3. 点 **立即构建**，等待 5-10 分钟（构建日志可看进度）
4. 构建成功后，复制镜像地址：`registry.cn-<区域>.aliyuncs.com/xiaozhi/xiyuan-xiaozhi:v1`

### 第 2 步：创建函数（自定义容器）

1. 函数计算控制台 → **创建函数** → 选 **使用容器镜像**（自定义容器）
2. 基础配置：
   - 服务名：`xiyuan-xiaozhi`（新服务）
   - 函数名：`backend`
   - 镜像：粘贴上一步的镜像地址
   - **启动命令**：`["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
   - 端口：`8000`
   - 内存：**1024 MB**、CPU 1 核、磁盘 512MB、超时 **120 秒**
3. 环境变量（关键）：
   | Key | Value |
   |---|---|
   | `DEEPSEEK_API_KEY` | `sk-...` 你的 DeepSeek Key |
   | `ALLOWED_ORIGINS` | `*` |
   | `HF_HOME` | `/tmp/hf_home` |
   | `HF_HUB_CACHE` | `/tmp/hf_home/hub` |
4. 网络：勾选 **允许公网访问**（默认有互联网访问）

### 第 3 步：创建 HTTP 触发器

1. 函数详情 → **触发器** → 创建触发器：
   - 类型：HTTP 触发器
   - 认证方式：**无需认证（anonymous）**
   - 请求方法：GET、POST
2. 创建后得到公网地址，形如：
   `https://backend-<id>.cn-shanghai.fc.aliyuncs.com/`

### 第 4 步：验证

浏览器访问 `https://你的函数地址/api/health`，应返回：
```json
{"status":"ok","kb_chunks":83,"kb_ready":true}
```
> ⚠️ 首次请求冷启动约 10-60 秒（加载模型），之后保持实例常驻。

---

## 路线二：Serverless Devs CLI 部署（进阶，可自动化）

```bash
# 1. 安装 CLI
curl -L https://registry.serverless-devs.com/s/install | bash
# 2. 配置阿里云密钥
s config add
#    选择 Aliyun，填入 AccessKey ID / Secret（RAM 用户，权限：AliyunFCFullAccess + ACR 推送）
# 3. 构建并部署
export DEEPSEEK_API_KEY=sk-xxx
export ACR_IMAGE=registry.cn-shanghai.aliyuncs.com/xiaozhi/xiyuan-xiaozhi:v1
s deploy --push-registry $ACR_IMAGE
# 4. 部署成功后输出公网域名
```

---

## 前端对接（我来完成）

把函数公网地址发给我，我会：
1. 填入 `frontend/js/app.js` 的 `DEFAULT_API_BASE`
2. 重新推送 gh-pages
3. 新生打开 https://atopos-suyu.github.io/xiyuan-xiaozhi/ 直接对话

## 常见问题

| 问题 | 解决 |
|---|---|
| 冷启动慢 | FC 实例空闲 5 分钟释放，可配"定时预热"或接受首次 1 分钟等待 |
| 镜像构建失败 | 看 ACR 构建日志；多为网络拉包失败，重试 |
| 磁盘/内存不足 | 镜像含模型约 300MB，磁盘 ≥512MB；内存 1024MB 足够 |
| 默认域名被墙？ | FC 默认域名免备案可直接访问（国内），无需备案 |
| 想绑自定义域名 | FC 自定义域名需已备案域名（函数计算控制台→自定义域名） |

## 安全提醒

- AccessKey 仅限 RAM 子账号 + 最小权限，用完可删除
- DEEPSEEK_API_KEY 用环境变量注入，勿写入代码
- 公网触发器建议配合流量限制（FC 支持并发度/限流配置）
