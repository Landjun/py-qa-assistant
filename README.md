# Python 学习答疑客服系统

基于 DeepSeek + RAG 的 Python 学习助手，支持意图识别、知识库检索、问答日志追踪。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 · FastAPI · SQLAlchemy 2.0 · aiosqlite · uv |
| 向量 | DashScope text-embedding-v4 (1024维) · FAISS IndexFlatIP |
| LLM | DeepSeek API (deepseek-chat) |
| 前端 | React 18 · TypeScript · Vite · TailwindCSS v3 · Zustand v5 · Axios |
| 认证 | bcrypt · PyJWT (HS256, 7天有效期) |

## 目录结构

```
py-qa-assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI 路由
│   │   ├── core/         # 配置 (config.py)
│   │   ├── db/           # 数据库初始化
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 模式
│   │   └── services/     # 业务逻辑
│   ├── data/             # SQLite + FAISS 索引（运行时生成）
│   ├── .env              # 本地环境变量（不提交）
│   ├── .env.example      # 环境变量模板
│   └── pyproject.toml
└── frontend/
    ├── src/
    │   ├── api/          # Axios 接口层
    │   ├── pages/        # 页面组件
    │   └── store/        # Zustand 状态管理
    ├── package.json
    └── vite.config.ts
```

## 快速启动

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，填写 DEEPSEEK_API_KEY、DASHSCOPE_API_KEY、JWT_SECRET_KEY
```

### 2. 启动后端

```bash
cd backend
uv sync                          # 安装依赖
uv run uvicorn app.main:app --reload --port 8000
```

后端启动后自动完成：
- 创建 SQLite 数据库 (`data/app.db`)
- 初始化 FAISS 索引 (`data/faiss.index`)
- 创建默认管理员账号 `admin@app.com / 123456`
- 执行增量数据库迁移

### 3. 启动前端

```bash
cd frontend
pnpm install                     # 安装依赖
pnpm dev                         # 开发模式，默认 http://localhost:5173
```

### 4. 生产构建

```bash
cd frontend
pnpm build                       # 产物输出到 dist/
```

## 环境变量说明

编辑 `backend/.env`：

```env
# DeepSeek 生成模型（必填）
DEEPSEEK_API_KEY=sk-xxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# DashScope 向量模型（必填，知识库功能需要）
DASHSCOPE_API_KEY=sk-xxxx

# 数据库（默认即可）
DATABASE_URL=sqlite:///./data/app.db
FAISS_INDEX_PATH=./data/faiss.index

# JWT 密钥（必填，至少32位随机字符串）
# 生成方式：openssl rand -hex 32
JWT_SECRET_KEY=your-secret-key-at-least-32-chars
```

### 获取 API Key

- **DeepSeek**：https://platform.deepseek.com/api_keys
- **DashScope**：https://dashscope.console.aliyun.com/（阿里云百炼，免费额度可用）

## 测试账号

| 字段 | 值 |
|------|----|
| 邮箱 | admin@app.com |
| 密码 | 123456 |

## 功能说明

### 意图识别

系统自动识别问题类型并路由到对应处理器：

| 意图 | 描述 | 触发示例 |
|------|------|----------|
| `PYTHON_QA` | Python 知识问答 + RAG 检索 | "Python 列表和元组的区别？" |
| `BUG_HELP` | Python 报错排查 | "TypeError: unhashable type 怎么解决？" |
| `FEEDBACK` | 用户反馈 | "这个功能很好用" |
| `CHAT` | 普通闲聊 | "你好" |

### 知识库管理

1. 登录后进入「知识库」页面
2. 上传 `.md` 格式文档
3. 系统自动分块 → DashScope 向量化 → 存入 FAISS
4. 提问时自动检索 Top-3 相关块（余弦相似度 ≥ 0.5）

### 问答日志

- 每次问答自动记录完整链路日志（intent、embedding、faiss、retrieval、deepseek 各步骤）
- 管理员可在「日志」页面查看、过滤、展开详情
- 日志写入为后台任务，不阻塞主流程

## API 文档

后端启动后访问：http://localhost:8000/docs

主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录，返回 JWT |
| POST | `/api/chat/ask` | 问答（意图识别 + RAG） |
| GET | `/api/conversations` | 会话列表 |
| GET | `/api/conversations/{id}/messages` | 会话消息 |
| GET | `/api/documents` | 知识库文档列表 |
| POST | `/api/documents/upload` | 上传 Markdown 文档 |
| GET | `/api/logs` | 问答日志列表（支持过滤） |
| GET | `/api/logs/{id}` | 日志详情（含各步骤） |

## 常见问题

**Q: 后端启动报 `DEEPSEEK_API_KEY 未配置`**
A: 检查 `backend/.env` 是否存在且包含 `DEEPSEEK_API_KEY=sk-...`

**Q: 知识库上传后检索无结果**
A: 确认 `DASHSCOPE_API_KEY` 已配置，上传时后台会打印向量化进度日志

**Q: `uv: command not found`**
A: 安装 uv：`pip install uv` 或参考 https://docs.astral.sh/uv/

**Q: `pnpm: command not found`**
A: 安装 pnpm：`npm install -g pnpm`

**Q: JWT token 过期**
A: 默认有效期 7 天，重新登录即可（可在 `.env` 中通过 `JWT_EXPIRE_MINUTES` 调整）

**Q: 前端 API 请求报 CORS 错误**
A: 确认后端运行在 `localhost:8000`，前端 `vite.config.ts` 已配置代理到该地址
