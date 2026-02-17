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
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../../services/api */ "./src/services/api.ts");
/* harmony import */ var _store_hooks__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../store/hooks */ "./src/store/hooks.ts");
/* harmony import */ var _store_slices_userSlice__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../store/slices/userSlice */ "./src/store/slices/userSlice.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__);









var MEMBER_PRICES = {
  member_month: 29.9,
  member_season: 69.9,
  member_year: 268
};
var MEMBER_NAMES = {
  member_month: '月卡',
  member_season: '季卡',
  member_year: '年卡'
};

/**
 * P28 支付确认页 - 报告解锁（走订单+确认支付）/ 会员开通 / 订单去支付
 */
var PaymentPage = function PaymentPage() {
  var _Taro$getCurrentInsta, _MEMBER_PRICES$member;
  var router = ((_Taro$getCurrentInsta = _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().getCurrentInstance().router) === null || _Taro$getCurrentInsta === void 0 ? void 0 : _Taro$getCurrentInsta.params) || {};
  var type = router.type,
    scanId = router.scanId,
    name = router.name,
    stage = router.stage,
    pkgParam = router.pkg,
    order_id = router.order_id,
    amount = router.amount;
  var isReportUnlock = !!(type && scanId !== undefined && scanId !== '');
  var isMembership = !!(pkgParam && String(pkgParam).startsWith('member_'));
  var isOrderPay = !!(order_id && Number(order_id) > 0);
  var dispatch = (0,_store_hooks__WEBPACK_IMPORTED_MODULE_5__.useAppDispatch)();
  var userInfo = (0,_store_hooks__WEBPACK_IMPORTED_MODULE_5__.useAppSelector)(function (state) {
    return state.user.userInfo;
  });
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState, 2),
    loading = _useState2[0],
    setLoading = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(0),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState3, 2),
    orderAmount = _useState4[0],
    setOrderAmount = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState5, 2),
    orderLoaded = _useState6[0],
    setOrderLoaded = _useState6[1];
  var reportPrice = 9.9;
  var memberPkg = isMembership ? String(pkgParam).toLowerCase() : '';
  var memberPrice = (_MEMBER_PRICES$member = MEMBER_PRICES[memberPkg]) !== null && _MEMBER_PRICES$member !== void 0 ? _MEMBER_PRICES$member : 0;
  var displayPrice = isReportUnlock ? reportPrice : isMembership ? memberPrice : orderAmount;
  (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(function () {
    if (isOrderPay && order_id) {
      _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.getOrder(Number(order_id)).then(function (res) {
        var _res$data, _d$amount;
        var d = (_res$data = res === null || res === void 0 ? void 0 : res.data) !== null && _res$data !== void 0 ? _res$data : res;
        setOrderAmount(Number((_d$amount = d === null || d === void 0 ? void 0 : d.amount) !== null && _d$amount !== void 0 ? _d$amount : 0));
        setOrderLoaded(true);
      }).catch(function () {
        return setOrderLoaded(true);
      });
    } else {
      setOrderLoaded(true);
    }
  }, [isOrderPay, order_id]);
  var redirectReport = function redirectReport(t, sid, isAcceptance, stageVal) {
    if (isAcceptance && stageVal) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
        url: "/pages/acceptance/index?stage=".concat(stageVal)
      });
    } else {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
        url: "/pages/report-detail/index?type=".concat(t, "&scanId=").concat(sid, "&name=").concat(encodeURIComponent(name || ''))
      });
    }
  };
  var handleReportUnlock = function handleReportUnlock() {
    var t = type || 'company';
    var sid = String(scanId || '0');
    var resourceId = Number(sid);
    if (!resourceId && t !== 'company') {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
        title: '参数错误，请从报告列表重新进入',
        icon: 'none'
      });
      return;
    }
    setLoading(true);
    _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.createOrder({
      order_type: 'report_single',
      resource_type: t,
      resource_id: resourceId
    }).then(function (res) {
      var _res$data2, _d$order_id, _d$amount2;
      var d = (_res$data2 = res === null || res === void 0 ? void 0 : res.data) !== null && _res$data2 !== void 0 ? _res$data2 : res;
      var status = d === null || d === void 0 ? void 0 : d.status;
      var orderId = (_d$order_id = d === null || d === void 0 ? void 0 : d.order_id) !== null && _d$order_id !== void 0 ? _d$order_id : 0;
      if (status === 'completed' && orderId === 0) {
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync("report_unlocked_".concat(t, "_").concat(sid), true);
        if (t === 'acceptance' && stage) _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync("report_unlocked_acceptance_".concat(stage), true);
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
          title: '已免费解锁（会员）',
          icon: 'success'
        });
        setTimeout(function () {
          return redirectReport(t, sid, t === 'acceptance', stage);
        }, 1200);
        return;
      }
      setLoading(false);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showModal({
        title: '支付确认',
        content: "\u89E3\u9501\u6743\u76CA\uFF1A\u8BE6\u7EC6\u98CE\u9669\u5206\u6790\u3001PDF\u5BFC\u51FA\u3001\u5F8B\u5E08\u89E3\u8BFB\u30011\u5BF91\u5BA2\u670D\u7B54\u7591\uFF1B\n\u4EF7\u683C\uFF1A\xA5".concat((_d$amount2 = d === null || d === void 0 ? void 0 : d.amount) !== null && _d$amount2 !== void 0 ? _d$amount2 : reportPrice, "\uFF1B\n\u4E00\u7ECF\u89E3\u9501\u4E0D\u652F\u6301\u9000\u6B3E\uFF0CPDF\u5BFC\u51FA\u6C38\u4E45\u6709\u6548"),
        success: function success(modalRes) {
          if (modalRes.confirm && orderId > 0) {
            setLoading(true);
            _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.confirmPaid(orderId).then(function () {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync("report_unlocked_".concat(t, "_").concat(sid), true);
              if (t === 'acceptance' && stage) _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync("report_unlocked_acceptance_".concat(stage), true);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
                title: '解锁成功',
                icon: 'success',
                duration: 2000
              });
              setTimeout(function () {
                return redirectReport(t, sid, t === 'acceptance', stage);
              }, 1500);
            }).catch(function (err) {
              var _err$data;
              setLoading(false);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
                title: (err === null || err === void 0 || (_err$data = err.data) === null || _err$data === void 0 ? void 0 : _err$data.detail) || (err === null || err === void 0 ? void 0 : err.message) || '支付确认失败',
                icon: 'none'
              });
            });
          }
        }
      });
    }).catch(function (err) {
      var _ref, _err$data$detail, _err$data2;
      setLoading(false);
      var msg = (_ref = (_err$data$detail = err === null || err === void 0 || (_err$data2 = err.data) === null || _err$data2 === void 0 ? void 0 : _err$data2.detail) !== null && _err$data$detail !== void 0 ? _err$data$detail : err === null || err === void 0 ? void 0 : err.message) !== null && _ref !== void 0 ? _ref : '创建订单失败';
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
        title: String(msg),
        icon: 'none'
      });
    });
  };
  var handleMembership = function handleMembership() {
    var pkg = memberPkg || 'member_year';
    if (!MEMBER_PRICES[pkg]) return;
    setLoading(true);
    _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.createOrder({
      order_type: pkg
    }).then(function (res) {
      var _res$data3, _d$order_id2, _d$amount3;
      var d = (_res$data3 = res === null || res === void 0 ? void 0 : res.data) !== null && _res$data3 !== void 0 ? _res$data3 : res;
      var status = d === null || d === void 0 ? void 0 : d.status;
      var orderId = (_d$order_id2 = d === null || d === void 0 ? void 0 : d.order_id) !== null && _d$order_id2 !== void 0 ? _d$order_id2 : 0;
      if (status === 'completed' && orderId === 0) {
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync('is_member', true);
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
          title: '已是会员',
          icon: 'success'
        });
        setTimeout(function () {
          return _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
            url: '/pages/profile/index'
          });
        }, 1200);
        return;
      }
      setLoading(false);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showModal({
        title: '开通会员',
        content: "\u786E\u8BA4\u5F00\u901A".concat(MEMBER_NAMES[pkg] || pkg, "\uFF1F\xA5").concat((_d$amount3 = d === null || d === void 0 ? void 0 : d.amount) !== null && _d$amount3 !== void 0 ? _d$amount3 : MEMBER_PRICES[pkg], "\u3002\u652F\u4ED8\u540E\u7ACB\u5373\u751F\u6548\u3002"),
        success: function success(modalRes) {
          if (modalRes.confirm && orderId > 0) {
            setLoading(true);
            _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.confirmPaid(orderId).then(function () {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync('is_member', true);

              // 直接更新本地用户信息，避免调用可能失败的getProfile API
              // 使用可选链操作符安全访问userInfo属性
              dispatch((0,_store_slices_userSlice__WEBPACK_IMPORTED_MODULE_6__.setUserInfo)({
                userId: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.userId) || 0,
                openid: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.openid) || '',
                nickname: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.nickname) || '装修用户',
                avatarUrl: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.avatarUrl) || '',
                phone: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.phone) || '',
                phoneVerified: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.phoneVerified) || false,
                isMember: true
              }));
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
                title: '开通成功',
                icon: 'success',
                duration: 2000
              });
              setTimeout(function () {
                return _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
                  url: '/pages/profile/index'
                });
              }, 1500);
            }).catch(function (err) {
              var _err$data3;
              setLoading(false);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
                title: (err === null || err === void 0 || (_err$data3 = err.data) === null || _err$data3 === void 0 ? void 0 : _err$data3.detail) || '支付确认失败',
                icon: 'none'
              });
            });
          }
        }
      });
    }).catch(function (err) {
      var _err$data$detail2, _err$data4;
      setLoading(false);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
        title: (_err$data$detail2 = err === null || err === void 0 || (_err$data4 = err.data) === null || _err$data4 === void 0 ? void 0 : _err$data4.detail) !== null && _err$data$detail2 !== void 0 ? _err$data$detail2 : '创建订单失败',
        icon: 'none'
      });
    });
  };
  var handleOrderPay = function handleOrderPay() {
    var oid = Number(order_id);
    if (!oid) return;
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showModal({
      title: '支付确认',
      content: "\u786E\u8BA4\u652F\u4ED8 \xA5".concat(orderAmount, "\uFF1F"),
      success: function success(res) {
        if (res.confirm) {
          setLoading(true);
          _services_api__WEBPACK_IMPORTED_MODULE_4__.paymentApi.confirmPaid(oid).then(function () {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
              title: '支付成功',
              icon: 'success'
            });
            setTimeout(function () {
              return _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().redirectTo({
                url: '/pages/order-list/index'
              });
            }, 1500);
          }).catch(function (err) {
            var _err$data5;
            setLoading(false);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
              title: (err === null || err === void 0 || (_err$data5 = err.data) === null || _err$data5 === void 0 ? void 0 : _err$data5.detail) || '支付失败',
              icon: 'none'
            });
          });
        }
      }
    });
  };
  var handlePay = function handlePay() {
    if (loading) return;
    if (isReportUnlock) return handleReportUnlock();
    if (isMembership) return handleMembership();
    if (isOrderPay) return handleOrderPay();
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
      title: '参数错误',
      icon: 'none'
    });
  };
  var title = isReportUnlock ? '解锁本份报告' : isMembership ? "\u5F00\u901A".concat(MEMBER_NAMES[memberPkg] || '会员') : '订单支付';
  var btnText = isReportUnlock ? "\u7ACB\u5373\u89E3\u9501 \xA5".concat(displayPrice) : isMembership ? "\u7ACB\u5373\u5F00\u901A \xA5".concat(displayPrice) : "\u7ACB\u5373\u652F\u4ED8 \xA5".concat(displayPrice);
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
    className: "payment-page",
    children: [isReportUnlock && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "benefits",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u8BE6\u7EC6\u98CE\u9669\u5206\u6790\u53CA\u6574\u6539\u5EFA\u8BAE"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u62A5\u544APDF\u5BFC\u51FA\u6743\u9650"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u4E13\u4E1A\u5F8B\u5E08\u89E3\u8BFB\uFF08\u6587\u5B57\u7248\uFF09"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 1\u5BF91\u5BA2\u670D\u7B54\u7591\uFF087\u5929\u5185\uFF09"
      })]
    }), isMembership && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "benefits",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u6240\u6709\u62A5\u544A\u514D\u8D39\u89E3\u9501"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 6\u5927\u9636\u6BB5AI\u9A8C\u6536\u65E0\u9650\u6B21"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u4F1A\u5458\u4E13\u5C5E\u5BA2\u670D"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: "\u2705 \u6570\u636E\u56DE\u6536\u7AD9\u3001PDF\u5BFC\u51FA\u65E0\u9650\u5236"
      })]
    }), isOrderPay && orderLoaded && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "benefits",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: ["\u8BA2\u5355\u53F7\uFF1A", order_id]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        children: ["\u652F\u4ED8\u91D1\u989D\uFF1A\xA5", orderAmount]
      })]
    }), orderLoaded && !(isOrderPay && orderAmount <= 0) && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.Fragment, {
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "btn primary",
        onClick: handlePay,
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          children: loading ? '处理中...' : btnText
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_7__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        className: "tip",
        children: [isReportUnlock && '基础风控免费，扩展内容付费。一经解锁不支持退款，PDF导出永久有效', isMembership && '会员开通后立即生效，支持7天无理由退款（未使用权益）', isOrderPay && '支付成功后订单状态将更新']
      })]
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