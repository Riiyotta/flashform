// §5.12 Footer physics letters, ported from FallingLetters-*.mjs (matter-js 0.18.0).
import Matter from 'matter-js'
import { clamp } from './core.js'

const TABLE = [
  { text: 's', sizes: { w: 210, h: 286 } }, { text: 'T', sizes: { w: 217, h: 280 } }, { text: 'A', sizes: { w: 255, h: 280 } },
  { text: 'Y', sizes: { w: 247, h: 281 } }, { text: 'I', sizes: { w: 35, h: 280 } }, { text: 'N', sizes: { w: 217, h: 280 } },
  { text: 'T', sizes: { w: 217, h: 280 } }, { text: 'O', sizes: { w: 268, h: 286 } }, { text: 'U', sizes: { w: 215, h: 283 } },
  { text: 'C', sizes: { w: 252, h: 286 } }, { text: 'H', sizes: { w: 215, h: 281 } },
]
const fluid = (max, min) => min + (max - min) * ((window.innerWidth - 375) / (1440 - 375))

export function fallingLetters(parent) {
  const { Engine, Render, Runner, MouseConstraint, Mouse, World, Bodies } = Matter
  let W = parent.offsetWidth
  let H = parent.offsetHeight
  const R = 2
  let dropped = false
  const timers = []
  const engine = Engine.create()
  const world = engine.world
  const render = Render.create({ element: parent, engine, options: { width: W, height: H, pixelRatio: 1, background: '#111606', wireframes: false } })
  const wallOpts = { render: { fillStyle: '#ffffff', visible: false }, isStatic: true }
  const u = 160
  World.add(world, [
    Bodies.rectangle(0, H + u / 2, W * R, u, wallOpts),
    Bodies.rectangle(-u / 2, -H, u, H * R + u + H * R, wallOpts),
    Bodies.rectangle(W + u / 2, -H, u, H * R + u + H * R, wallOpts),
    Bodies.rectangle(0, -H, W * R, u, wallOpts),
  ])
  let g = fluid(0.6, 0.2)
  const drop = (word) => {
    word.toUpperCase().split('').forEach((ch, i) => {
      const L = TABLE.find((l) => l.text.toUpperCase() === ch)
      let x = L.sizes.w * g + L.sizes.w * g * TABLE.findIndex((l) => l.text.toUpperCase() === ch)
      x = clamp(x, L.sizes.w * g, W)
      const body = Bodies.rectangle(x, -u, L.sizes.w * g, L.sizes.h * g, {
        isSleeping: false, restitution: 0.07, frictionAir: 1e-4, velocity: { x: 0, y: 0 }, angle: Math.random() * 0.5,
        render: { sprite: { texture: `/assets/letters/${L.text}.svg`, xScale: g, yScale: g } },
      })
      timers.push(setTimeout(() => World.add(world, body), i * 400))
    })
  }
  const mouse = Mouse.create(render.canvas)
  const mc = MouseConstraint.create(engine, { mouse, constraint: { stiffness: 0.02, angularStiffness: 0.02, render: { visible: false } } })
  World.add(world, mc)
  render.mouse = mouse
  // matter's Mouse blocks page wheel over the canvas; the original keeps those listeners (wheel still reaches the
  // smooth scroller because it listens on #scroll-container and preventDefault does not stop propagation).
  Render.run(render)
  const runner = Runner.create()
  Runner.run(runner, engine)

  const onResize = () => {
    W = parent.offsetWidth; H = parent.offsetHeight
    render.bounds.max.x = W; render.bounds.max.y = H
    render.options.width = W; render.options.height = H
    render.canvas.width = W; render.canvas.height = H
    g = fluid(0.6, 0.2)
  }
  window.addEventListener('resize', onResize)

  const later = (fn, ms) => timers.push(setTimeout(fn, ms))
  return {
    stop() { Render.stop(render); Runner.stop(runner) },
    play() {
      Render.run(render); Runner.run(runner, engine)
      if (!dropped) {
        drop('Stay')
        later(() => drop('In'), 2000)
        later(() => drop('Touch'), 3000)
        later(() => { drop('Stay'); later(() => drop('In'), 2000); later(() => drop('Touch'), 3000) }, 5000)
        dropped = true
      }
    },
    destroy() {
      timers.forEach(clearTimeout)
      window.removeEventListener('resize', onResize)
      // play() re-runs Render/Runner like the original (two loops share one frameRequestId), so stop on a few
      // consecutive frames to cancel every loop.
      let n = 0
      const kill = () => { Render.stop(render); Runner.stop(runner); if (++n < 4) requestAnimationFrame(kill) }
      kill()
      Mouse.clearSourceEvents?.(mouse)
      World.clear(world, false); Engine.clear(engine)
      render.canvas.remove()
      render.textures = {}
    },
  }
}
