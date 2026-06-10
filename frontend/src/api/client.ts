import axios from "axios";
import { useAuthStore } from "../store/auth";

const client = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (
      err.response?.status === 401 &&
      window.location.pathname !== "/login"
    ) {
      useAuthStore.getState().clearAuth();
      window.location.href = "/login";
    }
    const message =
      err.response?.data?.detail ??
      err.response?.data?.message ??
      err.message ??
      "请求失败，请稍后重试";
    return Promise.reject(new Error(message));
  },
);

export default client;
