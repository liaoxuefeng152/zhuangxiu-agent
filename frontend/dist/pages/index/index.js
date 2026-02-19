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
        var _data, _res$data, _d$count, token, userId, res, d, count, _t;
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
              _context.n = 2;
              return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().request({
                url: "".concat(_config_env__WEBPACK_IMPORTED_MODULE_9__.env.apiBaseUrl, "/messages/unread-count"),
                method: 'GET',
                header: {
                  Authorization: "Bearer ".concat(token),
                  'X-User-Id': userId != null && userId !== '' ? String(userId) : '',
                  'Content-Type': 'application/json'
                }
              });
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
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_14__.jsx)(_components_FloatingDesignerAvatar__WEBPACK_IMPORTED_MODULE_13__["default"], {
      showDragHint: true,
      initialPosition: {
        x: 20,
        y: 200
      }
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
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__);










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
    } : _ref$initialPosition;
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
  var _useState13 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(''),
    _useState14 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState13, 2),
    chatSessionId = _useState14[0],
    setChatSessionId = _useState14[1];
  var _useState15 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)([]),
    _useState16 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState15, 2),
    messages = _useState16[0],
    setMessages = _useState16[1];
  var _useState17 = (0,react__WEBPACK_IMPORTED_MODULE_4__.useState)(false),
    _useState18 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_3__["default"])(_useState17, 2),
    isCreatingSession = _useState18[0],
    setIsCreatingSession = _useState18[1];
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
  }, []);

  // 处理触摸开始
  var handleTouchStart = function handleTouchStart(e) {
    var touch = e.touches[0];
    startPosRef.current = {
      x: touch.clientX - position.x,
      y: touch.clientY - position.y
    };
    setDragging(true);
    setShowHint(false); // 开始拖拽时隐藏提示
  };

  // 处理触摸移动
  var handleTouchMove = function handleTouchMove(e) {
    if (!dragging) return;
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

            setShowDialog(true);
            setShowHint(false); // 点击时隐藏提示

            // 如果没有session，创建一个新的
            if (chatSessionId) {
              _context.n = 2;
              break;
            }
            _context.n = 2;
            return createNewChatSession();
          case 2:
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
      var response, welcomeMessage, _welcomeMessage, _t;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            _context2.p = 0;
            setIsCreatingSession(true);
            _context2.n = 1;
            return _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.createChatSession();
          case 1:
            response = _context2.v;
            setChatSessionId(response.session_id);
            setMessages(response.messages || []);

            // 如果没有初始消息，添加欢迎消息
            if (!response.messages || response.messages.length === 0) {
              welcomeMessage = {
                role: 'assistant',
                content: '您好！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
                timestamp: Date.now() / 1000
              };
              setMessages([welcomeMessage]);
            }
            _context2.n = 3;
            break;
          case 2:
            _context2.p = 2;
            _t = _context2.v;
            console.error('创建聊天session失败:', _t);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: _t.message || '创建对话失败，请稍后重试',
              icon: 'none'
            });

            // 如果创建失败，显示默认欢迎消息
            _welcomeMessage = {
              role: 'assistant',
              content: '您好！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
              timestamp: Date.now() / 1000
            };
            setMessages([_welcomeMessage]);
          case 3:
            _context2.p = 3;
            setIsCreatingSession(false);
            return _context2.f(3);
          case 4:
            return _context2.a(2);
        }
      }, _callee2, null, [[0, 2, 3, 4]]);
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
      var userMessage, userMsg, response, aiMsg, errorMsg, _t2;
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
            _context3.p = 2;
            _context3.n = 3;
            return _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.sendChatMessage(chatSessionId, userMessage);
          case 3:
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
                scrollViewRef.current.scrollToBottom();
              }
            }, 100);
            _context3.n = 5;
            break;
          case 4:
            _context3.p = 4;
            _t2 = _context3.v;
            console.error('发送消息失败:', _t2);
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
          case 5:
            _context3.p = 5;
            setLoading(false);
            return _context3.f(5);
          case 6:
            return _context3.a(2);
        }
      }, _callee3, null, [[2, 4, 5, 6]]);
    }));
    return function handleSendMessage() {
      return _ref4.apply(this, arguments);
    };
  }();

  // 快速问题示例
  var quickQuestions = ['现代简约风格的特点是什么？', '小户型如何设计显得空间更大？', '装修预算怎么分配比较合理？', '选择地板还是瓷砖比较好？', '厨房装修要注意哪些细节？'];
  var handleQuickQuestion = function handleQuickQuestion(question) {
    setInputMessage(question);
  };

  // 清空对话
  var handleClearChat = /*#__PURE__*/function () {
    var _ref5 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_2__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee4() {
      var welcomeMessage, _t3;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context4) {
        while (1) switch (_context4.p = _context4.n) {
          case 0:
            if (chatSessionId) {
              _context4.n = 1;
              break;
            }
            return _context4.a(2);
          case 1:
            _context4.p = 1;
            _context4.n = 2;
            return _services_api__WEBPACK_IMPORTED_MODULE_7__.designerApi.clearChatHistory(chatSessionId);
          case 2:
            // 重置消息，只保留欢迎消息
            welcomeMessage = {
              role: 'assistant',
              content: '对话已清空！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
              timestamp: Date.now() / 1000
            };
            setMessages([welcomeMessage]);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: '对话已清空',
              icon: 'success'
            });
            _context4.n = 4;
            break;
          case 3:
            _context4.p = 3;
            _t3 = _context4.v;
            console.error('清空对话失败:', _t3);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_6___default().showToast({
              title: _t3.message || '清空失败',
              icon: 'none'
            });
          case 4:
            return _context4.a(2);
        }
      }, _callee4, null, [[1, 3]]);
    }));
    return function handleClearChat() {
      return _ref5.apply(this, arguments);
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
          scrollViewRef.current.scrollToBottom();
        }
      }, 100);
    }
  }, [messages]);

  // 格式化时间
  var formatTime = function formatTime(timestamp) {
    var date = new Date(timestamp * 1000);
    return "".concat(date.getHours().toString().padStart(2, '0'), ":").concat(date.getMinutes().toString().padStart(2, '0'));
  };
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.Fragment, {
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
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
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "avatar-container",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Image, {
          className: "avatar-image",
          src: "https://img.alicdn.com/imgextra/i4/O1CN01Z5p5Lz1d0q7Q9X8Yj_!!6000000003675-2-tps-200-200.png",
          mode: "aspectFill"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "avatar-badge",
          children: "AI"
        })]
      }), showHint && isFirstTime && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "drag-hint",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
          className: "hint-text",
          children: "\u62D6\u62FD\u79FB\u52A8\u4F4D\u7F6E"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "hint-arrow",
          children: "\u2193"
        })]
      })]
    }), showDialog && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
      className: "designer-dialog-mask",
      onClick: handleCloseDialog,
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
        className: "designer-dialog",
        onClick: function onClick(e) {
          return e.stopPropagation();
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-header",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "dialog-title",
            children: "AI\u8BBE\u8BA1\u5E08\u804A\u5929"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "dialog-actions",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Button, {
              className: "clear-btn",
              onClick: handleClearChat,
              disabled: messages.length <= 1,
              children: "\u6E05\u7A7A"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "dialog-close",
              onClick: handleCloseDialog,
              children: "\xD7"
            })]
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-content",
          children: isCreatingSession ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
            className: "loading-container",
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
              children: "\u6B63\u5728\u521D\u59CB\u5316\u5BF9\u8BDD..."
            })
          }) : /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.Fragment, {
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.ScrollView, {
              className: "chat-messages",
              scrollY: true,
              ref: scrollViewRef,
              scrollWithAnimation: true,
              children: [messages.map(function (msg, index) {
                return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                  className: "message-item ".concat(msg.role === 'user' ? 'user-message' : 'ai-message'),
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "message-content",
                    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "message-text",
                      children: msg.content
                    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "message-time",
                      children: formatTime(msg.timestamp)
                    })]
                  })
                }, index);
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                ref: messagesEndRef
              })]
            }), messages.length <= 2 && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "quick-questions",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                className: "quick-title",
                children: "\u5FEB\u901F\u63D0\u95EE\uFF1A"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                className: "quick-questions-grid",
                children: quickQuestions.map(function (q, index) {
                  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
                    className: "quick-question-item",
                    onClick: function onClick() {
                      return handleQuickQuestion(q);
                    },
                    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
                      className: "quick-question-text",
                      children: q
                    })
                  }, index);
                })
              })]
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
              className: "input-area",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Input, {
                className: "message-input",
                placeholder: "\u8F93\u5165\u60A8\u7684\u95EE\u9898...",
                value: inputMessage,
                onInput: function onInput(e) {
                  return setInputMessage(e.detail.value);
                },
                focus: !inputMessage,
                confirmType: "send",
                onConfirm: handleSendMessage
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Button, {
                className: "send-btn",
                onClick: handleSendMessage,
                disabled: loading || !inputMessage.trim(),
                children: loading ? '思考中...' : '发送'
              })]
            })]
          })
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.View, {
          className: "dialog-footer",
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_8__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_5__.Text, {
            className: "footer-text",
            children: "AI\u8BBE\u8BA1\u5E08\u53EF\u89E3\u7B54\u88C5\u4FEE\u98CE\u683C\u3001\u5E03\u5C40\u3001\u6750\u6599\u3001\u9884\u7B97\u7B49\u95EE\u9898"
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


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/index/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map