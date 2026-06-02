# Render 部署指南

## 架构概览

```
Render Web Service (backend)   ←→   Render PostgreSQL
        ↕ CORS
Render Static Site (frontend)
```

---

## 前端（已完成）

| 项目 | 值 |
|------|----|
| Service type | Static Site |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Publish Directory | `frontend/dist` |
| URL | https://worldcup2026-izid.onrender.com |

---

## 后端（Day 3）

### 1. 在 Render 创建 Web Service

- **Service type**: Web Service  
- **Root Directory**: `backend`  
- **Runtime**: Python 3.11+  
- **Build Command**: `pip install -r requirements.txt`  
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. 环境变量（在 Render Dashboard → Environment 配置）

> ⚠️ 以下变量含敏感 key，只能在 Render Dashboard 填写，绝不提交到 GitHub。

| 变量名 | 值 | 说明 |
|--------|----|------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Render PostgreSQL 内部连接串，从 Render DB 页面复制 |
| `API_FOOTBALL_KEY` | `your_key` | API-Sports 密钥，仅后端读取 |
| `API_FOOTBALL_BASE_URL` | `https://v3.football.api-sports.io` | 默认值 |
| `AI_PROVIDER` | `mock` | Day 3 使用 mock；Day 4+ 切换为 deepseek |
| `APP_ENV` | `production` | |
| `APP_NAME` | `worldcup2026` | |
| `APP_BASE_URL` | `https://worldcup2026-izid.onrender.com` | 前端域名 |
| `CORS_ORIGINS` | `https://worldcup2026-izid.onrender.com` | 允许的前端域名，逗号分隔 |
| `ENABLE_REAL_MONEY_BETTING` | `false` | 必须保持 false |
| `ENABLE_TOKEN_WITHDRAWAL` | `false` | 必须保持 false |
| `MTC_DAILY_CHECKIN` | `10` | |
| `MTC_REPORT_UNLOCK_COST` | `390` | |

**R2 预留变量（Day 3 不用，占位）：**

| 变量名 | 值 |
|--------|----|
| `R2_ACCOUNT_ID` | _(留空或填 placeholder)_ |
| `R2_ACCESS_KEY_ID` | _(留空或填 placeholder)_ |
| `R2_SECRET_ACCESS_KEY` | _(留空或填 placeholder)_ |
| `R2_BUCKET` | `worldcup2026` |

### 3. Render PostgreSQL

1. Render Dashboard → New → PostgreSQL
2. 创建后复制 **Internal Database URL**
3. 粘贴到后端 Web Service 的 `DATABASE_URL` 环境变量

### 4. 数据库初始化 & Seed

首次部署后，在 Render Dashboard → Shell 执行：

```bash
# 数据库表已在 startup 自动创建（init_db）
# 运行 seed
python scripts/seed.py
```

或本地通过 SSH 跳板：
```bash
render shell --service <your-service-id>
python scripts/seed.py
```

---

## 本地开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 确保根目录 .env 存在（DATABASE_URL=sqlite:///./worldcup2026.db）
# 启动服务
uvicorn app.main:app --reload

# 初始化 & seed（首次）
python scripts/seed.py
```

访问：
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

---

## 安全合规检查清单

- [ ] `.env` 未提交 Git
- [ ] `API_FOOTBALL_KEY` 只在 Render 环境变量中
- [ ] `ENABLE_REAL_MONEY_BETTING=false`
- [ ] `ENABLE_TOKEN_WITHDRAWAL=false`
- [ ] API 响应无博彩类词汇
- [ ] MTC 说明为"平台积分"
