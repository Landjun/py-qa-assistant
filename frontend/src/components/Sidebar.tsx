import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

interface NavItem {
  to: string;
  label: string;
  badge?: string;
}

const ADMIN_NAV: (NavItem | null)[] = [
  { to: "/chat",      label: "问答" },
  { to: "/documents", label: "文档管理" },
  { to: "/logs",      label: "日志" },
  { to: "/settings",  label: "设置" },
  null, // divider
  { to: "/courses",   label: "课程管理",  badge: "即将上线" },
  { to: "/users",     label: "用户画像",  badge: "即将上线" },
];

const TEACHER_NAV: (NavItem | null)[] = [
  { to: "/chat",     label: "问答" },
  { to: "/logs",     label: "问答日志" },
  { to: "/settings", label: "设置" },
  null,
  { to: "/courses",  label: "课程内容（只读）", badge: "即将上线" },
];

export function Sidebar() {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();
  const role = user?.role ?? "student";
  const navItems = role === "admin" ? ADMIN_NAV : TEACHER_NAV;

  const handleLogout = () => {
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-gray-200 bg-white">
      <div className="flex items-center gap-2 px-4 py-5">
        <span className="text-lg">🐍</span>
        <span className="text-base font-semibold text-gray-800">Python 答疑客服</span>
      </div>

      {/* 角色徽章 */}
      <div className="mb-2 px-4">
        <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
          role === "admin"
            ? "bg-purple-100 text-purple-700"
            : "bg-blue-100 text-blue-700"
        }`}>
          {role === "admin" ? "管理员" : "教师"}
        </span>
      </div>

      <nav className="flex flex-col gap-0.5 px-2">
        {navItems.map((item, idx) =>
          item === null ? (
            <hr key={idx} className="my-2 border-gray-100" />
          ) : (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between rounded px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-gray-700 hover:bg-gray-100"
                }`
              }
            >
              <span>{item.label}</span>
              {item.badge && (
                <span className="ml-1 rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500">
                  {item.badge}
                </span>
              )}
            </NavLink>
          )
        )}
      </nav>

      <div className="mt-auto border-t border-gray-100 px-4 py-4">
        {user && (
          <p className="mb-2 truncate text-xs text-gray-400">{user.email}</p>
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
