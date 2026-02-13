"use strict";
(wx["webpackJsonp"] = wx["webpackJsonp"] || []).push([["pages/construction/index"],{

/***/ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/construction/index!./src/pages/construction/index.tsx":
/*!******************************************************************************************************************************!*\
  !*** ./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/construction/index!./src/pages/construction/index.tsx ***!
  \******************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_defineProperty_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/defineProperty.js */ "./node_modules/@babel/runtime/helpers/esm/defineProperty.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/regenerator.js */ "./node_modules/@babel/runtime/helpers/esm/regenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread2.js */ "./node_modules/@babel/runtime/helpers/esm/objectSpread2.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/slicedToArray.js */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @tarojs/taro */ "webpack/container/remote/@tarojs/taro");
/* harmony import */ var _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_tarojs_taro__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! dayjs */ "webpack/container/remote/dayjs");
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(dayjs__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _utils_navigation__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../utils/navigation */ "./src/utils/navigation.ts");
/* harmony import */ var _components_AcceptanceGuideModal__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../../components/AcceptanceGuideModal */ "./src/components/AcceptanceGuideModal/index.tsx");
/* harmony import */ var _services_api__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ../../services/api */ "./src/services/api.ts");
/* harmony import */ var _utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../../utils/constructionStage */ "./src/utils/constructionStage.ts");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__);















var STAGES = [{
  key: 'material',
  name: '材料进场核对',
  days: 3,
  label: 'S00',
  icon: '📦'
}, {
  key: 'plumbing',
  name: '隐蔽工程',
  days: 7,
  label: 'S01',
  icon: '🔌'
}, {
  key: 'carpentry',
  name: '泥瓦工',
  days: 10,
  label: 'S02',
  icon: '🧱'
}, {
  key: 'woodwork',
  name: '木工',
  days: 7,
  label: 'S03',
  icon: '🪚'
}, {
  key: 'painting',
  name: '油漆',
  days: 7,
  label: 'S04',
  icon: '🖌️'
}, {
  key: 'installation',
  name: '安装收尾',
  days: 5,
  label: 'S05',
  icon: '🔧'
}];
var TOTAL_DAYS = STAGES.reduce(function (s, x) {
  return s + x.days;
}, 0);
var STORAGE_KEY_DATE = 'construction_start_date';
var STORAGE_KEY_CALIBRATE = 'construction_stage_calibrate';
var REMIND_DAYS_OPTIONS = [1, 2, 3, 5, 7];
var DEVIATION_REASONS = ['材料未到', '施工拖延', '个人原因', '其他'];

/** scene 传 P15：施工验收 / 复检（S00 人工核对走 P37） */
var SCENE_ACCEPT = 'accept';
var SCENE_RECHECK = 'recheck';
var buildDefaultStageStatus = function buildDefaultStageStatus() {
  var defaults = {};
  STAGES.forEach(function (stage) {
    defaults[stage.key] = 'pending';
  });
  return defaults;
};
var getBackendStatusPayloadFromLocal = function getBackendStatusPayloadFromLocal(stageKey, status) {
  if (status === 'rectify') return 'need_rectify';
  if (status === 'completed') return (0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.getCompletionPayload)(stageKey);
  return null;
};

/**
 * P09 施工陪伴页 - 6大阶段 + 智能提醒，流程互锁，按原型布局
 */
var Construction = function Construction() {
  var _STAGES$find;
  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(''),
    _useState2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState, 2),
    startDate = _useState2[0],
    setStartDate = _useState2[1];
  var _useState3 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(buildDefaultStageStatus()),
    _useState4 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState3, 2),
    stageStatus = _useState4[0],
    setStageStatus = _useState4[1];
  var _useState5 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(null),
    _useState6 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState5, 2),
    guideStage = _useState6[0],
    setGuideStage = _useState6[1];
  var _useState7 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(true),
    _useState8 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState7, 2),
    loading = _useState8[0],
    setLoading = _useState8[1];
  var _useState9 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState0 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState9, 2),
    useApi = _useState0[0],
    setUseApi = _useState0[1];
  var _useState1 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(null),
    _useState10 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState1, 2),
    scrollToStageId = _useState10[0],
    setScrollToStageId = _useState10[1];
  var _useState11 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(null),
    _useState12 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState11, 2),
    highlightStageIndex = _useState12[0],
    setHighlightStageIndex = _useState12[1];
  var _useState13 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(null),
    _useState14 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState13, 2),
    expandedCard = _useState14[0],
    setExpandedCard = _useState14[1];
  var _useState15 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(false),
    _useState16 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState15, 2),
    remindModalVisible = _useState16[0],
    setRemindModalVisible = _useState16[1];
  var _useState17 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(3),
    _useState18 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState17, 2),
    remindDays = _useState18[0],
    setRemindDays = _useState18[1];
  var _useState19 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(true),
    _useState20 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState19, 2),
    remindOpen = _useState20[0],
    setRemindOpen = _useState20[1];
  var _useState21 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(''),
    _useState22 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState21, 2),
    deviationReason = _useState22[0],
    setDeviationReason = _useState22[1];
  var _useState23 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)({}),
    _useState24 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState23, 2),
    manualEndDates = _useState24[0],
    setManualEndDates = _useState24[1];
  var _useState25 = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(new Set()),
    _useState26 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_slicedToArray_js__WEBPACK_IMPORTED_MODULE_4__["default"])(_useState25, 2),
    pendingSyncStages = _useState26[0],
    setPendingSyncStages = _useState26[1];
  var hasToken = !!_tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('access_token');
  var loadFromApi = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_3__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee() {
    var _res$data, _data$stages, res, data, formatted, stages, status, calibrate, _e$response, _e$message, _e$response2, _e$message2, is404, is401, saved, statusSaved, calibrateSaved, parsed, _t;
    return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context) {
      while (1) switch (_context.p = _context.n) {
        case 0:
          if (hasToken) {
            _context.n = 1;
            break;
          }
          return _context.a(2);
        case 1:
          _context.p = 1;
          _context.n = 2;
          return (0,_services_api__WEBPACK_IMPORTED_MODULE_11__.getWithAuth)('/constructions/schedule');
        case 2:
          res = _context.v;
          data = (_res$data = res === null || res === void 0 ? void 0 : res.data) !== null && _res$data !== void 0 ? _res$data : res;
          if (data !== null && data !== void 0 && data.start_date) {
            formatted = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(data.start_date).format('YYYY-MM-DD');
            setStartDate(formatted);
            saveLocal(formatted, status);
          } else {
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync(_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.STAGE_STATUS_STORAGE_KEY, JSON.stringify(status));
          }
          stages = (_data$stages = data === null || data === void 0 ? void 0 : data.stages) !== null && _data$stages !== void 0 ? _data$stages : {};
          status = buildDefaultStageStatus();
          calibrate = {};
          STAGES.forEach(function (s) {
            var _stages$s$key, _stages$s$key2;
            status[s.key] = (0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.mapBackendStageStatus)((_stages$s$key = stages[s.key]) === null || _stages$s$key === void 0 ? void 0 : _stages$s$key.status, s.key);
            if ((_stages$s$key2 = stages[s.key]) !== null && _stages$s$key2 !== void 0 && _stages$s$key2.end_date) calibrate[s.key] = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(stages[s.key].end_date).format('YYYY-MM-DD');
          });
          setStageStatus(status);
          setPendingSyncStages(new Set());
          if (Object.keys(calibrate).length > 0) setManualEndDates(function (prev) {
            return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])({}, prev), calibrate);
          });
          setUseApi(true);
          _context.n = 4;
          break;
        case 3:
          _context.p = 3;
          _t = _context.v;
          // V2.6.2优化：静默处理401/404错误（未登录或未设置进度计划）
          is404 = (_t === null || _t === void 0 || (_e$response = _t.response) === null || _e$response === void 0 ? void 0 : _e$response.status) === 404 || (_t === null || _t === void 0 || (_e$message = _t.message) === null || _e$message === void 0 ? void 0 : _e$message.includes('404'));
          is401 = (_t === null || _t === void 0 || (_e$response2 = _t.response) === null || _e$response2 === void 0 ? void 0 : _e$response2.status) === 401 || (_t === null || _t === void 0 || (_e$message2 = _t.message) === null || _e$message2 === void 0 ? void 0 : _e$message2.includes('请稍后重试')) || (_t === null || _t === void 0 ? void 0 : _t.isSilent);
          if (is404 || is401) {
            // 静默处理，不显示错误提示
            saved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(STORAGE_KEY_DATE);
            statusSaved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.STAGE_STATUS_STORAGE_KEY);
            calibrateSaved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(STORAGE_KEY_CALIBRATE);
            if (saved) setStartDate(saved);
            if (statusSaved) {
              try {
                parsed = typeof statusSaved === 'string' ? JSON.parse(statusSaved) : statusSaved;
                setStageStatus((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])({}, buildDefaultStageStatus()), parsed));
              } catch (_) {
                setStageStatus(buildDefaultStageStatus());
              }
            } else {
              setStageStatus(buildDefaultStageStatus());
            }
            if (calibrateSaved) {
              try {
                setManualEndDates(typeof calibrateSaved === 'string' ? JSON.parse(calibrateSaved) : calibrateSaved);
              } catch (_) {}
            }
          }
          setUseApi(false);
        case 4:
          _context.p = 4;
          setLoading(false);
          return _context.f(4);
        case 5:
          return _context.a(2);
      }
    }, _callee, null, [[1, 3, 4, 5]]);
  })), [hasToken]);
  var loadFromLocal = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(function () {
    var saved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(STORAGE_KEY_DATE);
    var statusSaved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.STAGE_STATUS_STORAGE_KEY);
    var calibrateSaved = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync(STORAGE_KEY_CALIBRATE);
    if (saved) setStartDate(saved);
    if (statusSaved) {
      try {
        var parsed = typeof statusSaved === 'string' ? JSON.parse(statusSaved) : statusSaved;
        setStageStatus((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])({}, buildDefaultStageStatus()), parsed));
      } catch (_) {
        setStageStatus(buildDefaultStageStatus());
      }
    } else {
      setStageStatus(buildDefaultStageStatus());
    }
    if (calibrateSaved) {
      try {
        setManualEndDates(typeof calibrateSaved === 'string' ? JSON.parse(calibrateSaved) : calibrateSaved);
      } catch (_) {}
    }
    var rd = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('remind_days');
    if (typeof rd === 'number' && REMIND_DAYS_OPTIONS.includes(rd)) setRemindDays(rd);
    var ro = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('smart_remind');
    if (typeof ro === 'boolean') setRemindOpen(ro);
    setUseApi(false);
    setLoading(false);
  }, []);
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    if (hasToken) loadFromApi();else loadFromLocal();
  }, [hasToken, loadFromApi, loadFromLocal]);

  // 从材料核对/验收等子页返回时重新拉取，保证状态与「我的数据」一致
  (0,_tarojs_taro__WEBPACK_IMPORTED_MODULE_7__.useDidShow)(function () {
    if (hasToken) loadFromApi();else loadFromLocal();
  });
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    var idx = _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().getStorageSync('construction_scroll_stage');
    if (typeof idx === 'number' && idx >= 0 && idx < STAGES.length) {
      setScrollToStageId("stage-".concat(idx));
      setHighlightStageIndex(idx);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().removeStorageSync('construction_scroll_stage');
      var t = setTimeout(function () {
        return setHighlightStageIndex(null);
      }, 3500);
      return function () {
        return clearTimeout(t);
      };
    }
  }, [startDate]);
  (0,react__WEBPACK_IMPORTED_MODULE_5__.useEffect)(function () {
    if (!useApi || !hasToken || pendingSyncStages.size === 0) return;
    pendingSyncStages.forEach(function (stageKey) {
      var payload = getBackendStatusPayloadFromLocal(stageKey, stageStatus[stageKey]);
      if (!payload) {
        clearStagePending(stageKey);
        return;
      }
      (0,_services_api__WEBPACK_IMPORTED_MODULE_11__.putWithAuth)('/constructions/stage-status', {
        stage: (0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.getBackendStageCode)(stageKey),
        status: payload
      }).then(function () {
        (0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.persistStageStatusToStorage)(stageKey, payload);
        clearStagePending(stageKey);
      }).catch(function () {
        // 保持待同步状态，稍后继续重试
      });
    });
  }, [useApi, hasToken, pendingSyncStages, stageStatus, clearStagePending]);
  var saveLocal = function saveLocal(date, status) {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync(STORAGE_KEY_DATE, date);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync(_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.STAGE_STATUS_STORAGE_KEY, JSON.stringify(status));
  };
  var markStagePending = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(function (stageKey) {
    setPendingSyncStages(function (prev) {
      var next = new Set(prev);
      next.add(stageKey);
      return next;
    });
  }, []);
  var clearStagePending = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(function (stageKey) {
    setPendingSyncStages(function (prev) {
      if (!prev.has(stageKey)) return prev;
      var next = new Set(prev);
      next.delete(stageKey);
      return next;
    });
  }, []);
  var _useMemo = (0,react__WEBPACK_IMPORTED_MODULE_5__.useMemo)(function () {
      if (!startDate) return {
        schedule: [],
        endDate: '',
        progress: 0,
        completedCount: 0,
        daysBehind: 0,
        behindStageKey: ''
      };
      var start = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(startDate);
      var cursor = start;
      var schedule = [];
      var daysBehind = 0;
      var behindStageKey = '';
      for (var _i = 0, _STAGES = STAGES; _i < _STAGES.length; _i++) {
        var s = _STAGES[_i];
        var st = stageStatus[s.key] || 'pending';
        var startStr = cursor.format('YYYY-MM-DD');
        var manualEnd = manualEndDates[s.key];
        var _endDate = manualEnd ? dayjs__WEBPACK_IMPORTED_MODULE_8___default()(manualEnd) : cursor.add(s.days, 'day');
        var endStr = _endDate.format('YYYY-MM-DD');
        var remaining = void 0;
        if (st === 'in_progress' || st === 'pending') {
          var today = dayjs__WEBPACK_IMPORTED_MODULE_8___default()();
          if (today.isAfter(_endDate)) {
            var behind = today.diff(_endDate, 'day');
            if (behind > daysBehind) {
              daysBehind = behind;
              behindStageKey = s.key;
            }
          }
          remaining = Math.max(0, _endDate.diff(dayjs__WEBPACK_IMPORTED_MODULE_8___default()(), 'day'));
        }
        schedule.push({
          key: s.key,
          name: s.name,
          days: s.days,
          start: startStr,
          end: endStr,
          status: st,
          remaining: remaining
        });
        cursor = _endDate.add(1, 'day');
      }
      var completedCount = schedule.filter(function (x) {
        return x.status === 'completed';
      }).length;
      var progress = Math.round(completedCount / STAGES.length * 100);
      var lastEnd = schedule.length > 0 ? schedule[schedule.length - 1].end : '';
      return {
        schedule: schedule,
        endDate: lastEnd,
        progress: progress,
        completedCount: completedCount,
        daysBehind: daysBehind,
        behindStageKey: behindStageKey
      };
    }, [startDate, stageStatus, manualEndDates]),
    schedule = _useMemo.schedule,
    endDate = _useMemo.endDate,
    progress = _useMemo.progress,
    completedCount = _useMemo.completedCount,
    daysBehind = _useMemo.daysBehind,
    behindStageKey = _useMemo.behindStageKey;
  var handleSetDate = /*#__PURE__*/function () {
    var _ref2 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_3__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee2(e) {
      var _e$detail;
      var v, d, dateStr, nextStatus, _t2;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            v = (_e$detail = e.detail) === null || _e$detail === void 0 ? void 0 : _e$detail.value;
            if (v) {
              _context2.n = 1;
              break;
            }
            return _context2.a(2);
          case 1:
            d = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(v);
            if (!d.isBefore(dayjs__WEBPACK_IMPORTED_MODULE_8___default()(), 'day')) {
              _context2.n = 2;
              break;
            }
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: '请选择今日及以后的日期',
              icon: 'none'
            });
            return _context2.a(2);
          case 2:
            dateStr = d.format('YYYY-MM-DD');
            if (!(useApi && hasToken)) {
              _context2.n = 8;
              break;
            }
            _context2.p = 3;
            _context2.n = 4;
            return (0,_services_api__WEBPACK_IMPORTED_MODULE_11__.postWithAuth)('/constructions/start-date', {
              start_date: dateStr
            });
          case 4:
            setStartDate(dateStr);
            _context2.n = 5;
            return loadFromApi();
          case 5:
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: '进度计划更新成功',
              icon: 'success'
            });
            _context2.n = 7;
            break;
          case 6:
            _context2.p = 6;
            _t2 = _context2.v;
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: '更新失败',
              icon: 'none'
            });
          case 7:
            _context2.n = 9;
            break;
          case 8:
            setStartDate(dateStr);
            nextStatus = buildDefaultStageStatus();
            setStageStatus(nextStatus);
            saveLocal(dateStr, nextStatus);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: '进度计划更新成功',
              icon: 'success'
            });
          case 9:
            return _context2.a(2);
        }
      }, _callee2, null, [[3, 6]]);
    }));
    return function handleSetDate(_x) {
      return _ref2.apply(this, arguments);
    };
  }();
  var handleMarkRectify = /*#__PURE__*/function () {
    var _ref3 = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_3__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee3(key) {
      var _error$response, message, next, _t3;
      return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context3) {
        while (1) switch (_context3.p = _context3.n) {
          case 0:
            if (!(useApi && hasToken)) {
              _context3.n = 5;
              break;
            }
            _context3.p = 1;
            _context3.n = 2;
            return constructionApi.updateStageStatus((0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.getBackendStageCode)(key), 'need_rectify');
          case 2:
            (0,_utils_constructionStage__WEBPACK_IMPORTED_MODULE_12__.persistStageStatusToStorage)(key, 'need_rectify');
            clearStagePending(key);
            _context3.n = 4;
            break;
          case 3:
            _context3.p = 3;
            _t3 = _context3.v;
            message = (_t3 === null || _t3 === void 0 || (_error$response = _t3.response) === null || _error$response === void 0 || (_error$response = _error$response.data) === null || _error$response === void 0 ? void 0 : _error$response.detail) || '标记失败，请稍后重试';
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: message,
              icon: 'none'
            });
            return _context3.a(2);
          case 4:
            _context3.n = 6;
            break;
          case 5:
            markStagePending(key);
          case 6:
            next = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])({}, stageStatus), {}, (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_defineProperty_js__WEBPACK_IMPORTED_MODULE_0__["default"])({}, key, 'rectify'));
            setStageStatus(next);
            saveLocal(startDate, next);
            _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
              title: '已标记整改',
              icon: 'success'
            });
          case 7:
            return _context3.a(2);
        }
      }, _callee3, null, [[1, 3]]);
    }));
    return function handleMarkRectify(_x2) {
      return _ref3.apply(this, arguments);
    };
  }();
  var handleQuickDate = function handleQuickDate(days) {
    var d2 = dayjs__WEBPACK_IMPORTED_MODULE_8___default()().add(days, 'day').format('YYYY-MM-DD');
    if (useApi && hasToken) {
      (0,_services_api__WEBPACK_IMPORTED_MODULE_11__.postWithAuth)('/constructions/start-date', {
        start_date: d2
      }).then(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_3__["default"])(/*#__PURE__*/(0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().m(function _callee4() {
        return (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_regenerator_js__WEBPACK_IMPORTED_MODULE_1__["default"])().w(function (_context4) {
          while (1) switch (_context4.n) {
            case 0:
              setStartDate(d2);
              _context4.n = 1;
              return loadFromApi();
            case 1:
              _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
                title: '进度计划更新成功',
                icon: 'success'
              });
            case 2:
              return _context4.a(2);
          }
        }, _callee4);
      }))).catch(function () {
        return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
          title: '更新失败',
          icon: 'none'
        });
      });
    } else {
      setStartDate(d2);
      var nextStatus = buildDefaultStageStatus();
      setStageStatus(nextStatus);
      saveLocal(d2, nextStatus);
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '进度计划更新成功',
        icon: 'success'
      });
    }
  };
  var isAIActionLocked = function isAIActionLocked(index) {
    if (index === 0) return false;
    return stageStatus[STAGES[index - 1].key] !== 'completed';
  };
  var statusLabel = function statusLabel(s, index) {
    var isS00 = index === 0;
    if (s.status === 'completed') return isS00 ? '已核对' : '已通过';
    if (s.status === 'rectify') return '待整改';
    if (s.status === 'in_progress') return isS00 ? '待人工核对' : '待验收';
    return isS00 ? '待人工核对' : '待验收';
  };

  /** S00 人工核对：跳 P37 材料进场人工核对页；S01-S05 AI验收：跳 P15 拍照页 */
  var goStageCheck = function goStageCheck(index) {
    var s = STAGES[index];
    var locked = isAIActionLocked(index);
    if (locked) {
      var msg = index === 1 ? '请先完成材料进场人工核对' : "\u8BF7\u5148\u5B8C\u6210".concat(STAGES[index - 1].name, "\u9A8C\u6536");
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: msg,
        icon: 'none'
      });
      return;
    }
    var isS00 = index === 0;
    if (isS00) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
        url: "/pages/material-check/index?stage=material&scene=check"
      });
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '请按清单拍摄/上传材料照片完成人工核对',
        icon: 'none',
        duration: 2500
      });
    } else {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
        url: "/pages/photo/index?stage=".concat(s.key, "&scene=").concat(SCENE_ACCEPT)
      });
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '请拍摄/上传施工照片完成验收',
        icon: 'none',
        duration: 2500
      });
    }
  };

  /** 申请复检：跳 P15 带 scene=recheck，上传整改后照片后走复检流程 */
  var goRecheck = function goRecheck(stageKey) {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
      url: "/pages/photo/index?stage=".concat(stageKey, "&scene=").concat(SCENE_RECHECK)
    });
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
      title: '请上传整改后照片，将自动触发AI复检',
      icon: 'none',
      duration: 2500
    });
  };

  // V2.6.2优化：特殊申请功能移至设置页，此处删除

  var saveRemindSettings = function saveRemindSettings() {
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('remind_days', remindDays);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync('smart_remind', remindOpen);
    setRemindModalVisible(false);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
      title: '提醒设置成功',
      icon: 'success'
    });
  };
  var handleCalibrateTime = function handleCalibrateTime(stageKey, stageStart, e) {
    var _e$detail2;
    var v = e === null || e === void 0 || (_e$detail2 = e.detail) === null || _e$detail2 === void 0 ? void 0 : _e$detail2.value;
    if (!v) return;
    var d = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(v);
    var today = dayjs__WEBPACK_IMPORTED_MODULE_8___default()().startOf('day');
    var startDay = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(stageStart).startOf('day');
    if (d.isBefore(today)) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '请选择当前日期及以后的时间',
        icon: 'none',
        duration: 2500
      });
      return;
    }
    if (!d.isAfter(startDay)) {
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '校准时间须大于预计开始时间',
        icon: 'none',
        duration: 2500
      });
      return;
    }
    var newEnd = d.format('YYYY-MM-DD');
    var next = (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])((0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_objectSpread2_js__WEBPACK_IMPORTED_MODULE_2__["default"])({}, manualEndDates), {}, (0,_Users_mac_zhuangxiu_agent_backup_dev_frontend_node_modules_babel_runtime_helpers_esm_defineProperty_js__WEBPACK_IMPORTED_MODULE_0__["default"])({}, stageKey, newEnd));
    setManualEndDates(next);
    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().setStorageSync(STORAGE_KEY_CALIBRATE, JSON.stringify(next));
    setPendingSyncStages(function (s) {
      var n = new Set(s);
      n.delete(stageKey);
      return n;
    });
    var showSuccess = function showSuccess() {
      return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '时间校准成功，后续进度计划已同步更新',
        icon: 'none',
        duration: 3000
      });
    };
    var showCached = function showCached() {
      setPendingSyncStages(function (s) {
        return new Set(s).add(stageKey);
      });
      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
        title: '时间已缓存，联网后自动更新',
        icon: 'none',
        duration: 3000
      });
    };
    if (useApi && hasToken) {
      constructionApi.calibrateStageEnd(stageKey, newEnd).then(showSuccess).catch(showCached);
    } else {
      showSuccess();
    }
  };
  if (loading) {
    return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "construction-page",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "nav-bar",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "nav-title",
          children: "\u65BD\u5DE5\u966A\u4F34"
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "loading-wrap",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          children: "\u52A0\u8F7D\u4E2D\u2026"
        })
      })]
    });
  }
  if (!startDate) {
    return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "construction-page",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "nav-bar",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "nav-back",
          onClick: function onClick() {
            return (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_9__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_9__.TAB_HOME);
          },
          children: "\u8FD4\u56DE"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "nav-title",
          children: "\u65BD\u5DE5\u966A\u4F34"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "nav-placeholder"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "empty-state",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "empty-icon",
          children: "\uD83D\uDCC5"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "empty-text",
          children: "\u8BF7\u5148\u8BBE\u7F6E\u5F00\u5DE5\u65E5\u671F"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "date-card empty",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            className: "date-label",
            children: "\u8BBE\u7F6E\u5F00\u5DE5\u65E5\u671F"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "date-actions",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "remind-set",
              onClick: function onClick() {
                return setRemindModalVisible(true);
              },
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "remind-icon",
                children: "\uD83D\uDD14"
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "remind-text",
                children: "\u63D0\u9192\u8BBE\u7F6E"
              })]
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "quick-date-row",
              children: [7, 15, 30].map(function (d) {
                return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                  className: "quick-btn",
                  onClick: function onClick() {
                    return handleQuickDate(d);
                  },
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                    children: [d, "\u5929\u540E\u5F00\u5DE5"]
                  })
                }, d);
              })
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Picker, {
              mode: "date",
              value: dayjs__WEBPACK_IMPORTED_MODULE_8___default()().format('YYYY-MM-DD'),
              start: dayjs__WEBPACK_IMPORTED_MODULE_8___default()().format('YYYY-MM-DD'),
              onChange: handleSetDate,
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "set-date-btn",
                children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  children: "\u9009\u62E9\u5176\u4ED6\u65E5\u671F"
                })
              })
            })]
          })]
        })]
      }), remindModalVisible && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "remind-modal-mask",
        onClick: function onClick() {
          return setRemindModalVisible(false);
        },
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "remind-modal",
          onClick: function onClick(e) {
            return e.stopPropagation();
          },
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            className: "remind-modal-title",
            children: "\u63D0\u9192\u8BBE\u7F6E"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-row",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              children: "\u667A\u80FD\u63D0\u9192\u603B\u5F00\u5173"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "switch-wrap ".concat(remindOpen ? 'on' : ''),
              onClick: function onClick() {
                return setRemindOpen(!remindOpen);
              },
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "switch-dot",
                style: {
                  marginLeft: remindOpen ? '40rpx' : '0'
                }
              })
            })]
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-row",
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              children: "\u63D0\u9192\u63D0\u524D\u5929\u6570"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Picker, {
              mode: "selector",
              range: REMIND_DAYS_OPTIONS,
              value: REMIND_DAYS_OPTIONS.indexOf(remindDays),
              onChange: function onChange(e) {
                var _REMIND_DAYS_OPTIONS$;
                return setRemindDays((_REMIND_DAYS_OPTIONS$ = REMIND_DAYS_OPTIONS[Number(e.detail.value)]) !== null && _REMIND_DAYS_OPTIONS$ !== void 0 ? _REMIND_DAYS_OPTIONS$ : 3);
              },
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "picker-text",
                children: [remindDays, "\u5929"]
              })
            })]
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-save-btn",
            onClick: saveRemindSettings,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              children: "\u4FDD\u5B58\u8BBE\u7F6E"
            })
          })]
        })
      })]
    });
  }
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
    className: "construction-page",
    children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "nav-bar",
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        className: "nav-back",
        onClick: function onClick() {
          return (0,_utils_navigation__WEBPACK_IMPORTED_MODULE_9__.safeSwitchTab)(_utils_navigation__WEBPACK_IMPORTED_MODULE_9__.TAB_HOME);
        },
        children: "\u8FD4\u56DE"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
        className: "nav-title",
        children: "\u65BD\u5DE5\u966A\u4F34"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "nav-placeholder"
      })]
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.ScrollView, {
      scrollY: true,
      className: "scroll-body",
      scrollIntoView: scrollToStageId || undefined,
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "date-card",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "date-text",
          children: ["\u5F00\u5DE5\u65E5\u671F\uFF1A", startDate]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "date-actions",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Picker, {
            mode: "date",
            value: startDate,
            start: dayjs__WEBPACK_IMPORTED_MODULE_8___default()().format('YYYY-MM-DD'),
            onChange: handleSetDate,
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "date-edit",
              children: "\u7F16\u8F91"
            })
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "remind-set",
            onClick: function onClick() {
              return setRemindModalVisible(true);
            },
            children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "remind-icon",
              children: "\uD83D\uDD14"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "remind-text",
              children: "\u63D0\u9192\u8BBE\u7F6E"
            })]
          })]
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "overview-card",
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "overview-main",
          children: ["\u6574\u4F53\u8FDB\u5EA6\uFF1A", progress, "%"]
        }), daysBehind > 0 && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "overview-warn",
          children: [((_STAGES$find = STAGES.find(function (s) {
            return s.key === behindStageKey;
          })) === null || _STAGES$find === void 0 ? void 0 : _STAGES$find.name) || '当前', "\u9636\u6BB5\u843D\u540E\u8BA1\u5212", daysBehind, "\u5929"]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "overview-remind",
          children: "\u5F85\u63D0\u9192\u4E8B\u9879\u5C06\u663E\u793A\u4E8E\u6B64"
        })]
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "stages",
        children: schedule.map(function (s, i) {
          var locked = isAIActionLocked(i);
          var isS00 = i === 0;
          var progressPct = s.status === 'completed' ? 100 : s.status === 'in_progress' || s.status === 'rectify' ? 50 : 0;
          var today = dayjs__WEBPACK_IMPORTED_MODULE_8___default()();
          var startD = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(s.start).diff(today, 'day');
          var endD = dayjs__WEBPACK_IMPORTED_MODULE_8___default()(s.end).diff(today, 'day');
          var needRemind = s.status !== 'completed' && startD >= 0 && startD <= remindDays || endD >= 0 && endD <= remindDays;
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            id: "stage-".concat(i),
            className: "stage-card ".concat(highlightStageIndex === i ? 'stage-card-highlight' : ''),
            children: [needRemind && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "stage-reddot"
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "stage-header",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "stage-name-row",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "stage-icon",
                  children: STAGES[i].icon
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "stage-name",
                  children: [STAGES[i].label, " ", s.name]
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                  className: "status-badge ".concat(s.status),
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                    children: statusLabel(s, i)
                  })
                })]
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "stage-plan-time",
                children: [s.start, " ~ ", s.end, pendingSyncStages.has(s.key) && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "stage-pending-sync",
                  children: "\uFF08\u5F85\u540C\u6B65\uFF09"
                })]
              })]
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "progress-bar-wrap",
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "progress-fill ".concat(s.status),
                style: {
                  width: "".concat(progressPct, "%")
                }
              })
            }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "stage-actions",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "actions-left",
                children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "action-item ".concat(locked ? 'disabled' : ''),
                  onClick: function onClick() {
                    return locked ? undefined : goStageCheck(i);
                  },
                  children: isS00 ? '📋 人工核对' : '🔍 AI验收'
                }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                  className: "action-item ".concat(locked ? 'disabled' : ''),
                  onClick: function onClick() {
                    if (locked) {
                      _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
                        title: i === 1 ? '请先完成材料进场人工核对' : "\u8BF7\u5148\u5B8C\u6210".concat(STAGES[i - 1].name, "\u9A8C\u6536"),
                        icon: 'none'
                      });
                      return;
                    }
                    setGuideStage(s.key);
                  },
                  children: isS00 ? '📋 核对指引' : '📋 验收指引'
                })]
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                className: "actions-right",
                children: [!locked && (s.status === 'in_progress' || s.status === 'pending') ? /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Picker, {
                  mode: "date",
                  value: s.end,
                  start: dayjs__WEBPACK_IMPORTED_MODULE_8___default()().format('YYYY-MM-DD'),
                  onChange: function onChange(e) {
                    return handleCalibrateTime(s.key, s.start, e);
                  },
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                    className: "link-txt",
                    children: "\u8C03\u6574\u65F6\u95F4"
                  })
                }) : null, /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
                  className: "btn-done ".concat(s.status === 'completed' ? 'active' : ''),
                  children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                    children: statusLabel(s, i)
                  })
                })]
              })]
            }), s.status === 'completed' && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "record-panel",
              children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "record-text",
                children: [s.name, "\u8BB0\u5F55\uFF1A\u5DF2\u901A\u8FC7"]
              }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "link-txt",
                onClick: function onClick() {
                  if (locked) {
                    _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().showToast({
                      title: i === 1 ? '请先完成材料进场人工核对' : "\u8BF7\u5148\u5B8C\u6210".concat(STAGES[i - 1].name, "\u9A8C\u6536"),
                      icon: 'none'
                    });
                    return;
                  }
                  _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
                    url: isS00 ? '/pages/material-check/index?stage=material' : "/pages/acceptance/index?stage=".concat(s.key)
                  });
                },
                children: "\u67E5\u770B\u53F0\u8D26/\u62A5\u544A"
              })]
            }), s.status !== 'completed' && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
              className: "record-panel",
              children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
                className: "record-text",
                children: [s.name, "\u8BB0\u5F55\uFF1A", s.status === 'rectify' ? '待整改' : isS00 ? '待人工核对' : '待验收']
              })
            })]
          }, s.key);
        })
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "share-wrap",
        children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "btn-share",
          onClick: function onClick() {
            return _tarojs_taro__WEBPACK_IMPORTED_MODULE_7___default().navigateTo({
              url: '/pages/progress-share/index'
            });
          },
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            children: "\u4E00\u952E\u5206\u4EAB\u8FDB\u5EA6"
          })
        })
      })]
    }), remindModalVisible && /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
      className: "remind-modal-mask",
      onClick: function onClick() {
        return setRemindModalVisible(false);
      },
      children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
        className: "remind-modal",
        onClick: function onClick(e) {
          return e.stopPropagation();
        },
        children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
          className: "remind-modal-title",
          children: "\u63D0\u9192\u8BBE\u7F6E"
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "remind-row",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            children: "\u667A\u80FD\u63D0\u9192\u603B\u5F00\u5173"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
            className: "switch-wrap ".concat(remindOpen ? 'on' : ''),
            onClick: function onClick() {
              return setRemindOpen(!remindOpen);
            },
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "switch-dot",
              style: {
                marginLeft: remindOpen ? '40rpx' : '0'
              }
            })
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "remind-row",
          children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            children: "\u63D0\u9192\u63D0\u524D\u5929\u6570"
          }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Picker, {
            mode: "selector",
            range: REMIND_DAYS_OPTIONS,
            value: REMIND_DAYS_OPTIONS.indexOf(remindDays),
            onChange: function onChange(e) {
              var _REMIND_DAYS_OPTIONS$2;
              return setRemindDays((_REMIND_DAYS_OPTIONS$2 = REMIND_DAYS_OPTIONS[Number(e.detail.value)]) !== null && _REMIND_DAYS_OPTIONS$2 !== void 0 ? _REMIND_DAYS_OPTIONS$2 : 3);
            },
            children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
              className: "picker-text",
              children: [remindDays, "\u5929"]
            })
          })]
        }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.View, {
          className: "remind-save-btn",
          onClick: saveRemindSettings,
          children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_6__.Text, {
            children: "\u4FDD\u5B58\u8BBE\u7F6E"
          })
        })]
      })
    }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_13__.jsx)(_components_AcceptanceGuideModal__WEBPACK_IMPORTED_MODULE_10__["default"], {
      stageKey: guideStage || 'material',
      visible: !!guideStage,
      onClose: function onClose() {
        return setGuideStage(null);
      }
    })]
  });
};
/* harmony default export */ __webpack_exports__["default"] = (Construction);

/***/ }),

/***/ "./src/components/AcceptanceGuideModal/index.tsx":
/*!*******************************************************!*\
  !*** ./src/components/AcceptanceGuideModal/index.tsx ***!
  \*******************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/container/remote/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tarojs_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @tarojs/components */ "./node_modules/@tarojs/plugin-platform-weapp/dist/components-react.js");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react/jsx-runtime */ "webpack/container/remote/react/jsx-runtime");
/* harmony import */ var react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__);




/**
 * P30 验收指引弹窗 - 对应阶段验收要点
 */

var STAGE_GUIDES = {
  material: {
    title: 'S00 材料进场核对指引',
    points: ['1. 核对材料清单与合同/报价单是否一致', '2. 品牌、规格、数量逐一对照', '3. 必拍：材料清单+实物对比照', '4. 不合格项记录并要求更换']
  },
  plumbing: {
    title: 'S01 隐蔽工程验收要点',
    points: ['1. 强电与弱电间距≥30cm，交叉处锡箔纸屏蔽', '2. 线管弯曲半径≥6倍管径，无死弯', '3. 电线接头挂锡或使用接线端子', '4. 水管打压0.6-0.8MPa，30分钟压降≤0.05MPa', '5. 冷热水管左热右冷，间距≥15cm']
  },
  water_electric: {
    title: '水电验收要点',
    points: ['1. 强电与弱电间距≥30cm，交叉处锡箔纸屏蔽', '2. 线管弯曲半径≥6倍管径，无死弯', '3. 电线接头挂锡或使用接线端子', '4. 水管打压0.6-0.8MPa，30分钟压降≤0.05MPa', '5. 冷热水管左热右冷，间距≥15cm']
  },
  carpentry: {
    title: 'S02 泥瓦工验收要点',
    points: ['1. 瓷砖空鼓率≤5%，重点检查边角', '2. 吊顶龙骨间距符合规范，牢固无松动', '3. 木质材料做好防潮防腐处理', '4. 阴阳角垂直度偏差≤3mm']
  },
  woodwork: {
    title: 'S03 木工验收要点',
    points: ['1. 吊顶龙骨间距符合规范，牢固无松动', '2. 木质材料防潮防腐处理到位', '3. 阴阳角垂直度偏差≤3mm', '4. 柜体安装牢固、门缝均匀']
  },
  masonry_wood: {
    title: '泥木验收要点',
    points: ['1. 瓷砖空鼓率≤5%，重点检查边角', '2. 吊顶龙骨间距符合规范，牢固无松动', '3. 木质材料做好防潮防腐处理', '4. 阴阳角垂直度偏差≤3mm']
  },
  painting: {
    title: 'S04 油漆验收要点',
    points: ['1. 墙面平整，无裂纹、起皮、流坠', '2. 阴阳角顺直，无缺棱掉角', '3. 涂料色泽均匀，无色差', '4. 油漆表面光滑，无颗粒、刷痕']
  },
  paint: {
    title: '油漆验收要点',
    points: ['1. 墙面平整，无裂纹、起皮、流坠', '2. 阴阳角顺直，无缺棱掉角', '3. 涂料色泽均匀，无色差', '4. 油漆表面光滑，无颗粒、刷痕']
  },
  installation: {
    title: 'S05 安装收尾验收要点',
    points: ['1. 橱柜/卫浴/门安装牢固，开关顺畅', '2. 五金件无缺失、无松动', '3. 灯具/开关插座通电正常', '4. 整体保洁完成，无遗漏']
  },
  floor: {
    title: '地板验收要点',
    points: ['1. 地面平整度≤3mm/2m', '2. 地板拼接紧密，无起拱、异响', '3. 收边条安装牢固，无缝隙', '4. 地暖区域使用专用地板']
  },
  soft_furnishing: {
    title: '软装验收要点',
    points: ['1. 定制家具尺寸与图纸一致', '2. 五金件安装牢固，开关顺畅', '3. 软装材质无异味，环保达标', '4. 整体风格协调，无明显瑕疵']
  },
  soft: {
    title: '软装验收要点',
    points: ['1. 定制家具尺寸与图纸一致', '2. 五金件安装牢固，开关顺畅', '3. 软装材质无异味，环保达标', '4. 整体风格协调，无明显瑕疵']
  }
};
var AcceptanceGuideModal = function AcceptanceGuideModal(_ref) {
  var stageKey = _ref.stageKey,
    visible = _ref.visible,
    onClose = _ref.onClose;
  if (!visible) return null;
  var guide = STAGE_GUIDES[stageKey] || STAGE_GUIDES.material || STAGE_GUIDES.plumbing;
  return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
    className: "guide-modal-mask",
    onClick: onClose,
    children: /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsxs)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.View, {
      className: "guide-modal",
      onClick: function onClick(e) {
        return e.stopPropagation();
      },
      children: [/*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "close-btn",
        onClick: onClose,
        children: "\xD7"
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
        className: "modal-title",
        children: guide.title
      }), /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.ScrollView, {
        scrollY: true,
        className: "guide-content",
        children: guide.points.map(function (p, i) {
          return /*#__PURE__*/(0,react_jsx_runtime__WEBPACK_IMPORTED_MODULE_2__.jsx)(_tarojs_components__WEBPACK_IMPORTED_MODULE_1__.Text, {
            className: "guide-point",
            children: p
          }, i);
        })
      })]
    })
  });
};
/* harmony default export */ __webpack_exports__["default"] = (AcceptanceGuideModal);

/***/ }),

/***/ "./src/pages/construction/index.tsx":
/*!******************************************!*\
  !*** ./src/pages/construction/index.tsx ***!
  \******************************************/
/***/ (function(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {

/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @tarojs/runtime */ "webpack/container/remote/@tarojs/runtime");
/* harmony import */ var _tarojs_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_construction_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../../../node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/construction/index!./index.tsx */ "./node_modules/@tarojs/taro-loader/lib/entry-cache.js?name=pages/construction/index!./src/pages/construction/index.tsx");


var config = {"navigationBarTitleText":"施工陪伴","navigationBarBackgroundColor":"#1677FF","navigationBarTextStyle":"white","enablePullDownRefresh":true};


var inst = Page((0,_tarojs_runtime__WEBPACK_IMPORTED_MODULE_0__.createPageConfig)(_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_construction_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"], 'pages/construction/index', {root:{cn:[]}}, config || {}))


/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_tarojs_taro_loader_lib_entry_cache_js_name_pages_construction_index_index_tsx__WEBPACK_IMPORTED_MODULE_1__["default"]);


/***/ })

},
/******/ function(__webpack_require__) { // webpackRuntimeModules
/******/ var __webpack_exec__ = function(moduleId) { return __webpack_require__(__webpack_require__.s = moduleId); }
/******/ __webpack_require__.O(0, ["taro","vendors","common"], function() { return __webpack_exec__("./src/pages/construction/index.tsx"); });
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=index.js.map