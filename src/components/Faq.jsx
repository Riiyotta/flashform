import { useRef, useState } from 'react'
import { AccordionArrow } from './icons.jsx'

const QA = [
  ['Is it form builder?', 'No, this is the web service that provide an API for implementing backend function to HTML form. It just send all data from your website form to convinient messengers or other chanels.'],
  ['What I must to do for implementing this to my website form?', 'Just follow these three steps:<br/>1. Create an copy your personal ID link.<br/>2. Paste it in your HTML form or in fetch as URL.<br/>3. Choose where you want to send data from form.<br/>4. Done! The data from your website form is almost here.'],
  ['Are the instructions different for integration with different messengers?', 'Yes, there are certain differences in the instructions for each messenger. But we have done everything so that you as a user do not experience any inconvenience:)'],
  ['Is FlashForm a paid product?', 'You can use a free account if it is sufficient for your purposes. But if you need more integrations, then for $10 per month you get unlimited access to integrations.'],
]

// spec §7.3. Multiple items may be open; `--h` = scrollHeight * 0.01px so calc(var(--h)*100) = full height.
function AccordionItem({ num, q, a }) {
  const [opened, setOpened] = useState(false)
  const [h, setH] = useState(null)
  const textRef = useRef(null)
  const toggle = () => {
    setH(textRef.current.scrollHeight * 0.01)
    setOpened((o) => !o)
  }
  return (
    <div className={`accordion__item${opened ? ' opened' : ''}`} onClick={toggle}>
      <div className="accordion__overlay" />
      <div className="grid accordion__cols">
        <div className="h3 accordion__num">{String(num).padStart(2, '0')}</div>
        <h3 className="h4 accordion__h4">{q}</h3>
        <div className="accordion__arrow"><AccordionArrow /></div>
      </div>
      <div
        ref={textRef}
        className="accordion__text"
        style={h != null ? { '--h': `${h}px` } : undefined}
        dangerouslySetInnerHTML={{ __html: a }}
      />
      <div className="h-line accordion__line" />
    </div>
  )
}

export default function Faq() {
  return (
    <section id="faq" className="section home-11">
      <div className="container">
        <h2 className="h1 home-11__h">F<span className="h1--i">A</span>Q</h2>
        <div className="accordion">
          <div className="accordion__items">
            <div className="h-line accordion__line" />
            {QA.map(([q, a], i) => <AccordionItem key={i} num={i + 1} q={q} a={a} />)}
          </div>
        </div>
      </div>
    </section>
  )
}
