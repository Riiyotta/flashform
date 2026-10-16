const ITEMS = [
  ['For developers', "You don't need to write a backend for the form handler. With a service-side API, you only need to insert a unique ID into your HTML, and Flashform will do the rest"],
  ['For Site owners', 'It will be convenient for you to connect the form of your website to Webflow, for example, and send information to several communication channels at once, without programming skills'],
]

// spec §1.9
export default function Relief() {
  return (
    <section className="section home-8">
      <div className="container home-8__container">
        <div className="home-8__content" data-in-view="0.4">
          <div className="home-8__top">
            <h2 data-a-h="" className="h1 home-8__h home-8__h--1"><span className="h1--i">Flashform</span> relieves the headache</h2>
          </div>
          <div className="home-8__bottom">
            <h2 data-a-h="" className="h1 home-8__h home-8__h--2">of <span className="h1--i">developers</span> and site <span className="h1--i">owners</span></h2>
          </div>
        </div>
        <ul data-in-view="" className="home-8__items">
          {ITEMS.map(([h, t]) => (
            <li key={h} className="home-8__item home-8-item">
              <div data-a-l="" className="home-8-item__line" />
              <div className="grid home-8-item__content">
                <h3 data-a-twrapper="" className="home-8-item__h"><span data-a-t="">{h}</span></h3>
                <p data-a-twrapper="" className="home-8-item__text"><span data-a-t="">{t}</span></p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
