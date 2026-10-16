// WebGL sketches ported from ButterflyScetch / app.modern Scetch + Figure + Butterfly + Revealers chunks, using OGL.
// Pixel-unit perspective camera: fov = 2*atan(h/2/800), z = 800, so a 1x1 plane scaled to an element's rect
// lands exactly on that element.
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Renderer, Camera, Transform, Mesh, Program, Plane, Vec2, Vec3, Color } from 'ogl'
import { raf, resize } from './core.js'
import baseVert1 from './shaders/base-vert-webgl1.glsl?raw'
import baseVert2 from './shaders/base-vert-webgl2.glsl?raw'
import coverPrefix from './shaders/base-vert-cover-prefix.glsl?raw'
import baseFrag1 from './shaders/base-frag-webgl1.glsl?raw'
import baseFrag2 from './shaders/base-frag-webgl2.glsl?raw'
import butterflyVert from './shaders/butterfly.vert.glsl?raw'
import butterflyFrag from './shaders/butterfly.frag.glsl?raw'
import revealerVert from './shaders/revealer.vert.glsl?raw'
import revealerFrag from './shaders/revealer.frag.glsl?raw'

gsap.registerPlugin(ScrollTrigger)

class Sketch {
  constructor(selector, { dpr = 2, premultipliedAlpha = true, near = 1, far = 1000, checkInView = true } = {}) {
    this.$container = document.querySelector(selector)
    this.opts = { near, far, checkInView }
    this.sizes = { w: window.innerWidth, h: window.innerHeight }
    this.figures = []
    this.scene = new Transform()
    this.renderer = new Renderer({ dpr, antialias: true, alpha: true, premultipliedAlpha, depth: true, stencil: false, autoClear: true, webgl: 2 })
    this.setupCamera()
    this.renderer.setSize(this.sizes.w, this.sizes.h)
    this.$container.appendChild(this.renderer.gl.canvas)
    this.animate = this.animate.bind(this)
    this.onResize = this.onResize.bind(this)
    raf.on(this.animate)
    window.addEventListener('resize', this.onResize)
  }
  setupCamera() {
    const fov = (180 * (2 * Math.atan(this.sizes.h / 2 / 800))) / Math.PI
    this.camera = new Camera(this.renderer.gl, { fov, aspect: this.sizes.w / this.sizes.h, near: this.opts.near, far: this.opts.far })
    this.camera.position.set(0, 0, 800)
    this.camera.lookAt([0, 0, 0])
  }
  onResize() {
    this.sizes = { w: window.innerWidth, h: window.innerHeight }
    const rz = this.camera.rotation.z
    this.setupCamera()
    this.camera.rotation.z = rz
    this.figures.forEach((f) => { f.camera = this.camera })
    this.camera.perspective({ aspect: this.sizes.w / this.sizes.h })
    this.renderer.setSize(this.sizes.w, this.sizes.h)
  }
  get inView() {
    const r = this.$container.getBoundingClientRect()
    return r.top <= window.innerHeight && r.top >= -r.height
  }
  add(FigureClass, el) {
    const f = new FigureClass({ el, scene: this.scene, renderer: this.renderer, camera: this.camera })
    this.figures.push(f)
    return f
  }
  animate() {
    if (this.opts.checkInView && !this.inView) return
    this.figures.forEach((f) => { f.setSizes(); f.resize(); f.update() })
    this.renderer.render({ scene: this.scene, camera: this.camera })
  }
  destroy() {
    raf.off(this.animate)
    window.removeEventListener('resize', this.onResize)
    this.figures.forEach((f) => f.destroy())
    this.figures = []
    const gl = this.renderer.gl
    gl.getExtension('WEBGL_lose_context')?.loseContext()
    gl.canvas.remove()
  }
}

// Figure base (Figure-*.mjs): plane fitted to `el`'s client rect every frame; cover state true (default) prefix.
class Figure {
  constructor({ el, scene, renderer, camera }) {
    this.$el = el
    this.scene = scene
    this.renderer = renderer
    this.gl = renderer.gl
    this.camera = camera
    this.sizes = new Vec2(0, 0)
    this.offset = new Vec2(0, 0)
    this.time = 0
    this.rendering = false
    this.$el.classList.add('js-hidden')
    this.geometry = new Plane(this.gl, { width: 1, height: 1, widthSegments: 1, heightSegments: 1 })
  }
  get rect() { return this.$el.getBoundingClientRect() }
  createMaterial({ uniforms, vertex, fragment, transparent = true }) {
    const r = this.rect
    const isGL2 = this.renderer.isWebgl2
    const base = { size: { value: new Vec2(r.width, r.height) }, cover: { value: new Vec2(0.5, 0.5) }, uTime: { value: 0 }, resolution: { value: new Vec2(0, 0) } }
    let v = coverPrefix + '\n' + (isGL2 ? baseVert2 : baseVert1) + '\n' + vertex
    if (isGL2) v = '#version 300 es\n' + v
    const f = (isGL2 ? baseFrag2 : baseFrag1) + '\n' + fragment
    this.material = new Program(this.gl, { vertex: v, fragment: f, uniforms: { ...base, ...uniforms }, transparent, cullFace: null, depthTest: false, depthWrite: false })
    this.mesh = new Mesh(this.gl, { geometry: this.geometry, program: this.material })
    this.rendering = true
    this.setSizes()
    this.mesh.position.set(this.offset.x, this.offset.y, 0)
    this.mesh.scale.set(this.sizes.x, this.sizes.y, this.sizes.x / 2)
    this.mesh.setParent(this.scene)
  }
  setSizes() {
    if (!this.rendering) return
    const { width, height, top, left } = this.rect
    this.sizes.set(width, height)
    this.offset.set(left - window.innerWidth / 2 + width / 2, window.innerHeight / 2 - top - height / 2)
  }
  resize() {
    if (!this.rendering) return
    this.mesh.position.set(this.offset.x, this.offset.y, 0)
    this.mesh.scale.set(this.sizes.x, this.sizes.y, 1)
    this.material.uniforms.size.value.set(this.sizes.x, this.sizes.y)
  }
  update() {
    if (!this.rendering) return
    this.time++
    this.material.uniforms.uTime.value = this.time
  }
  destroy() {
    this.$el.classList.remove('js-hidden')
    this.mesh?.setParent(null)
    this.geometry.remove()
    this.material?.remove()
  }
}

// §5.6 Butterfly flower
class Butterfly extends Figure {
  constructor(o) {
    super(o)
    this.mousePosition = { x: 0.5, y: 0.5 }
    this.start = Date.now()
    this.timeOffset = 0
    this.camX = 0
    this.camY = 0
    this.onMouseMove = this.onMouseMove.bind(this)
    // u_mousePosition: in the original the inertia objects are overwritten with plain numbers on the first frame, so
    // `new Vec2(x.value, y.value)` is Vec2(0, 0) on every frame — the shader always sees (0, 0) (3 petals, x1.5 light).
    this.createMaterial({
      uniforms: {
        u_color1: { value: new Vec3(165, 104, 62) },
        u_color2: { value: new Vec3(69, 114, 78) },
        u_time: { value: 0 },
        u_timeOffset: { value: 7.4 },
        u_mousePosition: { value: new Vec2(0, 0) },
      },
      vertex: butterflyVert,
      fragment: butterflyFrag,
      transparent: true,
    })
    this.scene.scale.set(2, 2, 2)
    this.camera.rotation.z = 0.5
    this.scene.scale.x = 0
    this.scene.scale.y = 0
  }
  onLoad() {
    this.tl = gsap.timeline({
      onComplete: () => {
        document.body.addEventListener('touchmove', this.onMouseMove)
        document.body.addEventListener('mousemove', this.onMouseMove)
      },
    })
    this.tl.to(this.camera.rotation, { z: 0, duration: 2, ease: 'back.inOut(2)' }, 0)
    this.tl.to(this.scene.scale, { x: 2, y: 2, duration: 1.5, ease: 'back.out(2)' }, 0)
  }
  onMouseMove(e) {
    const x = e.pageX ?? e.touches?.[0]?.pageX
    const y = e.pageY ?? e.touches?.[0]?.pageY
    this.mousePosition.x = x / window.innerWidth
    this.mousePosition.y = y / window.innerHeight
  }
  update() {
    super.update()
    const cam = this.camera
    if (this.mousePosition.x && cam.position.x !== undefined) this.camX = ((this.mousePosition.x - 0.5) * 20 - cam.position.x) * 0.05
    if (this.mousePosition.y && cam.position.y !== undefined) this.camY = ((this.mousePosition.y - 0.5) * 25 - cam.position.y) * 0.05
    const fixedTime = 1e-4 * (Date.now() - this.start)
    this.timeOffset += (Math.abs(this.camX) + Math.abs(this.camY)) / 30
    this.material.uniforms.u_time.value = fixedTime + this.timeOffset
    cam.rotation.z += this.camY / 400 + this.camX / 200
  }
  destroy() {
    this.tl?.kill()
    document.body.removeEventListener('touchmove', this.onMouseMove)
    document.body.removeEventListener('mousemove', this.onMouseMove)
    super.destroy()
  }
}

// §5.7 Revealer noise dissolve; ScrollTrigger on the parent (.home-5__sticky), start "top+=40%", end "+=innerHeight"
class Revealer extends Figure {
  constructor(o) {
    super(o)
    this.value = 0
    this.createMaterial({
      uniforms: { uColor1: { value: new Color('#FFFFFF') }, uColor2: { value: new Color('#000000') }, uClicked: { value: 0 } },
      vertex: revealerVert,
      fragment: revealerFrag,
    })
    this.tl = gsap.timeline({
      scrollTrigger: {
        trigger: this.$el.parentElement, pin: false, start: 'top+=40%', end: `+=${window.innerHeight}`,
        scroller: '#scroll-container', scrub: 0.1,
        onUpdate: (t) => { this.value = t.progress; this.$el.setAttribute('moved', t.progress) },
      },
    }).to(this.material.uniforms.uClicked, { value: 1, ease: 'linear.none' }) // resolves to power1.out like the original
  }
  destroy() {
    this.tl?.scrollTrigger?.kill()
    this.tl?.kill()
    this.$el.removeAttribute('moved')
    super.destroy()
  }
}

export function createButterfly() {
  const sketch = new Sketch('#gl', { dpr: window.devicePixelRatio, premultipliedAlpha: false, near: 1, far: 1000, checkInView: true })
  const fig = sketch.add(Butterfly, document.querySelector('.home-1__gl'))
  return { sketch, fig, destroy: () => sketch.destroy() }
}

export function createRevealer() {
  const sketch = new Sketch('#gl-2', { dpr: 1, premultipliedAlpha: false, near: 0.01, far: 1e4, checkInView: false })
  const fig = sketch.add(Revealer, document.querySelector('.home__revealer'))
  return { sketch, fig, destroy: () => sketch.destroy() }
}

export { resize }
