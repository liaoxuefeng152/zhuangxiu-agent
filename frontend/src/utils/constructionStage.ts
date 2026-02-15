import Taro from '@tarojs/taro'

export type StageStatus = 'pending' | 'in_progress' | 'completed' | 'rectify' | 'rectify_done'

export const STAGE_STATUS_STORAGE_KEY = 'construction_stage_status'

export const STAGE_KEY_TO_BACKEND: Record<string, string> = {
  material: 'S00',
  plumbing: 'S01',
  carpentry: 'S02',
  woodwork: 'S03',
  painting: 'S04',
  installation: 'S05'
}

export const BACKEND_STAGE_TO_KEY = Object.fromEntries(
  Object.entries(STAGE_KEY_TO_BACKEND).map(([key, value]) => [value, key])
)

export const getBackendStageCode = (stageKey: string): string => {
  return STAGE_KEY_TO_BACKEND[stageKey] || stageKey
}

export const getCompletionPayload = (stageKey: string): string => {
  return stageKey === 'material' ? 'checked' : 'passed'
}

export const mapBackendStageStatus = (raw?: string, stageKey?: string): StageStatus => {
  if (!raw) return stageKey === 'material' ? 'in_progress' : 'pending'
  const normalized = String(raw ?? '').toLowerCase()
  if (['checked', 'passed', 'completed'].includes(normalized)) return 'completed'
  if (normalized === 'rectify_exhausted') return 'rectify_done'  // 复检3次仍未通过，可进入下一阶段
  if (['rectify', 'need_rectify', 'pending_recheck'].includes(normalized)) return 'rectify'
  if (['in_progress', 'checking'].includes(normalized)) return 'in_progress'
  if (stageKey === 'material') return 'in_progress'
  return 'pending'
}

export const persistStageStatusToStorage = (stageKey: string, backendStatus: string) => {
  try {
    const raw = Taro.getStorageSync(STAGE_STATUS_STORAGE_KEY)
    const current: Record<string, StageStatus> = raw ? JSON.parse(raw) : {}
    current[stageKey] = mapBackendStageStatus(backendStatus, stageKey)
    Taro.setStorageSync(STAGE_STATUS_STORAGE_KEY, JSON.stringify(current))
  } catch {
    // ignore storage failures
  }
}
