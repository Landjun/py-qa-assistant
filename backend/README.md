# Backend（教学运营售后 CRM）

> 仅面向结课后学员经营：学员录入 -> 聊天记录 -> AI分析 -> 画像 -> 跟进 -> 生命周期 -> 看板。

## 安装依赖

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 初始化数据库与种子数据

```bash
python scripts/init_db.py
```

## 重置数据库

```bash
python scripts/reset_db.py
```

## 启动后端

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## AI 模式切换

默认使用 mock 规则分析：

```bash
export AI_MODE=mock
```

切换到 llm 预留模式：

```bash
export AI_MODE=llm
```

> `AI_MODE=llm` 当前仍回退 mock 输出结构，后续在 `app/services/ai_service.py` 中接入真实模型 API。
