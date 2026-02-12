const config = {
  projectName: 'decoration-agent',
  date: '2024-01-01',
  designWidth: 750,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    828: 1.81 / 2
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  plugins: [],
  defineConstants: {
    // 小程序无 process，必须在编译时替换 process.env
    'process.env.TARO_ENV': JSON.stringify(process.env.TARO_ENV || 'weapp'),
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    'process.env.TARO_APP_API_BASE_URL': JSON.stringify(
      process.env.TARO_APP_API_BASE_URL || 'http://120.26.201.61:8000/api/v1'
    ),
    'process.env.TARO_APP_OSS_BASE_URL': JSON.stringify(process.env.TARO_APP_OSS_BASE_URL || ''),
    'process.env.TARO_APP_MODE': JSON.stringify(process.env.TARO_APP_MODE || 'prod'),
    'process.env.API_TIMEOUT': JSON.stringify(process.env.API_TIMEOUT || '30000'),
    'process.env.ENABLE_CACHE': JSON.stringify(process.env.ENABLE_CACHE === 'false' ? 'false' : 'true'),
  },
  copy: {
    patterns: [
      { from: 'src/assets', to: 'assets' }
    ],
    options: {
    }
  },
  framework: 'react',
  compiler: 'webpack5',
  cache: {
    enable: false // Webpack 持久化缓存配置，建议开启。默认配置请参考：https://docs.taro.zone/docs/config-detail#cache
  },
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {

        }
      },
      url: {
        enable: true,
        config: {
          limit: 1024 // 设定转换尺寸上限
        }
      },
      cssModules: {
        enable: false, // 默认为 false，如需使用 css modules 功能，则设为 true
        config: {
          namingPattern: 'module', // 转换模式，取值为 global/module
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    }
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {}
      },
      cssModules: {
        enable: false, // 默认为 false，如需使用 css modules 功能，则设为 true
        config: {
          namingPattern: 'module', // 转换模式，取值为 global/module
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    }
  }
}

module.exports = function (merge) {
  if (process.env.NODE_ENV === 'development') {
    return merge({}, config, require('./dev'))
  }
  return merge({}, config, {})
}
