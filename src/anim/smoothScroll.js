// Port of the original custom smooth scroller (window.ss, index-7e7e3586.mjs):
// virtual-scroll wheel deltas -> clamp ±120 -> * stepSize .8 -> target; each rAF current = lerp(current, target, .07),
// rounded to .01 and written to #scroll-container.scrollTop. Desktop only (innerWidth > 1060).
// Includes the custom scrollbar (thumb height vh*(vh/scrollHeight), inactivity 1s, drag + track click).
import { raf, clamp, lerp } from './core.js'

const KEYS = { UP: 'ArrowUp', DOWN: 'ArrowDown', TAB: 'Tab', PAGEUP: 'PageUp', PAGEDOWN: 'PageDown', HOME: 'Home', END: 'End' }
const isFirefox = typeof navigator !== 'undefined' && navigator.userAgent.indexOf('Firefox') > -1

// virtual-scroll (as bundled): binds BOTH `wheel` and `mousewheel` when the browser supports them (Chrome does),
// so each physical wheel event notifies twice — kept verbatim because it defines the real step distance.
class VirtualScroll {
  constructor(el, cb, { firefoxMultiplier = 40, mouseMultiplier = 1, passive = false } = {}) {
    this.el = el
    this.cb = cb
    this.opts = { firefoxMultiplier, mouseMultiplier }
    this.listenerOptions = { passive }
    this.onWheel = (e) => {
      let dy = e.wheelDeltaY || -1 * e.deltaY
      let dx = e.wheelDeltaX || -1 * e.deltaX
      if (isFirefox && e.deltaMode === 1) { dx *= this.opts.firefoxMultiplier; dy *= this.opts.firefoxMultiplier }
      this.cb({ deltaX: dx * this.opts.mouseMultiplier, deltaY: dy * this.opts.mouseMultiplier, originalEvent: e })
    }
    this.onMouseWheel = (e) => {
      this.cb({ deltaX: e.wheelDeltaX ? e.wheelDeltaX : 0, deltaY: e.wheelDeltaY ? e.wheelDeltaY : e.wheelDelta, originalEvent: e })
    }
    this.hasWheel = 'onwheel' in document
    this.hasMouseWheel = 'onmousewheel' in document
    if (this.hasWheel) el.addEventListener('wheel', this.onWheel, this.listenerOptions)
    if (this.hasMouseWheel) el.addEventListener('mousewheel', this.onMouseWheel, this.listenerOptions)
  }
  destroy() {
    this.el.removeEventListener('wheel', this.onWheel)
    this.el.removeEventListener('mousewheel', this.onMouseWheel)
  }
}

class Scrollbar {
  constructor(el, state) {
    this.$el = el
    this.state = state
    // Original CreateScrollbar: built on init (innerWidth > breakpoint only) and appended to #scroll-container.
    this.$scrollbar = document.createElement('div')
    this.$scrollbar.innerHTML = '<span class="scrollbar__thumb"></span>'
    this.$scrollbar.classList.add('scrollbar')
    el.appendChild(this.$scrollbar)
    this.$thumb = this.$scrollbar.querySelector('.scrollbar__thumb')
    this.timer = 0
    this.move = this.move.bind(this)
    this.reset = () => { this.timer = 0 }
    this.ticker = setInterval(() => { this.timer++ }, 1000)
    this.interval = setInterval(() => {
      if (this.timer >= 1) this.$thumb.classList.remove('scrolling')
      else this.$thumb.classList.add('scrolling')
    }, 120)
    this.$scrollbar.addEventListener('mouseenter', this.reset)
    raf.on(this.move)
    this.initDrag()
  }
  setHeight() {
    this.height = this.$el.scrollHeight
    const vh = window.innerHeight
    let h = vh * (vh / this.height)
    if (this.height === vh) h = 0
    this.$thumb.style.height = h + 'px'
  }
  move() {
    this.$scrollbar.classList.toggle('hidden', !!this.state.isFixed)
    if (this.state.scrolling) {
      const ch = document.documentElement.clientHeight
      this.$thumb.classList.add('scrolling')
      const p = (100 * this.state.scrolled) / (this.height - ch)
      this.$thumb.style.top = p.toFixed(2) + '%'
      this.$thumb.style.transform = `translateY(-${p.toFixed(2)}%)`
    }
    this.setHeight()
  }
  initDrag() {
    const sizes = () => { const h = this.$el.scrollHeight; return { height: h, max: h - window.innerHeight } }
    const compute = (y) => {
      const l = this.$scrollbar.offsetHeight
      this.state.scrollbar = true
      const s = sizes()
      this.state.target = clamp(s.height * (y / l), 0, s.max)
      setTimeout(() => { this.state.scrollbar = false }, 0)
    }
    this.update = (e) => {
      if (this.state.isFixed) return
      let y
      if ('ontouchstart' in document.documentElement) {
        const r = e.target?.getBoundingClientRect()
        y = e.pageY - r.top
      } else y = e.clientY
      compute(y)
    }
    this.start = () => {
      ;['mousemove', 'touchmove'].forEach((ev) => document.documentElement.addEventListener(ev, this.update))
      this.$thumb.classList.add('active')
    }
    this.end = () => {
      this.state.scrollbar = false
      this.$thumb.classList.remove('active')
      ;['mousemove', 'touchmove'].forEach((ev) => document.documentElement.removeEventListener(ev, this.update))
    }
    ;['mousedown', 'touchstart'].forEach((ev) => this.$scrollbar.addEventListener(ev, this.start, { passive: false }))
    ;['mouseup', 'touchend'].forEach((ev) => document.documentElement.addEventListener(ev, this.end))
    if (screen.width > 960) this.$scrollbar.addEventListener('click', this.update)
  }
  destroy() {
    raf.off(this.move)
    clearInterval(this.ticker)
    clearInterval(this.interval)
    this.$scrollbar.removeEventListener('mouseenter', this.reset)
    ;['mousedown', 'touchstart'].forEach((ev) => this.$scrollbar.removeEventListener(ev, this.start))
    ;['mouseup', 'touchend'].forEach((ev) => document.documentElement.removeEventListener(ev, this.end))
    ;['mousemove', 'touchmove'].forEach((ev) => document.documentElement.removeEventListener(ev, this.update))
    this.$scrollbar.removeEventListener('click', this.update)
    this.$scrollbar.remove()
  }
}

export class SmoothScroll {
  constructor(opts = {}) {
    this.opts = {
      el: document.querySelector('#scroll-container'),
      friction: 0.07, stepSize: 0.8, breakpoint: 1060, clampScrollDelta: 120, scrollbar: true, useKeyboard: true, isFixed: true,
      ...opts,
    }
    this.state = { scrolling: false, scrolled: 0, scrollbar: false, target: 0, isFixed: false }
    this.current = 0
    this.min = 0
    this.isInited = false
    this.animate = this.animate.bind(this)
    this.onKeyDown = this.onKeyDown.bind(this)
    this.resize = this.resize.bind(this)
    // the original's own resize emitter is debounced by 2s
    this.onWinResize = () => { clearTimeout(this.rt); this.rt = setTimeout(this.resize, 2000) }
    window.addEventListener('resize', this.onWinResize)
    this.resize(true)
  }
  resize(first) {
    if (window.innerWidth <= this.opts.breakpoint) {
      if (this.isInited) this.destroyInner()
      this.isInited = false
    } else {
      if (!this.isInited) this.init()
      if (first !== true) this.isFixed = false
    }
  }
  init() {
    this.state.target = 0
    this.current = this.opts.el.scrollTop = 0
    this.max = this.maxValue
    this.vs = new VirtualScroll(this.opts.el, (e) => {
      if (!this.canScroll) return
      const d = clamp(e.deltaY, -this.opts.clampScrollDelta, this.opts.clampScrollDelta)
      this.state.target -= d * this.opts.stepSize
      this.state.target = clamp(this.state.target, this.min, this.max)
    })
    if (this.opts.useKeyboard) window.addEventListener('keydown', this.onKeyDown, false)
    raf.on(this.animate)
    if (this.opts.scrollbar) this.scrollbar = new Scrollbar(this.opts.el, this.state)
    this.isInited = true
    this.isFixed = !!this.opts.isFixed
    document.documentElement.classList.add('has-ss')
  }
  get maxValue() { return this.opts.el.scrollHeight - window.innerHeight }
  get canScroll() { return !this.isFixed && this.opts.el.scrollHeight > window.innerHeight }
  get isFixed() { return this.state.isFixed }
  set isFixed(v) {
    this.state.isFixed = v
    this.opts.el.classList.toggle('e-fixed', !!v)
  }
  detectScrolling() {
    const d = Math.abs(Math.round(this.state.target) - Math.round(this.current))
    this.state.scrolling = !!(d >= 1 || this.state.scrollbar)
  }
  animate() {
    this.detectScrolling()
    this.max = this.maxValue
    if (this.state.scrolling) {
      this.current = lerp(this.current, this.state.target, this.opts.friction)
      this.current = Math.round(100 * this.current) / 100
      this.opts.el.scrollTop = this.current
      this.state.scrolled = this.current
    }
  }
  onKeyDown(e) {
    if (!this.canScroll) return
    switch (e.key) {
      case KEYS.TAB: this.state.target = document.activeElement.getBoundingClientRect().y; break
      case KEYS.UP: this.state.target -= 240; break
      case KEYS.DOWN: this.state.target += 240; break
      case KEYS.PAGEUP: this.state.target -= window.innerHeight; break
      case KEYS.PAGEDOWN: this.state.target += window.innerHeight; break
      case KEYS.HOME: this.state.target = this.min; break
      case KEYS.END: this.state.target = this.max; break
      default: return
    }
    this.state.target = clamp(this.state.target, this.min, this.max)
  }
  destroyInner() {
    raf.off(this.animate)
    this.vs?.destroy()
    this.scrollbar?.destroy()
    this.scrollbar = null
    window.removeEventListener('keydown', this.onKeyDown)
    this.isFixed = false
    document.documentElement.classList.remove('has-ss')
  }
  destroy() {
    clearTimeout(this.rt)
    window.removeEventListener('resize', this.onWinResize)
    if (this.isInited) this.destroyInner()
    this.isInited = false
  }
}
