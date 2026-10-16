# https://www.flshfrm.com/ (local React + Vite clone in this folder)

Source: https://www.flshfrm.com/ (local React + Vite clone in this folder)
Status: **measured-from-live-site** · production approved: **false**
1 routes · 1 templates · 19 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 1 template (Home (single-page site)) accounts for 1 of 1 routes (100%). The remaining 0 routes span 0 templates.

| template | routes | share |
|---|---:|---:|
| Home (single-page site) | 1 | 100% |

## Page chrome

**1 routes carry chrome = `full`** — Home (single-page site).

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `shell.intro-loader` | SHELL | 1 | 1 | `src/components/Loader.jsx + src/anim/loader.js` | Shown once per load on the 1 route, before any other section animates. |
| `shell.app-loader` | SHELL | 1 | 1 | `src/components/AppLoader.jsx` | Available on the 1 route; visible only during a form submit. |
| `shell.navbar` | SHELL | 1 | 1 | `src/components/Navbar.jsx` | Present on the 1 route at all widths; links collapse into the burger at ≤1060px. |
| `shell.mobile-menu` | SHELL | 1 | 1 | `src/components/MobileMenu.jsx (inside Navbar.jsx)` | Rendered on the 1 route only at ≤1060px. |
| `shell.scrollbar` | SHELL | 1 | 1 | `src/anim/smoothScroll.js` | Desktop only (>1060px) on the 1 route; native scrolling below that. |
| `shell.beta-popup` | SHELL | 1 | 1 | `src/components/BetaPopup.jsx` | Overlay on the 1 route, opened on demand. |
| `shell.toasts` | SHELL | 1 | 1 | `src/components/Toasts.jsx` | Overlay on the 1 route, shown after a form submit. |
| `shell.footer` | SHELL | 1 | 1 | `src/components/Footer.jsx + src/anim/fallingLetters.js` | Closes the 1 route. |
| `hero.home` | HERO | 1 | 1 | `src/components/Hero.jsx + src/anim/gl.js` | Opens the 1 route. |
| `story.meaning` | STORY | 1 | 1 | `src/components/Meaning.jsx` | Appears once, on the 1 route. |
| `story.purpose` | STORY | 1 | 1 | `src/components/Purpose.jsx (uses RoundedSection.jsx)` | Appears once, on the 1 route. |
| `story.why` | STORY | 1 | 1 | `src/components/Why.jsx` | Appears once, on the 1 route; target of the #why nav anchor. |
| `integration.steps` | INTEGRATION | 1 | 1 | `src/components/Integration.jsx + src/anim/scrollFx.js + src/anim/gl.js` | Appears once, on the 1 route; target of the #integration nav anchor. |
| `integration.messengers` | INTEGRATION | 1 | 1 | `src/components/Messengers.jsx` | Appears once, on the 1 route. |
| `value.benefits` | VALUE | 1 | 1 | `src/components/Benefits.jsx` | Appears once, on the 1 route; target of the #benefits nav anchor. |
| `value.relief` | VALUE | 1 | 1 | `src/components/Relief.jsx` | Appears once, on the 1 route. |
| `value.problems` | VALUE | 1 | 1 | `src/components/Problems.jsx (uses RoundedSection.jsx)` | Appears once, on the 1 route. |
| `roadmap.timeline` | ROADMAP | 1 | 1 | `src/components/Roadmap.jsx + src/anim/scrollFx.js` | On the 1 route at >1060px only (display:none at ≤1060px); target of the #roadmap nav anchor. |
| `support.faq` | SUPPORT | 1 | 1 | `src/components/Faq.jsx` | Appears once, on the 1 route; target of the #faq nav anchor. |

**0 shared sections** appear in more than one template and belong in a component library.

**19 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Home (single-page site) — `template.home`

1 route · `/` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.intro-loader` | page-local |
| 2 | SHELL | `shell.app-loader` | page-local |
| 3 | SHELL | `shell.navbar` | page-local |
| 4 | SHELL | `shell.mobile-menu` | page-local |
| 5 | HERO | `hero.home` | page-local |
| 6 | STORY | `story.meaning` | page-local |
| 7 | STORY | `story.purpose` | page-local |
| 8 | STORY | `story.why` | page-local |
| 9 | INTEGRATION | `integration.steps` | page-local |
| 10 | INTEGRATION | `integration.messengers` | page-local |
| 11 | VALUE | `value.benefits` | page-local |
| 12 | VALUE | `value.relief` | page-local |
| 13 | VALUE | `value.problems` | page-local |
| 14 | ROADMAP | `roadmap.timeline` | page-local |
| 15 | SUPPORT | `support.faq` | page-local |
| 16 | SHELL | `shell.footer` | page-local |
| 17 | SHELL | `shell.beta-popup` | page-local |
| 18 | SHELL | `shell.scrollbar` | page-local |
| 19 | SHELL | `shell.toasts` | page-local |

## Section reference

### SHELL

_Page chrome and overlays that are not part of the scrolling story: intro loader, navigation, menus, scroller UI, popup, toasts, footer._

**`shell.intro-loader`** — Full-screen intro: a grid of brand-word items that slides in by column, splits by line, then zooms through the centre word (~6s) before the page reveals.

· Shown once per load on the 1 route, before any other section animates. · appears on 1 routes · implemented by `src/components/Loader.jsx + src/anim/loader.js`

**`shell.app-loader`** — Small fixed circular spinner shown while a form submission is pending.

· Available on the 1 route; visible only during a form submit. · appears on 1 routes · implemented by `src/components/AppLoader.jsx`

**`shell.navbar`** — Glass top bar with difference blend: brand mark, anchor links (#why #integration #benefits #roadmap #faq) and a 'Join the beta' action; hides on scroll down, reveals near the top.

· Present on the 1 route at all widths; links collapse into the burger at ≤1060px. · appears on 1 routes · implemented by `src/components/Navbar.jsx`

**`shell.mobile-menu`** — Burger button plus small dropdown panel listing the same anchor links as the navbar.

· Rendered on the 1 route only at ≤1060px. · appears on 1 routes · implemented by `src/components/MobileMenu.jsx (inside Navbar.jsx)`

**`shell.scrollbar`** — Custom draggable scrollbar thumb driven by the custom smooth scroller.

· Desktop only (>1060px) on the 1 route; native scrolling below that. · appears on 1 routes · implemented by `src/anim/smoothScroll.js`

**`shell.beta-popup`** — Modal 'Join the beta' form (name + email) with backdrop and close button; opened from the navbar and CTA buttons.

· Overlay on the 1 route, opened on demand. · appears on 1 routes · implemented by `src/components/BetaPopup.jsx`

**`shell.toasts`** — Stacked success/error notifications with a 5s progress bar and close button.

· Overlay on the 1 route, shown after a form submit. · appears on 1 routes · implemented by `src/components/Toasts.jsx`

**`shell.footer`** — Footer with physics-driven draggable letters spelling 'STAY IN TOUCH', contact links, an email signup form and legal links (all external).

· Closes the 1 route. · appears on 1 routes · implemented by `src/components/Footer.jsx + src/anim/fallingLetters.js`

### HERO

_The pinned above-the-fold opening block._

**`hero.home`** — Pinned hero (200vh): split-text headline with italic accent words, intro paragraph, 'Try now' button, spinning globe icon and a WebGL flower.

· Opens the 1 route. · appears on 1 routes · implemented by `src/components/Hero.jsx + src/anim/gl.js`

### STORY

_Explanatory narrative sections introducing what the product is and why it exists._

**`story.meaning`** — 'What does it mean Flashform?' heading and paragraph beside a looping video (1.mp4, lighten blend).

· Appears once, on the 1 route. · appears on 1 routes · implemented by `src/components/Meaning.jsx`

**`story.purpose`** — Green rounded scaling panel 'Purpose of using Flashform': problem/solution text that scrolls inside a pinned card, plus 6 messenger icons.

· Appears once, on the 1 route. · appears on 1 routes · implemented by `src/components/Purpose.jsx (uses RoundedSection.jsx)`

**`story.why`** — #why — 'Designed to make life {easier}' heading and paragraph beside a looping video (2.mp4).

· Appears once, on the 1 route; target of the #why nav anchor. · appears on 1 routes · implemented by `src/components/Why.jsx`

### INTEGRATION

_How-to and connectivity sections: integration steps, screencast, supported messengers._

**`integration.steps`** — #integration — giant horizontally scrolling headline with per-letter rise, four numbered steps, then the screencast video that scales in and dissolves to black via a WebGL noise shader.

· Appears once, on the 1 route; target of the #integration nav anchor. · appears on 1 routes · implemented by `src/components/Integration.jsx + src/anim/scrollFx.js + src/anim/gl.js`

**`integration.messengers`** — 'Integration of your form with different {messengers}' heading with a large arrow and a 'Get a beta' button.

· Appears once, on the 1 route. · appears on 1 routes · implemented by `src/components/Messengers.jsx`

### VALUE

_Benefit and problem/solution sections aimed at developers and site owners._

**`value.benefits`** — #benefits — tilted 'A few important benefits' ticker marquee that flips direction with scroll, plus 6 offset green cards that scale in.

· Appears once, on the 1 route; target of the #benefits nav anchor. · appears on 1 routes · implemented by `src/components/Benefits.jsx`

**`value.relief`** — Two-column block on how the product helps developers and site owners ('For developers' / 'For Site owners').

· Appears once, on the 1 route. · appears on 1 routes · implemented by `src/components/Relief.jsx`

**`value.problems`** — Second green rounded scaling panel 'Problems that we solve' listing 3 items.

· Appears once, on the 1 route. · appears on 1 routes · implemented by `src/components/Problems.jsx (uses RoundedSection.jsx)`

### ROADMAP

_Release timeline content._

**`roadmap.timeline`** — #roadmap — large date mark and a horizontally scrolling drawn curve with 3 milestones that reveal as the curve passes them.

· On the 1 route at >1060px only (display:none at ≤1060px); target of the #roadmap nav anchor. · appears on 1 routes · implemented by `src/components/Roadmap.jsx + src/anim/scrollFx.js`

### SUPPORT

_Answers to common questions._

**`support.faq`** — #faq — 'FAQ' heading and a 4-item accordion; items open independently with a rotating arrow.

· Appears once, on the 1 route; target of the #faq nav anchor. · appears on 1 routes · implemented by `src/components/Faq.jsx`
