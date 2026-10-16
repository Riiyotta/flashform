import RoundedSection, { RoundedItem } from './RoundedSection.jsx'
import { Home3Icon3, Home3Icon4, Home3Icon5 } from './icons.jsx'

// spec §1.10 — rounded section #2
export default function Problems() {
  return (
    <RoundedSection title={<>Problems <span className="h1 h1--i">that we solve</span></>}>
      <RoundedItem Icon={Home3Icon3} title="Website conversion increases" texts={["Data from the form arrives instantly to selected messengers, so you can efficiently process requests from your customers. The speed of order processing affects the potential client's decision to work with you"]} />
      <RoundedItem Icon={Home3Icon4} title="Less time to set up the form" texts={["If you are a developer, you don't need to create a form backend every time in a new project. This will save time on routine things, which can be spent on more pleasant things"]} />
      <RoundedItem Icon={Home3Icon5} title="You don't need to know how to program" texts={['If you are not a developer, but are building a site yourself on Webflow or another builder, you can easily connect a form and send data to the messenger of your choice.']} />
    </RoundedSection>
  )
}
