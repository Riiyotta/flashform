import { BurgerClose } from './icons.jsx'

// Burger toggle (visible only ≤1060 via CSS), spec §7.1. Open state = `.burger--open`.
export default function MobileMenu({ open, onToggle }) {
  return (
    <button
      className={`navbar__burger burger${open ? ' burger--open' : ''}`}
      aria-label="Navigation button"
      onClick={onToggle}
    >
      <span className="burger__dot burger__dot--1" />
      <span className="burger__dot burger__dot--2">
        <span className="burger__close-icon"><BurgerClose /></span>
      </span>
      <span className="burger__dot burger__dot--3" />
    </button>
  )
}
