"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/onboarding/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/onboarding/index!./src/pages/onboarding/index.tsx":
/*!**************************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/onboarding/index!./src/pages/onboarding/index.tsx ***!
  \**************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_interopRequireWildcard_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/interopRequireWildcard.js */ "./node_modules/@babel/runtime/helpers/esm/interopRequireWildcard.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _components_ExampleImageModal__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../components/ExampleImageModal */ "./src/components/ExampleImageModal/index.tsx");
/* harmony import */ var _utils_navigation__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../../utils/navigation */ "./src/utils/navigation.ts");
/* harmony import */ var _config_assets__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../config/assets */ "./src/config/assets.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__);












/**
 * P01 引导页 - 装修避坑管家
 * 品牌介绍/隐私保障/服务承诺，3页滑动
 */

var Onboarding = function Onboarding() {
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(0),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState, 2),
    current = _useState2[0],
    setCurrent = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(3),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState3, 2),
    countdown = _useState4[0],
    setCountdown = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(null),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState5, 2),
    preview = _useState6[0],
    setPreview = _useState6[1];
  var countdownPaused = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(false);
  var timerRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(null);
  var countdownRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(3);
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    var timer = setTimeout(function () {
      try {
        if (_tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('onboarding_completed') || _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('has_onboarded')) {
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().reLaunch({
            url: '/pages/index/index'
          });
        }
      } catch (_) {}
    }, 100);
    return function () {
      return clearTimeout(timer);
    };
  }, []);
  var goToHome = (0,react__WEBPACK_IMPORTED_MODULE_4__.useCallback)(function () {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('onboarding_completed', true);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('has_onboarded', true);
    // 跳转 P02 后首先弹出城市选择，然后弹出「进度+消息提醒权限请求弹窗」
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('show_city_selection_modal', true);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('show_remind_permission_modal', true);
    (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_8__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_8__.TAB_HOME, {
      defer: 100
    });
  }, []);
  countdownRef.current = countdown;

  // 3秒倒计时，滑动时暂停；跳转用 setTimeout(0) 脱出 setInterval 栈，避免小程序 __subPageFrameEndTime__ 报错
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    var mounted = true;
    var tick = function tick() {
      try {
        if (!mounted) return;
        if (countdownPaused.current) return;
        var next = countdownRef.current - 1;
        if (next <= 0) {
          if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
          }
          // 延迟到下一事件循环再跳转，避免在 setInterval 回调栈内执行导致小程序框架报错
          setTimeout(function () {
            return goToHome();
          }, 0);
          return;
        }
        countdownRef.current = next;
        setCountdown(next);
      } catch (_) {
        // 小程序页面已销毁时回调仍可能被调度，吞掉异常
      }
    };
    timerRef.current = setInterval(tick, 1000);
    return function () {
      mounted = false;
      var id = timerRef.current;
      if (id) {
        clearInterval(id);
        timerRef.current = null;
      }
    };
  }, [goToHome]);
  var handleSwiperChange = function handleSwiperChange(e) {
    setCurrent(e.detail.current);
    var three = 3;
    countdownRef.current = three;
    setCountdown(three);
    countdownPaused.current = true;
    setTimeout(function () {
      countdownPaused.current = false;
    }, 500);
  };
  var handleStart = /*#__PURE__*/function () {
    var _ref = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().m(function _callee() {
      var res, code, _data, _loginRes$data, _yield$import, env, loginRes, d, token, userId, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            _context.p = 0;
            _context.n = 1;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().login();
          case 1:
            res = _context.v;
            code = res === null || res === void 0 ? void 0 : res.code;
            if (!code) {
              _context.n = 4;
              break;
            }
            _context.n = 2;
            return Promise.resolve().then(function () {
              return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_interopRequireWildcard_js__WEBPACK_IMPORTED_MODULE_1__["default"])(__webpack_require__(/*! ../../config/env */ "./src/config/env.ts"));
            });
          case 2:
            _yield$import = _context.v;
            env = _yield$import.env;
            _context.n = 3;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().request({
              url: "".concat(env.apiBaseUrl, "/users/login"),
              method: 'POST',
              header: {
                'Content-Type': 'application/json'
              },
              data: {
                code: code
              }
            });
          case 3:
            loginRes = _context.v;
            d = (_data = (_loginRes$data = loginRes.data) === null || _loginRes$data === void 0 ? void 0 : _loginRes$data.data) !== null && _data !== void 0 ? _data : loginRes.data;
            token = d === null || d === void 0 ? void 0 : d.access_token;
            userId = d === null || d === void 0 ? void 0 : d.user_id;
            if (token && userId) {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('access_token', token);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('user_id', userId);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('login_fresh_at', Date.now());
            }
          case 4:
            _context.n = 6;
            break;
          case 5:
            _context.p = 5;
            _t = _context.v;
          case 6:
            goToHome();
          case 7:
            return _context.a(2);
        }
      }, _callee, null, [[0, 5]]);
    }));
    return function handleStart() {
      return _ref.apply(this, arguments);
    };
  }();
  var showPreview = function showPreview(type) {
    var map = {
      company: {
        title: '公司检测',
        content: 'AI核验资质与纠纷记录，输入公司名称即可检测'
      },
      quote: {
        title: '报价单分析',
        content: 'AI识别漏项与虚高，上传报价单自动分析'
      },
      contract: {
        title: '合同审核',
        content: '高亮霸王条款与陷阱，上传合同AI逐条分析'
      },
      acceptance: {
        title: '验收分析',
        content: '拍摄/上传验收照片，AI识别施工问题并给出整改建议'
      }
    };
    var m = map[type] || map.quote;
    setPreview({
      type: type,
      title: m.title,
      content: m.content
    });
  };

  // 原型 P01：页1 装修避坑AI全程护航 / 页2 6大阶段标准化施工 / 页3 智能提醒
  var slides = [{
    id: 'brand',
    logo: '🛡️',
    title: '装修避坑，AI全程护航',
    subtitle: '让装修决策更安全',
    capabilities: [{
      icon: '🏢',
      text: '装修公司',
      desc: 'AI检测',
      type: 'company'
    }, {
      icon: '💰',
      text: '报价',
      desc: 'AI检测',
      type: 'quote'
    }, {
      icon: '📜',
      text: '合同',
      desc: 'AI检测',
      type: 'contract'
    }]
  }, {
    id: 'stages',
    icon: '📐',
    title: '6大阶段标准化施工',
    subtitle: '材料核对+5大工序AI验收，流程互锁',
    items: [{
      icon: '📦',
      text: '材料进场核对',
      desc: 'S00 台账生成'
    }, {
      icon: '🔌',
      text: '隐蔽工程→安装收尾',
      desc: 'S01-S05 逐级验收'
    }, {
      icon: '🔒',
      text: '流程互锁',
      desc: '前置未通过则后续锁定'
    }],
    linkText: '查看完整隐私政策',
    linkUrl: '/pages/neutral-statement/index'
  }, {
    id: 'remind',
    icon: '🔔',
    title: '智能提醒，装修不遗漏',
    subtitle: '阶段开始/验收前3天，微信+小程序双重提醒',
    items: [{
      icon: '📱',
      text: '微信服务通知',
      desc: '点击直达对应阶段'
    }, {
      icon: '🔴',
      text: '小程序内红点',
      desc: '消息中心+页面角标'
    }, {
      icon: '⚙️',
      text: '自定义提前天数',
      desc: '1/2/3/5/7天可选'
    }],
    linkText: '查看服务条款',
    linkUrl: '/pages/neutral-statement/index'
  }];
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
    className: "onboarding-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
      className: "skip-link",
      onClick: function onClick() {
        return goToHome();
      },
      children: "\u8DF3\u8FC7"
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Swiper, {
      className: "swiper",
      current: current,
      onChange: handleSwiperChange,
      indicatorDots: false,
      children: slides.map(function (s) {
        return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.SwiperItem, {
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "slide",
            children: s.id === 'brand' && s.capabilities ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "brand-slide-content",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "brand-logo",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "logo-icon",
                  children: s.logo
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "logo-text",
                  children: "\u88C5\u4FEE\u907F\u5751\u7BA1\u5BB6"
                })]
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "slide-title",
                children: s.title
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "slide-subtitle",
                children: s.subtitle
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "section-divider",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "divider-line"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "section-label",
                  children: "\u6838\u5FC3\u80FD\u529B"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "divider-line"
                })]
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "capability-grid",
                children: s.capabilities.map(function (cap) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "cap-item",
                    onClick: function onClick() {
                      return showPreview(cap.type);
                    },
                    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "cap-icon",
                      children: cap.icon
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "cap-title",
                      children: cap.text
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "cap-desc",
                      children: cap.desc
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "cap-hint",
                      children: "\u70B9\u51FB\u9884\u89C8\u793A\u4F8B"
                    })]
                  }, cap.type);
                })
              })]
            }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "commitment-slide",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "slide-icon-wrap",
                children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "slide-icon",
                  children: s.icon
                })
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "slide-title",
                children: s.title
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "slide-subtitle",
                children: s.subtitle
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "commitment-list",
                children: (s.items || []).map(function (item, idx) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "commitment-item",
                    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "commitment-icon",
                      children: item.icon
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                      className: "commitment-content",
                      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                        className: "commitment-title",
                        children: item.text
                      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                        className: "commitment-desc",
                        children: item.desc
                      })]
                    })]
                  }, idx);
                })
              }), s.linkText && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "policy-link",
                onClick: function onClick() {
                  return _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().navigateTo({
                    url: s.linkUrl || '/pages/neutral-statement/index'
                  });
                },
                children: s.linkText
              })]
            })
          })
        }, s.id);
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_components_ExampleImageModal__WEBPACK_IMPORTED_MODULE_7__["default"], {
      visible: !!preview,
      title: (preview === null || preview === void 0 ? void 0 : preview.title) || '功能预览',
      content: (preview === null || preview === void 0 ? void 0 : preview.content) || '',
      imageUrl: preview ? _config_assets__WEBPACK_IMPORTED_MODULE_9__.EXAMPLE_IMAGES[preview.type] : undefined,
      onClose: function onClose() {
        return setPreview(null);
      }
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
      className: "footer-slogan",
      children: "\u8BA9\u6BCF\u4E00\u6B65\u88C5\u4FEE\u51B3\u7B56\u90FD\u6709AI\u62A4\u822A"
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "footer",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "indicator-row",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "page-dots",
          children: slides.map(function (_, i) {
            return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "dot ".concat(current === i ? 'active' : '')
            }, i);
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "countdown",
          children: [countdown, "s"]
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "btn primary",
        onClick: handleStart,
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_10__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "btn-text",
          children: "\u5F00\u59CB\u4F7F\u7528"
        })
      })]
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (Onboarding);

/***/ }),

/***/ "./src/pages/onboarding/index.tsx":
/*!****************************************!*\
  !*** ./src/pages/onboarding/index.tsx ***!
  \****************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_onboarding_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/onboarding/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/onboarding/index!./src/pages/onboarding/index.tsx");


var config = {"navigationBarTitleText":"欢迎","navigationBarBackgroundColor":"#FAFCFF","navigationBarTextStyle":"black","disableScroll":false};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_onboarding_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/onboarding/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_onboarding_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/onboarding/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map