import { createContext, useCallback, useContext, useRef, useState } from 'react'

const UIContext = createContext(null)

export function UIProvider({ children }) {
  const [popupOpen, setPopupOpen] = useState(false)
  const [appLoading, setAppLoading] = useState(false)
  const [toasts, setToasts] = useState([])
  const idRef = useRef(0)

  // Hook for the Animation layer: it should lock the smooth scroller (ss.isFixed = popup open).
  const emitPopup = (open) => window.dispatchEvent(new CustomEvent('ff:popup', { detail: { open } }))
  const openPopup = useCallback(() => { setPopupOpen(true); emitPopup(true) }, [])
  const closePopup = useCallback(() => { setPopupOpen(false); emitPopup(false) }, [])

  const pushToast = useCallback((text, type = 'default') => {
    const id = ++idRef.current
    setToasts((t) => [...t, { id, text, type }])
  }, [])
  const removeToast = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), [])

  return (
    <UIContext.Provider value={{ popupOpen, openPopup, closePopup, appLoading, setAppLoading, toasts, pushToast, removeToast }}>
      {children}
    </UIContext.Provider>
  )
}

export const useUI = () => useContext(UIContext)
