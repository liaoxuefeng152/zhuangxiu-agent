"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/profile/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/profile/index!./src/pages/profile/index.tsx":
/*!********************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/profile/index!./src/pages/profile/index.tsx ***!
  \********************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _store_hooks__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../store/hooks */ "./src/store/hooks.ts");
/* harmony import */ var _store_slices_userSlice__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../store/slices/userSlice */ "./src/store/slices/userSlice.ts");
/* harmony import */ var _config_env__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../../config/env */ "./src/config/env.ts");
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../services/api */ "./src/services/api.ts");
/* harmony import */ var _utils_navigation__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../../utils/navigation */ "./src/utils/navigation.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__);













/**
 * P10 我的页面 - 个人数据聚合
 */

var Profile = function Profile() {
  var dispatch = (0,_store_hooks__WEBPACK_IMPORTED_MODULE_6__.useAppDispatch)();
  var userInfo = (0,_store_hooks__WEBPACK_IMPORTED_MODULE_6__.useAppSelector)(function (state) {
    return state.user.userInfo;
  });
  var isLoggedIn = (0,_store_hooks__WEBPACK_IMPORTED_MODULE_6__.useAppSelector)(function (state) {
    return state.user.isLoggedIn;
  });
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(0),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState, 2),
    companyScans = _useState2[0],
    setCompanyScans = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(0),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState3, 2),
    quoteCount = _useState4[0],
    setQuoteCount = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)(0),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState5, 2),
    contractCount = _useState6[0],
    setContractCount = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_3__.useState)([]),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_useState7, 2),
    reports = _useState8[0],
    setReports = _useState8[1];
  var base = _config_env__WEBPACK_IMPORTED_MODULE_8__.env.apiBaseUrl;

  /** 带认证头的请求（微信小程序下 axios 适配器可能不传 header，用 Taro.request 显式传参最稳） */
  var authHeader = function authHeader(token, userId) {
    return {
      Authorization: "Bearer ".concat(token),
      'X-User-Id': String(userId),
      'Content-Type': 'application/json'
    };
  };
  var loadUserInfo = /*#__PURE__*/function () {
    var _ref = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee(overrideToken, overrideUserId) {
      var _ref2;
      var token, userId, _data, _res$data, _u$user_id, res, raw, u, _u$user_id2, _u$openid, _u$nickname, _ref3, _u$avatar_url, _u$phone, _u$phone_verified, _ref4, _u$is_member, _u$points, expire, expireStr, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            token = (_ref2 = overrideToken !== null && overrideToken !== void 0 ? overrideToken : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('token')) !== null && _ref2 !== void 0 ? _ref2 : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('access_token');
            userId = overrideUserId !== null && overrideUserId !== void 0 ? overrideUserId : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('user_id');
            if (token) {
              _context.n = 1;
              break;
            }
            return _context.a(2);
          case 1:
            _context.p = 1;
            _context.n = 2;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().request({
              url: "".concat(base, "/users/profile"),
              method: 'GET',
              header: authHeader(token, userId != null ? String(userId) : '')
            });
          case 2:
            res = _context.v;
            raw = (_data = (_res$data = res.data) === null || _res$data === void 0 ? void 0 : _res$data.data) !== null && _data !== void 0 ? _data : res.data;
            u = raw;
            if (u && ((_u$user_id = u.user_id) !== null && _u$user_id !== void 0 ? _u$user_id : u.userId)) {
              expire = u.member_expire;
              expireStr = expire ? typeof expire === 'string' ? expire.slice(0, 10) : new Date(expire).toISOString().slice(0, 10) : undefined;
              dispatch((0,_store_slices_userSlice__WEBPACK_IMPORTED_MODULE_7__.setUserInfo)({
                userId: (_u$user_id2 = u.user_id) !== null && _u$user_id2 !== void 0 ? _u$user_id2 : u.userId,
                openid: (_u$openid = u.openid) !== null && _u$openid !== void 0 ? _u$openid : '',
                nickname: (_u$nickname = u.nickname) !== null && _u$nickname !== void 0 ? _u$nickname : '装修用户',
                avatarUrl: (_ref3 = (_u$avatar_url = u.avatar_url) !== null && _u$avatar_url !== void 0 ? _u$avatar_url : u.avatarUrl) !== null && _ref3 !== void 0 ? _ref3 : '',
                phone: (_u$phone = u.phone) !== null && _u$phone !== void 0 ? _u$phone : '',
                phoneVerified: (_u$phone_verified = u.phone_verified) !== null && _u$phone_verified !== void 0 ? _u$phone_verified : false,
                isMember: (_ref4 = (_u$is_member = u.is_member) !== null && _u$is_member !== void 0 ? _u$is_member : u.isMember) !== null && _ref4 !== void 0 ? _ref4 : false,
                memberExpire: expireStr,
                points: (_u$points = u.points) !== null && _u$points !== void 0 ? _u$points : 0
              }));
            }
            _context.n = 4;
            break;
          case 3:
            _context.p = 3;
            _t = _context.v;
          case 4:
            return _context.a(2);
        }
      }, _callee, null, [[1, 3]]);
    }));
    return function loadUserInfo(_x, _x2) {
      return _ref.apply(this, arguments);
    };
  }();
  var loadStats = /*#__PURE__*/function () {
    var _ref5 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee2(overrideToken, overrideUserId) {
      var _ref6;
      var token, userId, _s$total, _q$total, _c$total, h, _yield$Promise$all, _yield$Promise$all2, s, q, c, _t2;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            token = (_ref6 = overrideToken !== null && overrideToken !== void 0 ? overrideToken : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('token')) !== null && _ref6 !== void 0 ? _ref6 : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('access_token');
            userId = overrideUserId !== null && overrideUserId !== void 0 ? overrideUserId : _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getStorageSync('user_id');
            if (token) {
              _context2.n = 1;
              break;
            }
            return _context2.a(2);
          case 1:
            _context2.p = 1;
            // 一律用 Taro.request 并显式带鉴权，避免小程序下 axios 不传 header 导致 401
            h = authHeader(token, userId != null ? String(userId) : '');
            _context2.n = 2;
            return Promise.all([_tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().request({
              url: "".concat(base, "/companies/scans"),
              method: 'GET',
              header: h
            }).then(function (r) {
              var _ref7, _data2, _r$data;
              return (_ref7 = (_data2 = (_r$data = r.data) === null || _r$data === void 0 ? void 0 : _r$data.data) !== null && _data2 !== void 0 ? _data2 : r.data) !== null && _ref7 !== void 0 ? _ref7 : {};
            }), _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().request({
              url: "".concat(base, "/quotes/list"),
              method: 'GET',
              header: h
            }).then(function (r) {
              var _ref8, _data3, _r$data2;
              return (_ref8 = (_data3 = (_r$data2 = r.data) === null || _r$data2 === void 0 ? void 0 : _r$data2.data) !== null && _data3 !== void 0 ? _data3 : r.data) !== null && _ref8 !== void 0 ? _ref8 : {};
            }), _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().request({
              url: "".concat(base, "/contracts/list"),
              method: 'GET',
              header: h
            }).then(function (r) {
              var _ref9, _data4, _r$data3;
              return (_ref9 = (_data4 = (_r$data3 = r.data) === null || _r$data3 === void 0 ? void 0 : _r$data3.data) !== null && _data4 !== void 0 ? _data4 : r.data) !== null && _ref9 !== void 0 ? _ref9 : {};
            })]);
          case 2:
            _yield$Promise$all = _context2.v;
            _yield$Promise$all2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_yield$Promise$all, 3);
            s = _yield$Promise$all2[0];
            q = _yield$Promise$all2[1];
            c = _yield$Promise$all2[2];
            setCompanyScans((_s$total = s === null || s === void 0 ? void 0 : s.total) !== null && _s$total !== void 0 ? _s$total : 0);
            setQuoteCount((_q$total = q === null || q === void 0 ? void 0 : q.total) !== null && _q$total !== void 0 ? _q$total : 0);
            setContractCount((_c$total = c === null || c === void 0 ? void 0 : c.total) !== null && _c$total !== void 0 ? _c$total : 0);
            _context2.n = 4;
            break;
          case 3:
            _context2.p = 3;
            _t2 = _context2.v;
            setCompanyScans(0);
            setQuoteCount(0);
            setContractCount(0);
          case 4:
            return _context2.a(2);
        }
      }, _callee2, null, [[1, 3]]);
    }));
    return function loadStats(_x3, _x4) {
      return _ref5.apply(this, arguments);
    };
  }();
  (0,react__WEBPACK_IMPORTED_MODULE_3__.useEffect)(function () {
    if (isLoggedIn) {
      loadUserInfo();
      loadStats();
    }
  }, [isLoggedIn]);
  var handleLogin = /*#__PURE__*/function () {
    var _ref0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee3() {
      var _raw$data, _d$access_token, taroEnv, code, loginRes, res, raw, d, token, userId, statusOk, _d$openid, _d$nickname, _d$avatar_url, _d$is_member, _d$points, _ref1, _errRaw$detail, errRaw, errMsg, _ref10, _ref11, _ref12, _e$data$detail, _e$data, _e$data2, msg, _t3;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context3) {
        while (1) switch (_context3.p = _context3.n) {
          case 0:
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showLoading({
              title: '登录中...'
            });
            _context3.p = 1;
            // H5：Taro.login 不可用，用模拟登录。小程序：使用微信 code 真实登录
            taroEnv = typeof (_tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default()) !== 'undefined' ? _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getEnv() : '';
            if (!(taroEnv === 'h5')) {
              _context3.n = 2;
              break;
            }
            code = 'dev_h5_mock';
            _context3.n = 4;
            break;
          case 2:
            _context3.n = 3;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().login();
          case 3:
            loginRes = _context3.v;
            code = (loginRes === null || loginRes === void 0 ? void 0 : loginRes.code) || '';
          case 4:
            if (code) {
              _context3.n = 5;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().hideLoading();
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
              title: '获取登录凭证失败',
              icon: 'none'
            });
            return _context3.a(2);
          case 5:
            _context3.n = 6;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().request({
              url: "".concat(_config_env__WEBPACK_IMPORTED_MODULE_8__.env.apiBaseUrl, "/users/login"),
              method: 'POST',
              header: {
                'Content-Type': 'application/json'
              },
              data: {
                code: code
              }
            });
          case 6:
            res = _context3.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().hideLoading();
            raw = res.data;
            d = (_raw$data = raw === null || raw === void 0 ? void 0 : raw.data) !== null && _raw$data !== void 0 ? _raw$data : raw;
            token = (_d$access_token = d === null || d === void 0 ? void 0 : d.access_token) !== null && _d$access_token !== void 0 ? _d$access_token : d === null || d === void 0 ? void 0 : d.token;
            userId = d === null || d === void 0 ? void 0 : d.user_id;
            statusOk = res.statusCode >= 200 && res.statusCode < 300;
            if (token && userId != null && statusOk) {
              (0,_services_api__WEBPACK_IMPORTED_MODULE_9__.setAuthToken)(token, String(userId));
              dispatch((0,_store_slices_userSlice__WEBPACK_IMPORTED_MODULE_7__.setUserInfo)({
                userId: userId,
                openid: (_d$openid = d === null || d === void 0 ? void 0 : d.openid) !== null && _d$openid !== void 0 ? _d$openid : '',
                nickname: (_d$nickname = d === null || d === void 0 ? void 0 : d.nickname) !== null && _d$nickname !== void 0 ? _d$nickname : '装修用户',
                avatarUrl: (_d$avatar_url = d === null || d === void 0 ? void 0 : d.avatar_url) !== null && _d$avatar_url !== void 0 ? _d$avatar_url : '',
                phone: '',
                phoneVerified: false,
                isMember: (_d$is_member = d === null || d === void 0 ? void 0 : d.is_member) !== null && _d$is_member !== void 0 ? _d$is_member : false,
                points: (_d$points = d === null || d === void 0 ? void 0 : d.points) !== null && _d$points !== void 0 ? _d$points : 0
              }));
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
                title: '登录成功',
                icon: 'success'
              });
              // 用当前拿到的 token/userId 直接请求，不依赖 storage/拦截器，避免小程序 403/401
              loadUserInfo(token, String(userId));
              loadStats(token, String(userId));
            } else {
              errRaw = raw !== null && raw !== void 0 ? raw : res === null || res === void 0 ? void 0 : res.data;
              errMsg = (_ref1 = (_errRaw$detail = errRaw === null || errRaw === void 0 ? void 0 : errRaw.detail) !== null && _errRaw$detail !== void 0 ? _errRaw$detail : errRaw === null || errRaw === void 0 ? void 0 : errRaw.msg) !== null && _ref1 !== void 0 ? _ref1 : typeof errRaw === 'string' ? errRaw : '登录失败';
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
                title: typeof errMsg === 'string' ? errMsg : '登录失败',
                icon: 'none',
                duration: 3000
              });
            }
            _context3.n = 8;
            break;
          case 7:
            _context3.p = 7;
            _t3 = _context3.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().hideLoading();
            msg = (_ref10 = (_ref11 = (_ref12 = (_e$data$detail = _t3 === null || _t3 === void 0 || (_e$data = _t3.data) === null || _e$data === void 0 ? void 0 : _e$data.detail) !== null && _e$data$detail !== void 0 ? _e$data$detail : _t3 === null || _t3 === void 0 || (_e$data2 = _t3.data) === null || _e$data2 === void 0 ? void 0 : _e$data2.msg) !== null && _ref12 !== void 0 ? _ref12 : _t3 === null || _t3 === void 0 ? void 0 : _t3.errMsg) !== null && _ref11 !== void 0 ? _ref11 : _t3 === null || _t3 === void 0 ? void 0 : _t3.message) !== null && _ref10 !== void 0 ? _ref10 : '登录失败，请检查网络或后端';
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
              title: typeof msg === 'string' ? msg : '登录失败',
              icon: 'none',
              duration: 3000
            });
          case 8:
            return _context3.a(2);
        }
      }, _callee3, null, [[1, 7]]);
    }));
    return function handleLogin() {
      return _ref0.apply(this, arguments);
    };
  }();
  var handleLogout = function handleLogout() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: function success(res) {
        if (res.confirm) {
          (0,_services_api__WEBPACK_IMPORTED_MODULE_9__.clearAuthToken)();
          dispatch((0,_store_slices_userSlice__WEBPACK_IMPORTED_MODULE_7__.logout)());
          setCompanyScans(0);
          setQuoteCount(0);
          setContractCount(0);
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  };
  var navTo = function navTo(url) {
    return (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.navigateToUrl)(url);
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.ScrollView, {
    scrollY: true,
    className: "profile-page-outer",
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
      className: "profile-page",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "header-banner",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          className: "my-equity",
          onClick: function onClick() {
            return navTo('/pages/membership/index');
          },
          children: "\u6211\u7684\u6743\u76CA"
        }), isLoggedIn ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.Fragment, {
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "avatar-wrap",
            onClick: function onClick() {
              var _Taro$getUserProfile;
              return (_Taro$getUserProfile = (_tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default().getUserProfile)) === null || _Taro$getUserProfile === void 0 ? void 0 : _Taro$getUserProfile.call((_tarojs_taro__WEBPACK_IMPORTED_MODULE_5___default()), {
                desc: '用于展示'
              }).then(function () {}).catch(function () {});
            },
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              className: "avatar-placeholder",
              children: "\uD83D\uDC64"
            })
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "nickname",
            children: (userInfo === null || userInfo === void 0 ? void 0 : userInfo.nickname) || '装修用户'
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "member-badge",
            children: userInfo !== null && userInfo !== void 0 && userInfo.isMember ? userInfo.memberExpire ? function () {
              var exp = userInfo.memberExpire;
              var d = new Date(exp);
              var days = Math.ceil((d.getTime() - Date.now()) / 86400000);
              var suffix = '';
              if (days < 0) suffix = '（已过期，请续费）';else if (days <= 7) suffix = '（即将到期，请续费）';
              return "\u4F1A\u5458\u6709\u6548\u671F\u81F3 ".concat(exp).concat(suffix);
            }() : '6大阶段全解锁会员' : '普通用户'
          }), (userInfo === null || userInfo === void 0 ? void 0 : userInfo.points) !== undefined && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "points-badge",
            onClick: function onClick() {
              return navTo('/pages/points/index');
            },
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              className: "points-label",
              children: "\u79EF\u5206"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              className: "points-value",
              children: userInfo.points
            })]
          })]
        }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "login-cta",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "avatar-placeholder",
            children: "\uD83D\uDC64"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "login-text",
            children: "\u767B\u5F55\u540E\u67E5\u770B\u66F4\u591A\u4FE1\u606F"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
            className: "login-btn",
            onClick: handleLogin,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
              children: "\u7ACB\u5373\u767B\u5F55"
            })
          })]
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "section",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/data-manage/index?tab=report');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCC1"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u6211\u7684\u6570\u636E"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-desc",
            children: "\u62A5\u544A/\u7167\u7247\u7BA1\u7406"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/order-list/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCE6"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u6211\u7684\u8BA2\u5355"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/calendar/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCC5"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u88C5\u4FEE\u65E5\u5386"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/contact/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCDE"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u4E13\u5C5E\u5BA2\u670D"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "section",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/account-notify/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\u2699\uFE0F"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u8D26\u6237\u4E0E\u901A\u77E5\u8BBE\u7F6E"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/privacy/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDD12"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u9690\u79C1\u4FDD\u969C"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/guide/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCD6"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u4F7F\u7528\u6307\u5357"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/about/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\u2139\uFE0F"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u5173\u4E8E&\u5E2E\u52A9"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "folder-item",
          onClick: function onClick() {
            return navTo('/pages/feedback/index');
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-icon",
            children: "\uD83D\uDCAC"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "folder-name",
            children: "\u610F\u89C1\u53CD\u9988"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            className: "arrow",
            children: "\u203A"
          })]
        })]
      }), isLoggedIn && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "logout-section",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
          className: "logout-btn",
          onClick: handleLogout,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
            children: "\u9000\u51FA\u767B\u5F55"
          })
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.View, {
        className: "version-info",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_11__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_4__.Text, {
          children: "\u7248\u672C 2.1.0"
        })
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (Profile);

/***/ }),

/***/ "./src/pages/profile/index.tsx":
/*!*************************************!*\
  !*** ./src/pages/profile/index.tsx ***!
  \*************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_profile_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/profile/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/profile/index!./src/pages/profile/index.tsx");


var config = {"navigationBarTitleText":"我的","navigationBarBackgroundColor":"#1677FF","navigationBarTextStyle":"white","enablePullDownRefresh":true};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_profile_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/profile/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_profile_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/profile/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map