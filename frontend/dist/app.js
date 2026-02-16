require("./prebundle/vendors-node_modules_taro_weapp_prebundle_react-dom_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_chunk-IWKKQYBA_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_reduxjs_toolkit_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_chunk-IQGBDCAJ_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_react-redux_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_tarojs_plugin-framework-react_dist_runtime_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_axios-miniprogram-adapter_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_dayjs_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_tarojs_plugin-platform-weapp_dist_runtime_js.js");
require("./prebundle/node_modules_taro_weapp_prebundle_tarojs_runtime_js.js");
require("./prebundle/vendors-node_modules_taro_weapp_prebundle_chunk-RQETJ4ZT_js.js");
require("./prebundle/node_modules_taro_weapp_prebundle_tarojs_taro_js.js");
require("./prebundle/remoteEntry.js");
require("./prebundle/node_modules_taro_weapp_prebundle_react_jsx-runtime_js.js");
require("./prebundle/node_modules_taro_weapp_prebundle_react_js.js");

require("./common");
require("./vendors");
require("./taro");
require("./runtime");

(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["app"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=app!./src/app.tsx":
/*!************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=app!./src/app.tsx ***!
  \************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _process_shim__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./process-shim */ "./src/process-shim.ts");
/* harmony import */ var _process_shim__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_process_shim__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-redux */ "webpack/container/remote/react-redux");
/* harmony import */ var react_redux__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_redux__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _store__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./store */ "./src/store/index.ts");
/* harmony import */ var _store_slices_networkSlice__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./store/slices/networkSlice */ "./src/store/slices/networkSlice.ts");
/* harmony import */ var _components_NetworkError__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./components/NetworkError */ "./src/components/NetworkError/index.tsx");
/* harmony import */ var _config_env__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./config/env */ "./src/config/env.ts");
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./services/api */ "./src/services/api.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__);
/* provided dependency */ var window = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime")["window"];











/** 小程序页面销毁后定时器回调可能触发，导致 __subPageFrameEndTime__ of null；此处兜底吞掉该框架报错 */

function useSuppressSubPageFrameError() {
  react__WEBPACK_IMPORTED_MODULE_1__.useEffect(function () {
    var raw = typeof window !== 'undefined' && window.onerror;
    var handler = function handler(msg, url, line, col, err) {
      if (typeof msg === 'string' && msg.includes('__subPageFrameEndTime__')) return true;
      if (raw) return raw(msg, url, line, col, err);
      return false;
    };
    window.onerror = handler;
    return function () {
      window.onerror = raw;
    };
  }, []);
}

/** 小程序开发/体验版：无 token 时用 dev_weapp_mock 静默登录，便于在微信开发者工具里测试 */
function useDevSilentLogin() {
  react__WEBPACK_IMPORTED_MODULE_1__.useEffect(function () {
    if (false) // removed by dead control flow
{}
    var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().getStorageSync('token') || _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().getStorageSync('access_token');
    if (token) return;

    // 静默登录，失败时不提示用户（开发环境）
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().request({
      url: "".concat(_config_env__WEBPACK_IMPORTED_MODULE_7__.env.apiBaseUrl, "/users/login"),
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        code: 'dev_weapp_mock'
      }
    }).then(function (res) {
      var _data, _res$data, _d$access_token;
      var d = (_data = (_res$data = res.data) === null || _res$data === void 0 ? void 0 : _res$data.data) !== null && _data !== void 0 ? _data : res.data;
      var t = (_d$access_token = d === null || d === void 0 ? void 0 : d.access_token) !== null && _d$access_token !== void 0 ? _d$access_token : d === null || d === void 0 ? void 0 : d.token;
      var uid = d === null || d === void 0 ? void 0 : d.user_id;
      if (t && uid != null) {
        (0,_services_api__WEBPACK_IMPORTED_MODULE_8__.setAuthToken)(t, String(uid));
        console.log('[自动登录] 开发环境自动登录成功');
      } else {
        console.warn('[自动登录] 登录响应格式异常:', d);
      }
    }).catch(function (err) {
      // 开发环境记录错误日志，但不打扰用户
      console.error('[自动登录] 开发环境自动登录失败:', err);
      // 如果后端服务未启动，可以提示用户
      if (true) {
        console.warn('[自动登录] 提示：请确保后端服务已启动，或手动在"我的"页面登录');
      }
    });
  }, []);
}
function AppContent(_ref) {
  var children = _ref.children;
  useDevSilentLogin();
  useSuppressSubPageFrameError();
  var networkError = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useSelector)(function (s) {
    return s.network.error;
  });
  var dispatch = (0,react_redux__WEBPACK_IMPORTED_MODULE_3__.useDispatch)();
  var handleRetry = function handleRetry() {
    var _Taro$getCurrentInsta;
    dispatch((0,_store_slices_networkSlice__WEBPACK_IMPORTED_MODULE_5__.setNetworkError)(false));
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().reLaunch({
      url: ((_Taro$getCurrentInsta = _tarojs_taro__WEBPACK_IMPORTED_MODULE_2___default().getCurrentInstance().router) === null || _Taro$getCurrentInsta === void 0 ? void 0 : _Taro$getCurrentInsta.path) || '/pages/index/index'
    });
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.Fragment, {
    children: [children, /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_components_NetworkError__WEBPACK_IMPORTED_MODULE_6__["default"], {
      visible: networkError,
      onRetry: handleRetry
    })]
  });
}
function App(_ref2) {
  var children = _ref2.children;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(react_redux__WEBPACK_IMPORTED_MODULE_3__.Provider, {
    store: _store__WEBPACK_IMPORTED_MODULE_4__["default"],
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(AppContent, {
      children: children
    })
  });
}
/* harmony default export */ __webpack_exports__["default"] = (App);

/***/ }),

/***/ "./src/app.tsx":
/*!*********************!*\
  !*** ./src/app.tsx ***!
  \*********************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _tarojs_plugin_platform_weapp_dist_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/plugin-platform-weapp/dist/runtime */ "webpack/container/remote/@tarojs/plugin-platform-weapp/dist/runtime");
/* harmony import */ var _tarojs_plugin_platform_weapp_dist_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_plugin_platform_weapp_dist_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tarojs_plugin_framework_react_dist_runtime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/plugin-framework-react/dist/runtime */ "webpack/container/remote/@tarojs/plugin-framework-react/dist/runtime");
/* harmony import */ var _tarojs_plugin_framework_react_dist_runtime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_tarojs_plugin_framework_react_dist_runtime__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_app_app_tsx__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !!../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=app!./app.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=app!./src/app.tsx");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! react-dom */ "webpack/container/remote/react-dom");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_6__);











var config = {"pages":["pages/onboarding/index","pages/index/index","pages/company-scan/index","pages/scan-progress/index","pages/quote-upload/index","pages/contract-upload/index","pages/report-detail/index","pages/report-unlock/index","pages/report-list/index","pages/construction/index","pages/profile/index","pages/payment/index","pages/supervision/index","pages/guide/index","pages/settings/index","pages/neutral-statement/index","pages/account-notify/index","pages/about/index","pages/feedback/index","pages/contact/index","pages/photo/index","pages/photo-gallery/index","pages/acceptance/index","pages/material-check/index","pages/progress-share/index","pages/message/index","pages/order-list/index","pages/order-detail/index","pages/membership/index","pages/history/index","pages/network-error/index","pages/refund/index","pages/city-picker/index","pages/data-manage/index","pages/recycle-bin/index","pages/calendar/index","pages/privacy/index","pages/ai-supervision/index"],"window":{"backgroundTextStyle":"light","navigationBarBackgroundColor":"#fff","navigationBarTitleText":"装修避坑管家","navigationBarTextStyle":"black","backgroundColor":"#f5f5f5"},"tabBar":{"color":"#8C8C8C","selectedColor":"#1677FF","backgroundColor":"#fff","borderStyle":"black","list":[{"pagePath":"pages/index/index","text":"首页","iconPath":"assets/tabbar/home.png","selectedIconPath":"assets/tabbar/home-active.png"},{"pagePath":"pages/construction/index","text":"施工陪伴","iconPath":"assets/tabbar/construction.png","selectedIconPath":"assets/tabbar/construction-active.png"},{"pagePath":"pages/profile/index","text":"我的","iconPath":"assets/tabbar/profile.png","selectedIconPath":"assets/tabbar/profile-active.png"}]},"permission":{"scope.userLocation":{"desc":"你的位置信息将用于获取本地装修公司信息"}},"requiredPrivateInfos":["getLocation"],"usingComponents":{},"lazyCodeLoading":"requiredComponents"};
_tarojs_runtime__WEBPACK_IMPORTED_MODULE_1__.window.__taroAppConfig = config
var inst = App((0,_tarojs_plugin_framework_react_dist_runtime__WEBPACK_IMPORTED_MODULE_2__.createReactApp)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_app_app_tsx__WEBPACK_IMPORTED_MODULE_4__["default"], react__WEBPACK_IMPORTED_MODULE_5__, (react_dom__WEBPACK_IMPORTED_MODULE_6___default()), config))

;(0,_tarojs_taro__WEBPACK_IMPORTED_MODULE_3__.initPxTransform)({
  designWidth: 750,
  deviceRatio: {"640":1.17,"750":1,"828":0.905},
  baseFontSize: 20,
  unitPrecision: undefined,
  targetUnit: undefined
})


/***/ }),

/***/ "./src/components/NetworkError/index.tsx":
/*!***********************************************!*\
  !*** ./src/components/NetworkError/index.tsx ***!
  \***********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__);




/**
 * P32 网络异常提示 - 覆盖层，点击重试
 */

var NetworkError = function NetworkError(_ref) {
  var visible = _ref.visible,
    onRetry = _ref.onRetry;
  if (!visible) return null;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
    className: "network-error-mask",
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
      className: "network-error-content",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "error-icon",
        children: "\uD83D\uDCE1"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "error-text",
        children: "\u7F51\u7EDC\u5F02\u5E38\uFF0C\u8BF7\u68C0\u67E5\u7F51\u7EDC\u540E\u91CD\u8BD5"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
        className: "retry-btn",
        onClick: onRetry,
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
          children: "\u91CD\u8BD5 / \u5237\u65B0"
        })
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (NetworkError);

/***/ }),

/***/ "./src/process-shim.ts":
/*!*****************************!*\
  !*** ./src/process-shim.ts ***!
  \*****************************/
/***/ (function(__unused_webpack_module, __unused_webpack_exports, __webpack_require__) {

/**
 * 小程序运行时 process polyfill
 * 微信小程序无 process 对象，DefinePlugin 未替换到的 process.env 会报错
 */

var g = typeof globalThis !== 'undefined' ? globalThis : typeof __webpack_require__.g !== 'undefined' ? __webpack_require__.g : typeof self !== 'undefined' ? self : {};
if (g && typeof g.process === 'undefined') {
  g.process = {
    env: Object.create(null)
  };
}

/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/app.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);;;
//# sourceMappingURL=app.js.map