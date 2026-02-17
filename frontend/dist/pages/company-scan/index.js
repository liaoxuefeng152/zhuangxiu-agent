"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/company-scan/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/company-scan/index!./src/pages/company-scan/index.tsx":
/*!******************************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/company-scan/index!./src/pages/company-scan/index.tsx ***!
  \******************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js */ "./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../services/api */ "./src/services/api.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__);










var HISTORY_KEY = 'company_scan_history';
var MAX_HISTORY = 10;

/**
 * P03 公司名称输入页 - 装修公司风险检测（原型：历史记录、≥3字、已输入X/50字、手动提交二次确认）
 */
var CompanyScanPage = function CompanyScanPage() {
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(''),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState, 2),
    value = _useState2[0],
    setValue = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState3, 2),
    focus = _useState4[0],
    setFocus = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)([]),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState5, 2),
    suggestions = _useState6[0],
    setSuggestions = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState7, 2),
    historyOpen = _useState8[0],
    setHistoryOpen = _useState8[1];
  var _useState9 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)([]),
    _useState0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState9, 2),
    historyList = _useState0[0],
    setHistoryList = _useState0[1];
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    var v = value.replace(/\s+/g, '').replace(/[^\u4e00-\u9fa5a-zA-Z]/g, '');
    if (v.length < 3) {
      setSuggestions([]);
      return;
    }
    _services_api__WEBPACK_IMPORTED_MODULE_7__.companyApi.search(v, 5).then(function (res) {
      var _res$list;
      var list = (_res$list = res === null || res === void 0 ? void 0 : res.list) !== null && _res$list !== void 0 ? _res$list : [];
      setSuggestions(list.map(function (x) {
        return x.name || x;
      }).filter(Boolean));
    }).catch(function () {
      return setSuggestions([]);
    });
  }, [value]);
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    try {
      var raw = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync(HISTORY_KEY);
      var arr = raw ? Array.isArray(raw) ? raw : JSON.parse(raw) : [];
      setHistoryList(arr.slice(0, MAX_HISTORY));
    } catch (_unused) {
      setHistoryList([]);
    }
  }, [historyOpen]);
  var normalizedValue = value.replace(/\s+/g, '').slice(0, 50);
  var canSubmit = normalizedValue.length >= 3;
  var charCount = normalizedValue.length;
  var handleInput = function handleInput(e) {
    var _e$detail;
    return setValue((((_e$detail = e.detail) === null || _e$detail === void 0 ? void 0 : _e$detail.value) || '').replace(/\s+/g, ' ').trim());
  };
  var handleClear = function handleClear() {
    return setValue('');
  };
  var handleSelectSuggestion = function handleSelectSuggestion(name) {
    setValue(name);
    setFocus(false);
  };
  var pushHistory = function pushHistory(name) {
    try {
      var raw = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync(HISTORY_KEY);
      var arr = raw ? Array.isArray(raw) ? raw : JSON.parse(raw) : [];
      var next = [{
        name: name,
        time: new Date().toISOString()
      }].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(arr.filter(function (x) {
        return x.name !== name;
      }))).slice(0, MAX_HISTORY);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync(HISTORY_KEY, JSON.stringify(next));
    } catch (_) {}
  };
  var removeHistory = function removeHistory(name) {
    var next = historyList.filter(function (x) {
      return x.name !== name;
    });
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync(HISTORY_KEY, JSON.stringify(next));
    setHistoryList(next);
  };
  var handleScan = /*#__PURE__*/function () {
    var _ref = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee() {
      var name, _ref2, _res$id, _res$data, res, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            if (canSubmit) {
              _context.n = 1;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '请输入有效公司名称',
              icon: 'none'
            });
            return _context.a(2);
          case 1:
            name = normalizedValue || value.trim();
            _context.p = 2;
            _context.n = 3;
            return (0,_services_api__WEBPACK_IMPORTED_MODULE_7__.postWithAuth)('/companies/scan', {
              company_name: name
            });
          case 3:
            res = _context.v;
            pushHistory(name);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('has_company_scan', true);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=".concat((_ref2 = (_res$id = res === null || res === void 0 ? void 0 : res.id) !== null && _res$id !== void 0 ? _res$id : res === null || res === void 0 || (_res$data = res.data) === null || _res$data === void 0 ? void 0 : _res$data.id) !== null && _ref2 !== void 0 ? _ref2 : 0, "&companyName=").concat(encodeURIComponent(name), "&type=company")
            });
            _context.n = 5;
            break;
          case 4:
            _context.p = 4;
            _t = _context.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('has_company_scan', true);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=0&companyName=".concat(encodeURIComponent(name), "&type=company")
            });
          case 5:
            return _context.a(2);
        }
      }, _callee, null, [[2, 4]]);
    }));
    return function handleScan() {
      return _ref.apply(this, arguments);
    };
  }();
  var handleManualSubmit = function handleManualSubmit() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showModal({
      title: '确认提交？',
      content: '人工检测将在1-2个工作日完成，结果将推送至消息中心',
      success: function success(r) {
        if (r.confirm) {
          pushHistory(normalizedValue || value.trim());
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
            url: "/pages/scan-progress/index?scanId=0&companyName=".concat(encodeURIComponent(normalizedValue || value.trim()), "&type=company")
          });
        }
      }
    });
  };
  var handleRescan = /*#__PURE__*/function () {
    var _ref3 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee2(name) {
      var _ref4, _res$id2, _res$data2, res, _t2;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            setHistoryOpen(false);
            _context2.p = 1;
            _context2.n = 2;
            return (0,_services_api__WEBPACK_IMPORTED_MODULE_7__.postWithAuth)('/companies/scan', {
              company_name: name
            });
          case 2:
            res = _context2.v;
            pushHistory(name);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=".concat((_ref4 = (_res$id2 = res === null || res === void 0 ? void 0 : res.id) !== null && _res$id2 !== void 0 ? _res$id2 : res === null || res === void 0 || (_res$data2 = res.data) === null || _res$data2 === void 0 ? void 0 : _res$data2.id) !== null && _ref4 !== void 0 ? _ref4 : 0, "&companyName=").concat(encodeURIComponent(name), "&type=company")
            });
            _context2.n = 4;
            break;
          case 3:
            _context2.p = 3;
            _t2 = _context2.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
              url: "/pages/scan-progress/index?scanId=0&companyName=".concat(encodeURIComponent(name), "&type=company")
            });
          case 4:
            return _context2.a(2);
        }
      }, _callee2, null, [[1, 3]]);
    }));
    return function handleRescan(_x) {
      return _ref3.apply(this, arguments);
    };
  }();
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
    className: "company-scan-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "content",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "top-row",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "page-title",
          children: "\u88C5\u4FEE\u516C\u53F8\u68C0\u6D4B"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "history-link-top",
          onClick: function onClick() {
            return setHistoryOpen(true);
          },
          children: "\u5386\u53F2\u8BB0\u5F55"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "input-container",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "input-wrapper",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "search-icon",
            children: "\uD83D\uDD0D"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Input, {
            className: "input",
            placeholder: "\u8BF7\u8F93\u5165\u88C5\u4FEE\u516C\u53F8\u540D\u79F0/\u62FC\u97F3\u9996\u5B57\u6BCD",
            placeholderClass: "placeholder",
            value: value,
            onInput: handleInput,
            onFocus: function onFocus() {
              return setFocus(true);
            },
            onBlur: function onBlur() {
              return setTimeout(function () {
                return setFocus(false);
              }, 200);
            },
            maxlength: 50
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "char-count",
            children: ["\u5DF2\u8F93\u5165", charCount, "/50\u5B57"]
          }), value.length > 0 && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "clear-btn",
            onClick: handleClear,
            children: "\xD7"
          })]
        }), suggestions.length > 0 && focus && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "suggestions",
          children: suggestions.map(function (item) {
            return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "suggestion-item",
              onClick: function onClick() {
                return handleSelectSuggestion(item);
              },
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "main-text",
                children: item
              })
            }, item);
          })
        }), focus && suggestions.length === 0 && canSubmit && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "empty-suggest",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "empty-icon",
            children: "\uD83D\uDCED"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "empty-text",
            children: "\u672A\u627E\u5230\u76F8\u5173\u516C\u53F8\uFF0C\u8BF7\u6838\u5BF9\u540D\u79F0/\u5730\u533A"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "manual-btn",
            onClick: handleManualSubmit,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
              children: "\u624B\u52A8\u63D0\u4EA4\u68C0\u6D4B"
            })
          })]
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "scan-btn ".concat(canSubmit ? 'active' : 'disabled'),
        onClick: canSubmit ? handleScan : function () {
          return _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
            title: '请输入有效公司名称',
            icon: 'none'
          });
        },
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "btn-text",
          children: "\u5F00\u59CB\u68C0\u6D4B"
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "notice",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "notice-text",
          children: "\u68C0\u6D4B\u6570\u636E\u6765\u6E90\u4E8E\u516C\u5F00\u5DE5\u5546\u4FE1\u606F/\u6295\u8BC9\u5E73\u53F0\uFF0C\u4EC5\u4F9B\u53C2\u8003"
        })
      })]
    }), historyOpen && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "history-mask",
      onClick: function onClick() {
        return setHistoryOpen(false);
      },
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "history-modal",
        onClick: function onClick(e) {
          return e.stopPropagation();
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "history-title",
          children: "\u5386\u53F2\u8BB0\u5F55"
        }), historyList.length === 0 ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "history-empty",
          children: "\u6682\u65E0\u68C0\u6D4B\u8BB0\u5F55"
        }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.ScrollView, {
          scrollY: true,
          className: "history-list",
          children: historyList.map(function (item) {
            return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "history-item",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "history-name",
                children: item.name
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "history-actions",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "history-link",
                  onClick: function onClick() {
                    return handleRescan(item.name);
                  },
                  children: "\u91CD\u65B0\u68C0\u6D4B"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "history-link danger",
                  onClick: function onClick() {
                    return removeHistory(item.name);
                  },
                  children: "\u5220\u9664"
                })]
              })]
            }, item.name);
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "history-close",
          onClick: function onClick() {
            return setHistoryOpen(false);
          },
          children: "\u5173\u95ED"
        })]
      })
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (CompanyScanPage);

/***/ }),

/***/ "./src/pages/company-scan/index.tsx":
/*!******************************************!*\
  !*** ./src/pages/company-scan/index.tsx ***!
  \******************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_company_scan_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/company-scan/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/company-scan/index!./src/pages/company-scan/index.tsx");


var config = {"navigationBarTitleText":"公司风险检测","navigationBarBackgroundColor":"#1677FF","navigationBarTextStyle":"white","enablePullDownRefresh":true};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_company_scan_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/company-scan/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_company_scan_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/company-scan/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map