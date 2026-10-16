// Shared primitives ported from the original bundle (entry-*.mjs / @emotionagency utils).
// One rAF loop for every per-frame module (same as the original `raf`), a resize emitter whose `on()`
// fires the callback immediately, clamp/lerp, delayPromise and the matrix3d string builder.

class RAF {
  constructor() {
    this.cbs = []
    this.id = 0
    this.loop = this.loop.bind(this)
  }
  on(cb) {
    this.cbs.push(cb)
    if (!this.id) this.id = requestAnimationFrame(this.loop)
  }
  off(cb) {
    this.cbs = this.cbs.filter((c) => c !== cb)
    if (!this.cbs.length && this.id) { cancelAnimationFrame(this.id); this.id = 0 }
  }
  loop() {
    this.cbs.slice().forEach((cb) => cb())
    this.id = this.cbs.length ? requestAnimationFrame(this.loop) : 0
  }
}
export const raf = new RAF()

class Resize {
  constructor() {
    this.cbs = []
    this.handler = () => this.cbs.slice().forEach((cb) => cb())
    this.bound = false
  }
  on(cb) {
    cb()
    this.cbs.push(cb)
    if (!this.bound) { window.addEventListener('resize', this.handler); this.bound = true }
  }
  off(cb) {
    this.cbs = this.cbs.filter((c) => c !== cb)
    if (!this.cbs.length && this.bound) { window.removeEventListener('resize', this.handler); this.bound = false }
  }
}
export const resize = new Resize()

export const lerp = (a, b, t) => a * (1 - t) + b * t
export const clamp = (v, a, b) => Math.max(Math.min(v, Math.max(a, b)), Math.min(a, b))

// Cancellable delay so StrictMode unmounts can abort pending async chains.
export const delay = (ms, signal) => new Promise((res, rej) => {
  const t = setTimeout(res, ms)
  signal?.addEventListener('abort', () => { clearTimeout(t); rej(new DOMException('aborted', 'AbortError')) }, { once: true })
})

export const matrixTransform = ({ scale = { x: 1, y: 1 }, move = { x: 0, y: 0, z: 0 } } = {}) =>
  `matrix3d(${scale.x ?? 1},0,0,0,0,${scale.y ?? 1},0,0,0,0,1,0,${move.x ?? 0},${move.y ?? 0},${move.z ?? 0},1)`

// The original is Nuxt SSR: the loader markup paints from server HTML, but every onMounted (loader timeline, ss,
// ticker, page timers) only runs after the entry bundles hydrate and the loader's three dynamic import()s resolve,
// measured at ~570-850ms after navigation start (loader removed at mount + 5.4s = ~6.0-6.25s). The clone mounts at
// ~110ms, so all mount-time motion is deferred to MOUNT_AT ms after navigation start (performance.timeOrigin).
export const MOUNT_AT = 800
export const mountDelay = () => Math.max(0, MOUNT_AT - performance.now())

export const $sc = () => document.getElementById('scroll-container')
