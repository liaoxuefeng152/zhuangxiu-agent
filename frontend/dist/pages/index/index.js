"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/index/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/index/index!./src/pages/index/index.tsx":
/*!****************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/index/index!./src/pages/index/index.tsx ***!
  \****************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_interopRequireWildcard_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/interopRequireWildcard.js */ "./node_modules/@babel/runtime/helpers/esm/interopRequireWildcard.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread2.js */ "./node_modules/@babel/runtime/helpers/esm/objectSpread2.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _config_assets__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../../config/assets */ "./src/config/assets.ts");
/* harmony import */ var _config_env__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../config/env */ "./src/config/env.ts");
/* harmony import */ var _utils_navigation__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../../utils/navigation */ "./src/utils/navigation.ts");
/* harmony import */ var _components_UploadConfirmModal__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ../../components/UploadConfirmModal */ "./src/components/UploadConfirmModal/index.tsx");
/* harmony import */ var _components_CityPickerModal__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../../components/CityPickerModal */ "./src/components/CityPickerModal.tsx");
/* harmony import */ var _components_FloatingDesignerAvatar__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ../../components/FloatingDesignerAvatar */ "./src/components/FloatingDesignerAvatar.tsx");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__);
















/** 根据已选城市名取简称（如 深圳市→深，未选显示「定位」） */

function getCityShortName() {
  var city = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('selected_city');
  if (!city || !city.trim()) return '定位';
  var name = city.replace(/市$/, '').trim();
  return name.charAt(0) || '定位';
}

/**
 * P02 首页（优化版）- 核心功能聚合、6大阶段快捷、会员权益、城市定位入口
 */
var REMIND_PERMISSION_KEY = 'show_remind_permission_modal';
var CITY_SELECTION_KEY = 'show_city_selection_modal';
var Index = function Index() {
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(0),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState, 2),
    currentIndex = _useState2[0],
    setCurrentIndex = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState3, 2),
    hasNewMessage = _useState4[0],
    setHasNewMessage = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState5, 2),
    noMorePrompt = _useState6[0],
    setNoMorePrompt = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)({
      visible: false,
      type: 'quote',
      url: ''
    }),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState7, 2),
    uploadModal = _useState8[0],
    setUploadModal = _useState8[1];
  var _useState9 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState9, 2),
    remindPermissionModal = _useState0[0],
    setRemindPermissionModal = _useState0[1];
  var _useState1 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState10 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState1, 2),
    cityPickerModal = _useState10[0],
    setCityPickerModal = _useState10[1];
  var _useState11 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(function () {
      return getCityShortName();
    }),
    _useState12 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState11, 2),
    cityShort = _useState12[0],
    setCityShort = _useState12[1];

  // 监听 storage 变化更新城市显示；用 ref 避免定时器回调在页面销毁后 setState 导致 __subPageFrameEndTime__ 报错
  var mountedRef = (0,react__WEBPACK_IMPORTED_MODULE_5__.useRef)(true);
  var intervalRef = (0,react__WEBPACK_IMPORTED_MODULE_5__.useRef)(null);
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    mountedRef.current = true;
    var updateCityDisplay = function updateCityDisplay() {
      try {
        if (!mountedRef.current) return;
        var city = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('selected_city');
        var shortName = city ? city.replace(/市$/, '').trim().charAt(0) || '定位' : '定位';
        if (!mountedRef.current) return;
        setCityShort(shortName);
      } catch (_) {
        // 页面已销毁时 setState 可能报 __subPageFrameEndTime__，吞掉异常
      }
    };
    intervalRef.current = setInterval(updateCityDisplay, 500);
    return function () {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, []);
  var swiperList = [{
    id: 1,
    title: '花30万装修，不该靠运气',
    subtitle: 'AI帮你避坑',
    action: 'guide',
    image: _config_assets__WEBPACK_IMPORTED_MODULE_8__.BANNER_IMAGES[0]
  }, {
    id: 2,
    title: '装修公司靠谱吗？',
    subtitle: '10秒AI核验',
    action: 'company',
    image: _config_assets__WEBPACK_IMPORTED_MODULE_8__.BANNER_IMAGES[1]
  }, {
    id: 3,
    title: '报价单/合同藏陷阱？',
    subtitle: 'AI逐条分析',
    action: 'upload',
    image: _config_assets__WEBPACK_IMPORTED_MODULE_8__.BANNER_IMAGES[2]
  }];
  var handleScanCompany = function handleScanCompany() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
      url: '/pages/company-scan/index'
    });
  };
  var showUploadModal = function showUploadModal(type, url) {
    var hasCompanyScan = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('has_company_scan');
    if (!hasCompanyScan && !noMorePrompt) {
      setUploadModal({
        visible: true,
        type: type,
        url: url
      });
    } else {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
        url: url
      });
    }
  };
  var handleUploadConfirm = function handleUploadConfirm(noMore, url) {
    setUploadModal(function (m) {
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])({}, m), {}, {
        visible: false
      });
    });
    if (noMore) {
      setNoMorePrompt(true);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('no_upload_prompt', '1');
    }
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
      url: url
    });
  };
  var handleUploadGoScan = function handleUploadGoScan() {
    setUploadModal(function (m) {
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])({}, m), {}, {
        visible: false
      });
    });
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
      url: '/pages/company-scan/index'
    });
  };
  var handleUploadQuote = function handleUploadQuote() {
    return showUploadModal('quote', '/pages/quote-upload/index');
  };
  var handleUploadContract = function handleUploadContract() {
    return showUploadModal('contract', '/pages/contract-upload/index');
  };
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    var stored = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('no_upload_prompt');
    if (stored) setNoMorePrompt(true);
  }, []);

  // 用户进入首页后，首先弹出城市选择，其次是进度提醒
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    try {
      // 检查是否已选择城市
      var selectedCity = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('selected_city');
      var hasCity = selectedCity && selectedCity.trim();

      // 检查是否需要显示城市选择弹窗（从引导页跳转过来）
      var shouldShowCitySelection = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(CITY_SELECTION_KEY) || !hasCity;
      if (shouldShowCitySelection) {
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().removeStorageSync(CITY_SELECTION_KEY);
        // 如果没有选择城市，先弹出城市选择
        if (!hasCity) {
          setCityPickerModal(true);
        } else {
          // 如果已选择城市，检查是否需要显示进度提醒
          checkAndShowRemindModal();
        }
      } else {
        // 如果不需要显示城市选择，检查是否需要显示进度提醒
        checkAndShowRemindModal();
      }
    } catch (_) {}
  }, []);

  // 检查并显示进度提醒弹窗
  var checkAndShowRemindModal = function checkAndShowRemindModal() {
    try {
      if (_tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(REMIND_PERMISSION_KEY)) {
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().removeStorageSync(REMIND_PERMISSION_KEY);
        setRemindPermissionModal(true);
      }
    } catch (_) {}
  };

  // 城市选择确认回调
  var handleCityConfirm = function handleCityConfirm(city) {
    console.log('[首页] 城市选择确认', city);
    // 先关闭弹窗
    setCityPickerModal(false);
    // 更新城市显示（从storage读取最新值）
    var cityName = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('selected_city');
    var shortName = cityName ? cityName.replace(/市$/, '').trim().charAt(0) || '定位' : '定位';
    setCityShort(shortName);
    console.log('[首页] 更新城市显示', shortName);
    // 城市选择完成后，延迟显示进度提醒弹窗
    setTimeout(function () {
      checkAndShowRemindModal();
    }, 300);
  };

  // 城市选择关闭回调（用户取消）
  var handleCityClose = function handleCityClose() {
    setCityPickerModal(false);
    // 即使取消城市选择，也检查是否需要显示进度提醒
    setTimeout(function () {
      checkAndShowRemindModal();
    }, 300);
  };
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    var loadUnread = /*#__PURE__*/function () {
      var _ref = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee() {
        var _data, _res$data, _d$count, token, userId, timeoutPromise, requestPromise, res, d, count, _err$errMsg, _err$message, _err$errMsg2, _err$errMsg3, _t;
        return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context) {
          while (1) switch (_context.p = _context.n) {
            case 0:
              _context.p = 0;
              token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('access_token');
              userId = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('user_id');
              if (token) {
                _context.n = 1;
                break;
              }
              setHasNewMessage(false);
              return _context.a(2);
            case 1:
              // 设置请求超时（10秒）
              timeoutPromise = new Promise(function (_, reject) {
                setTimeout(function () {
                  return reject(new Error('请求超时，请检查网络连接'));
                }, 10000);
              }); // 小程序下 axios 可能不传 header，用 Taro.request 显式带鉴权
              requestPromise = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().request({
                url: "".concat(_config_env__WEBPACK_IMPORTED_MODULE_9__.env.apiBaseUrl, "/messages/unread-count"),
                method: 'GET',
                header: {
                  Authorization: "Bearer ".concat(token),
                  'X-User-Id': userId != null && userId !== '' ? String(userId) : '',
                  'Content-Type': 'application/json'
                },
                timeout: 10000 // 设置Taro请求超时
              }); // 使用Promise.race实现超时控制
              _context.n = 2;
              return Promise.race([requestPromise, timeoutPromise]);
            case 2:
              res = _context.v;
              d = (_data = (_res$data = res.data) === null || _res$data === void 0 ? void 0 : _res$data.data) !== null && _data !== void 0 ? _data : res.data;
              count = (_d$count = d === null || d === void 0 ? void 0 : d.count) !== null && _d$count !== void 0 ? _d$count : 0;
              setHasNewMessage(count > 0);
              _context.n = 4;
              break;
            case 3:
              _context.p = 3;
              _t = _context.v;
              console.log('[首页] 获取未读消息数失败:', _t);
              setHasNewMessage(false);

              // 根据错误类型提供更详细的日志
              if (_t !== null && _t !== void 0 && (_err$errMsg = _t.errMsg) !== null && _err$errMsg !== void 0 && _err$errMsg.includes('timeout') || _t !== null && _t !== void 0 && (_err$message = _t.message) !== null && _err$message !== void 0 && _err$message.includes('超时')) {
                console.log('[首页] 网络请求超时，可能是网络连接问题或服务器响应慢');
              } else if (_t !== null && _t !== void 0 && (_err$errMsg2 = _t.errMsg) !== null && _err$errMsg2 !== void 0 && _err$errMsg2.includes('fail') || (_t === null || _t === void 0 ? void 0 : _t.statusCode) === 404 || (_t === null || _t === void 0 ? void 0 : _t.statusCode) === 500) {
                console.log('[首页] 服务器请求失败，状态码:', _t === null || _t === void 0 ? void 0 : _t.statusCode);
              } else if (!(_t !== null && _t !== void 0 && (_err$errMsg3 = _t.errMsg) !== null && _err$errMsg3 !== void 0 && _err$errMsg3.includes('cancel'))) {
                // 非取消操作的错误才记录为警告
                console.warn('[首页] 获取未读消息数异常:', _t);
              }
            case 4:
              return _context.a(2);
          }
        }, _callee, null, [[0, 3]]);
      }));
      return function loadUnread() {
        return _ref.apply(this, arguments);
      };
    }();
    loadUnread();
  }, []);
  (0,_tarojs_taro__WEBPACK_IMPORTED_MODULE_7__.useDidShow)(function () {
    return setCityShort(getCityShortName());
  });

  // 原型 P02：AI施工验收 → P09；未设置开工日期则弹日期选择（7/15/30天）
  var handleAIConstruction = function handleAIConstruction() {
    var startDate = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('construction_start_date');
    if (!startDate) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showActionSheet({
        itemList: ['7天后开工', '15天后开工', '30天后开工', '选择其他日期'],
        success: function success(res) {
          if (res.tapIndex === 3) {
            (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.TAB_CONSTRUCTION, {
              defer: 150
            });
            return;
          }
          var days = [7, 15, 30][res.tapIndex];
          var d = new Date();
          d.setDate(d.getDate() + days);
          var dateStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('construction_start_date', dateStr);
          var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('access_token');
          if (token) {
            Promise.resolve().then(function () {
              return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_interopRequireWildcard_js__WEBPACK_IMPORTED_MODULE_0__["default"])(__webpack_require__(/*! ../../services/api */ "./src/services/api.ts"));
            }).then(function (_ref2) {
              var postWithAuth = _ref2.postWithAuth;
              postWithAuth('/constructions/start-date', {
                start_date: dateStr
              }).catch(function () {});
            });
          }
          _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
            title: '进度计划已更新',
            icon: 'success'
          });
          (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.TAB_CONSTRUCTION, {
            defer: 150
          });
        },
        fail: function fail() {} // 用户取消不视为错误
      });
    } else {
      (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.TAB_CONSTRUCTION);
    }
  };
  var goToConstructionStage = function goToConstructionStage(stageIndex) {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('construction_scroll_stage', stageIndex);
    (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_10__.TAB_CONSTRUCTION);
  };
  var handleRemindAllow = function handleRemindAllow() {
    setRemindPermissionModal(false);
    try {
      if (typeof (_tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().requestSubscribeMessage) === 'function') {
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().requestSubscribeMessage({
          tmplIds: [],
          entityIds: [],
          success: function success() {
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('remind_permission_granted', true);
          },
          fail: function fail() {}
        }).catch(function () {});
      }
    } catch (_) {}
  };
  var handleRemindReject = function handleRemindReject() {
    setRemindPermissionModal(false);
  };
  var handleSwiperClick = function handleSwiperClick(action) {
    switch (action) {
      case 'guide':
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
          url: '/pages/guide/index'
        });
        break;
      case 'company':
        handleScanCompany();
        break;
      case 'upload':
        _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showActionSheet({
          itemList: ['上传报价单', '上传合同'],
          success: function success(res) {
            if (res.tapIndex === 0) handleUploadQuote();else if (res.tapIndex === 1) handleUploadContract();
          },
          fail: function fail() {} // 用户取消不视为错误
        });
        break;
    }
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
    className: "index-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "header",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "city-entry",
        onClick: function onClick() {
          return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
            url: '/pages/city-picker/index'
          });
        },
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "city-entry-text",
          children: cityShort
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        className: "title",
        children: "\u88C5\u4FEE\u907F\u5751\u7BA1\u5BB6"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "message-icon",
        onClick: function onClick() {
          return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
            url: '/pages/message/index'
          });
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "icon-text",
          children: "\uD83D\uDD14"
        }), hasNewMessage && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "dot"
        })]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "swiper-container",
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Swiper, {
        className: "swiper",
        indicatorDots: true,
        indicatorColor: "rgba(255,255,255,0.4)",
        indicatorActiveColor: "#fff",
        autoplay: true,
        interval: 3000,
        circular: true,
        current: currentIndex,
        onChange: function onChange(e) {
          return setCurrentIndex(e.detail.current);
        },
        children: swiperList.map(function (item) {
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.SwiperItem, {
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "swiper-item",
              onClick: function onClick() {
                return handleSwiperClick(item.action);
              },
              children: [_config_assets__WEBPACK_IMPORTED_MODULE_8__.USE_BANNER_IMAGES && item.image ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Image, {
                src: item.image,
                className: "swiper-img",
                mode: "aspectFill"
              }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "swiper-bg"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "swiper-content",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "swiper-title",
                  style: {
                    color: '#FFD700'
                  },
                  children: item.title
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "swiper-subtitle",
                  style: {
                    color: '#FFEB3B'
                  },
                  children: item.subtitle
                })]
              })]
            })
          }, item.id);
        })
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "main-actions grid-four",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "action-card",
        onClick: handleScanCompany,
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-icon",
          children: "\uD83C\uDFE2"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-text",
          children: "\u88C5\u4FEE\u516C\u53F8\u68C0\u6D4B"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "action-card",
        onClick: handleUploadQuote,
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-icon",
          children: "\uD83D\uDCB0"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-text",
          children: "\u88C5\u4FEE\u62A5\u4EF7\u5206\u6790"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "action-card",
        onClick: handleUploadContract,
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-icon",
          children: "\uD83D\uDCDC"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-text",
          children: "\u88C5\u4FEE\u5408\u540C\u5BA1\u6838"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "action-card highlight",
        onClick: handleAIConstruction,
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-icon",
          children: "\uD83D\uDD0D"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-text",
          children: "AI\u65BD\u5DE5\u9A8C\u6536"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "action-card-hint",
          children: "6\u5927\u9636\u6BB5"
        })]
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "section-label",
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        children: "6\u5927\u9636\u6BB5"
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.ScrollView, {
      scrollX: true,
      className: "stage-quick-scroll",
      showScrollbar: false,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "stage-quick-list",
        children: ['S00材料', 'S01隐蔽', 'S02泥瓦', 'S03木工', 'S04油漆', 'S05收尾'].map(function (label, i) {
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "stage-quick-item",
            onClick: function onClick() {
              return goToConstructionStage(i);
            },
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "stage-quick-icon",
              children: ['📦', '🔌', '🧱', '🪵', '🖌', '✅'][i]
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "stage-quick-text",
              children: label
            })]
          }, i);
        })
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "member-card",
      onClick: function onClick() {
        return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
          url: '/pages/membership/index'
        });
      },
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        className: "member-card-text",
        children: "6\u5927\u9636\u6BB5\u5168\u62A5\u544A\u89E3\u9501+\u65E0\u9650\u6B21AI\u63D0\u9192"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        className: "member-card-btn",
        children: "\u7ACB\u5373\u5F00\u901A"
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "ai-designer-fixed-container",
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_components_FloatingDesignerAvatar__WEBPACK_IMPORTED_MODULE_13__["default"], {
        showDragHint: true,
        initialPosition: {
          x: 0,
          y: 0
        },
        fixedMode: true,
        fixedContainerClassName: "ai-designer-fixed"
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
      className: "tips-text",
      children: "\u672C\u5730\u88C5\u4FEE\u884C\u4E1A\u89C4\u8303\u5B9E\u65F6\u66F4\u65B0\uFF0CAI\u68C0\u6D4B\u66F4\u7CBE\u51C6"
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_components_UploadConfirmModal__WEBPACK_IMPORTED_MODULE_11__["default"], {
      visible: uploadModal.visible,
      type: uploadModal.type,
      onConfirm: function onConfirm(noMore) {
        return handleUploadConfirm(noMore, uploadModal.url);
      },
      onGoScan: handleUploadGoScan,
      onClose: function onClose() {
        return setUploadModal(function (m) {
          return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_3__["default"])({}, m), {}, {
            visible: false
          });
        });
      }
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_components_CityPickerModal__WEBPACK_IMPORTED_MODULE_12__["default"], {
      visible: cityPickerModal,
      onConfirm: handleCityConfirm,
      onClose: handleCityClose
    }), remindPermissionModal && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "remind-permission-mask",
      onClick: handleRemindReject,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "remind-permission-modal",
        onClick: function onClick(e) {
          return e.stopPropagation();
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "remind-permission-title",
          children: "\u8FDB\u5EA6+\u6D88\u606F\u63D0\u9192"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "remind-permission-desc",
          children: "\u5F00\u542F\u540E\uFF0C6\u5927\u9636\u6BB5\u5F00\u59CB/\u9A8C\u6536\u524D\u5C06\u4E3A\u60A8\u63A8\u9001\u5FAE\u4FE1\u670D\u52A1\u901A\u77E5\uFF0C\u88C5\u4FEE\u4E0D\u9057\u6F0F"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "remind-permission-btns",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-permission-btn reject",
            onClick: handleRemindReject,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              children: "\u62D2\u7EDD"
            })
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-permission-btn allow",
            onClick: handleRemindAllow,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              children: "\u5141\u8BB8"
            })
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "remind-permission-hint",
          children: "\u62D2\u7EDD\u540E\u53EF\u5728\u3010\u6211\u7684-\u8BBE\u7F6E\u3011\u4E8C\u6B21\u5F00\u542F"
        })]
      })
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (Index);

/***/ }),

/***/ "./src/components/CityPickerModal.tsx":
/*!********************************************!*\
  !*** ./src/components/CityPickerModal.tsx ***!
  \********************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__);






// 热门城市

var HOT_CITIES = [{
  label: '北京',
  value: '北京市'
}, {
  label: '上海',
  value: '上海市'
}, {
  label: '广州',
  value: '广州市'
}, {
  label: '深圳',
  value: '深圳市'
}, {
  label: '杭州',
  value: '杭州市'
}];
var PROVINCES = {
  广东: ['广州市', '深圳市', '东莞市', '佛山市', '珠海市', '惠州市', '中山市', '江门市', '湛江市', '茂名市', '肇庆市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '潮州市', '揭阳市', '云浮市'],
  北京: ['北京市'],
  上海: ['上海市'],
  浙江: ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
  江苏: ['南京市', '苏州市', '无锡市', '常州市', '南通市', '扬州市', '徐州市', '镇江市', '泰州市', '盐城市', '连云港市', '淮安市', '宿迁市'],
  四川: ['成都市', '绵阳市', '德阳市', '南充市', '宜宾市', '自贡市', '乐山市', '泸州市', '达州市', '内江市', '遂宁市', '攀枝花市', '眉山市', '广安市', '资阳市', '凉山州'],
  湖北: ['武汉市', '宜昌市', '襄阳市', '荆州市', '十堰市', '黄石市', '荆门市', '鄂州市', '孝感市', '黄冈市', '咸宁市', '随州市', '恩施州'],
  陕西: ['西安市', '咸阳市', '宝鸡市', '渭南市', '汉中市', '榆林市', '延安市', '安康市', '商洛市', '铜川市'],
  山东: ['济南市', '青岛市', '烟台市', '潍坊市', '临沂市', '淄博市', '济宁市', '泰安市', '威海市', '德州市', '聊城市', '滨州市', '菏泽市', '枣庄市', '日照市', '东营市'],
  河南: ['郑州市', '洛阳市', '南阳市', '许昌市', '周口市', '商丘市', '新乡市', '安阳市', '信阳市', '开封市', '平顶山市', '驻马店市', '焦作市', '漯河市', '濮阳市', '三门峡市', '鹤壁市', '许昌市'],
  福建: ['福州市', '厦门市', '泉州市', '漳州市', '莆田市', '龙岩市', '三明市', '南平市', '宁德市'],
  湖南: ['长沙市', '株洲市', '湘潭市', '衡阳市', '岳阳市', '常德市', '邵阳市', '益阳市', '娄底市', '郴州市', '永州市', '怀化市', '张家界市', '湘西州']
};
var PROVINCE_NAMES = Object.keys(PROVINCES);
var DEFAULT_PROVINCE = '广东';
var ALL_CITIES = PROVINCE_NAMES.flatMap(function (p) {
  return PROVINCES[p];
});
/**
 * 城市选择弹窗组件
 */
var CityPickerModal = function CityPickerModal(_ref) {
  var visible = _ref.visible,
    onConfirm = _ref.onConfirm,
    onClose = _ref.onClose;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(''),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState, 2),
    keyword = _useState2[0],
    setKeyword = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(DEFAULT_PROVINCE),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState3, 2),
    selectedProvince = _useState4[0],
    setSelectedProvince = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(''),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState5, 2),
    selectedCity = _useState6[0],
    setSelectedCity = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('loading'),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState7, 2),
    locationStatus = _useState8[0],
    setLocationStatus = _useState8[1];
  var _useState9 = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(''),
    _useState0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState9, 2),
    locationCityName = _useState0[0],
    setLocationCityName = _useState0[1];
  var filteredCities = (0,react__WEBPACK_IMPORTED_MODULE_1__.useMemo)(function () {
    var kw = keyword.trim().toLowerCase();
    if (!kw) return [];
    return ALL_CITIES.filter(function (c) {
      return c.toLowerCase().includes(kw) || c.replace(/市$/, '').toLowerCase().includes(kw);
    });
  }, [keyword]);
  var cityList = selectedProvince ? PROVINCES[selectedProvince] || [] : [];

  // 弹窗显示时自动定位
  (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(function () {
    if (!visible) return;
    setKeyword('');
    setSelectedCity('');
    setSelectedProvince(DEFAULT_PROVINCE);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().getLocation({
      type: 'wgs84',
      success: function success() {
        setLocationStatus('success');
        var saved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().getStorageSync('selected_city');
        setLocationCityName(saved || '当前城市');
        // 如果有已保存的城市，自动选中
        if (saved && saved.trim()) {
          setSelectedCity(saved.trim());
        }
      },
      fail: function fail() {
        return setLocationStatus('fail');
      }
    });
  }, [visible]);
  var handleConfirm = function handleConfirm() {
    console.log('[城市选择] handleConfirm 被调用', {
      selectedCity: selectedCity,
      keyword: keyword,
      filteredCities: filteredCities
    });
    var city = selectedCity || (keyword.trim() && filteredCities.length === 1 ? filteredCities[0] : '');
    console.log('[城市选择] 最终选择的城市', city);
    if (!city) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
        title: '请先选择一个城市',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    // 先保存到storage
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().setStorageSync('selected_city', city);
    console.log('[城市选择] 已保存城市到storage', city);

    // 调用回调，让父组件关闭弹窗并更新显示
    if (onConfirm) {
      console.log('[城市选择] 调用onConfirm回调', city);
      onConfirm(city);
    }

    // 显示成功提示
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
      title: "\u5DF2\u9009\u62E9".concat(city),
      icon: 'success',
      duration: 2000
    });
  };
  var handleClose = function handleClose() {
    if (onClose) {
      onClose();
    }
  };

  // 修复：确保正确判断是否有选择
  var hasSelection = !!selectedCity || keyword.trim() && filteredCities.length === 1;

  // 调试日志
  (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(function () {
    if (visible) {
      console.log('[城市选择] 状态更新', {
        selectedCity: selectedCity,
        hasSelection: hasSelection,
        keyword: keyword,
        filteredCities: filteredCities.length
      });
    }
  }, [selectedCity, hasSelection, keyword, filteredCities.length, visible]);
  if (!visible) return null;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
    className: "city-picker-modal-mask",
    onClick: handleClose,
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "city-picker-modal",
      onClick: function onClick(e) {
        return e.stopPropagation();
      },
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "city-picker-header",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          className: "city-picker-title",
          children: "\u9009\u62E9\u57CE\u5E02"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
          className: "city-picker-close",
          onClick: handleClose,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
            children: "\u2715"
          })
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.ScrollView, {
        scrollY: true,
        className: "city-picker-content-outer",
        enhanced: true,
        showScrollbar: false,
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
          className: "city-picker-content",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
            className: "location-tip",
            children: [locationStatus === 'loading' && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.Fragment, {
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-icon",
                children: "\uD83D\uDCCD"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-text loading",
                children: "\u5B9A\u4F4D\u4E2D..."
              })]
            }), locationStatus === 'success' && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.Fragment, {
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-icon",
                children: "\uD83D\uDCCD"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-text",
                children: "\u5F53\u524D\u5B9A\u4F4D\u57CE\u5E02\uFF1A"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-city",
                children: locationCityName
              })]
            }), locationStatus === 'fail' && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.Fragment, {
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-icon",
                children: "\u26A0\uFE0F"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "location-text fail",
                children: "\u5B9A\u4F4D\u5931\u8D25\uFF0C\u8BF7\u624B\u52A8\u9009\u62E9\u57CE\u5E02"
              })]
            })]
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
            className: "hot-section",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
              className: "section-title",
              children: "\u70ED\u95E8\u57CE\u5E02"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
              className: "hot-tags",
              children: HOT_CITIES.map(function (c) {
                return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
                  className: "hot-tag ".concat(selectedCity === c.value ? 'active' : ''),
                  onClick: function onClick(e) {
                    e.stopPropagation();
                    console.log('[城市选择] 点击热门城市', c.value);
                    setSelectedCity(c.value);
                  },
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                    children: c.label
                  })
                }, c.value);
              })
            })]
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
            className: "search-section",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
              className: "search-wrap",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "search-icon",
                children: "\uD83D\uDD0D"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Input, {
                className: "search-input",
                placeholder: "\u8F93\u5165\u57CE\u5E02\u540D\u6216\u62FC\u97F3\u641C\u7D22",
                placeholderClass: "search-placeholder",
                value: keyword,
                onInput: function onInput(e) {
                  var _e$detail;
                  return setKeyword(((_e$detail = e.detail) === null || _e$detail === void 0 ? void 0 : _e$detail.value) || '');
                }
              })]
            }), keyword.trim() && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
              className: "search-result-wrap",
              children: filteredCities.length === 0 ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                className: "search-no-result",
                children: "\u672A\u627E\u5230\u76F8\u5173\u57CE\u5E02"
              }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
                className: "search-result-list",
                children: filteredCities.map(function (c) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
                    className: "search-result-item ".concat(selectedCity === c ? 'active' : ''),
                    onClick: function onClick() {
                      return setSelectedCity(c);
                    },
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                      children: c
                    })
                  }, c);
                })
              })
            })]
          }), !keyword.trim() && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
            className: "pick-section",
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
              className: "pick-row",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.ScrollView, {
                scrollY: true,
                className: "province-list",
                enhanced: true,
                showScrollbar: false,
                children: PROVINCE_NAMES.map(function (p) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
                    className: "province-item ".concat(selectedProvince === p ? 'active' : ''),
                    onClick: function onClick() {
                      setSelectedProvince(p);
                      setSelectedCity('');
                    },
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                      children: p
                    })
                  }, p);
                })
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.ScrollView, {
                scrollY: true,
                className: "city-list",
                enhanced: true,
                showScrollbar: false,
                children: cityList.map(function (c) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
                    className: "city-item ".concat(selectedCity === c ? 'active' : ''),
                    onClick: function onClick() {
                      return setSelectedCity(c);
                    },
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
                      children: c
                    })
                  }, c);
                })
              })]
            })
          })]
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "city-picker-footer",
        style: {
          position: 'relative',
          zIndex: 100
        },
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
          className: "confirm-btn ".concat(hasSelection ? 'active' : ''),
          onClick: function onClick(e) {
            e.stopPropagation();
            console.log('[城市选择] 点击确认按钮', {
              hasSelection: hasSelection,
              selectedCity: selectedCity,
              keyword: keyword,
              filteredCities: filteredCities
            });
            if (hasSelection) {
              handleConfirm();
            } else {
              console.log('[城市选择] 没有选择城市，显示提示');
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_3___default().showToast({
                title: '请先选择一个城市',
                icon: 'none',
                duration: 2000
              });
            }
          },
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_4__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
            className: "btn-text",
            children: "\u786E\u8BA4\u9009\u62E9"
          })
        })
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (CityPickerModal);

/***/ }),

/***/ "./src/components/FloatingDesignerAvatar.tsx":
/*!***************************************************!*\
  !*** ./src/components/FloatingDesignerAvatar.tsx ***!
  \***************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js */ "./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../services/api */ "./src/services/api.ts");
/* harmony import */ var _utils_markdownRenderer__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../utils/markdownRenderer */ "./src/utils/markdownRenderer.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__);











/**
 * AI设计师悬浮头像组件 - 真正的聊天机器人
 * 功能：
 * 1. 可拖拽悬浮在页面任意位置
 * 2. 点击头像弹出AI设计师聊天对话框
 * 3. 支持多轮对话，维护对话历史
 * 4. 显示拖拽提示（首次显示）
 */
var FloatingDesignerAvatar = function FloatingDesignerAvatar(_ref) {
  var _ref$showDragHint = _ref.showDragHint,
    showDragHint = _ref$showDragHint === void 0 ? true : _ref$showDragHint,
    _ref$initialPosition = _ref.initialPosition,
    initialPosition = _ref$initialPosition === void 0 ? {
      x: 20,
      y: 200
    } : _ref$initialPosition,
    _ref$fixedMode = _ref.fixedMode,
    fixedMode = _ref$fixedMode === void 0 ? false : _ref$fixedMode,
    _ref$fixedContainerCl = _ref.fixedContainerClassName,
    fixedContainerClassName = _ref$fixedContainerCl === void 0 ? '' : _ref$fixedContainerCl;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(initialPosition),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState, 2),
    position = _useState2[0],
    setPosition = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState3, 2),
    dragging = _useState4[0],
    setDragging = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState5, 2),
    showDialog = _useState6[0],
    setShowDialog = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(''),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState7, 2),
    inputMessage = _useState8[0],
    setInputMessage = _useState8[1];
  var _useState9 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState9, 2),
    loading = _useState0[0],
    setLoading = _useState0[1];
  var _useState1 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(showDragHint),
    _useState10 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState1, 2),
    showHint = _useState10[0],
    setShowHint = _useState10[1];
  var _useState11 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(true),
    _useState12 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState11, 2),
    isFirstTime = _useState12[0],
    setIsFirstTime = _useState12[1];
  var _useState13 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(true),
    _useState14 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState13, 2),
    showStaticHint = _useState14[0],
    setShowStaticHint = _useState14[1]; // 静态提示语"试试和AI设计师咨询"
  var _useState15 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState16 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState15, 2),
    hasClicked = _useState16[0],
    setHasClicked = _useState16[1]; // 记录是否点击过
  var _useState17 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(''),
    _useState18 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState17, 2),
    chatSessionId = _useState18[0],
    setChatSessionId = _useState18[1];
  var _useState19 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)([]),
    _useState20 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState19, 2),
    messages = _useState20[0],
    setMessages = _useState20[1];
  var _useState21 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState22 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState21, 2),
    isCreatingSession = _useState22[0],
    setIsCreatingSession = _useState22[1];
  var startPosRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)({
    x: 0,
    y: 0
  });
  var avatarRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(null);
  var messagesEndRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(null);
  var scrollViewRef = (0,react__WEBPACK_IMPORTED_MODULE_4__.useRef)(null);

  // 检查是否是第一次显示
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    var hasSeen = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('has_seen_designer_avatar');
    if (hasSeen) {
      setIsFirstTime(false);
      setShowHint(false);
    } else {
      setIsFirstTime(true);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('has_seen_designer_avatar', '1');
    }

    // 固定模式下，默认显示静态提示语
    if (fixedMode) {
      setShowStaticHint(true);
    }
  }, [fixedMode]);

  // 处理触摸开始
  var handleTouchStart = function handleTouchStart(e) {
    if (fixedMode) return; // 固定模式下不可拖拽

    var touch = e.touches[0];
    startPosRef.current = {
      x: touch.clientX - position.x,
      y: touch.clientY - position.y
    };
    setDragging(true);
    setShowHint(false); // 开始拖拽时隐藏提示
    setShowStaticHint(false); // 隐藏静态提示语
  };

  // 处理触摸移动
  var handleTouchMove = function handleTouchMove(e) {
    if (!dragging || fixedMode) return;
    var touch = e.touches[0];
    var newX = touch.clientX - startPosRef.current.x;
    var newY = touch.clientY - startPosRef.current.y;

    // 限制在屏幕范围内
    var screenWidth = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getSystemInfoSync().windowWidth;
    var screenHeight = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getSystemInfoSync().windowHeight;
    var avatarSize = 60; // 头像大小

    var clampedX = Math.max(0, Math.min(newX, screenWidth - avatarSize));
    var clampedY = Math.max(0, Math.min(newY, screenHeight - avatarSize));
    setPosition({
      x: clampedX,
      y: clampedY
    });
  };

  // 处理触摸结束
  var handleTouchEnd = function handleTouchEnd() {
    setDragging(false);
    // 保存位置到本地存储
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().setStorageSync('designer_avatar_position', JSON.stringify(position));
  };

  // 检查用户是否已登录
  var checkUserLogin = function checkUserLogin() {
    var token = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('token') || _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('access_token');
    return !!token;
  };

  // 点击头像打开对话框
  var handleAvatarClick = /*#__PURE__*/function () {
    var _ref2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee() {
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context) {
        while (1) switch (_context.n) {
          case 0:
            if (!dragging) {
              _context.n = 1;
              break;
            }
            return _context.a(2);
          case 1:
            // 如果是拖拽结束，不打开对话框

            // 记录点击过
            setHasClicked(true);
            setShowStaticHint(false); // 点击后隐藏静态提示语

            // 如果是固定模式且第一次点击，显示拖拽提示
            if (fixedMode && !hasClicked) {
              setShowHint(true);
            }

            // 检查用户是否已登录
            if (checkUserLogin()) {
              _context.n = 2;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showModal({
              title: '请先登录',
              content: '使用AI设计师功能需要先登录账号',
              confirmText: '去登录',
              cancelText: '取消',
              success: function success(res) {
                if (res.confirm) {
                  // 跳转到个人中心页（登录页）
                  _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().switchTab({
                    url: '/pages/profile/index'
                  });
                }
              }
            });
            return _context.a(2);
          case 2:
            setShowDialog(true);
            setShowHint(false); // 点击时隐藏提示

            // 如果没有session，创建一个新的
            if (chatSessionId) {
              _context.n = 3;
              break;
            }
            _context.n = 3;
            return createNewChatSession();
          case 3:
            return _context.a(2);
        }
      }, _callee);
    }));
    return function handleAvatarClick() {
      return _ref2.apply(this, arguments);
    };
  }();

  // 创建新的聊天session
  var createNewChatSession = /*#__PURE__*/function () {
    var _ref3 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee2() {
      var timeoutPromise, requestPromise, response, welcomeMessage, _error$message, _error$errMsg, _error$message2, _error$message3, _error$message4, _error$message5, isUnauthorizedError, _welcomeMessage, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            if (checkUserLogin()) {
              _context2.n = 1;
              break;
            }
            setShowDialog(false);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '请先登录',
              icon: 'none'
            });
            return _context2.a(2);
          case 1:
            _context2.p = 1;
            setIsCreatingSession(true);

            // 设置创建会话超时（120秒/2分钟）
            timeoutPromise = new Promise(function (_, reject) {
              setTimeout(function () {
                return reject(new Error('创建会话超时，请检查网络连接'));
              }, 120000);
            }); // 创建聊天session
            requestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.createChatSession(); // 使用Promise.race实现超时控制
            _context2.n = 2;
            return Promise.race([requestPromise, timeoutPromise]);
          case 2:
            response = _context2.v;
            setChatSessionId(response.session_id);
            setMessages(response.messages || []);

            // 如果没有初始消息，添加欢迎消息
            if (!response.messages || response.messages.length === 0) {
              welcomeMessage = {
                role: 'assistant',
                content: '您好！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
                timestamp: Date.now() / 1000
              };
              setMessages([welcomeMessage]);
            }
            _context2.n = 7;
            break;
          case 3:
            _context2.p = 3;
            _t = _context2.v;
            console.error('创建聊天session失败:', _t);

            // 检查是否是超时错误
            if (!(_t !== null && _t !== void 0 && (_error$message = _t.message) !== null && _error$message !== void 0 && _error$message.includes('超时') || _t !== null && _t !== void 0 && (_error$errMsg = _t.errMsg) !== null && _error$errMsg !== void 0 && _error$errMsg.includes('timeout'))) {
              _context2.n = 4;
              break;
            }
            console.log('[AI设计师] 创建会话超时，可能是网络问题');
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '网络连接超时，请检查网络后重试',
              icon: 'none',
              duration: 3000
            });
            _context2.n = 6;
            break;
          case 4:
            isUnauthorizedError = _t.statusCode === 401 || _t.code === 401 || _t.response && _t.response.status === 401 || ((_error$message2 = _t.message) === null || _error$message2 === void 0 ? void 0 : _error$message2.includes('未授权')) || ((_error$message3 = _t.message) === null || _error$message3 === void 0 ? void 0 : _error$message3.includes('Unauthorized')) || ((_error$message4 = _t.message) === null || _error$message4 === void 0 ? void 0 : _error$message4.includes('登录')) || ((_error$message5 = _t.message) === null || _error$message5 === void 0 ? void 0 : _error$message5.includes('认证')); // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
            // 只需要关闭对话框即可，不显示任何错误提示
            if (!isUnauthorizedError) {
              _context2.n = 5;
              break;
            }
            console.log('401错误已由postWithAuth处理，关闭对话框，不显示错误提示');
            setShowDialog(false);
            return _context2.a(2);
          case 5:
            // 其他错误显示提示
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: _t.message || '创建对话失败，请稍后重试',
              icon: 'none'
            });
          case 6:
            // 如果创建失败，显示默认欢迎消息
            _welcomeMessage = {
              role: 'assistant',
              content: '您好！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
              timestamp: Date.now() / 1000
            };
            setMessages([_welcomeMessage]);
          case 7:
            _context2.p = 7;
            setIsCreatingSession(false);
            return _context2.f(7);
          case 8:
            return _context2.a(2);
        }
      }, _callee2, null, [[1, 3, 7, 8]]);
    }));
    return function createNewChatSession() {
      return _ref3.apply(this, arguments);
    };
  }();

  // 关闭对话框
  var handleCloseDialog = function handleCloseDialog() {
    setShowDialog(false);
    setInputMessage('');
  };

  // 发送消息
  var handleSendMessage = /*#__PURE__*/function () {
    var _ref4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee3() {
      var userMessage, userMsg, timeoutPromise, requestPromise, response, aiMsg, _error$message6, _error$errMsg2, _error$message7, _error$message8, timeoutMsg, _error$response, errorMsg, _t2;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context3) {
        while (1) switch (_context3.p = _context3.n) {
          case 0:
            if (!(!inputMessage.trim() || !chatSessionId)) {
              _context3.n = 1;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '请输入消息',
              icon: 'none'
            });
            return _context3.a(2);
          case 1:
            if (checkUserLogin()) {
              _context3.n = 2;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showModal({
              title: '请先登录',
              content: '发送消息需要先登录账号',
              confirmText: '去登录',
              cancelText: '取消',
              success: function success(res) {
                if (res.confirm) {
                  _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().switchTab({
                    url: '/pages/profile/index'
                  });
                }
              }
            });
            return _context3.a(2);
          case 2:
            userMessage = inputMessage.trim();
            setInputMessage('');

            // 添加用户消息到界面
            userMsg = {
              role: 'user',
              content: userMessage,
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [userMsg]);
            });
            setLoading(true);
            _context3.p = 3;
            // 设置请求超时（600秒/10分钟，因为AI生成效果图和漫游视频需要较长时间）
            timeoutPromise = new Promise(function (_, reject) {
              setTimeout(function () {
                return reject(new Error('请求超时，AI响应时间较长，请稍后重试'));
              }, 600000);
            }); // 发送消息到服务器
            requestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.sendChatMessage(chatSessionId, userMessage); // 使用Promise.race实现超时控制
            _context3.n = 4;
            return Promise.race([requestPromise, timeoutPromise]);
          case 4:
            response = _context3.v;
            // 添加AI回复到界面
            aiMsg = {
              role: 'assistant',
              content: response.answer,
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [aiMsg]);
            });

            // 滚动到底部
            setTimeout(function () {
              if (scrollViewRef.current) {
                // 在微信小程序中使用Taro的API滚动到底部
                try {
                  var _scrollViewRef$curren, _scrollViewRef$curren2;
                  // 使用scrollView的scrollToBottom方法
                  (_scrollViewRef$curren = (_scrollViewRef$curren2 = scrollViewRef.current).scrollToBottom) === null || _scrollViewRef$curren === void 0 || _scrollViewRef$curren.call(_scrollViewRef$curren2);
                } catch (error) {
                  console.log('滚动到底部失败:', error);
                  // 备用方案：使用scrollIntoView（如果可用）
                  if (messagesEndRef.current) {
                    var element = messagesEndRef.current;
                    if (element && element.nodeType === 1 && element.scrollIntoView) {
                      element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'end'
                      });
                    }
                  }
                }
              }
            }, 100);
            _context3.n = 6;
            break;
          case 5:
            _context3.p = 5;
            _t2 = _context3.v;
            console.error('发送消息失败:', _t2);

            // 检查是否是超时错误
            if (_t2 !== null && _t2 !== void 0 && (_error$message6 = _t2.message) !== null && _error$message6 !== void 0 && _error$message6.includes('超时') || _t2 !== null && _t2 !== void 0 && (_error$errMsg2 = _t2.errMsg) !== null && _error$errMsg2 !== void 0 && _error$errMsg2.includes('timeout')) {
              console.log('[AI设计师] 请求超时，可能是AI生成时间较长或网络问题');
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: 'AI响应时间较长，请稍后重试',
                icon: 'none',
                duration: 3000
              });

              // 添加超时提示消息
              timeoutMsg = {
                role: 'assistant',
                content: '抱歉，AI响应时间较长，请稍后重试或简化您的问题。',
                timestamp: Date.now() / 1000
              };
              setMessages(function (prev) {
                return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [timeoutMsg]);
              });
            }
            // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
            else if (_t2.statusCode === 401 || (_error$message7 = _t2.message) !== null && _error$message7 !== void 0 && _error$message7.includes('未授权') || (_error$message8 = _t2.message) !== null && _error$message8 !== void 0 && _error$message8.includes('登录')) {
              console.log('发送消息时401错误已由postWithAuth处理');
              // 不需要显示额外提示，postWithAuth已经处理了
            } else {
              // 添加调试日志，查看错误详情
              console.log('[AI设计师] 错误详情:', {
                message: _t2.message,
                statusCode: _t2.statusCode,
                response: _t2.response,
                data: (_error$response = _t2.response) === null || _error$response === void 0 ? void 0 : _error$response.data
              });
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: _t2.message || '发送失败，请稍后重试',
                icon: 'none'
              });

              // 添加错误消息
              errorMsg = {
                role: 'assistant',
                content: '抱歉，我暂时无法回答您的问题，请稍后重试。',
                timestamp: Date.now() / 1000
              };
              setMessages(function (prev) {
                return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [errorMsg]);
              });
            }
          case 6:
            _context3.p = 6;
            setLoading(false);
            return _context3.f(6);
          case 7:
            return _context3.a(2);
        }
      }, _callee3, null, [[3, 5, 6, 7]]);
    }));
    return function handleSendMessage() {
      return _ref4.apply(this, arguments);
    };
  }();

  // 快速问题示例
  var quickQuestions = ['现代简约风格的特点是什么？', '小户型如何设计显得空间更大？', '装修预算怎么分配比较合理？', '选择地板还是瓷砖比较好？', '厨房装修要注意哪些细节？'];

  // 处理图片上传
  var handleUploadImage = /*#__PURE__*/function () {
    var _ref5 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee4() {
      var res, tempFilePath, fileName, uploadTimeoutPromise, uploadRequestPromise, uploadResult, imageMessage, messageTimeoutPromise, messageRequestPromise, response, aiReply, _error$message9, _error$errMsg3, timeoutReply, retryMessage, _aiReply, _aiReply2, _uploadError$message, _uploadError$errMsg, _uploadError$message2, _uploadError$message3, _imageMessage, _aiReply3, isUserCancel, _t3, _t4, _t5;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context4) {
        while (1) switch (_context4.p = _context4.n) {
          case 0:
            if (checkUserLogin()) {
              _context4.n = 1;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showModal({
              title: '请先登录',
              content: '上传图片需要先登录账号',
              confirmText: '去登录',
              cancelText: '取消',
              success: function success(res) {
                if (res.confirm) {
                  _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().switchTab({
                    url: '/pages/profile/index'
                  });
                }
              }
            });
            return _context4.a(2);
          case 1:
            _context4.p = 1;
            _context4.n = 2;
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().chooseImage({
              count: 1,
              sizeType: ['compressed'],
              sourceType: ['album', 'camera']
            });
          case 2:
            res = _context4.v;
            if (!(res.tempFilePaths.length > 0)) {
              _context4.n = 16;
              break;
            }
            tempFilePath = res.tempFilePaths[0];
            fileName = "designer_".concat(Date.now(), ".jpg"); // 显示上传中提示
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showLoading({
              title: '上传户型图中...'
            });
            _context4.p = 3;
            // 设置图片上传超时（120秒/2分钟）
            uploadTimeoutPromise = new Promise(function (_, reject) {
              setTimeout(function () {
                return reject(new Error('图片上传超时，请检查网络连接'));
              }, 120000);
            }); // 调用图片上传API
            uploadRequestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.uploadImage(tempFilePath, fileName); // 使用Promise.race实现超时控制
            _context4.n = 4;
            return Promise.race([uploadRequestPromise, uploadTimeoutPromise]);
          case 4:
            uploadResult = _context4.v;
            if (!(uploadResult.success && uploadResult.image_url)) {
              _context4.n = 13;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().hideLoading();
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '户型图上传成功！',
              icon: 'success',
              duration: 2000
            });

            // 添加一条用户消息，显示已上传图片
            imageMessage = {
              role: 'user',
              content: "\uD83D\uDCF8 \u5DF2\u4E0A\u4F20\u6237\u578B\u56FE\uFF0C\u8BF7\u5E2E\u6211\u5206\u6790\u4E00\u4E0B",
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [imageMessage]);
            });

            // 如果有聊天session，发送消息给AI设计师
            if (!chatSessionId) {
              _context4.n = 10;
              break;
            }
            setLoading(true);
            _context4.p = 5;
            // 设置发送消息超时（600秒/10分钟，因为AI分析效果图和生成漫游视频需要较长时间）
            messageTimeoutPromise = new Promise(function (_, reject) {
              setTimeout(function () {
                return reject(new Error('AI分析超时，请稍后重试'));
              }, 600000);
            }); // 发送包含图片URL的消息
            messageRequestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.sendChatMessage(chatSessionId, '请帮我分析一下这个户型图，给出装修建议和效果图生成思路。', [uploadResult.image_url]); // 使用Promise.race实现超时控制
            _context4.n = 6;
            return Promise.race([messageRequestPromise, messageTimeoutPromise]);
          case 6:
            response = _context4.v;
            // 添加AI回复
            aiReply = {
              role: 'assistant',
              content: response.answer,
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [aiReply]);
            });
            _context4.n = 8;
            break;
          case 7:
            _context4.p = 7;
            _t3 = _context4.v;
            console.error('发送图片消息失败:', _t3);

            // 检查是否是超时错误
            if (_t3 !== null && _t3 !== void 0 && (_error$message9 = _t3.message) !== null && _error$message9 !== void 0 && _error$message9.includes('超时') || _t3 !== null && _t3 !== void 0 && (_error$errMsg3 = _t3.errMsg) !== null && _error$errMsg3 !== void 0 && _error$errMsg3.includes('timeout')) {
              console.log('[AI设计师] 图片分析超时，可能是AI处理时间较长');
              // 添加超时提示消息，并提供重试按钮
              timeoutReply = {
                role: 'assistant',
                content: '感谢上传户型图！AI分析时间较长，可能需要更多时间处理。\n\n您可以选择：\n1. 稍后重试查看分析结果\n2. 或者先问其他装修问题\n\n户型图分析、效果图生成和漫游视频功能已上线，我可以为您提供专业的装修建议！',
                timestamp: Date.now() / 1000
              };
              setMessages(function (prev) {
                return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [timeoutReply]);
              });

              // 添加一个重试按钮（通过特殊消息格式）
              retryMessage = {
                role: 'assistant',
                content: 'RETRY_ANALYSIS_BUTTON',
                // 特殊标记，用于识别重试按钮
                timestamp: Date.now() / 1000
              };
              setMessages(function (prev) {
                return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [retryMessage]);
              });
            } else {
              // 添加默认AI回复
              _aiReply = {
                role: 'assistant',
                content: '感谢上传户型图！我正在分析您的户型...\n\n户型图分析、效果图生成和漫游视频功能已上线，我可以为您提供专业的装修建议！',
                timestamp: Date.now() / 1000
              };
              setMessages(function (prev) {
                return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [_aiReply]);
              });
            }
          case 8:
            _context4.p = 8;
            setLoading(false);
            return _context4.f(8);
          case 9:
            _context4.n = 12;
            break;
          case 10:
            _context4.n = 11;
            return createNewChatSession();
          case 11:
            // 添加默认AI回复
            _aiReply2 = {
              role: 'assistant',
              content: '感谢上传户型图！我正在分析您的户型...\n\n户型图分析、效果图生成和漫游视频功能已上线，我可以为您提供专业的装修建议！',
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [_aiReply2]);
            });
          case 12:
            _context4.n = 14;
            break;
          case 13:
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().hideLoading();
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: uploadResult.error_message || '上传失败，请重试',
              icon: 'none',
              duration: 3000
            });
          case 14:
            _context4.n = 16;
            break;
          case 15:
            _context4.p = 15;
            _t4 = _context4.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().hideLoading();
            console.error('上传图片失败:', _t4);

            // 检查是否是超时错误
            if (_t4 !== null && _t4 !== void 0 && (_uploadError$message = _t4.message) !== null && _uploadError$message !== void 0 && _uploadError$message.includes('超时') || _t4 !== null && _t4 !== void 0 && (_uploadError$errMsg = _t4.errMsg) !== null && _uploadError$errMsg !== void 0 && _uploadError$errMsg.includes('timeout')) {
              console.log('[AI设计师] 图片上传超时，可能是网络问题');
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: '图片上传超时，请检查网络连接',
                icon: 'none',
                duration: 3000
              });
            }
            // 检查是否是401错误
            else if (_t4.statusCode === 401 || (_uploadError$message2 = _t4.message) !== null && _uploadError$message2 !== void 0 && _uploadError$message2.includes('未授权') || (_uploadError$message3 = _t4.message) !== null && _uploadError$message3 !== void 0 && _uploadError$message3.includes('登录')) {
              console.log('上传图片时401错误已处理');
              // postWithAuth已经处理了401错误，这里不需要重复处理
            } else {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: _t4.message || '上传失败，请检查网络',
                icon: 'none',
                duration: 3000
              });
            }

            // 即使上传失败，也添加一条消息，让用户知道功能已上线
            _imageMessage = {
              role: 'user',
              content: "\uD83D\uDCF8 \u5C1D\u8BD5\u4E0A\u4F20\u6237\u578B\u56FE\uFF08\u4E0A\u4F20\u5931\u8D25\uFF09",
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [_imageMessage]);
            });

            // 添加AI回复
            _aiReply3 = {
              role: 'assistant',
              content: '户型图上传功能已上线！下次请再试一下上传您的户型图，我可以为您提供专业的装修分析和效果图生成建议。',
              timestamp: Date.now() / 1000
            };
            setMessages(function (prev) {
              return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [_aiReply3]);
            });
          case 16:
            _context4.n = 18;
            break;
          case 17:
            _context4.p = 17;
            _t5 = _context4.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().hideLoading();

            // 检查是否是用户取消操作
            isUserCancel = _t5.errMsg && (_t5.errMsg.includes('cancel') || _t5.errMsg.includes('取消') || _t5.errMsg === 'chooseImage:fail cancel');
            if (!isUserCancel) {
              // 只有非取消错误才显示提示和记录错误日志
              console.error('选择图片失败:', _t5);
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: _t5.errMsg || '选择图片失败',
                icon: 'none',
                duration: 2000
              });
            } else {
              // 用户取消操作，不显示错误提示，只记录调试信息
              console.log('用户取消了图片选择');
            }
          case 18:
            return _context4.a(2);
        }
      }, _callee4, null, [[5, 7, 8, 9], [3, 15], [1, 17]]);
    }));
    return function handleUploadImage() {
      return _ref5.apply(this, arguments);
    };
  }();
  var handleQuickQuestion = function handleQuickQuestion(question) {
    setInputMessage(question);
  };

  // 清空对话
  var handleClearChat = /*#__PURE__*/function () {
    var _ref6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee5() {
      var timeoutPromise, requestPromise, welcomeMessage, _error$message0, _error$errMsg4, _error$message1, _error$message10, _t6;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context5) {
        while (1) switch (_context5.p = _context5.n) {
          case 0:
            if (chatSessionId) {
              _context5.n = 1;
              break;
            }
            return _context5.a(2);
          case 1:
            if (checkUserLogin()) {
              _context5.n = 2;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showModal({
              title: '请先登录',
              content: '清空对话需要先登录账号',
              confirmText: '去登录',
              cancelText: '取消',
              success: function success(res) {
                if (res.confirm) {
                  _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().switchTab({
                    url: '/pages/profile/index'
                  });
                }
              }
            });
            return _context5.a(2);
          case 2:
            _context5.p = 2;
            // 设置清空对话超时（60秒/1分钟）
            timeoutPromise = new Promise(function (_, reject) {
              setTimeout(function () {
                return reject(new Error('清空对话超时，请稍后重试'));
              }, 60000);
            }); // 清空对话历史
            requestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.clearChatHistory(chatSessionId); // 使用Promise.race实现超时控制
            _context5.n = 3;
            return Promise.race([requestPromise, timeoutPromise]);
          case 3:
            // 重置消息，只保留欢迎消息
            welcomeMessage = {
              role: 'assistant',
              content: '对话已清空！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
              timestamp: Date.now() / 1000
            };
            setMessages([welcomeMessage]);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '对话已清空',
              icon: 'success'
            });
            _context5.n = 5;
            break;
          case 4:
            _context5.p = 4;
            _t6 = _context5.v;
            console.error('清空对话失败:', _t6);

            // 检查是否是超时错误
            if (_t6 !== null && _t6 !== void 0 && (_error$message0 = _t6.message) !== null && _error$message0 !== void 0 && _error$message0.includes('超时') || _t6 !== null && _t6 !== void 0 && (_error$errMsg4 = _t6.errMsg) !== null && _error$errMsg4 !== void 0 && _error$errMsg4.includes('timeout')) {
              console.log('[AI设计师] 清空对话超时，可能是网络问题');
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: '清空对话超时，请稍后重试',
                icon: 'none',
                duration: 3000
              });
            }
            // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
            else if (_t6.statusCode === 401 || (_error$message1 = _t6.message) !== null && _error$message1 !== void 0 && _error$message1.includes('未授权') || (_error$message10 = _t6.message) !== null && _error$message10 !== void 0 && _error$message10.includes('登录')) {
              console.log('清空对话时401错误已由postWithAuth处理');
              // 不需要显示额外提示，postWithAuth已经处理了
            } else {
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                title: _t6.message || '清空失败',
                icon: 'none'
              });
            }
          case 5:
            return _context5.a(2);
        }
      }, _callee5, null, [[2, 4]]);
    }));
    return function handleClearChat() {
      return _ref6.apply(this, arguments);
    };
  }();

  // 从本地存储加载位置
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    try {
      var savedPos = _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().getStorageSync('designer_avatar_position');
      if (savedPos) {
        var pos = JSON.parse(savedPos);
        setPosition(pos);
      }
    } catch (error) {
      console.error('加载悬浮头像位置失败:', error);
    }
  }, []);

  // 自动隐藏提示
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    if (showHint) {
      var timer = setTimeout(function () {
        setShowHint(false);
      }, 5000); // 5秒后自动隐藏
      return function () {
        return clearTimeout(timer);
      };
    }
  }, [showHint]);

  // 滚动到底部
  (0,react__WEBPACK_IMPORTED_MODULE_4__.useEffect)(function () {
    if (messages.length > 0 && scrollViewRef.current) {
      setTimeout(function () {
        if (scrollViewRef.current) {
          // 在微信小程序中使用Taro的API滚动到底部
          try {
            var _scrollViewRef$curren3, _scrollViewRef$curren4;
            // 使用scrollView的scrollToBottom方法
            (_scrollViewRef$curren3 = (_scrollViewRef$curren4 = scrollViewRef.current).scrollToBottom) === null || _scrollViewRef$curren3 === void 0 || _scrollViewRef$curren3.call(_scrollViewRef$curren4);
          } catch (error) {
            console.log('滚动到底部失败:', error);
            // 备用方案：使用scrollIntoView（如果可用）
            if (messagesEndRef.current) {
              var element = messagesEndRef.current;
              if (element && element.nodeType === 1 && element.scrollIntoView) {
                element.scrollIntoView({
                  behavior: 'smooth',
                  block: 'end'
                });
              }
            }
          }
        }
      }, 100);
    }
  }, [messages]);

  // 格式化时间
  var formatTime = function formatTime(timestamp) {
    var date = new Date(timestamp * 1000);
    return "".concat(date.getHours().toString().padStart(2, '0'), ":").concat(date.getMinutes().toString().padStart(2, '0'));
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.Fragment, {
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "floating-designer-avatar ".concat(dragging ? 'dragging' : ''),
      style: {
        left: "".concat(position.x, "px"),
        top: "".concat(position.y, "px"),
        transform: dragging ? 'scale(1.1)' : 'scale(1)'
      },
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
      onClick: handleAvatarClick,
      ref: avatarRef,
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "avatar-container",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Image, {
          className: "avatar-image",
          src: "https://zhuangxiu-images-dev.oss-cn-hangzhou.aliyuncs.com/avatar/avatar.png",
          mode: "aspectFill"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "avatar-badge",
          children: "AI"
        })]
      }), showStaticHint && fixedMode && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "static-hint",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "static-hint-text",
          children: "\u8BD5\u8BD5\u548CAI\u8BBE\u8BA1\u5E08\u54A8\u8BE2"
        })
      }), showHint && isFirstTime && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "drag-hint",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "hint-text",
          children: "\u8BD5\u8BD5\u62D6\u62FD\u5B83\u5230\u5408\u9002\u7684\u4F4D\u7F6E"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "hint-arrow",
          children: "\u2193"
        })]
      })]
    }), showDialog && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "designer-dialog-mask",
      onClick: handleCloseDialog,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "designer-dialog",
        onClick: function onClick(e) {
          return e.stopPropagation();
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-header",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "dialog-title",
            children: "AI\u8BBE\u8BA1\u5E08\u804A\u5929"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "dialog-actions",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Button, {
              className: "clear-btn",
              onClick: handleClearChat,
              disabled: messages.length <= 1,
              children: "\u6E05\u7A7A"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "dialog-close",
              onClick: handleCloseDialog,
              children: "\xD7"
            })]
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-content",
          children: isCreatingSession ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "loading-container",
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
              children: "\u6B63\u5728\u521D\u59CB\u5316\u5BF9\u8BDD..."
            })
          }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.Fragment, {
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.ScrollView, {
              className: "chat-messages",
              scrollY: true,
              ref: scrollViewRef,
              scrollWithAnimation: true,
              children: [messages.map(function (msg, index) {
                // 检查是否是重试按钮消息
                if (msg.content === 'RETRY_ANALYSIS_BUTTON') {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "message-item ai-message",
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                      className: "message-content",
                      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                        className: "retry-button-container",
                        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                          className: "retry-button-text",
                          children: "AI\u5206\u6790\u53EF\u80FD\u9700\u8981\u66F4\u591A\u65F6\u95F4"
                        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Button, {
                          className: "retry-button",
                          onClick: /*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee6() {
                            var lastUserMessage, timeoutPromise, requestPromise, response, aiMsg, _error$message11, _error$errMsg5, _t7;
                            return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context6) {
                              while (1) switch (_context6.p = _context6.n) {
                                case 0:
                                  // 重试分析逻辑
                                  lastUserMessage = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(messages).reverse().find(function (m) {
                                    return m.role === 'user';
                                  });
                                  if (!(lastUserMessage && lastUserMessage.content.includes('已上传户型图'))) {
                                    _context6.n = 5;
                                    break;
                                  }
                                  _context6.p = 1;
                                  setLoading(true);

                                  // 设置请求超时（600秒/10分钟，因为AI分析效果图和生成漫游视频需要较长时间）
                                  timeoutPromise = new Promise(function (_, reject) {
                                    setTimeout(function () {
                                      return reject(new Error('请求超时，AI响应时间较长，请稍后重试'));
                                    }, 600000);
                                  }); // 发送消息到服务器
                                  requestPromise = _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.sendChatMessage(chatSessionId, '请帮我分析一下这个户型图，给出装修建议和效果图生成思路。', [] // 图片URL已经在session中，不需要重新传
                                  ); // 使用Promise.race实现超时控制
                                  _context6.n = 2;
                                  return Promise.race([requestPromise, timeoutPromise]);
                                case 2:
                                  response = _context6.v;
                                  // 添加AI回复到界面
                                  aiMsg = {
                                    role: 'assistant',
                                    content: response.answer,
                                    timestamp: Date.now() / 1000
                                  };
                                  setMessages(function (prev) {
                                    return [].concat((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_toConsumableArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(prev), [aiMsg]);
                                  });

                                  // 移除重试按钮消息
                                  setMessages(function (prev) {
                                    return prev.filter(function (msg) {
                                      return msg.content !== 'RETRY_ANALYSIS_BUTTON';
                                    });
                                  });
                                  _context6.n = 4;
                                  break;
                                case 3:
                                  _context6.p = 3;
                                  _t7 = _context6.v;
                                  console.error('重试分析失败:', _t7);

                                  // 检查是否是超时错误
                                  if (_t7 !== null && _t7 !== void 0 && (_error$message11 = _t7.message) !== null && _error$message11 !== void 0 && _error$message11.includes('超时') || _t7 !== null && _t7 !== void 0 && (_error$errMsg5 = _t7.errMsg) !== null && _error$errMsg5 !== void 0 && _error$errMsg5.includes('timeout')) {
                                    console.log('[AI设计师] 重试分析超时');
                                    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                                      title: 'AI响应时间较长，请稍后重试',
                                      icon: 'none',
                                      duration: 3000
                                    });
                                  } else {
                                    _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
                                      title: _t7.message || '重试失败，请稍后重试',
                                      icon: 'none'
                                    });
                                  }
                                case 4:
                                  _context6.p = 4;
                                  setLoading(false);
                                  return _context6.f(4);
                                case 5:
                                  return _context6.a(2);
                              }
                            }, _callee6, null, [[1, 3, 4, 5]]);
                          })),
                          children: "\u91CD\u8BD5\u67E5\u770B\u5206\u6790\u7ED3\u679C"
                        })]
                      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                        className: "message-time",
                        children: formatTime(msg.timestamp)
                      })]
                    })
                  }, index);
                }

                // 检查是否是AI消息
                var isAIMessage = msg.role === 'assistant';
                return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "message-item ".concat(msg.role === 'user' ? 'user-message' : 'ai-message'),
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "message-content",
                    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "message-text",
                      children: isAIMessage ? (0,_utils_markdownRenderer__WEBPACK_IMPORTED_MODULE_8__.renderFormattedText)(msg.content) : msg.content
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "message-time",
                      children: formatTime(msg.timestamp)
                    })]
                  })
                }, index);
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                ref: messagesEndRef
              })]
            }), messages.length <= 2 && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "upload-hint-section",
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "upload-hint-card",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "upload-hint-icon",
                  children: "\uD83D\uDCF8"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "upload-hint-title",
                  children: "\u4E0A\u4F20\u6237\u578B\u56FE\uFF0C\u4E00\u952E\u751F\u6210"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "upload-hint-subtitle",
                  children: "\u88C5\u4FEE\u6548\u679C\u56FE + \u6F2B\u6E38\u89C6\u9891"
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "upload-hint-btn",
                  onClick: handleUploadImage,
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                    className: "upload-hint-btn-text",
                    children: "\u4E0A\u4F20\u6237\u578B\u56FE"
                  })
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                  className: "upload-hint-tip",
                  children: "\u652F\u6301 JPG\u3001PNG \u683C\u5F0F\uFF0C\u5EFA\u8BAE\u4E0A\u4F20\u6E05\u6670\u6237\u578B\u56FE"
                })]
              })
            }), messages.length <= 2 && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "quick-questions",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "quick-title",
                children: "\u6216\u8005\u5FEB\u901F\u63D0\u95EE\uFF1A"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "quick-questions-grid",
                children: quickQuestions.map(function (q, index) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "quick-question-item",
                    onClick: function onClick() {
                      return handleQuickQuestion(q);
                    },
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "quick-question-text",
                      children: q
                    })
                  }, index);
                })
              })]
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "input-area",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "input-left",
                children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Input, {
                  className: "message-input",
                  placeholder: "\u8F93\u5165\u60A8\u7684\u95EE\u9898\u6216\u4E0A\u4F20\u6237\u578B\u56FE...",
                  value: inputMessage,
                  onInput: function onInput(e) {
                    return setInputMessage(e.detail.value);
                  },
                  focus: !inputMessage,
                  confirmType: "send",
                  onConfirm: handleSendMessage
                })
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "input-right",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "upload-btn-large",
                  onClick: handleUploadImage,
                  children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                    className: "upload-btn-large-icon",
                    children: "\uD83D\uDCF7"
                  }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                    className: "upload-btn-large-text",
                    children: "\u4E0A\u4F20"
                  })]
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Button, {
                  className: "send-btn",
                  onClick: handleSendMessage,
                  disabled: loading || !inputMessage.trim(),
                  children: loading ? '思考中...' : '发送'
                })]
              })]
            })]
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-footer",
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_9__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "footer-text",
            children: "AI\u88C5\u4FEE\u8BBE\u8BA1\u5E08 - \u6F2B\u6E38\u89C6\u9891\u751F\u6210\u5668 | \u4E0A\u4F20\u6237\u578B\u56FE\u751F\u6210\u6548\u679C\u56FE+\u89C6\u9891"
          })
        })]
      })
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (FloatingDesignerAvatar);

/***/ }),

/***/ "./src/components/UploadConfirmModal/index.tsx":
/*!*****************************************************!*\
  !*** ./src/components/UploadConfirmModal/index.tsx ***!
  \*****************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__);





/**
 * 上传前确认弹窗 - 未检测公司时展示，含「不再提示」勾选（PRD FR-007）
 */

var UploadConfirmModal = function UploadConfirmModal(_ref) {
  var visible = _ref.visible,
    type = _ref.type,
    onConfirm = _ref.onConfirm,
    onGoScan = _ref.onGoScan,
    onClose = _ref.onClose;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_0__["default"])(_useState, 2),
    noMore = _useState2[0],
    setNoMore = _useState2[1];
  var content = type === 'quote' ? '建议先检测装修公司风险，再上传报价单' : '建议先检测装修公司风险，再上传合同';
  if (!visible) return null;
  var handleConfirm = function handleConfirm() {
    onConfirm(noMore);
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
    className: "upload-confirm-mask",
    onClick: onClose,
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
      className: "upload-confirm-modal",
      onClick: function onClick(e) {
        return e.stopPropagation();
      },
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        className: "close-btn",
        onClick: onClose,
        children: "\xD7"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        className: "modal-title",
        children: "\u6E29\u99A8\u63D0\u793A"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
        className: "modal-content",
        children: content
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "checkbox-row",
        onClick: function onClick() {
          return setNoMore(!noMore);
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          className: "checkbox ".concat(noMore ? 'checked' : ''),
          children: noMore ? '✓' : ''
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
          className: "checkbox-label",
          children: "\u4E0D\u518D\u63D0\u793A"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
        className: "modal-btns",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
          className: "btn secondary",
          onClick: onGoScan,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
            children: "\u53BB\u68C0\u6D4B"
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.View, {
          className: "btn primary",
          onClick: handleConfirm,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_3__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_2__.Text, {
            children: "\u7EE7\u7EED\u4E0A\u4F20"
          })
        })]
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (UploadConfirmModal);

/***/ }),

/***/ "./src/pages/index/index.tsx":
/*!***********************************!*\
  !*** ./src/pages/index/index.tsx ***!
  \***********************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_index_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/index/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/index/index!./src/pages/index/index.tsx");


var config = {"navigationBarTitleText":"装修避坑管家","navigationBarBackgroundColor":"#1677FF","navigationBarTextStyle":"white","enableShareAppMessage":true,"onReachBottomDistance":50};

_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_index_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"].enableShareAppMessage = true
var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_index_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/index/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_index_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ }),

/***/ "./src/utils/markdownRenderer.ts":
/*!***************************************!*\
  !*** ./src/utils/markdownRenderer.ts ***!
  \***************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   renderFormattedText: function() { return /* binding */ renderFormattedText; }
/* harmony export */ });
/* unused harmony exports parseMarkdown, renderMarkdown, renderSimpleMarkdown, hasMarkdown, stripMarkdown, formatPlainText */
/**
 * 简单的Markdown渲染器 - 专为微信小程序设计
 * 支持基本的Markdown语法：
 * 1. 标题 (#, ##, ###)
 * 2. 粗体 (**text**)
 * 3. 斜体 (*text*)
 * 4. 列表 (- item)
 * 5. 链接 ([text](url))
 * 6. 代码块 (```code```)
 * 7. 行内代码 (`code`)
 * 8. 引用 (> text)
 * 9. 分割线 (---)
 */

/**
 * 解析Markdown文本为微信小程序可渲染的节点数组
 */
var parseMarkdown = function parseMarkdown(text) {
  if (!text) return [];
  var lines = text.split('\n');
  var nodes = [];
  var inCodeBlock = false;
  var codeBlockContent = '';
  var codeBlockLanguage = '';
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];

    // 处理代码块
    if (line.trim().startsWith('```')) {
      if (!inCodeBlock) {
        // 开始代码块
        inCodeBlock = true;
        codeBlockContent = '';
        codeBlockLanguage = line.trim().replace(/```/g, '').trim();
      } else {
        // 结束代码块
        inCodeBlock = false;
        nodes.push({
          type: 'code',
          language: codeBlockLanguage,
          content: codeBlockContent
        });
        continue;
      }
    } else if (inCodeBlock) {
      // 代码块内容
      codeBlockContent += line + '\n';
      continue;
    }

    // 处理空行
    if (line.trim() === '') {
      nodes.push({
        type: 'br'
      });
      continue;
    }

    // 处理标题
    var headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      var level = headingMatch[1].length;
      var content = headingMatch[2];
      nodes.push({
        type: 'heading',
        level: level,
        content: _parseInlineMarkdown(content)
      });
      continue;
    }

    // 处理引用
    if (line.trim().startsWith('> ')) {
      var _content = line.trim().substring(2);
      nodes.push({
        type: 'blockquote',
        content: _parseInlineMarkdown(_content)
      });
      continue;
    }

    // 处理分割线
    if (line.trim().match(/^[-*_]{3,}$/)) {
      nodes.push({
        type: 'hr'
      });
      continue;
    }

    // 处理无序列表
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      var _content2 = line.trim().substring(2);
      nodes.push({
        type: 'list-item',
        content: _parseInlineMarkdown(_content2)
      });
      continue;
    }

    // 处理有序列表
    var orderedListMatch = line.match(/^(\d+)\.\s+(.+)$/);
    if (orderedListMatch) {
      var number = orderedListMatch[1];
      var _content3 = orderedListMatch[2];
      nodes.push({
        type: 'ordered-list-item',
        number: number,
        content: _parseInlineMarkdown(_content3)
      });
      continue;
    }

    // 处理普通段落
    nodes.push({
      type: 'paragraph',
      content: _parseInlineMarkdown(line)
    });
  }

  // 如果代码块没有正确结束，添加最后一个代码块
  if (inCodeBlock) {
    nodes.push({
      type: 'code',
      language: codeBlockLanguage,
      content: codeBlockContent
    });
  }
  return nodes;
};

/**
 * 解析行内Markdown语法
 */
var _parseInlineMarkdown = function parseInlineMarkdown(text) {
  var nodes = [];
  var currentText = '';
  var i = 0;
  while (i < text.length) {
    // 处理粗体 (**text**)
    if (text.substr(i, 2) === '**') {
      if (currentText) {
        nodes.push({
          type: 'text',
          content: currentText
        });
        currentText = '';
      }
      var endIndex = text.indexOf('**', i + 2);
      if (endIndex !== -1) {
        var boldText = text.substring(i + 2, endIndex);
        nodes.push({
          type: 'bold',
          content: _parseInlineMarkdown(boldText)
        });
        i = endIndex + 2;
      } else {
        currentText += '**';
        i += 2;
      }
      continue;
    }

    // 处理斜体 (*text*)
    if (text[i] === '*' && (i === 0 || text[i - 1] !== '*')) {
      if (currentText) {
        nodes.push({
          type: 'text',
          content: currentText
        });
        currentText = '';
      }
      var _endIndex = text.indexOf('*', i + 1);
      if (_endIndex !== -1) {
        var italicText = text.substring(i + 1, _endIndex);
        nodes.push({
          type: 'italic',
          content: _parseInlineMarkdown(italicText)
        });
        i = _endIndex + 1;
      } else {
        currentText += '*';
        i += 1;
      }
      continue;
    }

    // 处理行内代码 (`code`)
    if (text[i] === '`') {
      if (currentText) {
        nodes.push({
          type: 'text',
          content: currentText
        });
        currentText = '';
      }
      var _endIndex2 = text.indexOf('`', i + 1);
      if (_endIndex2 !== -1) {
        var codeText = text.substring(i + 1, _endIndex2);
        nodes.push({
          type: 'inline-code',
          content: codeText
        });
        i = _endIndex2 + 1;
      } else {
        currentText += '`';
        i += 1;
      }
      continue;
    }

    // 处理链接 ([text](url))
    if (text[i] === '[') {
      if (currentText) {
        nodes.push({
          type: 'text',
          content: currentText
        });
        currentText = '';
      }
      var linkEndIndex = text.indexOf(']', i);
      if (linkEndIndex !== -1) {
        var urlStartIndex = text.indexOf('(', linkEndIndex);
        if (urlStartIndex !== -1 && urlStartIndex === linkEndIndex + 1) {
          var urlEndIndex = text.indexOf(')', urlStartIndex);
          if (urlEndIndex !== -1) {
            var linkText = text.substring(i + 1, linkEndIndex);
            var linkUrl = text.substring(urlStartIndex + 1, urlEndIndex);
            nodes.push({
              type: 'link',
              text: linkText,
              url: linkUrl
            });
            i = urlEndIndex + 1;
            continue;
          }
        }
      }
    }
    currentText += text[i];
    i++;
  }
  if (currentText) {
    nodes.push({
      type: 'text',
      content: currentText
    });
  }
  return nodes;
};

/**
 * 渲染Markdown节点为微信小程序组件
 */
var renderMarkdown = function renderMarkdown(nodes) {
  return nodes.map(function (node, index) {
    switch (node.type) {
      case 'heading':
        return {
          type: 'view',
          className: "markdown-heading markdown-h".concat(node.level),
          children: _renderInlineMarkdown(node.content)
        };
      case 'paragraph':
        return {
          type: 'view',
          className: 'markdown-paragraph',
          children: _renderInlineMarkdown(node.content)
        };
      case 'bold':
        return {
          type: 'text',
          className: 'markdown-bold',
          children: _renderInlineMarkdown(node.content)
        };
      case 'italic':
        return {
          type: 'text',
          className: 'markdown-italic',
          children: _renderInlineMarkdown(node.content)
        };
      case 'inline-code':
        return {
          type: 'text',
          className: 'markdown-inline-code',
          children: [{
            type: 'text',
            content: node.content
          }]
        };
      case 'code':
        return {
          type: 'view',
          className: 'markdown-code-block',
          children: [{
            type: 'text',
            className: 'markdown-code-language',
            children: [{
              type: 'text',
              content: node.language || 'code'
            }]
          }, {
            type: 'text',
            className: 'markdown-code-content',
            children: [{
              type: 'text',
              content: node.content
            }]
          }]
        };
      case 'link':
        return {
          type: 'text',
          className: 'markdown-link',
          children: [{
            type: 'text',
            content: node.text
          }],
          url: node.url
        };
      case 'list-item':
        return {
          type: 'view',
          className: 'markdown-list-item',
          children: [{
            type: 'text',
            className: 'markdown-list-bullet',
            children: [{
              type: 'text',
              content: '• '
            }]
          }, {
            type: 'text',
            className: 'markdown-list-content',
            children: _renderInlineMarkdown(node.content)
          }]
        };
      case 'ordered-list-item':
        return {
          type: 'view',
          className: 'markdown-ordered-list-item',
          children: [{
            type: 'text',
            className: 'markdown-ordered-list-number',
            children: [{
              type: 'text',
              content: "".concat(node.number, ". ")
            }]
          }, {
            type: 'text',
            className: 'markdown-ordered-list-content',
            children: _renderInlineMarkdown(node.content)
          }]
        };
      case 'blockquote':
        return {
          type: 'view',
          className: 'markdown-blockquote',
          children: _renderInlineMarkdown(node.content)
        };
      case 'hr':
        return {
          type: 'view',
          className: 'markdown-hr'
        };
      case 'br':
        return {
          type: 'view',
          className: 'markdown-br'
        };
      case 'text':
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{
            type: 'text',
            content: node.content
          }]
        };
      default:
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{
            type: 'text',
            content: JSON.stringify(node)
          }]
        };
    }
  });
};

/**
 * 渲染行内Markdown节点
 */
var _renderInlineMarkdown = function renderInlineMarkdown(nodes) {
  return nodes.map(function (node, index) {
    switch (node.type) {
      case 'text':
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{
            type: 'text',
            content: node.content
          }]
        };
      case 'bold':
        return {
          type: 'text',
          className: 'markdown-bold',
          children: _renderInlineMarkdown(node.content)
        };
      case 'italic':
        return {
          type: 'text',
          className: 'markdown-italic',
          children: _renderInlineMarkdown(node.content)
        };
      case 'inline-code':
        return {
          type: 'text',
          className: 'markdown-inline-code',
          children: [{
            type: 'text',
            content: node.content
          }]
        };
      case 'link':
        return {
          type: 'text',
          className: 'markdown-link',
          children: [{
            type: 'text',
            content: node.text
          }],
          url: node.url
        };
      default:
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{
            type: 'text',
            content: JSON.stringify(node)
          }]
        };
    }
  });
};

/**
 * 简化的Markdown渲染函数 - 直接返回文本，但添加CSS类名
 */
var renderSimpleMarkdown = function renderSimpleMarkdown(text) {
  if (!text) return '';

  // 替换基本的Markdown语法为HTML标签
  var html = text;

  // 处理标题
  html = html.replace(/^### (.+)$/gm, '<h3 class="markdown-h3">$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2 class="markdown-h2">$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1 class="markdown-h1">$1</h1>');

  // 处理粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="markdown-bold">$1</strong>');

  // 处理斜体
  html = html.replace(/\*(.+?)\*/g, '<em class="markdown-italic">$1</em>');

  // 处理行内代码
  html = html.replace(/`(.+?)`/g, '<code class="markdown-inline-code">$1</code>');

  // 处理代码块（简化版）
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="markdown-code-block"><code class="markdown-code-content">$1</code></pre>');

  // 处理无序列表
  html = html.replace(/^- (.+)$/gm, '<li class="markdown-list-item">$1</li>');
  html = html.replace(/^\* (.+)$/gm, '<li class="markdown-list-item">$1</li>');

  // 处理有序列表
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="markdown-ordered-list-item">$2</li>');

  // 处理引用
  html = html.replace(/^> (.+)$/gm, '<blockquote class="markdown-blockquote">$1</blockquote>');

  // 处理链接
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="markdown-link">$1</a>');

  // 处理换行
  html = html.replace(/\n/g, '<br class="markdown-br" />');
  return html;
};

/**
 * 检查文本是否包含Markdown语法
 */
var hasMarkdown = function hasMarkdown(text) {
  if (!text) return false;
  var markdownPatterns = [/^#{1,6}\s+.+$/m,
  // 标题
  /\*\*.+?\*\*/,
  // 粗体
  /\*.+?\*/,
  // 斜体
  /`[^`]+`/,
  // 行内代码
  /```[\s\S]*?```/,
  // 代码块
  /^-\s+.+$/m,
  // 无序列表
  /^\*\s+.+$/m,
  // 无序列表（星号）
  /^\d+\.\s+.+$/m,
  // 有序列表
  /^>\s+.+$/m,
  // 引用
  /\[.+\]\(.+\)/,
  // 链接
  /^[-*_]{3,}$/m // 分割线
  ];
  return markdownPatterns.some(function (pattern) {
    return pattern.test(text);
  });
};

/**
 * 去除Markdown格式，返回纯文本但保留基本结构
 * 移除Markdown标记，但保留换行和列表结构
 */
var stripMarkdown = function stripMarkdown(text) {
  if (!text) return '';
  var result = text;

  // 1. 处理代码块（保留内容，移除标记）
  result = result.replace(/```[\s\S]*?```/g, function (match) {
    // 移除开头的```和可能的语言标识，以及结尾的```
    var content = match.replace(/^```[a-zA-Z]*\n?/, '').replace(/\n?```$/, '');
    return "\u3010\u4EE3\u7801\u3011".concat(content, "\u3010/\u4EE3\u7801\u3011");
  });

  // 2. 处理行内代码（保留内容，移除标记）
  result = result.replace(/`([^`]+)`/g, '$1');

  // 3. 处理粗体和斜体（移除标记）
  result = result.replace(/\*\*(.+?)\*\*/g, '$1'); // 粗体
  result = result.replace(/\*(.+?)\*/g, '$1'); // 斜体

  // 4. 处理标题（移除#标记，但保留文本并添加换行）
  result = result.replace(/^#{1,6}\s+(.+)$/gm, '$1\n');

  // 5. 处理链接（保留文本，移除URL）
  result = result.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // 6. 处理引用（移除>标记，但保留文本）
  result = result.replace(/^>\s+(.+)$/gm, '$1');

  // 7. 处理无序列表（将-或*替换为•）
  // 注意：需要处理缩进，所以使用更复杂的正则
  result = result.replace(/^(\s*)[-\*]\s+(.+)$/gm, function (match, spaces, content) {
    return "".concat(spaces, "\u2022 ").concat(content);
  });

  // 8. 处理有序列表（保留数字和文本）
  // 注意：需要处理缩进
  result = result.replace(/^(\s*)(\d+)\.\s+(.+)$/gm, function (match, spaces, number, content) {
    return "".concat(spaces).concat(number, ". ").concat(content);
  });

  // 9. 处理分割线（替换为一行分隔符）
  result = result.replace(/^[-*_]{3,}$/gm, '---');
  return result;
};

/**
 * 格式化纯文本，添加段落分隔和列表缩进
 * 将连续的文本按自然段落分割，并添加适当的格式
 */
var formatPlainText = function formatPlainText(text) {
  if (!text) return '';

  // 先去除Markdown格式
  var result = stripMarkdown(text);

  // 按换行分割，处理空行和段落
  var lines = result.split('\n');
  var formattedLines = [];
  var inParagraph = false;
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line) {
      // 空行，结束当前段落
      if (inParagraph) {
        formattedLines.push('</p><p>');
        inParagraph = false;
      }
      continue;
    }

    // 检查是否是列表项
    var isListItem = line.startsWith('• ') || /^\d+\.\s/.test(line);
    if (isListItem) {
      // 列表项，结束前一个段落（如果有）
      if (inParagraph) {
        formattedLines.push('</p>');
        inParagraph = false;
      }
      // 添加列表项
      formattedLines.push("<li>".concat(line, "</li>"));
    } else {
      // 普通文本行
      if (!inParagraph) {
        formattedLines.push('<p>');
        inParagraph = true;
      }
      formattedLines.push(line);
    }
  }

  // 结束最后一个段落
  if (inParagraph) {
    formattedLines.push('</p>');
  }

  // 合并结果
  var formattedText = formattedLines.join(' ');

  // 清理多余的标签
  formattedText = formattedText.replace(/<\/p><p>/g, '</p>\n<p>');
  formattedText = formattedText.replace(/<li>/g, '\n<li>');
  formattedText = formattedText.replace(/<\/li>/g, '</li>\n');

  // 确保代码块有适当的换行
  formattedText = formattedText.replace(/【代码】/g, '\n<pre><code>');
  formattedText = formattedText.replace(/【\/代码】/g, '</code></pre>\n');
  return formattedText.trim();
};

/**
 * 简化的Markdown渲染函数 - 使用纯文本格式化替代HTML标签
 * 返回适合微信小程序Text组件渲染的文本
 */
var renderFormattedText = function renderFormattedText(text) {
  if (!text) return '';

  // 先去除Markdown格式
  var result = stripMarkdown(text);

  // 按换行分割，处理段落和列表
  var lines = result.split('\n');
  var formattedLines = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (!line) {
      // 空行，添加段落分隔
      formattedLines.push('\n\n');
      continue;
    }

    // 检查是否是列表项
    var isListItem = line.startsWith('• ') || /^\d+\.\s/.test(line);
    if (isListItem) {
      // 列表项，添加缩进
      formattedLines.push("  ".concat(line));
    } else if (line === '---') {
      // 分割线
      formattedLines.push('────────────');
    } else {
      // 普通文本行
      formattedLines.push(line);
    }
  }

  // 合并结果，确保适当的间距
  var formattedText = formattedLines.join('\n');

  // 清理多余的换行
  formattedText = formattedText.replace(/\n{3,}/g, '\n\n');
  return formattedText.trim();
};

/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/index/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map