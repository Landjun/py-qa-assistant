# 教学运营售后 CRM（Phase 1）

> **项目定位（严格范围）**：
> 本项目只服务于“教学运营售后、结课后学员经营”，不做招生前端、销售签约、排课系统、复杂权限、多租户、复杂 BI。
>
> 第一阶段主链路：
> **学员录入 -> 聊天记录 -> AI分析 -> 画像生成 -> 跟进记录 -> 生命周期推进 -> 基础看板**

---

## 1. 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- SQLite

### 前端
- Vue 3
- Vite
- Vue Router
- Pinia
- Element Plus
- Axios

---

## 2. 项目目录结构

```text
Intelligent-Q-A-Assistant/
├─ README.md
├─ PHASE1_ARCHITECTURE_PLAN.md
├─ backend/
│  ├─ requirements.txt
│  ├─ .gitignore
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/                  # 配置、数据库、统一响应、错误处理
│  │  ├─ models/                # students/profiles/chat_records/ai_analyses/follow_ups/stage_logs/assets
│  │  ├─ schemas/               # Pydantic schema
│  │  ├─ crud/                  # 数据访问层
│  │  ├─ services/              # ai_service(mock/llm预留), seed
│  │  └─ api/                   # /api/* 路由
│  └─ scripts/
│     ├─ init_db.py             # 建表+初始化种子数据
│     └─ reset_db.py            # 重置 SQLite 并重建种子数据
└─ frontend/
   ├─ package.json
   ├─ vite.config.ts
   └─ src/
      ├─ api/
      ├─ stores/
      ├─ router/
      ├─ layout/
      ├─ views/
      └─ components/
```

---

## 3. 后端启动步骤（默认 8000）

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 初始化数据库 + 种子数据
python scripts/init_db.py

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：
- Swagger: http://127.0.0.1:8000/docs

---

## 4. 前端启动步骤（默认 5173）

```bash
cd frontend
npm install
npm run dev
```

访问地址：
- http://127.0.0.1:5173

`frontend/vite.config.ts` 已将 `/api` 代理到 `http://127.0.0.1:8000`。

---

## 5. 前后端联调说明

1) 先启动后端（8000）
2) 再启动前端（5173）
3) 前端所有请求走 `/api/*`，由 Vite 代理到后端
4) 推荐联调顺序（与主链路一致）：
   - 学员中心新增学员
   - 学员详情录入聊天记录
   - AI分析页或学员详情触发分析
   - 一键同步分析到画像
   - 新增跟进记录
   - 调整生命周期阶段
   - 首页看板查看经营结果

---

## 6. 数据库初始化说明

### 默认 SQLite 文件
- 路径：`backend/crm.db`
- 由 `sqlite:///./crm.db` 指向（工作目录为 `backend`）

### 初始化命令
```bash
cd backend
source .venv/bin/activate
python scripts/init_db.py
```

---

## 7. 种子数据说明（已覆盖第一阶段联调）

初始化脚本会生成：
- **3个学员**
- **每个学员 1 条画像**（共3条）
- **每个学员 2 条聊天记录**（共6条）
- **至少2条跟进记录**（当前3条）
- **至少5条资产库内容**（当前5条）

用于快速演示“结课后学员经营”全链路。

---

## 8. Mock AI 分析说明

当前默认使用 mock 规则分析（关键词驱动），并输出固定结构化字段：
- `stage`
- `main_need`
- `core_concerns`
- `interest_direction`
- `risk_points`
- `recommended_course`
- `recommended_action`
- `tags`
- `summary`

示例规则：
- 包含“赚钱/副业/变现” => 偏 AI 副业导向
- 包含“学不会/零基础/怕跟不上” => 识别学习顾虑
- 包含“价格/预算/太贵” => 识别价格敏感
- 包含“报名/想参加/开课” => 提升到高意向

---

## 9. 后续替换为真实大模型 API（保留接口）

后端已预留：
- `analyze_chat_with_mock()`
- `analyze_chat_with_llm()`

建议替换步骤：
1) 在 `backend/app/services/ai_service.py` 中实现 `analyze_chat_with_llm()` 的真实 HTTP 调用
2) 保持返回字段结构不变（避免前端和存储层改动）
3) 将 `AI_MODE` 设置为 `llm`（见下文 FAQ）
4) 重新启动后端

---

## 10. 常见问题排查（FAQ）

### Q1：前后端跨域怎么处理？
- 开发环境推荐使用前端代理（`vite.config.ts`）。
- 后端也已开启 CORS（`allow_origins=['*']`）用于本地联调兜底。

### Q2：SQLite 文件在哪？
- 在 `backend/crm.db`。
- 若你在 `backend` 目录外启动后端，SQLite 相对路径可能变化，建议始终在 `backend` 目录执行启动命令。

### Q3：接口报错怎么排查？
1. 先看后端终端日志（FastAPI 会打印 traceback）
2. 用 `http://127.0.0.1:8000/docs` 手动调接口验证请求参数
3. 检查前端请求路径是否以 `/api` 开头
4. 检查 `chat_record_id` 是否属于对应 `student_id`

### Q4：如何重置数据库？
```bash
cd backend
source .venv/bin/activate
python scripts/reset_db.py
```
该命令会删除 `crm.db` 并重新建表、重新灌入种子数据。

### Q5：如何切换 mock AI 和真实 AI？
- 默认 `AI_MODE=mock`
- 切换方式（Linux/macOS）：
```bash
cd backend
export AI_MODE=llm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- 若 `analyze_chat_with_llm()` 尚未完成，系统会回退到 mock 输出结构。

---

## 11. 交付边界声明（避免范围漂移）

本项目当前版本只实现“教学运营售后、结课后学员经营”的第一阶段能力，不包含：
- 招生前端 CRM
- 销售签约流程
- 教学排课系统
- 自动群发/企业微信自动同步
- 复杂权限、多角色审批
- 多租户
- 复杂 BI

