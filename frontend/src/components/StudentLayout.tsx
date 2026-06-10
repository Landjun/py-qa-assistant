import { Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

export default function StudentLayout() {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <header className="flex shrink-0 items-center justify-between border-b border-gray-200 bg-white px-5 py-3 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-lg">🐍</span>
          <h1 className="text-base font-semibold text-gray-800">Python 答疑助手</h1>
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-xs text-gray-400">{user.email}</span>
          )}
          <button
            onClick={handleLogout}
            className="rounded px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100"
          >
            退出登录
          </button>
        </div>
      </header>
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
