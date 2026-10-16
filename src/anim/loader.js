// §5.1 Intro loader timeline — same call sequence as the original layout's Loader setup (default-*.mjs).
// Measured on the live site (rAF sampling from mount): center chars settle ~0.6s; --ct lines from +1.0s; col-1 .done
// at ~2.7s; all items lines at +2.6s; non-ec fade 3.6–4.1s; --ec scale 1 -> 100 / opacity 1 -> 0 over 4.1–5.4s
// (power3.inOut); loader removed at mount + 5.4s, mount = MOUNT_AT (~0.8s) -> ~6.2s.
import gsap from 'gsap'
import { delay, mountDelay } from './core.js'
import { splitTextAnimation, revertReveals } from './reveal.js'

export function runLoader(root, onDone) {
  const ac = new AbortController()
  const { signal } = ac
  const timers = []
  let tl
  const q = (s) => root.querySelector(s)
  ;(async () => {
    await delay(mountDelay(), signal) // Nuxt hydration + dynamic-import offset (see core.js MOUNT_AT)
    const $c = q('.loader__item--c'), $ct = q('.loader__item--ct'), $cb = q('.loader__item--cb'), $ec = q('.loader__item--ec'), $col1 = q('.loader__col--1')
    splitTextAnimation().animateByChars($c)
    await delay(1000, signal)
    splitTextAnimation().animateByLines($ct)
    await delay(100, signal)
    splitTextAnimation().animateByLines($cb)
    await delay(500, signal)
    tl = gsap.timeline()
    tl.to($col1.querySelectorAll('.loader__item'), {
      duration: 1, css: { left: 0, transform: 'translateX(0)' }, ease: 'power2.inOut', stagger: 0.01,
      onComplete: () => $col1.classList.add('done'),
    })
    await delay(1000, signal)
    const all = root.querySelectorAll('.loader__item')
    const notEc = root.querySelectorAll('.loader__item:not(.loader__item--ec)')
    all.forEach((el, i) => timers.push(setTimeout(() => splitTextAnimation().animateByLines(el, 0.9), 20 * i)))
    await delay(1000, signal)
    tl.to(notEc, { duration: 0.5, opacity: 0 })
    tl.to($ec, { duration: 1.3, scale: 100, opacity: 0, ease: 'power3.inOut', force3D: false })
    await delay(1800, signal)
    onDone()
  })().catch((e) => { if (e?.name !== 'AbortError') throw e })

  return () => {
    ac.abort()
    timers.forEach(clearTimeout)
    tl?.kill()
    gsap.killTweensOf(root.querySelectorAll('*'))
    revertReveals(root, { clearTimers: false })
    root.querySelector('.loader__col--1')?.classList.remove('done')
    root.querySelectorAll('.loader__item').forEach((el) => el.removeAttribute('style'))
  }
}
