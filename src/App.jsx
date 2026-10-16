import { useEffect, useLayoutEffect, useState } from 'react'
import { initPage, startIntro } from './anim/index.js'
import { mountDelay } from './anim/core.js'
import { UIProvider } from './context.jsx'
import Loader from './components/Loader.jsx'
import AppLoader from './components/AppLoader.jsx'
import Navbar from './components/Navbar.jsx'
import Hero from './components/Hero.jsx'
import Meaning from './components/Meaning.jsx'
import Purpose from './components/Purpose.jsx'
import Why from './components/Why.jsx'
import Integration from './components/Integration.jsx'
import Messengers from './components/Messengers.jsx'
import Benefits from './components/Benefits.jsx'
import Relief from './components/Relief.jsx'
import Problems from './components/Problems.jsx'
import Roadmap from './components/Roadmap.jsx'
import Faq from './components/Faq.jsx'
import Footer from './components/Footer.jsx'
import BetaPopup from './components/BetaPopup.jsx'
import Toasts from './components/Toasts.jsx'

// Intro loader (spec §5.1). Its timeline lives in src/anim/loader.js and calls onComplete at ~6.2s.
export const LOADER_ENABLED = true

export default function App() {
  const [loaderVisible, setLoaderVisible] = useState(LOADER_ENABLED)

  // spec §0.6: --vh / --vw on <body>, updated on resize (CSS defaults: 100vh / 100vw).
  useLayoutEffect(() => {
    const set = () => {
      document.body.style.setProperty('--vh', `${window.innerHeight}px`)
      document.body.style.setProperty('--vw', `${window.innerWidth}px`)
    }
    set()
    window.addEventListener('resize', set)
    return () => window.removeEventListener('resize', set)
  }, [])

  // All page motion (smooth scroll, reveals, ScrollTriggers, WebGL, physics). StrictMode-safe: full revert on cleanup.
  // Deferred to MOUNT_AT like the original's post-hydration layout/page onMounted (see src/anim/core.js).
  useEffect(() => {
    let cleanup
    const t = setTimeout(() => {
      cleanup = initPage()
      if (!LOADER_ENABLED) startIntro()
    }, mountDelay())
    return () => { clearTimeout(t); cleanup?.() }
  }, [])

  const onLoaderComplete = () => {
    setLoaderVisible(false)
    startIntro()
  }

  return (
    <UIProvider>
      <div className="app-grid container grid">
        {Array.from({ length: 12 }, (_, i) => <div key={i} className="app-grid__col" />)}
      </div>
      {loaderVisible && <Loader onComplete={onLoaderComplete} />}
      <AppLoader />
      <div id="scroll-container">
        <div data-page="">
          <main>
            <Navbar />
            <Hero />
            <div className="over-revealer home-2-over-revealer">
              <Meaning />
              <Purpose />
              <Why />
              <Integration />
            </div>
            <div className="over-revealer home-6-over-revealer">
              <Messengers />
              <Benefits />
              <Relief />
              <Problems />
              <Roadmap />
              <Faq />
            </div>
          </main>
          <Footer />
          <div className="new-form"><BetaPopup /></div>
        </div>
        {/* Custom scrollbar (spec §0.6) is created/removed by SmoothScroll (src/anim/smoothScroll.js), desktop only. */}
      </div>
      <Toasts />
    </UIProvider>
  )
}
