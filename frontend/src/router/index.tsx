import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import App from "../App";
import LoginPage from "../pages/LoginPage";
import ChatPage from "../pages/ChatPage";
import DocumentPage from "../pages/DocumentPage";
import LogPage from "../pages/LogPage";
import SettingPage from "../pages/SettingPage";
import { useAuthStore } from "../store/auth";

function ProtectedRoute() {
  const token = useAuthStore((s) => s.token);
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        element: <App />,
        children: [
          { index: true, element: <Navigate to="/chat" replace /> },
          { path: "chat", element: <ChatPage /> },
          { path: "documents", element: <DocumentPage /> },
          { path: "logs", element: <LogPage /> },
          { path: "settings", element: <SettingPage /> },
        ],
      },
    ],
  },
]);
