import { useEffect, useRef } from 'react'
import { runLoader } from '../anim/loader.js'

// Intro loader markup, spec §5.1. Timeline: src/anim/loader.js (calls onComplete when finished so App unmounts it).
const WORD = 'Flashform ®'
const Item = ({ mod, h }) => (
  <div className={`loader__item${mod ? ` loader__item--${mod}` : ''}`} {...(h ? { 'data-a-h': '' } : { 'data-a-p': '' })}>{WORD}</div>
)

export default function Loader({ onComplete }) {
  const ref = useRef(null)
  const done = useRef(onComplete)
  done.current = onComplete
  useEffect(() => runLoader(ref.current, () => done.current()), [])
  return (
    <div className="loader" ref={ref}>
      <div className="container loader__container">
        <div className="loader__cols">
          <div className="loader__col loader__col--1">
            <Item mod="ct" /><Item /><Item mod="c" h /><Item /><Item mod="cb" />
          </div>
          <div className="loader__col loader__col--2"><Item /><Item /><Item /><Item /><Item /></div>
          <div className="loader__col loader__col--3"><Item /><Item /><Item mod="ec" /><Item /><Item /></div>
          <div className="loader__col loader__col--4"><Item /><Item /><Item /><Item /><Item /></div>
          <div className="loader__col loader__col--5"><Item /><Item /><Item /><Item /><Item /></div>
        </div>
      </div>
    </div>
  )
}
