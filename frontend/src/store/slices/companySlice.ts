import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface CompanyState {
  currentScan: any
  scanHistory: any[]
}

const initialState: CompanyState = {
  currentScan: null,
  scanHistory: []
}

const companySlice = createSlice({
  name: 'company',
  initialState,
  reducers: {
    setCurrentScan: (state, action: PayloadAction<any>) => {
      state.currentScan = action.payload
    },
    setScanHistory: (state, action: PayloadAction<any[]>) => {
      state.scanHistory = action.payload
    },
    addScanToHistory: (state, action: PayloadAction<any>) => {
      state.scanHistory.unshift(action.payload)
    }
  }
})

export const { setCurrentScan, setScanHistory, addScanToHistory } = companySlice.actions
export default companySlice.reducer
