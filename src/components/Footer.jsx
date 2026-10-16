import { useRef, useState } from 'react'
import { Logo } from './icons.jsx'
import Button from './Button.jsx'
import Input from './Input.jsx'
import { useUI } from '../context.jsx'
import { EMAIL_RE, submitForm } from './submitForm.js'

const CONTACTS = [
  ['hello@emotion-agency.com', 'mailto:hello@emotion-agency.com'],
  ['Whatsapp', 'https://wa.me/+380970422959'],
  ['Telegram', 'https://t.me/rstetsr'],
]

function FooterForm() {
  const ui = useUI()
  const [email, setEmail] = useState('')
  const [error, setError] = useState(null)
  const ref = useRef(null)
  const onSubmit = async (e) => {
    e.preventDefault()
    if (!EMAIL_RE.test(email)) { setError('incorrect email'); ref.current.focus(); return }
    setError(null)
    if (await submitForm({ Email: email }, ui)) setEmail('')
  }
  return (
    <form className="form footer__form" noValidate onSubmit={onSubmit}>
      <Input id="email" className="form__input" label="Your Email" required value={email} onChange={setEmail} error={error} inputRef={ref} />
      <Button className="form__btn input-btn">Join</Button>
    </form>
  )
}

// spec §1.13. `#letter-parent` = matter-js mount (Render creates its canvas sized to this element, bg #111606).
// Static fallback: empty 100vh (≤460: 50vh) dark area.
export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__container">
        <div className="footer__top">
          <div id="letter-parent">
            <div className="letter-over" />
          </div>
        </div>
        <div className="footer__bottom">
          <div className="footer__line" />
          <div className="grid footer__content">
            <div className="footer__item foter__item--1"><Logo /></div>
            <div className="footer__item foter__item--2">
              <h3 className="footer__h">Contact us</h3>
              <ul className="footer__contacts">
                {CONTACTS.map(([label, href]) => (
                  <li key={href} className="footer__contact footer-contact">
                    <Button as="a" href={href} target="_blank" rel="noreferer noopener" className="footer-contact__btn">{label}</Button>
                  </li>
                ))}
              </ul>
            </div>
            <div className="footer__item foter__item--4">
              <h3 className="footer__h">Join the beta</h3>
              <FooterForm />
            </div>
          </div>
          <div className="footer__info">
            <div className="grid footer__info-content">
              <div className="footer__item foter__item--1"><small className="footer__copy">©2022 Flashform</small></div>
              <div className="footer__item foter__item--2">
                <a className="footer__legal" href="https://www.termsandconditionsgenerator.com/live.php?token=KqfzIWBkH418WdHEZEWKRACbvJtGFf0j" target="_blank" rel="noreferer noopener">Terms and conditions</a>
              </div>
              <div className="footer__item foter__item--3">
                <a className="footer__legal" href="https://www.privacypolicygenerator.info/live.php?token=iEz9YG406khJuP5hPg30r2GlroSf2mmH" target="_blank" rel="noreferer noopener">Privacy Policy</a>
              </div>
              <div className="footer__item foter__item--4">
                <a href="https://emotion-agency.com/en/" target="_blank" rel="noreferer noopener" className="footer__by">by emotion</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
