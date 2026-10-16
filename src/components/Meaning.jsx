// spec §1.3
export default function Meaning() {
  return (
    <section data-in-view="0.4" className="section home-2">
      <div className="container home-2__container">
        <div className="home-2__left">
          <div className="home-2__visual">
            <video src="/assets/video/1.mp4" autoPlay muted loop playsInline />
          </div>
        </div>
        <div className="home-2__right">
          <h2 data-a-h="" className="h1 home-2__h">What does it mean <span className="h1 h1--i">{' Flashform? '}</span></h2>
          <p data-a-p="" className="home-2__text redline-text">
            This is a simply-use service, which allows to you configure the sending of contact forms from your website to selected messengers in a few clicks
          </p>
        </div>
      </div>
    </section>
  )
}
