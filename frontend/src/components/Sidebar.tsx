import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

const navItems = [
  { to: "/chat", label: "问答" },
  { to: "/documents", label: "文档管理" },
  { to: "/logs", label: "日志" },
  { to: "/settings", label: "设置" },
];

export function Sidebar() {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="flex w-56 flex-col border-r border-gray-200 bg-white">
      <div className="px-4 py-5 text-lg font-semibold">Python 答疑客服</div>
      <nav className="flex flex-col gap-1 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `rounded px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-700 hover:bg-gray-100"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t border-gray-100 px-4 py-4">
        {user && (
          <p className="mb-2 truncate text-xs text-gray-500">{user.email}</p>
        )}
        <button
          onClick={handleLogout}
          className="w-full rounded px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-100"
        >
          退出登录
        </button>
      </div>
    </aside>
  );
}
