import RoundedSection, { RoundedItem } from './RoundedSection.jsx'
import { Home3Icon1, Home3Icon2 } from './icons.jsx'

const CHANNELS = [
  { name: 'What’sApp', icon: 'whatsapp' },
  { name: 'Email', icon: 'email' },
  { name: 'Telegram', icon: 'telegram' },
  { name: 'Facebook Messanger', icon: 'messanger' },
  { name: 'Discord', icon: 'discord' },
  { name: 'Etc.', icon: 'plus' },
]

// spec §1.4 — rounded section #1
export default function Purpose() {
  return (
    <RoundedSection title={<>Purpose of using <span className="h1 h1--i">Flashform</span></>}>
      <RoundedItem
        Icon={Home3Icon1}
        title="The problem"
        texts={[
          'When you build the website, the one of the most popular issue is a sending data from contact form to channel that convenient for you or your client.',
          'A lot of time is spent on creating the form, integrating it into the website, and making sure that the information from the form reaches the chosen communication channel quickly and consistently',
          'We have been constantly faced with this problem for several years as web developers. Every time we made a new site, we spent a lot of time to ensure that the information from the form was quickly sent to a convenient communication channel, and not just to email',
        ]}
      />
      <RoundedItem
        Icon={Home3Icon2}
        title="Solution"
        line={false}
        texts={[
          'Therefore, we have created a web service that allows you to connect your contact form to the chosen messenger or email in a few clicks, without the need to write dozens of lines of code, in a matter of minutes',
          'Thus, when a user fills out the contact form on the site, you instantly receive this information in:',
        ]}
      >
        <ul className="home-3-item__ul">
          {CHANNELS.map((c, i) => (
            <li key={c.icon} className="home-3-item-li home-3-item__li">
              <div className="home-3-item-li__line" />
              <div className="home-3-item-li__content">
                <p className="home-3-item-li__name">{c.name}</p>
                <img src={`/assets/icons/${c.icon}.svg`} className="home-3-item-li__icon" alt={c.name} />
              </div>
              {i === CHANNELS.length - 1 && <div className="home-3-item-li__line" />}
            </li>
          ))}
        </ul>
      </RoundedItem>
    </RoundedSection>
  )
}
