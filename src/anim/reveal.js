// Port of the original animations-*.mjs (splitTextAnimation + sectionAnimation) and ScrollAnimations-*.mjs.
import gsap from 'gsap'
import SplitType from 'split-type'
import { raf } from './core.js'

const splits = new Set() // every SplitType instance, reverted on cleanup (StrictMode / unmount safe)

export const splitTextAnimation = () => {
  let lines, chars
  const split = (el, types = 'chars, lines') => {
    if (el.classList.contains('splitted')) return
    const st = new SplitType(el, { types, tagName: 'span', lineClass: 'e-line' })
    splits.add(st)
    ;(st.lines || []).forEach((line, i) => {
      line.innerHTML = `<span class="line-inner">${line.innerHTML}</span>`
      line.setAttribute('data-line', line.innerText)
      line.setAttribute('data-line-idx', i)
    })
    lines = [...el.querySelectorAll('.line-inner')]
    chars = [...el.querySelectorAll('.char')]
    el.classList.add('splitted')
  }
  return {
    animateByChars(el, duration = 0.5, stagger = 0.07) {
      split(el, 'lines, words, chars')
      el.style.opacity = 1
      if (chars?.length) {
        lines.forEach((line) => {
          const c = line.querySelectorAll('.char')
          gsap.to(c, { duration, y: 0, scaleY: 1, stagger, ease: 'back.out(2)' })
          gsap.to(c, { duration: duration * 1.1, stagger, opacity: 1, ease: 'back.out(2)' })
        })
      }
    },
    animateByLines(el, duration = 1, stagger = 0.1) {
      split(el, 'lines, words')
      el.style.opacity = 1
      if (lines?.length) {
        gsap.to(lines, { duration, y: '0%', rotation: 0, stagger, ease: 'power4.out' })
        gsap.to(lines, { duration: duration * 1.2, stagger, opacity: 1, ease: 'power4.out' })
      }
    },
  }
}

// sectionAnimation(section): [data-a-l] lines, [data-a-t] rise, [data-a-o] fade, [data-a-h] chars (n*300ms),
// [data-a-p] lines ((n+1)*700ms). Timers are tracked so cleanup can cancel them.
const timers = new Set()
const later = (fn, ms) => { const t = setTimeout(() => { timers.delete(t); fn() }, ms); timers.add(t) }

export const sectionAnimation = (el) => {
  const l = el.querySelectorAll('[data-a-l]')
  const t = el.querySelectorAll('[data-a-t]')
  const o = el.querySelectorAll('[data-a-o]')
  const h = el.querySelectorAll('[data-a-h]')
  const p = el.querySelectorAll('[data-a-p]')
  const ease = 'power3.out'
  if (l.length) gsap.to(l, { duration: 1, scaleX: 1, delay: 0, ease: 'power1.inOut', stagger: 0.1 })
  if (t.length) gsap.to(t, { duration: 0.7, delay: 0, opacity: 1, y: 0, ease, stagger: 0.1 })
  if (o.length) gsap.to(o, { duration: 0.8, delay: 0, opacity: 1, ease, stagger: 0.1 })
  h.forEach((e, n) => later(() => splitTextAnimation().animateByChars(e), n * 300))
  p.forEach((e, n) => later(() => splitTextAnimation().animateByLines(e), (n + 1) * 700))
}

export { later }

// ScrollAnimations: each rAF, a [data-in-view] element activates once when 0 < rect.top <= innerHeight * threshold.
export class ScrollAnimations {
  constructor() {
    this.sections = [...document.querySelectorAll('[data-in-view]')]
    this.check = () => {
      this.sections.forEach((s) => {
        const top = s.getBoundingClientRect().top
        const th = +s.dataset.inView || 0.9
        if (top <= window.innerHeight * th && top > 0 && !s.classList.contains('activated')) {
          s.classList.add('activated')
          sectionAnimation(s)
        }
      })
    }
    raf.on(this.check)
  }
  destroy() {
    raf.off(this.check)
    this.sections.forEach((s) => s.classList.remove('activated'))
  }
}

// Cleanup scoped to `root`: cancel pending timers (global), kill tweens on split targets, revert SplitType DOM
// and inline styles written by the reveal tweens.
export const revertReveals = (root = document, { clearTimers = true } = {}) => {
  if (clearTimers) { timers.forEach(clearTimeout); timers.clear() }
  splits.forEach((st) => {
    const els = (st.elements || []).filter((el) => root === document || root.contains(el))
    if (!els.length) return
    els.forEach((el) => {
      gsap.killTweensOf(el.querySelectorAll('.char, .line-inner'))
      el.classList.remove('splitted')
      el.style.removeProperty('opacity')
    })
    st.revert()
    splits.delete(st)
  })
  const els = root.querySelectorAll('[data-a-l], [data-a-t], [data-a-o], [data-a-h], [data-a-p]')
  gsap.killTweensOf(els)
  els.forEach((e) => { ['opacity', 'transform', 'translate', 'rotate', 'scale'].forEach((p) => e.style.removeProperty(p)) })
}
