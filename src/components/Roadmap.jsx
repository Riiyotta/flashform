import { ArrowDownLarge, RoadmapCurve } from './icons.jsx'

const ITEMS = [
  ['jan', '19', '{Beta release}'],
  ['march', '03', '{Hopefully, a release}'],
  ['apr', '23', '{Add new messengers}'],
]

// spec §1.11 (display:none ≤1060 via CSS). Hooks: `.wrapper`/`.scroller`/`.scroller-el` horizontal scroll,
// curve `path` stroke-dash drawing, `.roadmap__item` gets `.is-visible`.
// Static fallback: curve fully drawn, items visible.
export default function Roadmap() {
  return (
    <section id="roadmap" className="section home-10" data-in-view="0.4">
      <div className="container home-10__container">
        <div className="home-10__content">
          <div className="home-10__top">
            <h2 data-a-h="" className="h1 home-10__h">Project <span className="h1--i">roadmap</span></h2>
            <p data-a-p="" className="home-10__text">
              Part of the Flashform is already done, but we continue to work on it to give you the best user experience
            </p>
          </div>
          <div className="home-10__bottom">
            <ArrowDownLarge data-a-t="" className="home-10__bottom-arrow" />
            <div className="home-10__bottom-date-wrapper">
              <small data-a-o="" className="home-10__bottom-date-description">{'{Alpha release}'}</small>
              <span data-a-t="" className="home-10__bottom-date">Dec <span className="home-10__bottom-day" data-a-h="">19</span></span>
            </div>
          </div>
        </div>
      </div>
      <div className="wrapper">
        <div className="scroller">
          <div className="scroller-el">
            <div className="home-10__roadmap roadmap">
              <RoadmapCurve />
              <small className="roadmap__circle" />
              {ITEMS.map(([m, d, t]) => (
                <div key={d} className="roadmap__item">
                  <span className="roadmap__date">{m} <span>{d}</span></span>
                  <p className="roadmap__title">{t}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
