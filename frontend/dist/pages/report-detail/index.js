"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/report-detail/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/report-detail/index!./src/pages/report-detail/index.tsx":
/*!********************************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/report-detail/index!./src/pages/report-detail/index.tsx ***!
  \********************************************************************************************************************************/
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
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__);









var RISK_TEXT = {
  high: '⚠️ 高风险',
  warning: '⚠️ 1项警告',
  compliant: '✅ 合规'
};

/** 将后端合同分析结果转为报告页用的 { tag, text } 列表 */
function mapContractToItems(data) {
  var items = [];
  (data.risk_items || []).forEach(function (it) {
    var tag = it.risk_level === 'high' ? '风险条款' : '警告';
    items.push({
      tag: tag,
      text: (it.term || it.description || '').slice(0, 120)
    });
  });
  (data.unfair_terms || []).forEach(function (it) {
    items.push({
      tag: '霸王条款',
      text: (it.term || it.description || '').slice(0, 120)
    });
  });
  (data.missing_terms || []).forEach(function (it) {
    items.push({
      tag: '漏项',
      text: (it.term || it.reason || '').slice(0, 120)
    });
  });
  (data.suggested_modifications || []).forEach(function (it) {
    items.push({
      tag: '建议',
      text: (it.modified || it.reason || '').slice(0, 120)
    });
  });
  return items;
}

/**
 * P06/P08/P11-P13 报告详情/预览页 - 30%预览+灰色遮挡+解锁
 * 合同类型时拉取 GET /contracts/contract/:id，与后端字段 risk_level/risk_items/unfair_terms 等对齐
 */
var ReportDetailPage = function ReportDetailPage() {
  var _Taro$getCurrentInsta, _report$items$slice, _report$items, _report$items$slice2, _report$items2;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(null),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState, 2),
    report = _useState2[0],
    setReport = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(false),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState3, 2),
    unlocked = _useState4[0],
    setUnlocked = _useState4[1];
  var _ref = ((_Taro$getCurrentInsta = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getCurrentInstance().router) === null || _Taro$getCurrentInsta === void 0 ? void 0 : _Taro$getCurrentInsta.params) || {},
    type = _ref.type,
    scanId = _ref.scanId,
    name = _ref.name;
  var titles = {
    company: '公司风险报告',
    quote: '报价单分析报告',
    contract: '合同审核报告'
  };
  var allItems = {
    company: [{
      tag: '高风险',
      text: '该公司存在多起法律纠纷记录'
    }, {
      tag: '警告',
      text: '注册资本较低，建议谨慎合作'
    }, {
      tag: '合规',
      text: '工商信息正常'
    }, {
      tag: '建议',
      text: '建议实地考察并核实施工资质'
    }, {
      tag: '参考',
      text: '参考《民法典》第577条关于违约责任'
    }],
    quote: [{
      tag: '漏项',
      text: '防水工程未列入报价'
    }, {
      tag: '虚高',
      text: '水电改造单价高于市场均价20%'
    }, {
      tag: '建议',
      text: '建议补充吊顶材料品牌及规格'
    }, {
      tag: '省钱',
      text: '可比价3家后签订补充协议'
    }],
    contract: [{
      tag: '霸王条款',
      text: '乙方单方变更设计无需甲方同意'
    }, {
      tag: '陷阱',
      text: '保修期起算时间模糊'
    }, {
      tag: '建议',
      text: '建议明确增项上限比例'
    }, {
      tag: '法条',
      text: '参考《民法典》第496条格式条款'
    }]
  };
  (0,react__WEBPACK_IMPORTED_MODULE_3__.useEffect)(function () {
    var key = "report_unlocked_".concat(type, "_").concat(scanId || '0');
    setUnlocked(!!_tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync(key));
    if (type === 'contract' && scanId) {
      _services_api__WEBPACK_IMPORTED_MODULE_6__.contractApi.getAnalysis(Number(scanId)).then(function (res) {
        var _res$data;
        var data = (_res$data = res === null || res === void 0 ? void 0 : res.data) !== null && _res$data !== void 0 ? _res$data : res;
        var riskLevel = data.risk_level || 'compliant';
        var items = mapContractToItems(data);
        var previewCount = Math.max(1, Math.ceil(items.length * 0.3));
        setReport({
          time: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '—',
          reportNo: 'R-C-' + (data.id || scanId),
          riskLevel: riskLevel,
          riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
          items: items.length ? items : allItems.contract,
          previewCount: previewCount,
          summary: data.summary
        });
      }).catch(function () {
        var riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)];
        var items = allItems.contract;
        setReport({
          time: '—',
          reportNo: 'R-C-' + scanId,
          riskLevel: riskLevel,
          riskText: RISK_TEXT[riskLevel],
          items: items,
          previewCount: Math.ceil(items.length * 0.3) || 1
        });
      });
      return;
    }
    var riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)];
    var items = allItems[type] || allItems.company;
    var previewCount = Math.ceil(items.length * 0.3) || 1;
    setReport({
      time: '2026-01-19 10:25',
      reportNo: 'R' + Date.now().toString(36).toUpperCase(),
      riskLevel: riskLevel,
      riskText: RISK_TEXT[riskLevel],
      items: items,
      previewCount: previewCount
    });
  }, [type, scanId]);
  var handleUnlock = function handleUnlock() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
      url: "/pages/report-unlock/index?type=".concat(type || 'company', "&scanId=").concat(scanId || 0, "&name=").concat(encodeURIComponent(name || ''))
    });
  };
  var handleSupervision = function handleSupervision() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
      url: '/pages/supervision/index'
    });
  };
  var handleExportPdf = /*#__PURE__*/function () {
    var _ref2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee() {
      var rt, rid, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            rt = type || 'company';
            rid = parseInt(String(scanId || 0), 10);
            if (!(!rid && rt !== 'company')) {
              _context.n = 1;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showModal({
              title: '无法导出',
              content: '当前报告无有效编号（R-C-0），无法导出。请到「我的」→「报告列表」中打开已分析成功的合同报告后再导出。',
              confirmText: '去列表',
              cancelText: '知道了',
              success: function success(res) {
                if (res.confirm) _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().navigateTo({
                  url: '/pages/report-list/index'
                });
              }
            });
            return _context.a(2);
          case 1:
            _context.p = 1;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showLoading({
              title: '导出中...'
            });
            _context.n = 2;
            return _services_api__WEBPACK_IMPORTED_MODULE_6__.reportApi.downloadPdf(rt, rid || 0);
          case 2:
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().hideLoading();
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
              title: '导出成功',
              icon: 'success'
            });
            _context.n = 4;
            break;
          case 3:
            _context.p = 3;
            _t = _context.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().hideLoading();
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
              title: '导出失败，请确保已解锁',
              icon: 'none'
            });
          case 4:
            return _context.a(2);
        }
      }, _callee, null, [[1, 3]]);
    }));
    return function handleExportPdf() {
      return _ref2.apply(this, arguments);
    };
  }();
  var handleRiskClick = function handleRiskClick(item) {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showModal({
      title: '风险解读',
      content: "".concat(item.text, "\n\n\u5173\u8054\uFF1A\u884C\u4E1A\u89C4\u8303\u53CA\u300A\u6C11\u6CD5\u5178\u300B\u76F8\u5173\u6761\u6B3E"),
      showCancel: false
    });
  };
  var previewItems = (_report$items$slice = report === null || report === void 0 || (_report$items = report.items) === null || _report$items === void 0 ? void 0 : _report$items.slice(0, report.previewCount)) !== null && _report$items$slice !== void 0 ? _report$items$slice : [];
  var lockedItems = (_report$items$slice2 = report === null || report === void 0 || (_report$items2 = report.items) === null || _report$items2 === void 0 ? void 0 : _report$items2.slice(report.previewCount)) !== null && _report$items$slice2 !== void 0 ? _report$items$slice2 : [];
  var showOverlay = !unlocked && lockedItems.length > 0;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.ScrollView, {
    scrollY: true,
    className: "report-detail-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "header",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "report-name",
        children: [titles[type || 'company'], " - ", name || '未命名']
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "gen-time",
        children: ["\u751F\u6210\u65F6\u95F4\uFF1A", report === null || report === void 0 ? void 0 : report.time]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "report-no",
        children: ["\u62A5\u544A\u7F16\u53F7\uFF1A", report === null || report === void 0 ? void 0 : report.reportNo]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "risk-badge ".concat(report === null || report === void 0 ? void 0 : report.riskLevel),
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "risk-text",
        children: report === null || report === void 0 ? void 0 : report.riskText
      })
    }), (report === null || report === void 0 ? void 0 : report.summary) && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "summary-wrap",
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
        className: "summary-text",
        children: report.summary
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "items-wrap",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "items",
        children: [previewItems.map(function (item, i) {
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "item",
            onClick: function onClick() {
              return handleRiskClick(item);
            },
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
              className: "tag ".concat(item.tag === '高风险' || item.tag === '霸王条款' || item.tag === '漏项' ? 'high' : item.tag === '警告' || item.tag === '虚高' || item.tag === '陷阱' ? 'warn' : 'ok'),
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
                children: item.tag
              })
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              className: "item-text",
              children: item.text
            })]
          }, i);
        }), unlocked && lockedItems.map(function (item, i) {
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "item",
            onClick: function onClick() {
              return handleRiskClick(item);
            },
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
              className: "tag ".concat(item.tag === '高风险' ? 'high' : item.tag === '警告' ? 'warn' : 'ok'),
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
                children: item.tag
              })
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              className: "item-text",
              children: item.text
            })]
          }, 'lock-' + i);
        })]
      }), showOverlay && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "content-overlay",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          className: "overlay-text",
          children: "\u89E3\u9501\u5B8C\u6574\u62A5\u544A\uFF0C\u67E5\u770B\u5168\u90E8\u5206\u6790\u5185\u5BB9"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          className: "overlay-hint",
          children: "\u672A\u89E3\u9501\u53EF\u80FD\u9057\u6F0F\u5173\u952E\u98CE\u9669\u4FE1\u606F"
        })]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "actions",
      children: !unlocked ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.Fragment, {
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "btn primary",
          onClick: handleUnlock,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            children: "\u89E3\u9501\u5B8C\u6574\u62A5\u544A"
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "btn secondary",
          onClick: handleSupervision,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            children: "\u54A8\u8BE2\u76D1\u7406"
          })
        })]
      }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.Fragment, {
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "btn primary",
          onClick: handleExportPdf,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            children: "\u5BFC\u51FAPDF"
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "btn secondary",
          onClick: handleSupervision,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            children: "\u54A8\u8BE2\u76D1\u7406"
          })
        })]
      })
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (ReportDetailPage);

/***/ }),

/***/ "./src/pages/report-detail/index.tsx":
/*!*******************************************!*\
  !*** ./src/pages/report-detail/index.tsx ***!
  \*******************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_report_detail_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/report-detail/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/report-detail/index!./src/pages/report-detail/index.tsx");


var config = {};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_report_detail_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/report-detail/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_report_detail_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/report-detail/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map