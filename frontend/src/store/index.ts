import { configureStore } from '@reduxjs/toolkit'
import userReducer from './slices/userSlice'
import companyReducer from './slices/companySlice'
import quoteReducer from './slices/quoteSlice'
import contractReducer from './slices/contractSlice'
import constructionReducer from './slices/constructionSlice'
import orderReducer from './slices/orderSlice'

const store = configureStore({
  reducer: {
    user: userReducer,
    company: companyReducer,
    quote: quoteReducer,
    contract: contractReducer,
    construction: constructionReducer,
    order: orderReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    }),
})

export default store
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
