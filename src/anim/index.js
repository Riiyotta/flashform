// Page motion orchestrator. Mirrors the original mount order:
//  layout mount  -> smooth scroller (isFixed while the loader runs), WebGL sketches, navbarPos, Sticky,
//                   HorizontalScroll x2, roadmap, ticker (all immediate)
//  first frame   -> Revealer ScrollTrigger (created after Sticky/HorizontalScroll have sized their wrappers)
//  page +1000ms  -> SectionScale, CardsScale, SplitHeading, ScrollAnimations
//  footer +2000ms-> FallingLetters (plays while #letter-parent top < innerHeight/2)
//  loader end    -> hero intro (sectionAnimation(.home-1)), Butterfly onLoad, ss.isFixed = false
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { raf, delay } from './core.js'
import { SmoothScroll } from './smoothScroll.js'
import { ScrollAnimations, sectionAnimation, revertReveals } from './reveal.js'
import { sectionScale, cardsScale, splitHeading, sticky, horizontalScroll, roadmap, ticker, navbarPos } from './scrollFx.js'
import { createButterfly, createRevealer } from './gl.js'
import { fallingLetters } from './fallingLetters.js'

gsap.registerPlugin(ScrollTrigger)
if (import.meta.env.DEV) window.__ST = ScrollTrigger // debug handle for motion QA (dev only)

let butterfly = null
let introDone = false

export function initPage() {
  const ac = new AbortController()
  const { signal } = ac
  const d = [] // disposers, run in reverse
  const add = (fn) => fn && d.push(fn)
  const qa = (s) => [...document.querySelectorAll(s)]
  const sc = document.getElementById('scroll-container')
  document.documentElement.classList.add('js-anim')
  introDone = false

  // Smooth scroller (desktop). isFixed: true until the loader ends (or immediately false if the loader is disabled).
  const ss = new SmoothScroll({ isFixed: true })
  window.ss = ss
  add(() => { ss.destroy(); if (window.ss === ss) delete window.ss })

  const onPopup = (e) => { if (window.ss) window.ss.isFixed = !!e.detail?.open }
  window.addEventListener('ff:popup', onPopup)
  add(() => window.removeEventListener('ff:popup', onPopup))

  // The original reloads on every resize above 768px so every measured layout is rebuilt from scratch.
  const onResize = () => { if (window.innerWidth > 768) window.location.reload() }
  window.addEventListener('resize', onResize)
  add(() => window.removeEventListener('resize', onResize))

  butterfly = createButterfly()
  window.scetch = butterfly.sketch
  add(() => { butterfly?.destroy(); butterfly = null; delete window.scetch })

  add(navbarPos())
  qa('.sticky-wrapper').forEach((el) => add(sticky(el)))
  // Roadmap first: in the original the (child) roadmap component sets its inline width on mount before the parent
  // HorizontalScroll measures scrollWidth (2342px wrapper at 1440x900, not 2343px).
  const rm = document.querySelector('.home-10__roadmap')
  if (rm) add(roadmap(rm))
  qa('.wrapper').forEach((el) => add(horizontalScroll(el)))
  const tk = document.querySelector('.ticker__items')
  if (tk) add(ticker(tk, { duration: 80, direction: 1 }))

  let revealer = null
  const rid = requestAnimationFrame(() => requestAnimationFrame(() => {
    if (signal.aborted) return
    revealer = createRevealer()
    window.scetch2 = revealer.sketch
  }))
  add(() => { cancelAnimationFrame(rid); revealer?.destroy(); revealer = null; delete window.scetch2 })

  ;(async () => {
    await delay(1000, signal)
    add(sectionScale(qa('[data-section-scale]')))
    add(cardsScale(qa('[data-cards-scale]')))
    add(splitHeading(document.querySelector('.home-5__h')))
    const sa = new ScrollAnimations()
    add(() => sa.destroy())
  })().catch(() => {})

  ;(async () => {
    await delay(2000, signal)
    const parent = document.getElementById('letter-parent')
    if (!parent) return
    const fl = fallingLetters(parent)
    let playing = false
    const check = () => {
      if (parent.getBoundingClientRect().top < window.innerHeight / 2) { if (!playing) fl.play(); playing = true }
      else { if (playing) fl.stop(); playing = false }
    }
    raf.on(check)
    add(() => { raf.off(check); fl.destroy() })
  })().catch(() => {})

  return () => {
    ac.abort()
    while (d.length) { try { d.pop()() } catch (e) { console.warn(e) } }
    revertReveals(document.querySelector('main') || document)
    document.querySelectorAll('.activated').forEach((el) => el.classList.remove('activated'))
    qa('[data-section-scale], [data-cards-scale]').forEach((el) => { el.style.removeProperty('transform'); el.style.removeProperty('opacity'); el.style.removeProperty('translate'); el.style.removeProperty('rotate'); el.style.removeProperty('scale') })
    sc && (sc.scrollTop = 0)
  }
}

// Called when the loader timeline finishes (or right away when the loader is disabled).
export function startIntro() {
  if (introDone) return
  introDone = true
  const hero = document.querySelector('.home-1')
  if (hero) sectionAnimation(hero)
  butterfly?.fig?.onLoad()
  if (window.ss) window.ss.isFixed = false
}
