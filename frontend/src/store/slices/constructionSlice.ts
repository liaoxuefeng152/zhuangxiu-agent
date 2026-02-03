import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ConstructionState {
  schedule: any
}

const initialState: ConstructionState = {
  schedule: null
}

const constructionSlice = createSlice({
  name: 'construction',
  initialState,
  reducers: {
    setSchedule: (state, action: PayloadAction<any>) => {
      state.schedule = action.payload
    },
    updateSchedule: (state, action: PayloadAction<any>) => {
      if (state.schedule) {
        state.schedule = { ...state.schedule, ...action.payload }
      }
    }
  }
})

export const { setSchedule, updateSchedule } = constructionSlice.actions
export default constructionSlice.reducer
