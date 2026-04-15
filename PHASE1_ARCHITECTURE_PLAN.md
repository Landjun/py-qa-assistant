# 结课后学员经营 CRM（Phase 1）工程化方案

> 定位：仅面向教学运营售后，仅服务结课后学员经营，不覆盖招生销售、排课、自动化营销、多租户等复杂场景。

## 1. 完整项目目录结构

```text
Intelligent-Q-A-Assistant/
├─ README.md
├─ .gitignore
├─ docker-compose.yml                 # 可选：本地一键启动前后端（Phase 1 可先不用）
├─ docs/
│  ├─ product/
│  │  ├─ scope.md                     # 范围定义（做什么/不做什么）
│  │  ├─ workflow.md                  # 业务闭环说明
│  │  └─ glossary.md                  # 生命周期阶段、标签定义
│  ├─ api/
│  │  └─ openapi-overview.md          # API 分组清单
│  ├─ db/
│  │  ├─ erd.md                       # 表关系说明
│  │  └─ migration-note.md            # SQLite 演进策略
│  └─ frontend/
│     └─ routes-and-pages.md          # 页面职责、路由说明
├─ backend/
│  ├─ app/
│  │  ├─ main.py                      # FastAPI 入口
│  │  ├─ core/
│  │  │  ├─ config.py                 # 配置（环境变量、常量）
│  │  │  ├─ security.py               # 登录鉴权（JWT）
│  │  │  └─ database.py               # SQLAlchemy Session/engine
│  │  ├─ models/                      # SQLAlchemy ORM
│  │  │  ├─ base.py
│  │  │  ├─ user.py
│  │  │  ├─ student.py
│  │  │  ├─ student_profile.py
│  │  │  ├─lifecycle.py
│  │  │  ├─ chat.py
│  │  │  ├─ followup.py
│  │  │  └─ asset.py
│  │  ├─ schemas/                     # Pydantic 请求/响应模型
│  │  │  ├─ auth.py
│  │  │  ├─ dashboard.py
│  │  │  ├─ student.py
│  │  │  ├─ profile.py
│  │  │  ├─ chat.py
│  │  │  ├─ lifecycle.py
│  │  │  ├─ followup.py
│  │  │  └─ asset.py
│  │  ├─ crud/                        # 纯数据库操作层
│  │  │  ├─ crud_student.py
│  │  │  ├─ crud_profile.py
│  │  │  ├─ crud_chat.py
│  │  │  ├─ crud_lifecycle.py
│  │  │  ├─ crud_followup.py
│  │  │  └─ crud_asset.py
│  │  ├─ services/                    # 业务编排与规则
│  │  │  ├─ dashboard_service.py
│  │  │  ├─ profile_service.py
│  │  │  ├─ ai_analysis_service.py
│  │  │  ├─ lifecycle_service.py
│  │  │  └─ import_service.py
│  │  ├─ api/
│  │  │  ├─ deps.py                   # 路由依赖（鉴权、分页参数）
│  │  │  └─ v1/
│  │  │     ├─ api.py                 # v1 路由聚合
│  │  │     ├─ endpoints/
│  │  │     │  ├─ auth.py
│  │  │     │  ├─ dashboard.py
│  │  │     │  ├─ students.py
│  │  │     │  ├─ profiles.py
│  │  │     │  ├─ chats.py
│  │  │     │  ├─ lifecycle.py
│  │  │     │  ├─ followups.py
│  │  │     │  └─ assets.py
│  │  ├─ utils/
│  │  │  ├─ time.py
│  │  │  └─ pagination.py
│  │  └─ tests/
│  │     ├─ conftest.py
│  │     ├─ test_auth.py
│  │     ├─ test_students.py
│  │     └─ test_lifecycle_flow.py
│  ├─ requirements.txt
│  └─ uvicorn.sh
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.ts
│  ├─ tsconfig.json
│  └─ src/
│     ├─ main.ts
│     ├─ App.vue
│     ├─ router/
│     │  └─ index.ts
│     ├─ stores/
│     │  ├─ auth.ts
│     │  ├─ dashboard.ts
│     │  ├─ student.ts
│     │  ├─ profile.ts
│     │  ├─ lifecycle.ts
│     │  ├─ followup.ts
│     │  └─ asset.ts
│     ├─ api/
│     │  ├─ http.ts
│     │  ├─ auth.ts
│     │  ├─ dashboard.ts
│     │  ├─ students.ts
│     │  ├─ profiles.ts
│     │  ├─ chats.ts
│     │  ├─ lifecycle.ts
│     │  ├─ followups.ts
│     │  └─ assets.ts
│     ├─ layout/
│     │  ├─ MainLayout.vue
│     │  └─ AppHeader.vue
│     ├─ components/
│     │  ├─ common/
│     │  │  ├─ SearchBar.vue
│     │  │  ├─ EmptyState.vue
│     │  │  └─ ConfirmDialog.vue
│     │  ├─ dashboard/
│     │  │  ├─ MetricCard.vue
│     │  │  └─ StageDistributionChart.vue
│     │  ├─ students/
│     │  │  ├─ StudentTable.vue
│     │  │  └─ StudentTagPanel.vue
│     │  ├─ profiles/
│     │  │  ├─ ProfileForm.vue
│     │  │  └─ PersonaSummary.vue
│     │  ├─ chats/
│     │  │  ├─ ChatImportPanel.vue
│     │  │  └─ AiInsightCard.vue
│     │  ├─ lifecycle/
│     │  │  ├─ StageBoard.vue
│     │  │  └─ StageActionDrawer.vue
│     │  ├─ followups/
│     │  │  ├─ FollowupTimeline.vue
│     │  │  └─ FollowupForm.vue
│     │  └─ assets/
│     │     ├─ AssetLibraryTable.vue
│     │     └─ AssetUploader.vue
│     ├─ views/
│     │  ├─ LoginView.vue
│     │  ├─ DashboardView.vue
│     │  ├─ StudentCenterView.vue
│     │  ├─ ProfileCenterView.vue
│     │  ├─ ChatAnalysisView.vue
│     │  ├─ LifecycleView.vue
│     │  ├─ FollowupView.vue
│     │  └─ AssetLibraryView.vue
│     ├─ types/
│     │  ├─ auth.ts
│     │  ├─ student.ts
│     │  ├─ profile.ts
│     │  ├─ chat.ts
│     │  ├─ lifecycle.ts
│     │  ├─ followup.ts
│     │  └─ asset.ts
│     └─ styles/
│        └─ index.scss
└─ scripts/
   ├─ init_db.py                       # 初始化 SQLite 和种子数据
   └─ seed_demo_data.py
```

## 2. 前后端模块划分

### 后端模块
1. **Auth 模块**
   - 功能：登录、JWT 签发、当前用户信息。
   - 边界：仅单组织本地系统，Phase 1 支持单角色（运营）。

2. **Student 模块（学员中心）**
   - 功能：结课学员新增/编辑/查询、分层标签管理、状态过滤。
   - 关键字段：课程、结课日期、近30天互动、分层等级。

3. **Profile 模块（画像中心）**
   - 功能：维护学员静态画像 + 动态画像（目标、痛点、消费倾向、风险信号）。
   - 数据来源：人工填写 + AI 分析结果回填。

4. **Chat & AI 模块**
   - 功能：聊天记录导入、消息存储、AI 摘要、意图识别、情绪倾向、复购信号。
   - 输出：画像更新建议、生命周期阶段建议、跟进建议。

5. **Lifecycle 模块**
   - 功能：生命周期阶段定义、阶段变更、阶段原因、下一步建议动作。
   - 阶段建议（Phase 1）：
     - `graduated_observe`（结课观察）
     - `active_followup`（积极跟进）
     - `repurchase_ready`（复购就绪）
     - `repurchase_done`（已复购）
     - `at_risk`（流失风险）

6. **Followup 模块**
   - 功能：记录触达动作（私聊/电话/社群）、结果、下次跟进时间、责任人。
   - 联动：更新生命周期推进和看板统计。

7. **Asset 模块（最小资产库）**
   - 功能：管理复购经营中使用的模板资产（话术、案例、SOP、海报、链接）。
   - 目标：提高复用，降低人肉重复输出。

8. **Dashboard 模块**
   - 功能：核心指标聚合（学员总量、阶段分布、复购转化、跟进完成率）。
   - 输出：今日待跟进、近7天经营趋势。

### 前端模块
- **全局层**：路由守卫、鉴权状态、Axios 拦截器、全局布局。
- **页面层**：8 个页面一页一职责。
- **组件层**：按业务域拆组件，避免超大页面。
- **状态层（Pinia）**：按域建 store，不做“单一巨型 store”。
- **接口层（api/*.ts）**：请求与页面解耦，方便后续替换后端。

## 3. 数据库表关系设计（SQLite）

## 3.1 核心实体

1. `users`
   - 系统登录用户（运营人员）
   - 关键字段：`id`, `username`, `password_hash`, `display_name`, `is_active`, `created_at`

2. `students`
   - 结课后学员主表
   - 关键字段：`id`, `name`, `phone`, `wechat_id`, `course_name`, `graduation_date`, `layer_level`, `status`, `owner_user_id`, `created_at`, `updated_at`

3. `student_profiles`
   - 学员画像表（1:1）
   - 关键字段：`student_id(unique)`, `career_stage`, `core_goal`, `pain_points`, `budget_level`, `decision_style`, `risk_flags`, `ai_summary`, `updated_at`

4. `chat_sessions`
   - 一次导入会话（用于批次管理）
   - 关键字段：`id`, `student_id`, `source_type`, `imported_at`, `message_count`, `raw_file_path`

5. `chat_messages`
   - 聊天消息明细（1:N）
   - 关键字段：`id`, `session_id`, `sender_type(student/operator)`, `content`, `sent_at`

6. `ai_analysis_results`
   - AI 分析结果（按 session 存）
   - 关键字段：`id`, `session_id`, `summary`, `sentiment_score`, `intents_json`, `repurchase_signal_score`, `suggested_stage`, `suggested_actions`, `created_at`

7. `lifecycle_records`
   - 生命周期变更历史
   - 关键字段：`id`, `student_id`, `from_stage`, `to_stage`, `reason`, `operator_id`, `created_at`

8. `student_current_stage`
   - 学员当前生命周期快照（1:1）
   - 关键字段：`student_id(unique)`, `current_stage`, `stage_updated_at`, `next_action`, `next_action_due_at`

9. `followup_records`
   - 跟进记录
   - 关键字段：`id`, `student_id`, `channel`, `content`, `result`, `next_followup_at`, `operator_id`, `created_at`

10. `assets`
    - 最小资产库
    - 关键字段：`id`, `asset_type`, `title`, `description`, `content_text`, `file_url`, `tags`, `created_by`, `created_at`, `updated_at`

## 3.2 关系（ER 简版）
- `users (1) -> (N) students`（owner）
- `students (1) -> (1) student_profiles`
- `students (1) -> (N) chat_sessions -> (N) chat_messages`
- `chat_sessions (1) -> (1) ai_analysis_results`（Phase 1 可按 1:1 约束）
- `students (1) -> (N) lifecycle_records`
- `students (1) -> (1) student_current_stage`
- `students (1) -> (N) followup_records`
- `users (1) -> (N) followup_records`
- `users (1) -> (N) assets`

## 4. API 列表（v1）

> 前缀：`/api/v1`

### 4.1 Auth
- `POST /auth/login`：登录
- `GET /auth/me`：当前登录用户

### 4.2 Dashboard
- `GET /dashboard/metrics`：核心指标
- `GET /dashboard/todo-followups`：待跟进列表
- `GET /dashboard/trends?days=7`：趋势统计

### 4.3 Students（学员中心）
- `POST /students`：创建学员
- `GET /students`：分页查询（按姓名/层级/阶段/课程过滤）
- `GET /students/{student_id}`：学员详情
- `PUT /students/{student_id}`：更新学员
- `PATCH /students/{student_id}/layer`：更新学员分层

### 4.4 Profiles（画像中心）
- `GET /profiles/{student_id}`：查询画像
- `PUT /profiles/{student_id}`：更新画像
- `POST /profiles/{student_id}/refresh-from-ai`：根据 AI 结果更新画像建议

### 4.5 Chats & AI
- `POST /chats/{student_id}/import`：导入聊天记录（文本/CSV）
- `GET /chats/{student_id}/sessions`：会话列表
- `GET /chats/sessions/{session_id}/messages`：消息明细
- `POST /chats/sessions/{session_id}/analyze`：触发 AI 分析
- `GET /chats/sessions/{session_id}/analysis`：查看 AI 分析结果

### 4.6 Lifecycle
- `GET /lifecycle/{student_id}`：当前阶段 + 历史
- `POST /lifecycle/{student_id}/transition`：推进/回退阶段
- `GET /lifecycle/stages/distribution`：阶段分布（看板/列表）

### 4.7 Followups
- `POST /followups`：新增跟进记录
- `GET /followups`：分页查询（按日期/负责人/阶段）
- `GET /followups/{student_id}/timeline`：学员跟进时间线
- `PATCH /followups/{id}/done`：标记完成

### 4.8 Assets
- `POST /assets`：新增资产
- `GET /assets`：资产列表
- `GET /assets/{id}`：资产详情
- `PUT /assets/{id}`：更新资产
- `DELETE /assets/{id}`：删除资产

## 5. 页面列表与页面职责

1. **登录页（LoginView）**
   - 账号密码登录
   - 登录态持久化，跳转首页

2. **首页看板（DashboardView）**
   - 核心经营指标卡片（总学员、复购率、阶段分布、待跟进）
   - 近7天跟进与转化趋势
   - 今日待办跟进清单

3. **学员中心（StudentCenterView）**
   - 学员列表、搜索筛选、分层标签
   - 学员基础信息维护
   - 进入画像/聊天/生命周期详情入口

4. **画像中心（ProfileCenterView）**
   - 展示并编辑学员画像
   - 采纳 AI 给出的画像补全建议

5. **聊天记录与 AI 分析（ChatAnalysisView）**
   - 导入聊天记录
   - 查看会话与消息
   - 触发 AI 分析，展示摘要/意图/复购信号

6. **生命周期管理（LifecycleView）**
   - 查看当前阶段和历史迁移
   - 手动推进/回退阶段并填写原因
   - 生成下一步动作建议

7. **跟进记录（FollowupView）**
   - 记录每次跟进动作
   - 时间线查看，管理下次跟进计划
   - 关联生命周期状态变化

8. **最小资产库（AssetLibraryView）**
   - 维护话术模板、案例、SOP、素材链接
   - 标签化检索，提高复用效率

## 6. 开发顺序建议（可直接进入编码）

### Sprint 0（0.5~1 天）基础工程
1. 初始化前后端工程脚手架
2. 约定代码规范（lint、format、commit message）
3. 打通前后端联调链路（前端 Axios -> FastAPI）

### Sprint 1（1~2 天）认证 + 学员主链路
1. 登录鉴权（JWT）
2. 学员中心（增删改查 + 分层）
3. 基础数据库建表与种子数据

### Sprint 2（2 天）聊天导入 + AI 分析
1. 聊天记录导入与存储
2. AI 分析结果落表
3. 从 AI 结果回填画像建议

### Sprint 3（1~2 天）生命周期 + 跟进
1. 生命周期阶段推进与历史记录
2. 跟进记录与待办提醒
3. 生命周期与跟进联动规则

### Sprint 4（1 天）资产库 + 看板
1. 最小资产库 CRUD
2. 首页指标聚合与趋势接口
3. 前端页面串联业务闭环

### Sprint 5（0.5~1 天）验收与扩展点
1. 端到端走通闭环：
   - 录入学员 -> 导入聊天 -> AI分析 -> 画像更新 -> 生命周期推进 -> 跟进 -> 看板反馈
2. 补充测试用例（至少覆盖核心流程）
3. 规划 Phase 2 扩展（自动提醒、标签策略、轻量权限）

---

## 附：工程落地建议（保证后续可扩展）
- 先保持“单体后端 + 模块化分层”，避免过早微服务。
- 所有枚举（生命周期阶段、分层等级、跟进渠道）集中管理，避免魔法字符串。
- API 统一响应结构（`code/message/data`）和统一错误处理。
- 聊天原始数据与 AI 结果分表存储，便于替换模型与重跑分析。
- 先用 SQLite，ORM 模型为后续迁移 PostgreSQL 留足字段类型空间。
