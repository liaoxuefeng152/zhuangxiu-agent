"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/payment/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/payment/index!./src/pages/payment/index.tsx":
/*!********************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/payment/index!./src/pages/payment/index.tsx ***!
  \********************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__);






/**
 * P28 完整报告解锁页
 */

var PaymentPage = function PaymentPage() {
  var _Taro$getCurrentInsta;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('single'),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState, 2),
    pkg = _useState2[0],
    setPkg = _useState2[1];
  var price = pkg === 'single' ? 9.9 : 25;
  var _ref = ((_Taro$getCurrentInsta = _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().getCurrentInstance().router) === null || _Taro$getCurrentInsta === void 0 ? void 0 : _Taro$getCurrentInsta.params) || {},
    type = _ref.type,
    scanId = _ref.scanId,
    name = _ref.name;
  var handleUnlock = function handleUnlock() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showModal({
      title: '支付确认',
      content: "\u89E3\u9501\u6743\u76CA\uFF1A\u8BE6\u7EC6\u98CE\u9669\u5206\u6790\u3001PDF\u5BFC\u51FA\u3001\u5F8B\u5E08\u89E3\u8BFB\u30011\u5BF91\u5BA2\u670D\u7B54\u7591\uFF1B\n\u4EF7\u683C\uFF1A\xA5".concat(price, "\uFF1B\n\u4E00\u7ECF\u89E3\u9501\u4E0D\u652F\u6301\u9000\u6B3E\uFF0CPDF\u5BFC\u51FA\u6C38\u4E45\u6709\u6548"),
      success: function success(res) {
        if (res.confirm) {
          var t = type || 'company';
          var sid = scanId || '0';
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync("report_unlocked_".concat(t, "_").concat(sid), true);
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
            title: '解锁成功',
            icon: 'success',
            duration: 2000
          });
          setTimeout(function () {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
              url: "/pages/report-detail/index?type=".concat(t, "&scanId=").concat(sid, "&name=").concat(encodeURIComponent(name || ''))
            });
          }, 1500);
        }
      }
    });
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
    className: "payment-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "benefits",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u8BE6\u7EC6\u98CE\u9669\u5206\u6790\u53CA\u6574\u6539\u5EFA\u8BAE"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u62A5\u544APDF\u5BFC\u51FA\u6743\u9650"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u4E13\u4E1A\u5F8B\u5E08\u89E3\u8BFB\uFF08\u6587\u5B57\u7248\uFF09"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 1\u5BF91\u5BA2\u670D\u7B54\u7591\uFF087\u5929\u5185\uFF09"
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "price-section",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "option ".concat(pkg === 'single' ? 'active' : ''),
        onClick: function onClick() {
          return setPkg('single');
        },
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          children: "\u5355\u4EFD\u62A5\u544A \xA59.9"
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "option ".concat(pkg === 'triple' ? 'active' : ''),
        onClick: function onClick() {
          return setPkg('triple');
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          children: "3\u4EFD\u62A5\u544A \xA525"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          className: "save",
          children: "\u7ACB\u7701\xA54.7"
        })]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "btn primary",
      onClick: handleUnlock,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: ["\u7ACB\u5373\u89E3\u9501 \xA5", price]
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
      className: "tip",
      children: "\u57FA\u7840\u98CE\u63A7\u514D\u8D39\uFF0C\u6269\u5C55\u5185\u5BB9\u4ED8\u8D39\u3002\u4E00\u7ECF\u89E3\u9501\u4E0D\u652F\u6301\u9000\u6B3E\uFF0CPDF\u5BFC\u51FA\u6C38\u4E45\u6709\u6548"
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (PaymentPage);

/***/ }),

/***/ "./src/pages/payment/index.tsx":
/*!*************************************!*\
  !*** ./src/pages/payment/index.tsx ***!
  \*************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_payment_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/payment/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/payment/index!./src/pages/payment/index.tsx");


var config = {};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_payment_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/payment/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_payment_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/payment/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map