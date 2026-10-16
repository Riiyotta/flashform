// Shared rounded accent panel (spec §1.4 / §1.10, motion §5.4 + §5.9).
// JS hooks: `.sticky-wrapper` height, `[data-section-sticky]` gets `.sticky-activated`,
// `[data-section-sticky-scroller]` is translated, `[data-section-scale]` scales .88 -> 1.
export default function RoundedSection({ title, children }) {
  return (
    <div className="sticky-wrapper">
      <div data-section-sticky="">
        <section className="rounded-section home-3" data-section-scale="">
          <div className="rounded-section__wrapper">
            <div data-section-sticky-scroller="" className="container grid home-3__container">
              <div className="home-3__left">
                <h2 className="h1 home-3__h">{title}</h2>
              </div>
              <div className="home-3__right">{children}</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export function RoundedItem({ Icon, title, texts, line = true, children }) {
  return (
    <div className="home-3__item home-3-item">
      <div className="home-3-item__top">
        <Icon className="home-3-item__icon" />
        <h3 className="home-3-item__h">{title}</h3>
      </div>
      {texts.map((t, i) => <p key={i} className="home-3-item__text">{t}</p>)}
      {children}
      {line && <div className="home-3-item__line" />}
    </div>
  )
}
