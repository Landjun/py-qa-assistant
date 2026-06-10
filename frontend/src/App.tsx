import { Outlet } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";

// 应用外壳：左侧导航 + 右侧路由出口
export default function App() {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
