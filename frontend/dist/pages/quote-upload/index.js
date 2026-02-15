"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/quote-upload/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/quote-upload/index!./src/pages/quote-upload/index.tsx":
/*!******************************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/quote-upload/index!./src/pages/quote-upload/index.tsx ***!
  \******************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../services/api */ "./src/services/api.ts");
/* harmony import */ var _components_ExampleImageModal__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../components/ExampleImageModal */ "./src/components/ExampleImageModal/index.tsx");
/* harmony import */ var _config_assets__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../../config/assets */ "./src/config/assets.ts");
/* harmony import */ var _utils_auth__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../utils/auth */ "./src/utils/auth.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__);












/**
 * P05 上传报价单页
 */

var QuoteUploadPage = function QuoteUploadPage() {
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(null),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState, 2),
    file = _useState2[0],
    setFile = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(false),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState3, 2),
    showExample = _useState4[0],
    setShowExample = _useState4[1];
  var hasCompanyScan = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('has_company_scan');
  var showUploadMenu = function showUploadMenu() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showActionSheet({
      itemList: ['选择文件', '拍照上传'],
      success: function success(res) {
        if (res.tapIndex === 0) chooseFile();else takePhoto();
      },
      fail: function fail() {} // 用户取消不视为错误
    });
  };
  var chooseFile = function chooseFile() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'jpg', 'jpeg', 'png'],
      success: function success(res) {
        var f = res.tempFiles[0];
        if (f.size > 10 * 1024 * 1024) {
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
            title: '文件不能超过10MB',
            icon: 'none'
          });
          return;
        }
        setFile({
          path: f.path,
          name: f.name,
          size: f.size
        });
      },
      fail: function fail(err) {
        var _err$errMsg;
        if (!(err !== null && err !== void 0 && (_err$errMsg = err.errMsg) !== null && _err$errMsg !== void 0 && _err$errMsg.includes('cancel'))) _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
          title: '选择失败',
          icon: 'none'
        });
      }
    });
  };
  var takePhoto = function takePhoto() {
    var p = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().chooseImage({
      count: 1,
      sourceType: ['camera'],
      success: function success(res) {
        var path = res.tempFilePaths[0];
        setFile({
          path: path,
          name: "quote_".concat(Date.now(), ".jpg"),
          size: 0
        });
      },
      fail: function fail(err) {
        var _err$errMsg2;
        if (!(err !== null && err !== void 0 && (_err$errMsg2 = err.errMsg) !== null && _err$errMsg2 !== void 0 && _err$errMsg2.includes('cancel'))) _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
          title: '选择失败',
          icon: 'none'
        });
      }
    });
    if (p && typeof p.catch === 'function') p.catch(function () {});
  };
  var handleUpload = /*#__PURE__*/function () {
    var _ref = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee() {
      var _ref2, _res$task_id, userId, res, quoteId, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            if (file) {
              _context.n = 1;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
              title: '请先选择或拍摄文件',
              icon: 'none'
            });
            return _context.a(2);
          case 1:
            if ((0,_utils_auth__WEBPACK_IMPORTED_MODULE_9__.checkLogin)()) {
              _context.n = 2;
              break;
            }
            return _context.a(2);
          case 2:
            _context.p = 2;
            userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('user_id');
            _context.n = 3;
            return _services_api__WEBPACK_IMPORTED_MODULE_6__.quoteApi.upload(file.path, file.name);
          case 3:
            res = _context.v;
            quoteId = (_ref2 = (_res$task_id = res === null || res === void 0 ? void 0 : res.task_id) !== null && _res$task_id !== void 0 ? _res$task_id : res === null || res === void 0 ? void 0 : res.id) !== null && _ref2 !== void 0 ? _ref2 : 0;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=".concat(quoteId, "&companyName=&type=quote")
            });
            _context.n = 5;
            break;
          case 4:
            _context.p = 4;
            _t = _context.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=0&companyName=&type=quote"
            });
          case 5:
            return _context.a(2);
        }
      }, _callee, null, [[2, 4]]);
    }));
    return function handleUpload() {
      return _ref.apply(this, arguments);
    };
  }();
  var handleBack = function handleBack() {
    if (file) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showModal({
        title: '确认',
        content: '是否放弃上传？',
        success: function success(r) {
          if (r.confirm) _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateBack();
        }
      });
    } else {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateBack();
    }
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
    className: "upload-page",
    children: [!hasCompanyScan && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "warn-bar",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "warn-text",
        children: "\u26A0\uFE0F \u672A\u68C0\u6D4B\u88C5\u4FEE\u516C\u53F8\uFF0C\u5206\u6790\u7ED3\u679C\u53EF\u80FD\u5B58\u5728\u504F\u5DEE"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "link",
        onClick: function onClick() {
          return _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
            url: '/pages/company-scan/index'
          });
        },
        children: "\u7ACB\u5373\u68C0\u6D4B"
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "upload-area",
      onClick: showUploadMenu,
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "upload-icon",
        children: "\uD83D\uDCC4"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "upload-text",
        children: "\u70B9\u51FB\u4E0A\u4F20PDF/JPG/PNG"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "upload-hint",
        children: "\u5355\u6587\u4EF6\u226410MB"
      }), file && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "progress-bar-wrap",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "progress-fill",
          style: {
            width: '100%'
          }
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "example-link",
        onClick: function onClick(e) {
          e.stopPropagation();
          setShowExample(true);
        },
        children: "\u793A\u4F8B\u67E5\u770B"
      }), file && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "file-info",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          children: file.name
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          className: "change",
          onClick: function onClick(e) {
            e.stopPropagation();
            setFile(null);
          },
          children: "\u66F4\u6362\u6587\u4EF6"
        })]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
      className: "bottom-hint",
      children: "\u8BF7\u4E0A\u4F20\u6E05\u6670\u7684\u62A5\u4EF7\u5355\u539F\u4EF6\uFF0C\u5206\u6790\u7ED3\u679C\u66F4\u7CBE\u51C6"
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "btn primary full",
      onClick: handleUpload,
      style: {
        opacity: file ? 1 : 0.5
      },
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        children: "\u5F00\u59CB\u5206\u6790"
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_components_ExampleImageModal__WEBPACK_IMPORTED_MODULE_7__["default"], {
      visible: showExample,
      title: "\u62A5\u4EF7\u5355\u793A\u4F8B",
      content: "\u8BF7\u4E0A\u4F20\u5305\u542B\u9879\u76EE\u660E\u7EC6\u3001\u5355\u4EF7\u3001\u603B\u4EF7\u7684\u62A5\u4EF7\u5355\uFF0C\u683C\u5F0F\u6E05\u6670\u4FBF\u4E8EAI\u5206\u6790",
      imageUrl: _config_assets__WEBPACK_IMPORTED_MODULE_8__.EXAMPLE_IMAGES.quote,
      onClose: function onClose() {
        return setShowExample(false);
      }
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
      className: "privacy",
      children: "\u4E0A\u4F20\u6587\u4EF6\u4EC5\u7528\u4E8EAI\u5206\u6790\uFF0C\u672C\u5730\u52A0\u5BC6\u5B58\u50A8\uFF0C\u4E0D\u4F1A\u6CC4\u9732"
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (QuoteUploadPage);

/***/ }),

/***/ "./src/pages/quote-upload/index.tsx":
/*!******************************************!*\
  !*** ./src/pages/quote-upload/index.tsx ***!
  \******************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_quote_upload_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/quote-upload/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/quote-upload/index!./src/pages/quote-upload/index.tsx");


var config = {"navigationBarTitleText":"上传报价单"};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_quote_upload_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/quote-upload/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_quote_upload_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/quote-upload/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map