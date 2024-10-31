import {defineConfig} from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0", // 设置服务器监听的主机地址
    // 可选，根据需要开启 https
    // https: true
  },
});
