// Scroll-driven modules, ported 1:1 from the original chunks (SectionScale, CardsScale, SplitHeading, Sticky,
// HorizontalScroll, roadmap component, Ticker, navbarPos). ScrollTrigger uses `scroller: #scroll-container`
// directly, exactly like the original: the smooth scroller writes real scrollTop, so no scrollerProxy is needed.
//
// NOTE on eases: the original passes ease "linear.none", which is NOT a registered GSAP ease name, so GSAP falls
// back to its default `power1.out`. The live measurements (SectionScale, CardsScale) fit power1.out over the
// trigger range exactly, so the same string is kept on purpose.
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import SplitType from 'split-type'
import { raf, resize, clamp, matrixTransform, $sc } from './core.js'

gsap.registerPlugin(ScrollTrigger)
const ORIGINAL_EASE = 'linear.none' // resolves to GSAP default power1.out, as on the live site

// §5.4 SectionScale: start "top-=100%" (100% of the element's own height), end "+=innerHeight", scrub .1
export function sectionScale(els, breakpoint = 960) {
  const tls = []
  if (window.innerWidth > breakpoint) {
    els.forEach((el) => {
      tls.push(gsap.timeline({
        scrollTrigger: { trigger: el, pin: false, start: 'top-=100%', end: `+=${window.innerHeight}`, scroller: '#scroll-container', scrub: 0.1 },
      }).to(el, { scale: 1, opacity: 1, ease: ORIGINAL_EASE }))
    })
  }
  return () => tls.forEach((tl) => { tl.scrollTrigger?.kill(); tl.kill() })
}

// §5.8 CardsScale: inline translateY(17*i*2.4px) scaleY(1+i*.07), ScrollTrigger end "+=bottom" (original literal)
export function cardsScale(els, breakpoint = 960) {
  const tls = []
  if (window.innerWidth > breakpoint) {
    els.forEach((el, i) => {
      el.style.transform = `translateY(${17 * (i * 2.4)}px) scaleY(${1 + i * 0.07})`
      tls.push(gsap.timeline({
        scrollTrigger: { trigger: el, pin: false, end: '+=bottom', scroller: '#scroll-container', scrub: 0.1 },
      }).to(el, { y: 0, scaleY: 1, ease: ORIGINAL_EASE }))
    })
  }
  return () => tls.forEach((tl) => { tl.scrollTrigger?.kill(); tl.kill() })
}

// §5.5 SplitHeading on .home-5__h: SplitType words+chars, one scrubbed ScrollTrigger per char
export function splitHeading(el) {
  if (!el || el.classList.contains('splitted')) return () => {}
  const text = new SplitType(el, { types: 'words, chars', tagName: 'span' })
  el.classList.add('splitted')
  let tls = []
  const animate = () => {
    if (window.innerWidth < 960) return
    text.chars.forEach((c, i) => {
      const d = i > 1 ? 0.02 * i : 0
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: c, pin: false,
          start: `left +=${window.innerWidth / 2}`,
          end: `right right-=${c.getBoundingClientRect().right}px`,
          scrub: 0.01, scroller: $sc(),
        },
      })
      tl.to(c, { y: 0, opacity: 1, ease: 'back.out(1.2)', delay: d })
      tls.push(tl)
    })
  }
  resize.on(animate)
  return () => {
    resize.off(animate)
    tls.forEach((tl) => { tl.scrollTrigger?.kill(); tl.kill() })
    tls = []
    gsap.killTweensOf(text.chars || [])
    text.revert()
    el.classList.remove('splitted')
  }
}

// §5.9 Sticky inner scroll for rounded sections
export function sticky(stickyWrapper) {
  const $el = stickyWrapper.querySelector('[data-section-sticky-scroller]')
  const $wrapper = stickyWrapper.querySelector('[data-section-sticky]')
  const $container = $wrapper.parentElement
  const animate = () => {
    const elHeight = $el.getBoundingClientRect().height
    if (elHeight < window.innerHeight) { $wrapper.classList.remove('sticky-activated'); return }
    $wrapper.classList.add('sticky-activated')
    $container.style.height = elHeight + 'px'
    const offset = clamp($container.getBoundingClientRect().top, 0, -(elHeight - window.innerHeight))
    $el.style.transform = matrixTransform({ move: { y: offset } })
    $el.style.willChange = 'transform'
  }
  raf.on(animate)
  return () => {
    raf.off(animate)
    $wrapper.classList.remove('sticky-activated')
    $container.style.removeProperty('height')
    $el.style.removeProperty('transform')
    $el.style.removeProperty('will-change')
  }
}

// §5.5 HorizontalScroll: wrapper height = scrollWidth - (innerWidth - innerHeight); translateX = clamp(top, -h+vh, 0)
// The original gates on `screen.width > 1060`; innerWidth is also checked so a narrow desktop window (where the CSS
// un-sticks .scroller) does not get a 6000px empty wrapper.
export function horizontalScroll(container) {
  const $container = container
  const $el = container.querySelector('.scroller-el')
  const scrollHeight = () => $el.scrollWidth - (window.innerWidth - window.innerHeight)
  const setHeight = () => {
    const h = scrollHeight()
    $container.style.height = h + 'px'
    $container.parentElement.style.setProperty('--hh', h + 'px')
  }
  const inView = () => { const r = $container.getBoundingClientRect(); return r.top <= window.innerHeight && r.top >= -r.height }
  const animate = () => {
    if (!inView()) return
    setHeight()
    const offset = clamp($container.getBoundingClientRect().top, -scrollHeight() + window.innerHeight, 0)
    $el.style.transform = matrixTransform({ move: { x: offset } })
    $el.style.setProperty('--t', offset)
    $el.style.willChange = 'transform'
  }
  let on = false
  const onResize = () => {
    if (screen.width > 1060 && window.innerWidth > 1060) { setHeight(); if (!on) { raf.on(animate); on = true } }
    else { if (on) { raf.off(animate); on = false } $container.style.removeProperty('height'); $el.style.removeProperty('transform') }
  }
  resize.on(onResize)
  return () => {
    resize.off(onResize)
    raf.off(animate)
    $container.style.removeProperty('height')
    $container.parentElement.style.removeProperty('--hh')
    $el.style.removeProperty('transform')
    $el.style.removeProperty('--t')
    $el.style.removeProperty('will-change')
  }
}

// §5.5 Roadmap: inline width from the path's rendered width, stroke-dash draw, .is-visible at -y >= 8 / 30 / 52
export function roadmap(el) {
  const path = el.querySelector('path')
  const items = [...el.querySelectorAll('.roadmap__item')]
  const wrapper = el.closest('.wrapper')
  const onResize = () => { el.style.width = path.getBoundingClientRect().width + 'px' }
  resize.on(onResize)
  const L = path.getTotalLength()
  path.style.strokeDasharray = L + 'px'
  path.style.strokeDashoffset = L + 'px'
  const inView = () => { const d = el.getBoundingClientRect(); return d.top <= window.innerHeight && d.top >= -d.height }
  const frame = () => {
    if (!inView()) return
    const wr = wrapper.getBoundingClientRect()
    const y = (wr.top / wr.height) * 100
    const m = L + (y * L) / 95
    items[0].classList.toggle('is-visible', -y >= 8)
    items[1].classList.toggle('is-visible', -y >= 30)
    items[2].classList.toggle('is-visible', -y >= 52)
    path.style.strokeDashoffset = clamp(m - window.innerHeight, 0, L + window.innerHeight) + 'px'
  }
  raf.on(frame)
  return () => {
    resize.off(onResize)
    raf.off(frame)
    el.style.removeProperty('width')
    path.style.removeProperty('stroke-dasharray')
    path.style.removeProperty('stroke-dashoffset')
    items.forEach((i) => i.classList.remove('is-visible'))
  }
}

// §5.10 Ticker (duration 80, direction 1)
export function ticker($el, { duration = 80, direction = 1 } = {}) {
  const sc = $sc()
  let time = 0, targetY = 0, directionResult = 1, top, currentTop
  const isScrolling = () => window.ss?.state?.scrolling ?? false
  const velocity = () => (isScrolling() ? sc.scrollTop - (window.ss?.state?.target ?? 0) : 0)
  const getDirection = () => {
    if (top < currentTop) directionResult = -1
    if (top > currentTop) directionResult = 1
    return directionResult * direction
  }
  const calculate = () => {
    const w = $el.getBoundingClientRect().width
    const t = time / 60
    if (t > duration) time = 0
    if (-t > duration) time = -(duration / 2) * 60
    targetY = w * (t / duration)
    let s = (targetY / w) * 100
    if (s <= -50) { s = 0; targetY = 0; time = 0 }
    if (s > 0) { s = -50; targetY = -w / 2; time = -(duration / 2) * 60 }
  }
  const animate = () => {
    top = -sc.scrollTop
    time += getDirection() + (velocity() / 100) * direction
    calculate()
    $el.style.transform = matrixTransform({ move: { x: targetY } })
    $el.style.willChange = 'transform'
    $el.style.setProperty('--dir', getDirection())
    currentTop = -sc.scrollTop
  }
  raf.on(animate)
  return () => { raf.off(animate); $el.style.removeProperty('transform'); $el.style.removeProperty('will-change'); $el.style.removeProperty('--dir') }
}

// §1.1 navbarPos: body.nav-hidden on scroll down, removed on scroll up; while hidden, mouse screenY <= 300 reveals
export function navbarPos() {
  const sc = $sc()
  let hovered = false, scrollPos = 0, top = 0
  const mouseFunc = (e) => {
    if (e.screenY <= 300) { document.body.classList.remove('nav-hidden'); hovered = true }
    else { hovered = false; document.body.classList.add('nav-hidden') }
  }
  const add = () => { document.body.classList.remove('nav-hidden'); document.removeEventListener('mousemove', mouseFunc) }
  const remove = () => { document.body.classList.add('nav-hidden'); document.addEventListener('mousemove', mouseFunc) }
  const scrollNav = () => {
    top = -sc.scrollTop
    if (hovered) return
    const isVisible = top > scrollPos // original also ORs window.smoothScroll?.isFixed, which is never defined
    const isHidden = top < scrollPos && scrollPos < 0 && -top >= 0
    if (isVisible) add()
    if (isHidden) remove()
    scrollPos = -sc.scrollTop
  }
  raf.on(scrollNav)
  return () => { raf.off(scrollNav); document.removeEventListener('mousemove', mouseFunc); document.body.classList.remove('nav-hidden') }
}

// §1.1 anchor click: el.top + scrollTop + innerHeight*.3, 1s (gsap default ease power1.out)
export function anchorScroll(href) {
  const target = href && document.querySelector(href)
  if (!target) return
  const sc = $sc()
  const y = target.getBoundingClientRect().top + sc.scrollTop + window.innerHeight * 0.3
  // Original: innerWidth >= 1024 tweens ss.state.target; below that tweens scrollTop. ss only runs above 1060, so the
  // smooth-scroller branch is used whenever it is actually active (avoids a dead zone at 1024–1060).
  if (window.ss?.isInited) gsap.to(window.ss.state, { duration: 1, target: y, overwrite: true })
  else gsap.to(sc, { duration: 1, scrollTop: y })
}
