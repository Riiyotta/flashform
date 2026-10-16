const STEPS = [
  'Create and copy your personal ID link',
  'Paste it in your HTML form or in fetch as URL',
  'Choose where you want to send data from form',
  'Done! The data from your website form is almost here',
]

// spec §1.6. Hooks: `.wrapper` (JS height) > `.scroller` (sticky) > `.scroller-el` (JS translateX) for the
// horizontal headline; `.home-5__h` is split into words/chars by the Animation layer.
// `#gl-2` = revealer OGL canvas mount; `.home__revealer` = fixed anchor plane for that shader.
export default function Integration() {
  return (
    <section id="integration" className="section section--pb section--nm home-5">
      <div className="wrapper">
        <div className="scroller">
          <div className="scroller-el">
            <div className="home-5__h-wrapper">
              <h2 className="h1 home-5__h">How you can integrate it with your code?</h2>
            </div>
          </div>
        </div>
      </div>
      <div data-in-view="" className="container home-5__container">
        <ul className="home-5__items">
          {STEPS.map((s, i) => (
            <li key={i} className="home-5-li home-5__li">
              <div data-a-l="" className="home-5-li__line" />
              <div className="home-5-li__content">
                <span data-a-twrapper="" className="home-5-li__step"><span data-a-t="">Step {i + 1}</span></span>
                <p data-a-twrapper="" className="home-5-li__text"><span data-a-t="">{s}</span></p>
              </div>
              {i === STEPS.length - 1 && <div data-a-l="" className="home-5-li__line" />}
            </li>
          ))}
        </ul>
        <div className="home-5__sticky-wrapper">
          <div className="home-5__sticky">
            <div data-section-scale="" className="home-5__video-wrapper">
              <video src="/assets/video/screencast.mp4" autoPlay muted loop playsInline />
            </div>
            <div id="gl-2" />
            <div className="home__revealer js-hidden" />
          </div>
        </div>
      </div>
    </section>
  )
}
