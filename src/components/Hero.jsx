import { Globe } from './icons.jsx'
import Button from './Button.jsx'
import { useUI } from '../context.jsx'

// spec §1.2. `.home-1__gl` = size/position anchor for the OGL flower; `#gl` = canvas mount (OGL appends its canvas).
export default function Hero() {
  const { openPopup } = useUI()
  return (
    <div className="home-1-sticky-wrapper">
      <div className="home-1-sticky">
        <section className="section section--nm home-1">
          <div className="container home-1__container">
            <div className="home-1__top">
              <h1 data-a-h="" className="h1 home-1__h1">
                <span className="home-1__h1-first">We <small className="home-1__h1-small">'re</small></span> just sending <span className="h1--i">forms</span>
              </h1>
              <div className="home-1__right">
                <Globe data-a-o="" />
                <Button className="home-1__btn" data-a-t="" onClick={openPopup}>Try now</Button>
              </div>
            </div>
            <h2 data-a-h="" className="h1 h1--i home-1__h2">and that’s all</h2>
            <p data-a-p="" className="home-1__text redline-text">
              We are not a form builder. We do not seek to solve all problems. We Just send form data to instant messengers and email in the most convenient way
            </p>
            <Button className="home-1__btn home-1__btn--mobile" data-a-t="" onClick={openPopup}>Try now</Button>
          </div>
          <div className="home-1__gl js-hidden" />
          <div id="gl" data-a-o="" />
        </section>
      </div>
    </div>
  )
}
