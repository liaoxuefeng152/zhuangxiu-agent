import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UserInfo {
  userId: number
  openid: string
  nickname: string
  avatarUrl: string
  phone: string
  phoneVerified: boolean
  isMember: boolean
  memberExpire?: string // 会员到期日 YYYY-MM-DD，用于续费提醒
  points?: number // 用户积分（V2.6.7新增）
}

interface UserState {
  userInfo: UserInfo | null
  isLoggedIn: boolean
}

const initialState: UserState = {
  userInfo: null,
  isLoggedIn: false
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserInfo: (state, action: PayloadAction<UserInfo>) => {
      state.userInfo = action.payload
      state.isLoggedIn = true
    },
    logout: (state) => {
      state.userInfo = null
      state.isLoggedIn = false
    },
    updateUserInfo: (state, action: PayloadAction<Partial<UserInfo>>) => {
      if (state.userInfo) {
        state.userInfo = { ...state.userInfo, ...action.payload }
      }
    }
  }
})

export const { setUserInfo, logout, updateUserInfo } = userSlice.actions
export default userSlice.reducer
