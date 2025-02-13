const isDev = process.env.NODE_ENV === 'development';

// 基础混淆配置
const baseConfig = {
  compact: true,
  controlFlowFlattening: false,
  controlFlowFlatteningThreshold: 0.5,
  deadCodeInjection: true,
  deadCodeInjectionThreshold: 0.4,
  debugProtection: true,
  debugProtectionInterval: 2000,
  disableConsoleOutput: true,
  identifierNamesGenerator: 'hexadecimal',
  log: false,
  numbersToExpressions: true,
  renameGlobals: false,
  rotateStringArray: true,
  selfDefending: true,
  shuffleStringArray: true,
  splitStrings: true,
  splitStringsChunkLength: 10,
  stringArray: false,
  stringArrayEncoding: ['base64'],
  stringArrayThreshold: 0.5,
  transformObjectKeys: true,
  unicodeEscapeSequence: false,
};

// 业务模块配置
const businessConfig = {
  ...baseConfig,
  reservedNames: [
    '^useRequestStore$',
    '^useInfluencerStore$',
    '^defineStore$',
    '^ref$',
    '^BASE_URL$',
    'get',
    'post',
    'put',
    'del'
  ],
  exclude: [
    'node_modules/**',
    '**/*.d.ts',
    'src/types/**',
    'src/assets/**',
    'src/style.css'
  ]
};

// 工具模块配置
const utilsConfig = {
  ...baseConfig,
  controlFlowFlattening: true, // 对工具类启用更强的混淆
  stringArray: true,
  reservedNames: [
    '^useRequestStore$',
    'get',
    'post',
    'put',
    'del'
  ],
  include: [
    'src/utils/**'
  ]
};

// Store模块配置
const storeConfig = {
  ...baseConfig,
  stringArray: true,
  reservedNames: [
    '^defineStore$',
    '^useRequestStore$',
    '^useInfluencerStore$',
    'state',
    'getters',
    'actions'
  ],
  include: [
    'src/store/**'
  ]
};

// 组件模块配置
const componentsConfig = {
  ...baseConfig,
  deadCodeInjection: false, // 组件不启用死代码注入，避免影响性能
  reservedNames: [
    '^ref$',
    '^reactive$',
    '^computed$',
    '^watch$',
    '^onMounted$',
    '^defineProps$',
    '^defineEmits$'
  ],
  include: [
    'src/components/**'
  ]
};

export default isDev
  ? {} // 开发模式下不进行混淆
  : {
    // 生产环境下根据不同模块应用不同的混淆配置
    bundles: [
      {
        input: 'src/utils/**',
        output: 'dist/utils',
        ...utilsConfig
      },
      {
        input: 'src/store/**',
        output: 'dist/store',
        ...storeConfig
      },
      {
        input: 'src/components/**',
        output: 'dist/components',
        ...componentsConfig
      },
      {
        input: ['src/**', '!src/utils/**', '!src/store/**', '!src/components/**'],
        output: 'dist',
        ...businessConfig
      }
    ]
  };
