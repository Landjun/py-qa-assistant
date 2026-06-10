import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import App from "../App";
import StudentLayout from "../components/StudentLayout";
import LoginPage from "../pages/LoginPage";
import ChatPage from "../pages/ChatPage";
import DocumentPage from "../pages/DocumentPage";
import LogPage from "../pages/LogPage";
import SettingPage from "../pages/SettingPage";
import PlaceholderPage from "../pages/PlaceholderPage";
import CoursePage from "../pages/CoursePage";
import { useAuthStore } from "../store/auth";

function ProtectedRoute() {
  const token = useAuthStore((s) => s.token);
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

function RoleLayout() {
  const role = useAuthStore((s) => s.user?.role);
  return role === "student" ? <StudentLayout /> : <App />;
}

function RoleGuard({ allowedRoles }: { allowedRoles: string[] }) {
  const role = useAuthStore((s) => s.user?.role ?? "student");
  return allowedRoles.includes(role) ? <Outlet /> : <Navigate to="/chat" replace />;
}

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        element: <RoleLayout />,
        children: [
          { index: true, element: <Navigate to="/chat" replace /> },
          { path: "chat", element: <ChatPage /> },
          { path: "courses", element: <CoursePage /> },
          {
            element: <RoleGuard allowedRoles={["admin", "teacher"]} />,
            children: [
              { path: "documents", element: <DocumentPage /> },
              { path: "logs", element: <LogPage /> },
              { path: "settings", element: <SettingPage /> },
            ],
          },
          {
            element: <RoleGuard allowedRoles={["admin"]} />,
            children: [
              {
                path: "users",
                element: (
                  <PlaceholderPage title="用户画像" description="用户画像功能即将上线，敬请期待" />
                ),
              },
            ],
          },
          { path: "*", element: <Navigate to="/chat" replace /> },
        ],
      },
    ],
  },
]);
