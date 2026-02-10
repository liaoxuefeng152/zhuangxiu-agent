import { createSlice } from '@reduxjs/toolkit'

const networkSlice = createSlice({
  name: 'network',
  initialState: { error: false },
  reducers: {
    setNetworkError: (state, action) => {
      state.error = action.payload
    }
  }
})

export const { setNetworkError } = networkSlice.actions
export default networkSlice.reducer
