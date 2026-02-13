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

  // 优先使用result_json中的数据，如果没有则使用顶层字段
  var resultJson = data.result_json || {};
  var riskItems = resultJson.risk_items || data.risk_items || [];
  var unfairTerms = resultJson.unfair_terms || data.unfair_terms || [];
  var missingTerms = resultJson.missing_terms || data.missing_terms || [];
  var suggestedModifications = resultJson.suggested_modifications || data.suggested_modifications || [];

  // 风险项
  riskItems.forEach(function (it) {
    var tag = it.risk_level === 'high' ? '风险条款' : '警告';
    var text = "".concat(it.term || '', "\uFF1A").concat(it.description || '');
    items.push({
      tag: tag,
      text: text.slice(0, 120)
    });
  });

  // 霸王条款
  unfairTerms.forEach(function (it) {
    var text = "".concat(it.term || '', "\uFF1A").concat(it.description || '');
    items.push({
      tag: '霸王条款',
      text: text.slice(0, 120)
    });
  });

  // 漏项
  missingTerms.forEach(function (it) {
    var text = "".concat(it.term || '', "\uFF08").concat(it.importance || '中', "\uFF09\uFF1A").concat(it.reason || '');
    items.push({
      tag: '漏项',
      text: text.slice(0, 120)
    });
  });

  // 建议修改
  suggestedModifications.forEach(function (it) {
    var text = "".concat(it.modified || '', "\uFF1A").concat(it.reason || '');
    items.push({
      tag: '建议',
      text: text.slice(0, 120)
    });
  });
  return items;
}

/** 将后端报价单分析结果转为报告页用的 { tag, text } 列表 */
function mapQuoteToItems(data) {
  var items = [];

  // 优先使用result_json中的数据，如果没有则使用顶层字段
  var resultJson = data.result_json || {};
  var highRiskItems = resultJson.high_risk_items || data.high_risk_items || [];
  var warningItems = resultJson.warning_items || data.warning_items || [];
  var missingItems = resultJson.missing_items || data.missing_items || [];
  var overpricedItems = resultJson.overpriced_items || data.overpriced_items || [];
  var suggestions = resultJson.suggestions || data.suggestions || [];

  // 高风险项 -> "漏项"或"高风险"
  highRiskItems.forEach(function (it) {
    var tag = it.category === '漏项' ? '漏项' : '高风险';
    var text = "".concat(it.item || '', "\uFF1A").concat(it.description || '').concat(it.impact ? "\uFF08".concat(it.impact, "\uFF09") : '');
    items.push({
      tag: tag,
      text: text.slice(0, 120)
    });
  });

  // 警告项 -> "警告"或"虚高"
  warningItems.forEach(function (it) {
    var tag = it.category === '虚高' ? '虚高' : '警告';
    var text = "".concat(it.item || '', "\uFF1A").concat(it.description || '');
    items.push({
      tag: tag,
      text: text.slice(0, 120)
    });
  });

  // 漏项
  missingItems.forEach(function (it) {
    var text = "".concat(it.item || '', "\uFF08").concat(it.importance || '中', "\uFF09\uFF1A").concat(it.reason || '');
    items.push({
      tag: '漏项',
      text: text.slice(0, 120)
    });
  });

  // 虚高项
  overpricedItems.forEach(function (it) {
    var text = "".concat(it.item || '', "\uFF1A\u62A5\u4EF7").concat(it.quoted_price || '', "\u5143\uFF0C").concat(it.market_ref_price || '', "\uFF0C").concat(it.price_diff || '');
    items.push({
      tag: '虚高',
      text: text.slice(0, 120)
    });
  });

  // 建议
  suggestions.forEach(function (suggestion) {
    items.push({
      tag: '建议',
      text: suggestion.slice(0, 120)
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

    // 合同类型：调用API获取分析结果
    if (type === 'contract' && scanId) {
      // 检查scanId是否有效（必须大于0）
      var contractId = Number(scanId);
      if (!contractId || contractId <= 0) {
        console.warn('获取合同分析结果失败: 无效的合同ID', scanId);
        // 使用默认数据
        var _riskLevel = 'compliant';
        var _items = allItems.contract;
        setReport({
          time: '—',
          reportNo: 'R-C-' + (scanId || '0'),
          riskLevel: _riskLevel,
          riskText: RISK_TEXT[_riskLevel],
          items: _items,
          previewCount: Math.ceil(_items.length * 0.3) || 1
        });
        return;
      }

      // 检查是否已登录
      var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('access_token');
      if (!token) {
        console.warn('获取合同分析结果失败: 未登录');
        // 未登录时使用默认数据
        var _riskLevel2 = 'compliant';
        var _items2 = allItems.contract;
        setReport({
          time: '—',
          reportNo: 'R-C-' + scanId,
          riskLevel: _riskLevel2,
          riskText: RISK_TEXT[_riskLevel2],
          items: _items2,
          previewCount: Math.ceil(_items2.length * 0.3) || 1
        });
        return;
      }
      (0,_services_api__WEBPACK_IMPORTED_MODULE_6__.getWithAuth)("/contracts/contract/".concat(contractId)).then(function (data) {
        var _data$result_json;
        var riskLevel = data.risk_level || 'compliant';
        var items = mapContractToItems(data);
        var previewCount = Math.max(1, Math.ceil(items.length * 0.3));

        // 生成摘要：优先使用result_json中的summary，如果没有则使用顶层summary
        var summary = ((_data$result_json = data.result_json) === null || _data$result_json === void 0 ? void 0 : _data$result_json.summary) || data.summary || (items.length > 0 ? "\u53D1\u73B0".concat(items.length, "\u9879\u98CE\u9669\u548C\u5EFA\u8BAE") : '分析完成');
        setReport({
          time: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '—',
          reportNo: 'R-C-' + (data.id || scanId),
          riskLevel: riskLevel,
          riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
          items: items.length ? items : allItems.contract,
          previewCount: previewCount,
          summary: summary
        });
      }).catch(function (err) {
        var _err$response, _err$message;
        console.error('获取合同分析结果失败:', err);
        // 401错误表示未登录或token失效，不强制跳转
        if ((err === null || err === void 0 || (_err$response = err.response) === null || _err$response === void 0 ? void 0 : _err$response.status) === 401 || err !== null && err !== void 0 && (_err$message = err.message) !== null && _err$message !== void 0 && _err$message.includes('401')) {
          console.warn('获取合同分析结果失败: 认证失败');
        }
        // 失败时使用默认数据
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

    // 报价单类型：调用API获取分析结果
    if (type === 'quote' && scanId) {
      // 检查scanId是否有效（必须大于0）
      var quoteId = Number(scanId);
      if (!quoteId || quoteId <= 0 || isNaN(quoteId)) {
        console.warn('获取报价单分析结果失败: 无效的报价单ID', scanId);
        // 使用默认数据
        var _riskLevel3 = 'compliant';
        var _items3 = allItems.quote;
        setReport({
          time: '—',
          reportNo: 'R-Q-' + (scanId || '0'),
          riskLevel: _riskLevel3,
          riskText: RISK_TEXT[_riskLevel3],
          items: _items3,
          previewCount: Math.ceil(_items3.length * 0.3) || 1,
          summary: '无效的报价单ID'
        });
        return;
      }

      // 检查是否已登录
      var _token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('access_token');
      if (!_token) {
        console.warn('获取报价单分析结果失败: 未登录');
        // 未登录时使用默认数据
        var _riskLevel4 = 'compliant';
        var _items4 = allItems.quote;
        setReport({
          time: '—',
          reportNo: 'R-Q-' + scanId,
          riskLevel: _riskLevel4,
          riskText: RISK_TEXT[_riskLevel4],
          items: _items4,
          previewCount: Math.ceil(_items4.length * 0.3) || 1,
          summary: '请先登录后查看完整报告'
        });
        return;
      }
      (0,_services_api__WEBPACK_IMPORTED_MODULE_6__.getWithAuth)("/quotes/quote/".concat(quoteId)).then(function (data) {
        var _data$result_json2;
        // 根据risk_score确定风险等级：0-30低风险，31-60中等风险，61-100高风险
        var riskScore = data.risk_score || 0;
        var riskLevel;
        if (riskScore >= 61) {
          riskLevel = 'high';
        } else if (riskScore >= 31) {
          riskLevel = 'warning';
        } else {
          riskLevel = 'compliant';
        }
        var items = mapQuoteToItems(data);
        var previewCount = Math.max(1, Math.ceil(items.length * 0.3));

        // 生成摘要
        var summary = ((_data$result_json2 = data.result_json) === null || _data$result_json2 === void 0 || (_data$result_json2 = _data$result_json2.suggestions) === null || _data$result_json2 === void 0 ? void 0 : _data$result_json2[0]) || (items.length > 0 ? "\u53D1\u73B0".concat(items.length, "\u9879\u98CE\u9669\u548C\u5EFA\u8BAE") : '分析完成');
        setReport({
          time: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '—',
          reportNo: 'R-Q-' + (data.id || scanId),
          riskLevel: riskLevel,
          riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
          items: items.length ? items : allItems.quote,
          previewCount: previewCount,
          summary: summary
        });
      }).catch(function (err) {
        var _err$response2, _err$message2;
        console.error('获取报价单分析结果失败:', err);
        // 401错误表示未登录或token失效
        if ((err === null || err === void 0 || (_err$response2 = err.response) === null || _err$response2 === void 0 ? void 0 : _err$response2.status) === 401 || err !== null && err !== void 0 && (_err$message2 = err.message) !== null && _err$message2 !== void 0 && _err$message2.includes('401')) {
          console.warn('获取报价单分析结果失败: 认证失败');
          // 不强制跳转，使用默认数据继续显示
        }
        // 失败时使用默认数据
        var riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)];
        var items = allItems.quote;
        setReport({
          time: '—',
          reportNo: 'R-Q-' + scanId,
          riskLevel: riskLevel,
          riskText: RISK_TEXT[riskLevel],
          items: items,
          previewCount: Math.ceil(items.length * 0.3) || 1
        });
      });
      return;
    }

    // 其他类型（公司检测等）：使用默认数据
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