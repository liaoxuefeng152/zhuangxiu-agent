import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ContractState {
  currentContract: any
  contractHistory: any[]
}

const initialState: ContractState = {
  currentContract: null,
  contractHistory: []
}

const contractSlice = createSlice({
  name: 'contract',
  initialState,
  reducers: {
    setCurrentContract: (state, action: PayloadAction<any>) => {
      state.currentContract = action.payload
    },
    setContractHistory: (state, action: PayloadAction<any[]>) => {
      state.contractHistory = action.payload
    },
    addContractToHistory: (state, action: PayloadAction<any>) => {
      state.contractHistory.unshift(action.payload)
    }
  }
})

export const { setCurrentContract, setContractHistory, addContractToHistory } = contractSlice.actions
export default contractSlice.reducer
