# 后端 — Python 学习答疑客服系统

FastAPI + SQLite + (预留) FAISS / DeepSeek / DashScope。依赖用 **uv** 管理。

## 环境准备

复制环境变量模板并按需填写（密钥不要提交）：

```powershell
copy .env.example .env
```

`.env` 字段：

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 生成模型密钥 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址，默认 `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称，默认 `deepseek-chat` |
| `DASHSCOPE_API_KEY` | DashScope embedding / rerank 密钥（预留） |
| `DATABASE_URL` | SQLite 连接，默认 `sqlite:///./data/app.db` |
| `FAISS_INDEX_PATH` | FAISS 索引文件路径，默认 `./data/faiss.index` |

## 安装依赖

```powershell
uv sync            # 安装运行 + dev 依赖（fastapi/uvicorn/pytest 等）
uv sync --extra rag  # 需要 RAG 相关依赖时再装（faiss-cpu/openai/dashscope/rank-bm25）
```

## 启动

```powershell
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
curl http://127.0.0.1:8000/health
# {"status":"ok","service":"python-qa-customer-service"}
```

## 测试

```powershell
uv run pytest
```

## 目录

```
app/
  main.py        FastAPI 入口（CORS + 异常处理 + 路由）
  api/           路由层（当前：health）
  core/          config 配置读取 / exceptions 统一异常
  db/            数据库（预留）
  models/        ORM 模型（预留）
  schemas/       Pydantic 模型（预留）
  services/      外部模型调用 & RAG 检索封装（预留）
  utils/         通用工具（预留）
data/            SQLite 与 FAISS 索引存放目录
tests/           pytest 测试
```
