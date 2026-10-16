// spec §1.5
export default function Why() {
  return (
    <section id="why" className="section home-4" data-in-view="0.3">
      <div className="container home-4__container">
        <div className="home-4__left">
          <h2 data-a-h="" className="h1 home-4__h">Designed to make life <span className="h1 h1--i">{' {easier} '}</span></h2>
          <p data-a-p="" className="home-4__text redline-text">
            It is enough to waste time on monotonous activities. We know that whenever you're programming, the least you want to do is customize contact forms
          </p>
        </div>
        <div className="home-4__right">
          <video src="/assets/video/2.mp4" autoPlay muted loop playsInline className="home-4__visual" />
        </div>
      </div>
    </section>
  )
}
