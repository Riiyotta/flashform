import { ArrowDownLarge, TickerStar } from './icons.jsx'

const CARDS = [
  ['No-code', "Yeah, it's almost a no-code decision. This service is like a breath of fresh air: ease in use and functional. You don't need to know programming languages to get a request from a potential client in a convenient place"],
  ['Beautiful and simple', "You know, we really made a lot of effort to make such a banal at first glance service a pleasure to use. Fresh design with familiar elements. Isn't this happiness? Is the Flashform looks simple? You are all right!"],
  ['One function', 'You understand, nothing extra. We simply take and send data from website contact forms to messengers of your choice. One service — one function. And it does the job as it should, without much fuss'],
  ['To anyone', 'And that, is one of the best features of this product. It is designed both for professional developers who hate routine actions in their work, and for beginners in business who are making their first or second website in their life'],
  ['Who loves quality', 'A business needs a contact form to work properly, right? The flash form will do its main job well — it will send you a messenger message about a new application from the website as soon as someone fills out the form'],
  ['And that’s all', 'With practical experience, the developers of this product have only one goal in mind — to make work life a little easier. No, no less functional (this is important). Namely, it is easier, throwing a lifeline from boring tasks'],
]

// spec §1.8. Hooks: `.ticker__items` (JS translateX + --dir), `[data-cards-scale]` cards (CardsScale §5.8).
export default function Benefits() {
  return (
    <section id="benefits" data-in-view="0.5" className="section home-7">
      <div className="ticker">
        <div className="ticker__items">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="ticker__item">
              <TickerStar />{' \u00a0 '}<div className="ticker__text">A few important <span className="h1--i">benefits</span></div>
            </div>
          ))}
        </div>
      </div>
      <div className="container home-7__container">
        <div className="home-7__content">
          <div className="home-7__text-wrapper">
            <ArrowDownLarge data-a-t="" className="home-7__icon" />
            <p data-a-p="" className="home-7__text redline-text">
              Each of these benefits has been tested first-hand by Flashform developers. But what can I say: our product is a symbiosis of practical solutions that were made to facilitate daily work
            </p>
          </div>
          <ul className="grid home-7__items">
            {CARDS.map(([title, text]) => (
              <li key={title} data-cards-scale="" className="home-7-item home-7__item">
                <p className="home-7-item__text">{text}</p>
                <h3 className="home-7-item__title">{title}</h3>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
