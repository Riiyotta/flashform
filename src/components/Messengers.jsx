import { ArrowDownLarge } from './icons.jsx'
import Button from './Button.jsx'
import { useUI } from '../context.jsx'

// spec §1.7 (no reveal animation in this section)
export default function Messengers() {
  const { openPopup } = useUI()
  return (
    <section className="section home-6">
      <div className="container home-6__container">
        <h2 className="h1 home-6__h">Integration of your form with different <span className="h1 h1--i">{' {messengers} '}</span></h2>
        <ArrowDownLarge className="home-6__arrow" />
        <p className="home-6__text">
          Most often, the data that a potential client leaves in the form are sent to email or to the CRM system. But the fact is that a small business does not always use a CRM system, and also does not always have a manager who monitors customer requests via email in real time
        </p>
        <Button className="home-6__btn" onClick={openPopup}>Get a beta</Button>
      </div>
    </section>
  )
}
