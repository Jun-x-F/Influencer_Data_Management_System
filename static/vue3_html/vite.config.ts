import {defineConfig} from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import JavaScriptObfuscator from 'javascript-obfuscator'
import {createFilter} from '@rollup/pluginutils'

// 导入混淆配置
import obfuscatorConfig from './obfuscator.config.js'

// 创建自定义混淆插件
function obfuscatorPlugin(options = {}) {
  const filter = createFilter(
    options.include || ['**/*.js', '**/*.ts'],
    options.exclude || ['node_modules/**']
  )

  return {
    name: 'vite-plugin-javascript-obfuscator',
    transform(code, id) {
      if (!filter(id)) return null

      // 对匹配的文件进行混淆
      const result = JavaScriptObfuscator.obfuscate(
        code,
        options.options || obfuscatorConfig
      )

      return {
        code: result.getObfuscatedCode(),
        map: null
      }
    }
  }
}

export default defineConfig({
  plugins: [
    vue(),
    obfuscatorPlugin({
      include: [
        'src/config/request.ts',
        'src/store/useInfluencerStore.ts'
      ],
      exclude: [
        'src/components/**/*.vue',
        'src/views/**/*.vue'
      ],
      options: obfuscatorConfig
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  assetsInclude: ['**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.gif', '**/*.svg'],
  server: {
    host: "0.0.0.0", // 设置服务器监听的主机地址
    port: 5174
    // 可选，根据需要开启 https
    // https: true
  },
  build: {
    // 生产环境配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 只在 preview 时移除console
        drop_debugger: true  // 只在 preview 时移除debugger
      }
    },
    // 调整chunk警告限制
    chunkSizeWarningLimit: 1000,
    // 输出目录配置
    outDir: 'dist',
    assetsDir: 'assets',
    // 优化分包策略
    rollupOptions: {
      output: {
        manualChunks: undefined,  // 禁用代码分割
      }
    }
  }
});
