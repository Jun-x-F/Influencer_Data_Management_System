const isDev = process.env.NODE_ENV === 'development';

export default isDev
  ? {} // 开发模式下不进行混淆，允许 F12 控制台输出
  : {
    // 生产环境下启用混淆的配置
    compact: true,
    controlFlowFlattening: false,
    controlFlowFlatteningThreshold: 0.5,
    deadCodeInjection: true,
    deadCodeInjectionThreshold: 0.4,
    debugProtection: true,
    debugProtectionInterval: 2000,
    disableConsoleOutput: true, // 生产环境下禁止控制台输出
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

    // 需要保留的标识符（不进行混淆）
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
      // 添加其他需要保留的函数名或变量名
    ],

    // 排除混淆的文件
    exclude: [
      'node_modules/**',
      '**/*.d.ts'
    ]
  };
