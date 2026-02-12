"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["common"],{

/***/ "./src/components/EmptyState/index.tsx":
/*!*********************************************!*\
  !*** ./src/components/EmptyState/index.tsx ***!
  \*********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__);





/**
 * P34 空数据页 - 通用占位
 */

var DEFAULT = {
  report: {
    text: '暂无报告数据',
    action: '去检测',
    url: '/pages/company-scan/index'
  },
  photo: {
    text: '暂无施工照片',
    action: '去拍摄',
    url: '/pages/photo/index'
  },
  order: {
    text: '暂无订单',
    action: '去下单',
    url: '/pages/index/index'
  },
  message: {
    text: '暂无消息',
    action: '',
    url: ''
  }
};
var EmptyState = function EmptyState(_ref) {
  var _ref$type = _ref.type,
    type = _ref$type === void 0 ? 'report' : _ref$type,
    text = _ref.text,
    actionText = _ref.actionText,
    actionUrl = _ref.actionUrl;
  var d = DEFAULT[type] || DEFAULT.report;
  var displayText = text !== null && text !== void 0 ? text : d.text;
  var btnText = actionText !== null && actionText !== void 0 ? actionText : d.action;
  var btnUrl = actionUrl !== null && actionUrl !== void 0 ? actionUrl : d.url;
  var handleAction = function handleAction() {
    if (btnUrl) _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().navigateTo({
      url: btnUrl
    });
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
    className: "empty-state",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
      className: "empty-icon",
      children: "\uD83D\uDCCB"
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
      className: "empty-text",
      children: displayText
    }), btnText && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
      className: "empty-btn",
      onClick: handleAction,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        children: btnText
      })
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (EmptyState);

/***/ }),

/***/ "./src/components/ExampleImageModal/index.tsx":
/*!****************************************************!*\
  !*** ./src/components/ExampleImageModal/index.tsx ***!
  \****************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__);




/**
 * 示例图弹窗 - 支持图片+文字，PRD D02/D05
 */
var ExampleImageModal = function ExampleImageModal(_ref) {
  var visible = _ref.visible,
    title = _ref.title,
    content = _ref.content,
    imageUrl = _ref.imageUrl,
    onClose = _ref.onClose;
  if (!visible) return null;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
    className: "example-modal-mask",
    onClick: onClose,
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
      className: "example-modal",
      onClick: function onClick(e) {
        return e.stopPropagation();
      },
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "example-modal-title",
        children: title
      }), imageUrl ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Image, {
        src: imageUrl,
        className: "example-img",
        mode: "widthFix",
        showMenuByLongpress: true
      }) : null, /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "example-modal-content",
        children: content
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "example-modal-close",
        onClick: onClose,
        children: "\u6211\u77E5\u9053\u4E86"
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (ExampleImageModal);

/***/ }),

/***/ "./src/config/assets.ts":
/*!******************************!*\
  !*** ./src/config/assets.ts ***!
  \******************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   BANNER_IMAGES: function() { return /* binding */ BANNER_IMAGES; },
/* harmony export */   EXAMPLE_IMAGES: function() { return /* binding */ EXAMPLE_IMAGES; },
/* harmony export */   USE_BANNER_IMAGES: function() { return /* binding */ USE_BANNER_IMAGES; }
/* harmony export */ });
/* unused harmony exports OSS_BASE, TABBAR, getImageUrl */
/**
 * 静态资源配置
 * - 开发阶段：使用本地 assets
 * - 上线后可切换阿里云 OSS，仅需修改 OSS_BASE
 *
 * 注意：TabBar 图标必须使用本地路径，不支持网络图片
 */

/** 阿里云 OSS 基础地址，通过环境变量 TARO_APP_OSS_BASE_URL 配置 */
var OSS_BASE = "https://zhuangxiu-images.oss-cn-hangzhou.aliyuncs.com" || 0;

/** TabBar 图标（必须本地，微信小程序限制） */
var TABBAR = {
  home: 'assets/tabbar/home.png',
  homeActive: 'assets/tabbar/home-active.png',
  construction: 'assets/tabbar/construction.png',
  constructionActive: 'assets/tabbar/construction-active.png',
  profile: 'assets/tabbar/profile.png',
  profileActive: 'assets/tabbar/profile-active.png'
};

/**
 * 获取图片 URL
 * @param path 相对路径，如 'banner1.png'
 * @returns 完整 URL（OSS 或本地）
 */
function getImageUrl(path) {
  if (OSS_BASE) {
    return "".concat(OSS_BASE.replace(/\/$/, ''), "/").concat(path.replace(/^\//, ''));
  }
  return "/".concat(path).replace(/\/+/g, '/');
}

/**
 * 首页轮播图 - 阿里云 OSS 地址
 * 配置方式：在 .env 中设置 TARO_APP_OSS_BASE_URL
 * OSS 路径：banners/banner1.png、banners/banner2.png、banners/banner3.png
 */
var OSS_BANNER_BASE = "https://zhuangxiu-images.oss-cn-hangzhou.aliyuncs.com" || 0;
var LOCAL_BANNERS = ['assets/banners/banner1.png', 'assets/banners/banner2.png', 'assets/banners/banner3.png'];
var BANNER_IMAGES = OSS_BANNER_BASE ? ["".concat(OSS_BANNER_BASE.replace(/\/$/, ''), "/banners/banner1.png"), "".concat(OSS_BANNER_BASE.replace(/\/$/, ''), "/banners/banner2.png"), "".concat(OSS_BANNER_BASE.replace(/\/$/, ''), "/banners/banner3.png")] : LOCAL_BANNERS;

/** 是否使用轮播图 */
var USE_BANNER_IMAGES = BANNER_IMAGES.some(function (url) {
  return !!url;
});

/** 示例图 URL（PRD D02/D05） */
var OSS_EXAMPLE_BASE = "https://zhuangxiu-images.oss-cn-hangzhou.aliyuncs.com" || 0;
var EXAMPLE_IMAGES = {
  company: OSS_EXAMPLE_BASE ? "".concat(OSS_EXAMPLE_BASE.replace(/\/$/, ''), "/examples/company_sample.png") : '',
  quote: OSS_EXAMPLE_BASE ? "".concat(OSS_EXAMPLE_BASE.replace(/\/$/, ''), "/examples/quote_sample.png") : '',
  contract: OSS_EXAMPLE_BASE ? "".concat(OSS_EXAMPLE_BASE.replace(/\/$/, ''), "/examples/contract_sample.png") : '',
  acceptance: OSS_EXAMPLE_BASE ? "".concat(OSS_EXAMPLE_BASE.replace(/\/$/, ''), "/examples/acceptance_sample.png") : ''
};

/***/ }),

/***/ "./src/config/env.ts":
/*!***************************!*\
  !*** ./src/config/env.ts ***!
  \***************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   env: function() { return /* binding */ env; }
/* harmony export */ });
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread2.js */ "./node_modules/@babel/runtime/helpers/esm/objectSpread2.js");

/**
 * 环境配置
 * 支持多环境配置管理
 */

var getEnvConfig = function getEnvConfig() {
  // 优先使用环境变量 TARO_APP_API_BASE_URL（.env.development / .env.production）
  var apiBaseUrl = "http://120.26.201.61:8001/api/v1" || (0);
  var common = {
    apiBaseUrl: apiBaseUrl,
    apiTimeout: parseInt("30000" || 0),
    enableCache: "true" !== 'false',
    debugMode: "development" !== 'production'
  };
  if (true) {
    return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])({}, common), {}, {
      apiTimeout: parseInt("30000" || 0)
    });
  }
  // removed by dead control flow

};
var env = getEnvConfig();
/* harmony default export */ __webpack_exports__["default"] = (env);

/***/ }),

/***/ "./src/services/api.ts":
/*!*****************************!*\
  !*** ./src/services/api.ts ***!
  \*****************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   acceptanceApi: function() { return /* binding */ acceptanceApi; },
/* harmony export */   companyApi: function() { return /* binding */ companyApi; },
/* harmony export */   constructionApi: function() { return /* binding */ constructionApi; },
/* harmony export */   constructionPhotoApi: function() { return /* binding */ constructionPhotoApi; },
/* harmony export */   contractApi: function() { return /* binding */ contractApi; },
/* harmony export */   feedbackApi: function() { return /* binding */ feedbackApi; },
/* harmony export */   materialChecksApi: function() { return /* binding */ materialChecksApi; },
/* harmony export */   materialsApi: function() { return /* binding */ materialsApi; },
/* harmony export */   messageApi: function() { return /* binding */ messageApi; },
/* harmony export */   paymentApi: function() { return /* binding */ paymentApi; },
/* harmony export */   quoteApi: function() { return /* binding */ quoteApi; },
/* harmony export */   reportApi: function() { return /* binding */ reportApi; },
/* harmony export */   userApi: function() { return /* binding */ userApi; }
/* harmony export */ });
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_typeof_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/typeof.js */ "./node_modules/@babel/runtime/helpers/esm/typeof.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! axios */ "./node_modules/axios/lib/axios.js");
/* harmony import */ var axios_miniprogram_adapter__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! axios-miniprogram-adapter */ "webpack/container/remote/axios-miniprogram-adapter");
/* harmony import */ var axios_miniprogram_adapter__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(axios_miniprogram_adapter__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _store__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../store */ "./src/store/index.ts");
/* harmony import */ var _store_slices_networkSlice__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../store/slices/networkSlice */ "./src/store/slices/networkSlice.ts");
/* harmony import */ var _store_slices_userSlice__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../store/slices/userSlice */ "./src/store/slices/userSlice.ts");
/* harmony import */ var _config_env__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../config/env */ "./src/config/env.ts");
/* provided dependency */ var URLSearchParams = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime")["URLSearchParams"];




/**
 * API服务层 - 封装所有后端API请求
 */








// API 基础配置：统一从 env 读取
var BASE_URL = _config_env__WEBPACK_IMPORTED_MODULE_10__.env.apiBaseUrl;

/** Taro.uploadFile 等非 axios 请求需手动带上的鉴权 header（微信小程序可能不传 header，URL query 为备用） */
var getAuthHeaders = function getAuthHeaders() {
  var h = {};
  var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('access_token');
  var userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('user_id');
  if (token) h['Authorization'] = "Bearer ".concat(token);
  if (userId != null && userId !== '' && String(userId).trim() !== '') {
    h['X-User-Id'] = String(userId).trim();
  }
  return h;
};

/** 微信小程序 uploadFile 可能不传自定义 header，将鉴权放入 URL query 作为备用 */
var appendAuthQuery = function appendAuthQuery(url) {
  var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('access_token');
  var userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('user_id');
  return appendAuthToUrl(url, token, userId);
};

/** 使用显式 token/userId 拼鉴权 URL（避免 uploadFile 时读 storage 竞态） */
var appendAuthToUrl = function appendAuthToUrl(url, token, userId) {
  var params = new URLSearchParams();
  if (token) params.set('access_token', token);
  if (userId != null && userId !== '' && String(userId).trim() !== '') params.set('user_id', String(userId).trim());
  var qs = params.toString();
  return qs ? "".concat(url).concat(url.includes('?') ? '&' : '?').concat(qs) : url;
};

/** 使用显式 token/userId 构建鉴权 header */
var buildAuthHeaders = function buildAuthHeaders(token, userId) {
  var h = {};
  if (token) h['Authorization'] = "Bearer ".concat(token);
  if (userId != null && userId !== '' && String(userId).trim() !== '') h['X-User-Id'] = String(userId).trim();
  return h;
};

// 微信小程序无 xhr/fetch，需使用适配器
var axiosConfig = {
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};
if (true) {
  axiosConfig.adapter = (axios_miniprogram_adapter__WEBPACK_IMPORTED_MODULE_6___default());
}
var instance = axios__WEBPACK_IMPORTED_MODULE_5__["default"].create(axiosConfig);

// 请求拦截器
instance.interceptors.request.use(function (config) {
  // 添加token
  var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('access_token');
  if (token) {
    config.headers.Authorization = "Bearer ".concat(token);
  }

  // 添加用户ID
  var userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('user_id');
  if (userId) {
    config.headers['X-User-Id'] = userId;
  }
  return config;
}, function (error) {
  return Promise.reject(error);
});

// 响应拦截器：兼容两种后端格式
// 1) { code: 0, msg, data }  2) 直接返回数据 { access_token, id, ... }
instance.interceptors.response.use(function (response) {
  var body = response.data;
  var code = body === null || body === void 0 ? void 0 : body.code;
  var msg = body === null || body === void 0 ? void 0 : body.msg;
  var data = body === null || body === void 0 ? void 0 : body.data;

  // 格式1：标准 ApiResponse，code=0 表示成功
  if (code === 0) {
    return data;
  }

  // 格式2：直接返回数据（如 login、profile、scan 等 response_model）
  if (code === undefined && body && (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_typeof_js__WEBPACK_IMPORTED_MODULE_3__["default"])(body) === 'object' && !body.error_id) {
    return body;
  }

  // 业务错误
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().showToast({
    title: msg || (body === null || body === void 0 ? void 0 : body.detail) || '请求失败',
    icon: 'none',
    duration: 2000
  });
  return Promise.reject(new Error(msg || '请求失败'));
}, function (error) {
  var _error$response$data$, _error$response, _error$response2, _backendMsg$;
  // HTTP错误：优先使用后端返回的 detail/msg
  var backendMsg = (_error$response$data$ = (_error$response = error.response) === null || _error$response === void 0 || (_error$response = _error$response.data) === null || _error$response === void 0 ? void 0 : _error$response.detail) !== null && _error$response$data$ !== void 0 ? _error$response$data$ : (_error$response2 = error.response) === null || _error$response2 === void 0 || (_error$response2 = _error$response2.data) === null || _error$response2 === void 0 ? void 0 : _error$response2.msg;
  var detailStr = typeof backendMsg === 'string' ? backendMsg : Array.isArray(backendMsg) && (_backendMsg$ = backendMsg[0]) !== null && _backendMsg$ !== void 0 && _backendMsg$.msg ? backendMsg[0].msg : null;
  var message = detailStr || '网络请求失败';
  if (error.response) {
    var status = error.response.status;
    switch (status) {
      case 401:
        {
          message = '登录已过期，请重新登录';
          var config = error.config;
          var skip401Handler = (config === null || config === void 0 ? void 0 : config.skip401Handler) === true;
          // 若刚登录成功不久（30秒内），可能是页面预加载或竞态，暂不清除避免误杀
          var freshAt = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('login_fresh_at');
          var now = Date.now();
          var recentlyLoggedIn = freshAt && now - Number(freshAt) < 30000;
          if (skip401Handler || recentlyLoggedIn) {
            if (recentlyLoggedIn) _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().removeStorageSync('login_fresh_at');
            return Promise.reject(new Error('请稍后重试'));
          }
          // 清除 token，后端可能因过期或 SECRET_KEY 变更而拒绝
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().removeStorageSync('access_token');
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().removeStorageSync('user_id');
          try {
            _store__WEBPACK_IMPORTED_MODULE_7__["default"].dispatch((0,_store_slices_userSlice__WEBPACK_IMPORTED_MODULE_9__.logout)());
          } catch (_) {}
          var hasOnboarded = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('onboarding_completed') || _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('has_onboarded');
          if (hasOnboarded) {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().reLaunch({
              url: '/pages/index/index'
            });
            setTimeout(function () {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().showModal({
                title: '登录已过期',
                content: '您的登录已过期或需要重新验证，请重新登录后继续使用',
                showCancel: true,
                cancelText: '知道了',
                confirmText: '去登录',
                success: function success(res) {
                  if (res.confirm) _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().switchTab({
                    url: '/pages/profile/index'
                  });
                }
              });
            }, 500);
          } else {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().reLaunch({
              url: '/pages/onboarding/index'
            });
          }
          break;
        }
      case 403:
        message = detailStr || '无权限访问';
        break;
      case 404:
        message = detailStr || '请求的资源不存在';
        break;
      case 500:
        message = detailStr || '服务器内部错误';
        break;
      default:
        message = detailStr || "\u8BF7\u6C42\u9519\u8BEF: ".concat(status);
    }
  } else if (error.request) {
    message = '网络连接失败，请检查网络';
    _store__WEBPACK_IMPORTED_MODULE_7__["default"].dispatch((0,_store_slices_networkSlice__WEBPACK_IMPORTED_MODULE_8__.setNetworkError)(true));
    try {
      var _inst$router;
      var inst = _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getCurrentInstance();
      var from = (_inst$router = inst.router) !== null && _inst$router !== void 0 && _inst$router.path ? "".concat(inst.router.path).concat(inst.router.params && Object.keys(inst.router.params).length ? '?' + Object.entries(inst.router.params).map(function (_ref) {
        var _ref2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_ref, 2),
          k = _ref2[0],
          v = _ref2[1];
        return "".concat(k, "=").concat(v);
      }).join('&') : '') : '';
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().redirectTo({
        url: '/pages/network-error/index' + (from ? '?from=' + encodeURIComponent(from) : '')
      });
    } catch (_) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().showToast({
        title: message,
        icon: 'none',
        duration: 2000
      });
    }
    return Promise.reject(error);
  }
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().showToast({
    title: message,
    icon: 'none',
    duration: 2000
  });
  return Promise.reject(error);
});

/**
 * 用户相关API
 */
var userApi = {
  // 微信登录
  login: function login(code) {
    return instance.post('/users/login', {
      code: code
    });
  },
  // 获取用户信息
  getProfile: function getProfile() {
    return instance.get('/users/profile');
  },
  // 更新用户信息
  updateProfile: function updateProfile(data) {
    return instance.put('/users/profile', data);
  }
};

/**
 * 公司检测相关API
 */
var companyApi = {
  // 扫描公司
  scan: function scan(companyName) {
    return instance.post('/companies/scan', {
      company_name: companyName
    });
  },
  // 获取扫描结果
  getResult: function getResult(scanId) {
    return instance.get("/companies/scan/".concat(scanId));
  },
  // 获取扫描列表
  getList: function getList(params) {
    return instance.get('/companies/scans', {
      params: params
    });
  },
  // 公司名称模糊搜索 (FR-012)
  search: function search(keyword, limit) {
    return instance.get('/companies/search', {
      params: {
        q: keyword,
        limit: limit || 5
      }
    });
  }
};

/**
 * 报价单相关API
 */
var quoteApi = {
  // 上传报价单
  upload: function upload(filePath, fileName) {
    return new Promise(function (resolve, reject) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().uploadFile({
        url: appendAuthQuery("".concat(BASE_URL, "/quotes/upload")),
        filePath: filePath,
        name: 'file',
        header: getAuthHeaders(),
        success: function success(res) {
          try {
            var data = JSON.parse(res.data);
            resolve(data);
          } catch (error) {
            reject(error);
          }
        },
        fail: reject
      });
    });
  },
  // 获取分析结果
  getAnalysis: function getAnalysis(quoteId) {
    return instance.get("/quotes/quote/".concat(quoteId));
  },
  // 获取报价单列表
  getList: function getList(params) {
    return instance.get('/quotes/list', {
      params: params
    });
  }
};

/**
 * 合同相关API
 */
var contractApi = {
  // 上传合同
  upload: function upload(filePath, fileName) {
    return new Promise(function (resolve, reject) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().uploadFile({
        url: appendAuthQuery("".concat(BASE_URL, "/contracts/upload")),
        filePath: filePath,
        name: 'file',
        header: getAuthHeaders(),
        success: function success(res) {
          try {
            var data = JSON.parse(res.data);
            resolve(data);
          } catch (error) {
            reject(error);
          }
        },
        fail: reject
      });
    });
  },
  // 获取分析结果
  getAnalysis: function getAnalysis(contractId) {
    return instance.get("/contracts/contract/".concat(contractId));
  },
  // 获取合同列表
  getList: function getList(params) {
    return instance.get('/contracts/list', {
      params: params
    });
  }
};

/**
 * 施工进度相关API
 */
var constructionApi = {
  // 获取进度计划（后台拉取，401 时仅静默失败不弹「登录已过期」）
  getSchedule: function getSchedule() {
    return instance.get('/constructions/schedule', {
      skip401Handler: true
    });
  },
  // 设置开工日期
  setStartDate: function setStartDate(startDate) {
    return instance.post('/constructions/start-date', {
      start_date: startDate
    });
  },
  // 更新阶段状态
  updateStageStatus: function updateStageStatus(stage, status) {
    return instance.put('/constructions/stage-status', {
      stage: stage,
      status: status
    });
  },
  // 校准阶段验收时间（后续阶段顺延，提醒联动）
  calibrateStageEnd: function calibrateStageEnd(stage, endDate) {
    return instance.post('/constructions/calibrate', {
      stage: stage,
      end_date: endDate
    });
  },
  // 重置进度
  resetSchedule: function resetSchedule() {
    return instance.delete('/constructions/schedule');
  }
};

/**
 * 材料进场核对相关API
 */
var materialsApi = {
  /** 材料进场核对通过（简化接口，无留证） */
  verify: function verify() {
    return instance.post('/materials/verify', {});
  }
};

/**
 * 材料进场人工核对 P37（FR-019~FR-023，支持留证）
 */
var materialChecksApi = {
  getMaterialList: function getMaterialList() {
    return instance.get('/material-checks/material-list');
  },
  /** 提交核对结果，pass 需 items 每项至少1张照片，fail 需 problem_note≥10字 */
  submit: function submit(data) {
    return instance.post('/material-checks/submit', data);
  }
};

/**
 * 订单支付相关API
 */
var paymentApi = {
  // 创建订单
  createOrder: function createOrder(data) {
    return instance.post('/payments/create', data);
  },
  // 发起支付
  pay: function pay(orderId) {
    return instance.post('/payments/pay', {
      order_id: orderId
    });
  },
  // 获取订单列表
  getOrders: function getOrders(params) {
    return instance.get('/payments/orders', {
      params: params
    });
  },
  // 获取订单详情
  getOrder: function getOrder(orderId) {
    return instance.get("/payments/order/".concat(orderId));
  }
};

/**
 * 消息中心 API
 */
var messageApi = {
  getList: function getList(params) {
    return instance.get('/messages', {
      params: params
    });
  },
  getUnreadCount: function getUnreadCount() {
    return instance.get('/messages/unread-count');
  },
  markRead: function markRead(msgId) {
    return instance.put("/messages/".concat(msgId, "/read"));
  },
  markAllRead: function markAllRead() {
    return instance.put('/messages/read-all');
  }
};

/**
 * 意见反馈 API
 */
var feedbackApi = {
  submit: function submit(content, images) {
    return instance.post('/feedback', {
      content: content,
      images: images
    });
  }
};

/**
 * 施工照片 API
 * 推荐：uploadDirect（后端签名+前端直传 OSS）
 * 备用：upload（经后端代理上传）
 */
var constructionPhotoApi = {
  /** 获取 OSS 直传 policy（后端签名） */
  getUploadPolicy: function getUploadPolicy(stage) {
    return instance.get('/oss/upload-policy', {
      params: {
        stage: stage
      }
    });
  },
  /** 直传 OSS 后注册照片 */
  register: function register(stage, key) {
    return instance.post('/construction-photos/register', {
      stage: stage,
      key: key
    });
  },
  /**
   * 后端签名 + 前端直传 OSS（阿里云最佳实践）
   * 失败时自动回退到 upload 代理上传
   */
  uploadDirect: function () {
    var _uploadDirect = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee2(filePath, stage) {
      var policyRes, host, policy, OSSAccessKeyId, signature, dir, ext, key, _t2;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            _context2.p = 0;
            _context2.n = 1;
            return instance.get('/oss/upload-policy', {
              params: {
                stage: stage
              }
            });
          case 1:
            policyRes = _context2.v;
            host = policyRes.host, policy = policyRes.policy, OSSAccessKeyId = policyRes.OSSAccessKeyId, signature = policyRes.signature, dir = policyRes.dir;
            ext = (filePath.split('.').pop() || 'jpg').toLowerCase().replace('jpeg', 'jpg') || 'jpg';
            key = "".concat(dir).concat(Date.now(), "_").concat(Math.floor(Math.random() * 10000), ".").concat(ext);
            return _context2.a(2, new Promise(function (resolve, reject) {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().uploadFile({
                url: host,
                filePath: filePath,
                name: 'file',
                formData: {
                  key: key,
                  policy: policy,
                  OSSAccessKeyId: OSSAccessKeyId,
                  Signature: signature,
                  success_action_status: '200'
                },
                success: function () {
                  var _success = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee(res) {
                    var reg, _t;
                    return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
                      while (1) switch (_context.p = _context.n) {
                        case 0:
                          if (!(res.statusCode >= 200 && res.statusCode < 300)) {
                            _context.n = 5;
                            break;
                          }
                          _context.p = 1;
                          _context.n = 2;
                          return instance.post('/construction-photos/register', {
                            stage: stage,
                            key: key
                          });
                        case 2:
                          reg = _context.v;
                          resolve(reg !== null && reg !== void 0 && reg.file_url ? reg : {
                            file_url: "".concat(host, "/").concat(key)
                          });
                          _context.n = 4;
                          break;
                        case 3:
                          _context.p = 3;
                          _t = _context.v;
                          reject(_t);
                        case 4:
                          _context.n = 6;
                          break;
                        case 5:
                          reject(new Error(typeof res.data === 'string' ? res.data : "\u4E0A\u4F20\u5931\u8D25 ".concat(res.statusCode)));
                        case 6:
                          return _context.a(2);
                      }
                    }, _callee, null, [[1, 3]]);
                  }));
                  function success(_x3) {
                    return _success.apply(this, arguments);
                  }
                  return success;
                }(),
                fail: reject
              });
            }));
          case 2:
            _context2.p = 2;
            _t2 = _context2.v;
            return _context2.a(2, constructionPhotoApi.upload(filePath, stage));
        }
      }, _callee2, null, [[0, 2]]);
    }));
    function uploadDirect(_x, _x2) {
      return _uploadDirect.apply(this, arguments);
    }
    return uploadDirect;
  }(),
  /** 经后端代理上传（微信小程序 uploadFile 带 Token 走此路径） */
  upload: function upload(filePath, stage) {
    return new Promise(function (resolve, reject) {
      var base = (BASE_URL || '').replace(/\/$/, '');
      var url = appendAuthQuery("".concat(base, "/construction-photos/upload?stage=").concat(encodeURIComponent(stage)));
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().uploadFile({
        url: url,
        filePath: filePath,
        name: 'file',
        header: getAuthHeaders(),
        success: function success(res) {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            var msg = "\u4E0A\u4F20\u5931\u8D25 ".concat(res.statusCode);
            try {
              var _errData$detail, _d$;
              var errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
              var d = (_errData$detail = errData === null || errData === void 0 ? void 0 : errData.detail) !== null && _errData$detail !== void 0 ? _errData$detail : errData === null || errData === void 0 ? void 0 : errData.msg;
              if (typeof d === 'string' && d) msg = d;else if (Array.isArray(d) && (_d$ = d[0]) !== null && _d$ !== void 0 && _d$.msg) msg = d[0].msg;
              if (res.statusCode === 401) msg = '请先登录';
            } catch (_unused) {/* keep default msg */}
            reject(new Error(msg));
            return;
          }
          try {
            var _data$data;
            var data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
            var out = (_data$data = data === null || data === void 0 ? void 0 : data.data) !== null && _data$data !== void 0 ? _data$data : data;
            resolve(out !== null && out !== void 0 && out.file_url ? out : {
              file_url: out
            });
          } catch (_unused2) {
            reject(new Error('解析失败'));
          }
        },
        fail: function fail(err) {
          return reject(err instanceof Error ? err : new Error((err === null || err === void 0 ? void 0 : err.errMsg) || (err === null || err === void 0 ? void 0 : err.message) || '网络请求失败'));
        }
      });
    });
  },
  getList: function getList(stage) {
    return instance.get('/construction-photos', {
      params: stage ? {
        stage: stage
      } : {}
    });
  },
  delete: function _delete(photoId) {
    return instance.delete("/construction-photos/".concat(photoId));
  },
  move: function move(photoId, stage) {
    return instance.put("/construction-photos/".concat(photoId, "/move"), {
      stage: stage
    });
  }
};

/**
 * 验收分析 API
 * uploadPhoto 支持传入 auth，微信小程序 uploadFile 可能不传 header，URL query 为唯一可靠方式
 */
var acceptanceApi = {
  uploadPhoto: function uploadPhoto(filePath, auth) {
    var _auth$token, _auth$userId;
    var token = (_auth$token = auth === null || auth === void 0 ? void 0 : auth.token) !== null && _auth$token !== void 0 ? _auth$token : _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('access_token');
    var userId = (_auth$userId = auth === null || auth === void 0 ? void 0 : auth.userId) !== null && _auth$userId !== void 0 ? _auth$userId : _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().getStorageSync('user_id');
    var url = appendAuthToUrl("".concat(BASE_URL, "/acceptance/upload-photo"), token, userId);
    var headers = auth ? buildAuthHeaders(token, userId) : getAuthHeaders();
    // 微信 uploadFile 可能不传 header/query，formData 最可靠
    var formData = {};
    if (token) formData['access_token'] = token;
    if (userId != null && userId !== '' && String(userId).trim() !== '') formData['user_id'] = String(userId).trim();
    return new Promise(function (resolve, reject) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().uploadFile({
        url: url,
        filePath: filePath,
        name: 'file',
        formData: formData,
        header: headers,
        success: function success(res) {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            try {
              var _errData$detail2, _d$2;
              var errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
              var d = (_errData$detail2 = errData === null || errData === void 0 ? void 0 : errData.detail) !== null && _errData$detail2 !== void 0 ? _errData$detail2 : errData === null || errData === void 0 ? void 0 : errData.msg;
              var msg = typeof d === 'string' ? d : Array.isArray(d) && (_d$2 = d[0]) !== null && _d$2 !== void 0 && _d$2.msg ? d[0].msg : "\u4E0A\u4F20\u5931\u8D25 ".concat(res.statusCode);
              reject(new Error(res.statusCode === 401 ? '请先登录' : msg));
            } catch (_unused3) {
              reject(new Error("\u4E0A\u4F20\u5931\u8D25 ".concat(res.statusCode)));
            }
            return;
          }
          try {
            var _data$data2;
            var data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
            var out = (_data$data2 = data === null || data === void 0 ? void 0 : data.data) !== null && _data$data2 !== void 0 ? _data$data2 : data;
            resolve(out !== null && out !== void 0 && out.file_url ? out : {
              file_url: out
            });
          } catch (_unused4) {
            reject(new Error('解析失败'));
          }
        },
        fail: function fail(err) {
          return reject(err instanceof Error ? err : new Error((err === null || err === void 0 ? void 0 : err.errMsg) || (err === null || err === void 0 ? void 0 : err.message) || '网络请求失败'));
        }
      });
    });
  },
  analyze: function analyze(stage, fileUrls) {
    return instance.post('/acceptance/analyze', {
      stage: stage,
      file_urls: fileUrls
    });
  },
  getResult: function getResult(analysisId) {
    return instance.get("/acceptance/".concat(analysisId));
  },
  getList: function getList(params) {
    return instance.get('/acceptance', {
      params: params
    });
  }
};

/**
 * 报告导出 API
 */
var reportApi = {
  getExportPdfUrl: function getExportPdfUrl(reportType, resourceId) {
    return "".concat(BASE_URL, "/reports/export-pdf?report_type=").concat(reportType, "&resource_id=").concat(resourceId);
  },
  downloadPdf: function downloadPdf(reportType, resourceId, filename) {
    return new Promise(function (resolve, reject) {
      var baseUrl = "".concat(BASE_URL, "/reports/export-pdf?report_type=").concat(reportType, "&resource_id=").concat(resourceId);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().downloadFile({
        url: appendAuthQuery(baseUrl),
        header: getAuthHeaders(),
        success: function success(res) {
          if (res.statusCode === 200) {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_4___default().saveFile({
              tempFilePath: res.tempFilePath
            }).then(function (saveRes) {
              return resolve(saveRes.savedFilePath);
            }).catch(reject);
          } else reject(new Error('导出失败'));
        },
        fail: reject
      });
    });
  }
};
/* harmony default export */ __webpack_exports__["default"] = (instance);

/***/ }),

/***/ "./src/store/hooks.ts":
/*!****************************!*\
  !*** ./src/store/hooks.ts ***!
  \****************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   useAppDispatch: function() { return /* binding */ useAppDispatch; },
/* harmony export */   useAppSelector: function() { return /* binding */ useAppSelector; }
/* harmony export */ });
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react-redux */ "webpack/container/remote/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_0__);

var useAppDispatch = react_redux__WEBPACK_IMPORTED_MODULE_0__.useDispatch;
var useAppSelector = react_redux__WEBPACK_IMPORTED_MODULE_0__.useSelector;

/***/ }),

/***/ "./src/store/index.ts":
/*!****************************!*\
  !*** ./src/store/index.ts ***!
  \****************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _slices_userSlice__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./slices/userSlice */ "./src/store/slices/userSlice.ts");
/* harmony import */ var _slices_companySlice__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./slices/companySlice */ "./src/store/slices/companySlice.ts");
/* harmony import */ var _slices_quoteSlice__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./slices/quoteSlice */ "./src/store/slices/quoteSlice.ts");
/* harmony import */ var _slices_contractSlice__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./slices/contractSlice */ "./src/store/slices/contractSlice.ts");
/* harmony import */ var _slices_constructionSlice__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./slices/constructionSlice */ "./src/store/slices/constructionSlice.ts");
/* harmony import */ var _slices_orderSlice__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./slices/orderSlice */ "./src/store/slices/orderSlice.ts");
/* harmony import */ var _slices_networkSlice__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./slices/networkSlice */ "./src/store/slices/networkSlice.ts");








var store = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.configureStore)({
  reducer: {
    user: _slices_userSlice__WEBPACK_IMPORTED_MODULE_1__["default"],
    network: _slices_networkSlice__WEBPACK_IMPORTED_MODULE_7__["default"],
    company: _slices_companySlice__WEBPACK_IMPORTED_MODULE_2__["default"],
    quote: _slices_quoteSlice__WEBPACK_IMPORTED_MODULE_3__["default"],
    contract: _slices_contractSlice__WEBPACK_IMPORTED_MODULE_4__["default"],
    construction: _slices_constructionSlice__WEBPACK_IMPORTED_MODULE_5__["default"],
    order: _slices_orderSlice__WEBPACK_IMPORTED_MODULE_6__["default"]
  },
  middleware: function middleware(getDefaultMiddleware) {
    return getDefaultMiddleware({
      serializableCheck: false
    });
  }
});
/* harmony default export */ __webpack_exports__["default"] = (store);

/***/ }),

/***/ "./src/store/slices/companySlice.ts":
/*!******************************************!*\
  !*** ./src/store/slices/companySlice.ts ***!
  \******************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* unused harmony exports setCurrentScan, setScanHistory, addScanToHistory */
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

var initialState = {
  currentScan: null,
  scanHistory: []
};
var companySlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
  name: 'company',
  initialState: initialState,
  reducers: {
    setCurrentScan: function setCurrentScan(state, action) {
      state.currentScan = action.payload;
    },
    setScanHistory: function setScanHistory(state, action) {
      state.scanHistory = action.payload;
    },
    addScanToHistory: function addScanToHistory(state, action) {
      state.scanHistory.unshift(action.payload);
    }
  }
});
var _companySlice$actions = companySlice.actions,
  setCurrentScan = _companySlice$actions.setCurrentScan,
  setScanHistory = _companySlice$actions.setScanHistory,
  addScanToHistory = _companySlice$actions.addScanToHistory;

/* harmony default export */ __webpack_exports__["default"] = (companySlice.reducer);

/***/ }),

/***/ "./src/store/slices/constructionSlice.ts":
/*!***********************************************!*\
  !*** ./src/store/slices/constructionSlice.ts ***!
  \***********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* unused harmony exports setSchedule, updateSchedule */
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread2.js */ "./node_modules/@babel/runtime/helpers/esm/objectSpread2.js");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__);


var initialState = {
  schedule: null
};
var constructionSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__.createSlice)({
  name: 'construction',
  initialState: initialState,
  reducers: {
    setSchedule: function setSchedule(state, action) {
      state.schedule = action.payload;
    },
    updateSchedule: function updateSchedule(state, action) {
      if (state.schedule) {
        state.schedule = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])({}, state.schedule), action.payload);
      }
    }
  }
});
var _constructionSlice$ac = constructionSlice.actions,
  setSchedule = _constructionSlice$ac.setSchedule,
  updateSchedule = _constructionSlice$ac.updateSchedule;

/* harmony default export */ __webpack_exports__["default"] = (constructionSlice.reducer);

/***/ }),

/***/ "./src/store/slices/contractSlice.ts":
/*!*******************************************!*\
  !*** ./src/store/slices/contractSlice.ts ***!
  \*******************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* unused harmony exports setCurrentContract, setContractHistory, addContractToHistory */
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

var initialState = {
  currentContract: null,
  contractHistory: []
};
var contractSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
  name: 'contract',
  initialState: initialState,
  reducers: {
    setCurrentContract: function setCurrentContract(state, action) {
      state.currentContract = action.payload;
    },
    setContractHistory: function setContractHistory(state, action) {
      state.contractHistory = action.payload;
    },
    addContractToHistory: function addContractToHistory(state, action) {
      state.contractHistory.unshift(action.payload);
    }
  }
});
var _contractSlice$action = contractSlice.actions,
  setCurrentContract = _contractSlice$action.setCurrentContract,
  setContractHistory = _contractSlice$action.setContractHistory,
  addContractToHistory = _contractSlice$action.addContractToHistory;

/* harmony default export */ __webpack_exports__["default"] = (contractSlice.reducer);

/***/ }),

/***/ "./src/store/slices/networkSlice.ts":
/*!******************************************!*\
  !*** ./src/store/slices/networkSlice.ts ***!
  \******************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   setNetworkError: function() { return /* binding */ setNetworkError; }
/* harmony export */ });
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

var networkSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
  name: 'network',
  initialState: {
    error: false
  },
  reducers: {
    setNetworkError: function setNetworkError(state, action) {
      state.error = action.payload;
    }
  }
});
var setNetworkError = networkSlice.actions.setNetworkError;

/* harmony default export */ __webpack_exports__["default"] = (networkSlice.reducer);

/***/ }),

/***/ "./src/store/slices/orderSlice.ts":
/*!****************************************!*\
  !*** ./src/store/slices/orderSlice.ts ***!
  \****************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* unused harmony exports setCurrentOrder, setOrderHistory, addOrderToHistory */
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

var initialState = {
  currentOrder: null,
  orderHistory: []
};
var orderSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
  name: 'order',
  initialState: initialState,
  reducers: {
    setCurrentOrder: function setCurrentOrder(state, action) {
      state.currentOrder = action.payload;
    },
    setOrderHistory: function setOrderHistory(state, action) {
      state.orderHistory = action.payload;
    },
    addOrderToHistory: function addOrderToHistory(state, action) {
      state.orderHistory.unshift(action.payload);
    }
  }
});
var _orderSlice$actions = orderSlice.actions,
  setCurrentOrder = _orderSlice$actions.setCurrentOrder,
  setOrderHistory = _orderSlice$actions.setOrderHistory,
  addOrderToHistory = _orderSlice$actions.addOrderToHistory;

/* harmony default export */ __webpack_exports__["default"] = (orderSlice.reducer);

/***/ }),

/***/ "./src/store/slices/quoteSlice.ts":
/*!****************************************!*\
  !*** ./src/store/slices/quoteSlice.ts ***!
  \****************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* unused harmony exports setCurrentQuote, setQuoteHistory, addQuoteToHistory */
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__);

var initialState = {
  currentQuote: null,
  quoteHistory: []
};
var quoteSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_0__.createSlice)({
  name: 'quote',
  initialState: initialState,
  reducers: {
    setCurrentQuote: function setCurrentQuote(state, action) {
      state.currentQuote = action.payload;
    },
    setQuoteHistory: function setQuoteHistory(state, action) {
      state.quoteHistory = action.payload;
    },
    addQuoteToHistory: function addQuoteToHistory(state, action) {
      state.quoteHistory.unshift(action.payload);
    }
  }
});
var _quoteSlice$actions = quoteSlice.actions,
  setCurrentQuote = _quoteSlice$actions.setCurrentQuote,
  setQuoteHistory = _quoteSlice$actions.setQuoteHistory,
  addQuoteToHistory = _quoteSlice$actions.addQuoteToHistory;

/* harmony default export */ __webpack_exports__["default"] = (quoteSlice.reducer);

/***/ }),

/***/ "./src/store/slices/userSlice.ts":
/*!***************************************!*\
  !*** ./src/store/slices/userSlice.ts ***!
  \***************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   logout: function() { return /* binding */ logout; },
/* harmony export */   setUserInfo: function() { return /* binding */ setUserInfo; }
/* harmony export */ });
/* unused harmony export updateUserInfo */
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread2.js */ "./node_modules/@babel/runtime/helpers/esm/objectSpread2.js");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @reduxjs/toolkit */ "webpack/container/remote/@reduxjs/toolkit");
/* harmony import */ var _reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__);


var initialState = {
  userInfo: null,
  isLoggedIn: false
};
var userSlice = (0,_reduxjs_toolkit__WEBPACK_IMPORTED_MODULE_1__.createSlice)({
  name: 'user',
  initialState: initialState,
  reducers: {
    setUserInfo: function setUserInfo(state, action) {
      state.userInfo = action.payload;
      state.isLoggedIn = true;
    },
    logout: function logout(state) {
      state.userInfo = null;
      state.isLoggedIn = false;
    },
    updateUserInfo: function updateUserInfo(state, action) {
      if (state.userInfo) {
        state.userInfo = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_0__["default"])({}, state.userInfo), action.payload);
      }
    }
  }
});
var _userSlice$actions = userSlice.actions,
  setUserInfo = _userSlice$actions.setUserInfo,
  logout = _userSlice$actions.logout,
  updateUserInfo = _userSlice$actions.updateUserInfo;

/* harmony default export */ __webpack_exports__["default"] = (userSlice.reducer);

/***/ }),

/***/ "./src/utils/auth.ts":
/*!***************************!*\
  !*** ./src/utils/auth.ts ***!
  \***************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   checkLogin: function() { return /* binding */ checkLogin; }
/* harmony export */ });
/* unused harmony exports isLoggedIn, getToken, getUserId, clearLogin, saveLogin, isTokenExpired */
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_0__);
/**
 * 认证工具函数
 * 提供登录状态检查、登录跳转等功能
 */


/**
 * 检查用户是否已登录
 */
function isLoggedIn() {
  var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().getStorageSync('access_token');
  return !!token;
}

/**
 * 获取当前用户的Token
 */
function getToken() {
  return _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().getStorageSync('access_token') || null;
}

/**
 * 获取当前用户的ID
 */
function getUserId() {
  var userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().getStorageSync('user_id');
  return userId ? Number(userId) : null;
}

/**
 * 检查登录状态，如果未登录则提示并跳转
 * @param showModal 是否显示确认弹窗（默认true）
 * @param redirectTo 跳转目标（默认"我的"页面）
 * @returns 是否已登录
 */
function checkLogin() {
  var showModal = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;
  var redirectTo = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 'profile';
  if (isLoggedIn()) {
    return true;
  }
  if (showModal) {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().showModal({
      title: '需要登录',
      content: '此功能需要登录，是否前往登录？',
      confirmText: '去登录',
      cancelText: '取消',
      success: function success(res) {
        if (res.confirm) {
          if (redirectTo === 'profile') {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().switchTab({
              url: '/pages/profile/index'
            });
          } else {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().switchTab({
              url: '/pages/index/index'
            });
          }
        }
      }
    });
  }
  return false;
}

/**
 * 清除登录信息
 */
function clearLogin() {
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().removeStorageSync('access_token');
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().removeStorageSync('user_id');
}

/**
 * 保存登录信息
 */
function saveLogin(token, userId) {
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().setStorageSync('access_token', token);
  _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().setStorageSync('user_id', String(userId));
}

/**
 * 检查Token是否过期（简单检查，实际过期由后端401判断）
 * @returns 是否可能过期（true表示可能过期，需要重新登录）
 */
function isTokenExpired() {
  var token = getToken();
  if (!token) return true;
  try {
    // JWT Token格式：header.payload.signature
    var parts = token.split('.');
    if (parts.length !== 3) return true;

    // 解码payload
    var payload = JSON.parse(decodeURIComponent(atob(parts[1]).split('').map(function (c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join('')));

    // 检查过期时间（exp是秒级时间戳）
    if (payload.exp) {
      var expTime = payload.exp * 1000; // 转换为毫秒
      var now = Date.now();
      // 提前5分钟判定为过期
      return expTime - now < 300000;
    }
    return false;
  } catch (error) {
    console.error('Token解析失败:', error);
    return true;
  }
}

/***/ }),

/***/ "./src/utils/constructionStage.ts":
/*!****************************************!*\
  !*** ./src/utils/constructionStage.ts ***!
  \****************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   STAGE_STATUS_STORAGE_KEY: function() { return /* binding */ STAGE_STATUS_STORAGE_KEY; },
/* harmony export */   getBackendStageCode: function() { return /* binding */ getBackendStageCode; },
/* harmony export */   getCompletionPayload: function() { return /* binding */ getCompletionPayload; },
/* harmony export */   mapBackendStageStatus: function() { return /* binding */ mapBackendStageStatus; },
/* harmony export */   persistStageStatusToStorage: function() { return /* binding */ persistStageStatusToStorage; }
/* harmony export */ });
/* unused harmony exports STAGE_KEY_TO_BACKEND, BACKEND_STAGE_TO_KEY */
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_1__);


var STAGE_STATUS_STORAGE_KEY = 'construction_stage_status';
var STAGE_KEY_TO_BACKEND = {
  material: 'S00',
  plumbing: 'S01',
  carpentry: 'S02',
  woodwork: 'S03',
  painting: 'S04',
  installation: 'S05'
};
var BACKEND_STAGE_TO_KEY = Object.fromEntries(Object.entries(STAGE_KEY_TO_BACKEND).map(function (_ref) {
  var _ref2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_ref, 2),
    key = _ref2[0],
    value = _ref2[1];
  return [value, key];
}));
var getBackendStageCode = function getBackendStageCode(stageKey) {
  return STAGE_KEY_TO_BACKEND[stageKey] || stageKey;
};
var getCompletionPayload = function getCompletionPayload(stageKey) {
  return stageKey === 'material' ? 'checked' : 'passed';
};
var mapBackendStageStatus = function mapBackendStageStatus(raw, stageKey) {
  if (!raw) return stageKey === 'material' ? 'in_progress' : 'pending';
  var normalized = String(raw !== null && raw !== void 0 ? raw : '').toLowerCase();
  if (['checked', 'passed', 'completed'].includes(normalized)) return 'completed';
  if (['rectify', 'need_rectify', 'pending_recheck'].includes(normalized)) return 'rectify';
  if (['in_progress', 'checking'].includes(normalized)) return 'in_progress';
  if (stageKey === 'material') return 'in_progress';
  return 'pending';
};
var persistStageStatusToStorage = function persistStageStatusToStorage(stageKey, backendStatus) {
  try {
    var raw = _tarojs_taro__WEBPACK_IMPORTED_MODULE_1___default().getStorageSync(STAGE_STATUS_STORAGE_KEY);
    var current = raw ? JSON.parse(raw) : {};
    current[stageKey] = mapBackendStageStatus(backendStatus, stageKey);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_1___default().setStorageSync(STAGE_STATUS_STORAGE_KEY, JSON.stringify(current));
  } catch (_unused) {
    // ignore storage failures
  }
};

/***/ }),

/***/ "./src/utils/navigation.ts":
/*!*********************************!*\
  !*** ./src/utils/navigation.ts ***!
  \*********************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TAB_CONSTRUCTION: function() { return /* binding */ TAB_CONSTRUCTION; },
/* harmony export */   TAB_HOME: function() { return /* binding */ TAB_HOME; },
/* harmony export */   safeSwitchTab: function() { return /* binding */ safeSwitchTab; }
/* harmony export */ });
/* unused harmony export TAB_PROFILE */
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_0__);

var TAB_HOME = '/pages/index/index';
var TAB_CONSTRUCTION = '/pages/construction/index';
var TAB_PROFILE = '/pages/profile/index';

/** Delay (ms) before switchTab to avoid timeout when called from modal/actionSheet/toast */
var DEFER_MS = 120;
/** Retry delay (ms) if first switchTab fails with timeout */
var RETRY_MS = 300;

/**
 * WeChat Mini Program switchTab can fail with "switchTab:fail timeout" when:
 * - Called synchronously from modal/actionSheet/toast success callback
 * - Target tab page is slow to load
 * This helper defers the call and retries once on failure.
 */
function safeSwitchTab(url) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  var _options$defer = options.defer,
    defer = _options$defer === void 0 ? DEFER_MS : _options$defer,
    _options$retry = options.retry,
    retry = _options$retry === void 0 ? true : _options$retry;
  var doSwitch = function doSwitch() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().switchTab({
      url: url,
      fail: function fail(err) {
        var _err$errMsg;
        if (retry && err !== null && err !== void 0 && (_err$errMsg = err.errMsg) !== null && _err$errMsg !== void 0 && _err$errMsg.includes('timeout')) {
          setTimeout(function () {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_0___default().switchTab({
              url: url
            });
          }, RETRY_MS);
        }
      }
    });
  };
  if (defer > 0) {
    setTimeout(doSwitch, defer);
  } else {
    doSwitch();
  }
}

/***/ })

}]);
//# sourceMappingURL=common.js.map