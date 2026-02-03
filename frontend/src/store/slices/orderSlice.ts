import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface OrderState {
  currentOrder: any
  orderHistory: any[]
}

const initialState: OrderState = {
  currentOrder: null,
  orderHistory: []
}

const orderSlice = createSlice({
  name: 'order',
  initialState,
  reducers: {
    setCurrentOrder: (state, action: PayloadAction<any>) => {
      state.currentOrder = action.payload
    },
    setOrderHistory: (state, action: PayloadAction<any[]>) => {
      state.orderHistory = action.payload
    },
    addOrderToHistory: (state, action: PayloadAction<any>) => {
      state.orderHistory.unshift(action.payload)
    }
  }
})

export const { setCurrentOrder, setOrderHistory, addOrderToHistory } = orderSlice.actions
export default orderSlice.reducer
