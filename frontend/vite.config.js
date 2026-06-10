import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        // 预留：后端代理。后端默认跑在 8000。
        proxy: {
            "/api": {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
            },
        },
    },
});
