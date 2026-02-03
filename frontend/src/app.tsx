import * as React from 'react'
import { Provider } from 'react-redux'
import store from './store'

function App({ children }: React.PropsWithChildren<{}>) {
  return (
    <Provider store={store}>
      {children}
    </Provider>
  )
}

export default App
