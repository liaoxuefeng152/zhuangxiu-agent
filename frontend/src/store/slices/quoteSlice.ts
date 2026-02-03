import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface QuoteState {
  currentQuote: any
  quoteHistory: any[]
}

const initialState: QuoteState = {
  currentQuote: null,
  quoteHistory: []
}

const quoteSlice = createSlice({
  name: 'quote',
  initialState,
  reducers: {
    setCurrentQuote: (state, action: PayloadAction<any>) => {
      state.currentQuote = action.payload
    },
    setQuoteHistory: (state, action: PayloadAction<any[]>) => {
      state.quoteHistory = action.payload
    },
    addQuoteToHistory: (state, action: PayloadAction<any>) => {
      state.quoteHistory.unshift(action.payload)
    }
  }
})

export const { setCurrentQuote, setQuoteHistory, addQuoteToHistory } = quoteSlice.actions
export default quoteSlice.reducer
