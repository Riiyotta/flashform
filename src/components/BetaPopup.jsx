import { useEffect, useRef, useState } from 'react'
import Button from './Button.jsx'
import Input from './Input.jsx'
import { useUI } from '../context.jsx'
import { EMAIL_RE, submitForm } from './submitForm.js'

// spec §7.2. Mirrors the Vue `popup` transition: enter-from / leave-to classes, .3s ease.
export default function BetaPopup() {
  const ui = useUI()
  const { popupOpen, closePopup } = ui
  const [rendered, setRendered] = useState(false)
  const [phase, setPhase] = useState('popup-enter-from')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState(null)
  const emailRef = useRef(null)

  useEffect(() => {
    if (popupOpen) {
      setRendered(true)
      setPhase('popup-enter-from')
      let r2
      const r1 = requestAnimationFrame(() => { r2 = requestAnimationFrame(() => setPhase('')) })
      return () => { cancelAnimationFrame(r1); cancelAnimationFrame(r2) }
    }
    if (rendered) {
      setPhase('popup-leave-to')
      const t = setTimeout(() => setRendered(false), 300)
      return () => clearTimeout(t)
    }
  }, [popupOpen]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!rendered) return null

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!EMAIL_RE.test(email)) { setError('incorrect email'); emailRef.current.focus(); return }
    setError(null)
    const ok = await submitForm({ Name: name, Email: email }, ui)
    if (ok) { setName(''); setEmail('') }
    closePopup()
  }

  return (
    <div className={`popup ${phase}`.trim()}>
      <div className="popup__backdrop" onClick={closePopup} />
      <div className="popup__window">
        <button className="popup__btn" aria-label="Close" onClick={closePopup}>
          <span className="popup__close-icon"><svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 0C6.2 0 0 6.2 0 14C0 21.8 6.2 28 14 28C21.8 28 28 21.8 28 14C28 6.2 21.8 0 14 0ZM19.4 21L14 15.6L8.6 21L7 19.4L12.4 14L7 8.6L8.6 7L14 12.4L19.4 7L21 8.6L15.6 14L21 19.4L19.4 21Z" fill="#333333" fillOpacity="0.9" />
          </svg></span>
        </button>
        <form className="form popup__form" noValidate onSubmit={onSubmit}>
          <legend className="popup__form-h">Join the beta</legend>
          <Input id="name" className="form__input popup__form-input" label="Your Name" validation value={name} onChange={setName} />
          <Input id="email-2" className="form__input popup__form-input" label="Your Email" required value={email} onChange={setEmail} error={error} inputRef={emailRef} />
          <Button className="popup__form-btn">Join</Button>
        </form>
      </div>
    </div>
  )
}
