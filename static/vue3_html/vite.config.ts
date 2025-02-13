import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import JavaScriptObfuscator from 'javascript-obfuscator'
import { createFilter } from '@rollup/pluginutils'

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
        {
          ...obfuscatorConfig,
          ...options.options,
          removeComments: true,  // 移除注释
          removeConsoleLog: true,  // 移除console.log
          debugProtection: true,  // 添加调试保护
          debugProtectionInterval: 3000  // 设置为3000毫秒
        }
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
        'src/views/**/*.vue',
      ],
      options: {
        ...obfuscatorConfig,
        removeComments: true,
        removeConsoleLog: true,
        debugProtection: true,
        debugProtectionInterval: 3000  // 设置为3000毫秒
      }
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
        manualChunks: {
          'vendor': [
            'vue',
            'vue-router',
            'pinia',
            '@vue/runtime-core',
            '@vue/runtime-dom',
            'element-plus',
            '@element-plus/icons-vue'
          ]
        },
        // 用于从入口点创建的块的打包输出格式[name]表示文件名,[hash]表示该文件内容hash值
        entryFileNames: 'js/[name].[hash].js',
        // 用于命名代码拆分时创建的共享块的输出命名
        chunkFileNames: (chunkInfo) => {
          const id = chunkInfo.facadeModuleId || '';
          // 基于目录结构的分包
          if (id.includes('src/')) {
            if (id.includes('src/assets/')) return 'js/assets.[hash].js';
            if (id.includes('src/components/')) return 'js/components.[hash].js';
            if (id.includes('src/config/')) return 'js/config.[hash].js';
            if (id.includes('src/router/')) return 'js/router.[hash].js';
            if (id.includes('src/store/')) return 'js/store.[hash].js';
            if (id.includes('src/types/')) return 'js/types.[hash].js';
            if (id.includes('src/utils/')) return 'js/utils.[hash].js';
          }
          // 其他模块
          return 'js/[name].[hash].js';
        },
        // 用于输出静态资源的命名，[ext]表示文件扩展名
        assetFileNames: '[ext]/[name].[hash].[ext]'
      }
    }
  }
});
