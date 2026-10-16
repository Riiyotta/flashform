import { useEffect, useState } from 'react'
import { Logo, SigninArrow } from './icons.jsx'
import MobileMenu from './MobileMenu.jsx'
import { useUI } from '../context.jsx'
import { anchorScroll } from '../anim/scrollFx.js'

const LINKS = [
  { href: '#why', label: 'Why flashform' },
  { href: '#integration', label: 'Integration' },
  { href: '#benefits', label: 'Benefits' },
  { href: '#roadmap', label: 'Roadmap', mobHidden: true },
  { href: '#faq', label: 'FAQ' },
]

// spec §1.1. Anchor smooth-scroll (+30% vh offset, 1s) via anchorScroll; nav-hidden handled by src/anim navbarPos.
export default function Navbar() {
  const { openPopup } = useUI()
  const [open, setOpen] = useState(false)

  // Clicking anywhere (including a menu item) closes the menu, spec §7.1.
  useEffect(() => {
    if (!open) return
    const close = (e) => { if (!e.target.closest('.burger')) setOpen(false) }
    document.body.addEventListener('click', close)
    return () => document.body.removeEventListener('click', close)
  }, [open])

  return (
    <header className={`navbar${open ? ' navbar--fixed' : ''}`}>
      <div className="container navbar__container">
        <div className="navbar__content">
          <a href="/" className="navbar__logo" aria-label="FlashForm"><Logo /></a>
          <nav className={`navbar__nav${open ? ' open' : ''}`}>
            <ul className="navbar__ul">
              {LINKS.map((l) => (
                <li key={l.href} className={`${l.mobHidden ? 'navbar__item--mob-hidden ' : ''}navbar__item`}>
                  <a href={l.href} className="navbar__link" onClick={(e) => { e.preventDefault(); anchorScroll(l.href) }}>{l.label}</a>
                </li>
              ))}
              <li className="navbar__item">
                <button className="navbar__link navbar__link--signin" onClick={openPopup}>
                  <span>Join the beta</span>
                  <SigninArrow />
                </button>
              </li>
            </ul>
          </nav>
          <MobileMenu open={open} onToggle={() => setOpen((o) => !o)} />
        </div>
      </div>
    </header>
  )
}
