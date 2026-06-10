# 前端 — Python 学习答疑客服系统

Vite + React + TypeScript + TailwindCSS + Zustand + Axios。依赖用 **pnpm** 管理。

## 安装依赖

```powershell
pnpm install
```

## 启动（开发）

```powershell
pnpm dev
# http://localhost:5173
```

## 构建（生产）

```powershell
pnpm build
# 产物在 dist/
```

## 目录

```
src/
  main.tsx          应用入口
  App.tsx           外壳（左栏导航 + Outlet）
  router/           React Router 路由配置
  pages/
    LoginPage.tsx   登录页（骨架）
    ChatPage.tsx    问答页（输入框 + 发送按钮）
    DocumentPage.tsx 文档管理（骨架）
    LogPage.tsx     日志（骨架）
    SettingPage.tsx 设置（骨架）
  components/
    Sidebar.tsx     左侧导航栏
  api/
    client.ts       axios 封装（baseURL=/api，统一错误处理）
  stores/           Zustand 状态（预留）
  styles/
    index.css       TailwindCSS 全局样式
```

## 后端代理

Vite dev server 已配置 `/api` → `http://127.0.0.1:8000`，前端直接请求 `/api/*` 即可。
