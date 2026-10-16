Source: https://www.flshfrm.com/

# Flashform clone spec (measured 2026-10-16)

Original stack: Nuxt 3 (Vue 3) SSR, GSAP 3.10.4 + ScrollTrigger 3.10.4, SplitType (text splitting into `.e-line` / `.line-inner` / `.word` / `.char`), OGL (WebGL, not three.js) for two shader canvases, matter-js 0.18.0 for footer physics letters, and a custom virtual-scroll smooth scroller (`window.ss`) on desktop. Built by Emotion Agency. No framer-motion, Lottie, Lenis, Locomotive, or IntersectionObserver.

**Routes:** there is only one route, `/`. Nav items are in-page anchors (`#why`, `#integration`, `#benefits`, `#roadmap`, `#faq`) plus a "Join the beta" popup button. All footer links go off-domain (mailto, wa.me, t.me, termsandconditionsgenerator.com, privacypolicygenerator.info, emotion-agency.com). No other same-domain pages exist.

**References in `/Users/riyaghosh/V3/FLASHFORM/reference/`:**
- `1440-fullpage.png` (1440x21455): stitched from 24 contiguous 900px captures taken with real smooth-scroll state, so sticky, horizontal, and WebGL states are what a user would see at each slice. Seams near the horizontal-scroll sections may drift by up to ~140px because the JS changes scrollHeight at runtime (21261 to 21455).
- `1440-vp-*.png`: single viewports at named scroll positions. The number in the filename is the scrollTop.
- `390-fullpage.png`: true full-page capture. On mobile the page uses native scroll.
- `1280-vp-hero.png`, `768-vp-hero.png`, `768-vp-mobile-menu-open.png`, `768-vp-popup-open.png`, `1440-hover-try-now.png`.
- `inline-svg/*.svg`: the exact inline SVG markup taken from the live DOM (logo, icons, arrows, roadmap curve).
- `shaders/*.glsl`: verbatim GLSL for the two WebGL effects.
- `original-entry.319c9ada.pretty.css`: the site's full compiled CSS, one rule per line. It is the ground truth for every value below.

---

## 0. Global system

### 0.1 Units and scaling (critical)
- `html { font-size: .8333333333vw }` gives 12px at 1440 and 10.667px at 1280. Almost every desktop size is a **vw value**. The px values below were measured at 1440 (and at 1280 where noted). At 1280 every vw value scales by 1280/1440 = 0.8889. Measurements confirm this exactly (for example h1 is 112.5px at 1440 and 100px at 1280).
- Body has no font-size on desktop, so it inherits html: **0.8333vw (12px at 1440)**. At `max-width:1060px` body is **14px** (html stays .8333vw but is unused).
- `body { line-height: 1.5em }`. Because it is `em`, children inherit the **computed px value** (18px at 1440, 16px at 1280, 21px at mobile), not a ratio. Many elements depend on this. For example `.accordion__num` is 24px text on an 18px line-height. **Tailwind preflight sets a unitless `line-height:1.5` on html, which breaks this, so override it on `body` with `1.5em`.**
- **Buttons render in Arial.** The original reset never sets a font on `<button>`, so Chrome uses the UA default font. Measured: "Try now", "Get a beta", the popup "Join", and the nav "Join the beta" `<button>` all compute to `Arial 400`. Exceptions: the nav button inherits `font: inherit` from `.navbar__link`, so it is NeueHaas. The footer "Join" button is `.input-btn`, which sets Aeonik explicitly. Footer contact "buttons" are `<a>` tags, so they are NeueHaas. **Tailwind preflight sets `button { font-family: inherit }`, so the clone must restore `font-family: Arial` on `.button` elements** to match.
- Desktop/mobile switch is **1060px**. Other breakpoints: 1366 (rounded-section margin), 960 (2-column sections stack; SectionScale, CardsScale, and SplitHeading JS are disabled at ≤960), 768, 460 (grid becomes 4 columns), and `orientation: landscape and max-width: 960px` (hero un-sticks).
- At widths over 768 the original calls `location.reload()` on every window resize. This is optional to replicate.

### 0.2 Color tokens (`:root`)
| token | value | use |
|---|---|---|
| `--black` | `#111606` rgb(17,22,6) | page bg, text on accent |
| `--accent` | `#b1dd40` rgb(177,221,64) | **default text color**, lines, cards, rounded sections |
| `--white` | `#ffffff` | app-loader circle, selection bg |
| `--red` | `#e73737` rgb(231,55,55) | required `*`, input errors, danger toast |
| nav glass | `#ffffff05` = rgba(255,255,255,0.02) | `.navbar__content` bg |
| ticker band | `#ffffff0d` = rgba(255,255,255,0.05) | `.ticker` bg |
| over-revealer glow | `box-shadow: 0 -16px 44px #b1dd4029` (rgba(177,221,64,0.16)) | top edge of `.over-revealer` panels |
| popup backdrop | `#000c` = rgba(0,0,0,0.8) | |
| scrollbar thumb | `#6b6b6b` (idle), accent when hovered/dragged | |
| popup close icon | `#333333` at fill-opacity 0.9 | |
| footer line | accent at opacity .2 | |
| Butterfly shader | color1 rgb(165,104,62) `#a5683e`, color2 rgb(69,114,78) `#45724e` | hero WebGL flower (looks orange-to-green) |
| Revealer shader | `#FFFFFF` to `#000000` | noise dissolve |
| matter.js canvas bg | `#111606` | |
- `::selection { color: var(--accent); background: white }`. In inputs: `color: white`. In popup inputs: `background: black; color: accent`.
- Autofill: `-webkit-text-fill-color: accent` (popup: black), `box-shadow: 0 0 0 1000px #00000003 inset`, transition `background-color 5000s`.
- There are no gradients in the UI. The only CSS gradients are in Nuxt's unused error page.

### 0.3 Fonts (all self-hosted; preloaded with `<link rel=preload as=font type=font/woff2 crossorigin=anonymous>`)
```css
@font-face{font-family:Aeonik;font-display:swap;src:url(/fonts/Aeonik-Regular.woff2) format("woff2");font-weight:400;font-style:normal}
@font-face{font-family:Recife;font-display:swap;src:url(/fonts/RecifeDisplayWeb-BookItalic.woff2) format("woff2");font-weight:350;font-style:normal}
@font-face{font-family:NeueHaas;font-display:swap;src:url(/fonts/NeueHaasDisplay-Medium.woff2) format("woff2");font-weight:600;font-style:normal}
@font-face{font-family:NeueHaas;font-display:swap;src:url(/fonts/NeueHaasDisplay-Roman.woff2) format("woff2");font-weight:500;font-style:normal}
```
- Fallback stack for all three: `-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Open Sans, Helvetica Neue, sans-serif`.
- NeueHaas **500 maps to the "Roman" file and 600 maps to the "Medium" file**. Elements that ask for weight 400 (`.home-8-item__h`) fall back to the 500 face.
- Recife is declared `font-style: normal` even though the file is an italic cut. Never use `font-style: italic` with it, or the browser will synthesize a slant.
- `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale` on body.

### 0.4 Type roles (computed at 1440 / 1280; mobile values apply at ≤1060)
| role | selector | family/weight | size 1440 / 1280 | line-height | other | mobile ≤1060 |
|---|---|---|---|---|---|---|
| Display H1 | `.h1` | Aeonik 400 | 7.8125vw = 112.5 / 100px | 1em | ls normal | 56px |
| Display italic | `.h1--i` (span inside h1/h2) | Recife 350 | inherits | inherits | | |
| Body | `body` | NeueHaas 500 | .8333vw = 12 / 10.667px | 1.5em = 18 / 16px | color accent | 14px / 21px |
| Redline paragraph | `.redline-text` | NeueHaas 500 (Aeonik on home-7) | 12px | 1em (set per element) | uppercase; `text-indent: 7.65625vw` = 110.25px (≤1060: 86px). After SplitType runs, the indent becomes `margin-left` on the first `.line-inner` | 14px |
| Hero "'re" | `.home-1__h1-small` | Aeonik 400 | 1.25vw = 18px | inherited 112.5px | abs top 0, right .5208vw (7.5px) | 12px, right 4px |
| Section h3 (rounded) | `.home-3-item__h` | Aeonik 400 | 2.5vw = 36 / 32px | 1em | max-w 34.6875vw | 28px |
| Rounded body | `.home-3-item__text` | NeueHaas 500 | 1.0417vw = 15 / 13.33px | 1.5em | | 16px |
| Integration list name | `.home-3-item-li__name` | NeueHaas 500 | 1.25vw = 18px | 18px (inherited) | | 20px |
| Step label | `.home-5-li__step` | Aeonik 400 | 15px | 1em | "Step 1" | 16px |
| Step text | `.home-5-li__text` | Aeonik 400 | 2.1875vw = 31.5 / 28px | 1em | uppercase | 28px |
| Horizontal headline | `.home-5__h` | Aeonik 400 | 26.0417vw = 375 / 333.3px | 1em | nowrap (≥1060) | 56px (`.h1`), normal flow |
| FAQ headline | `.home-11__h` | Aeonik 400 | 375px | 1em | center | 100px |
| Ticker | `.ticker__item` | Aeonik 400 | 10.4167vw = 150 / 133.3px | 93% (139.5px) | | 48px |
| Benefit card title | `.home-7-item__title` | Aeonik 400 | 2.6042vw = 37.5 / 33.3px | 1em | | 24px |
| Benefit card text | `.home-7-item__text` | NeueHaas 500 | 12px | 18px | black | 14px/21px |
| Dev/owner h3 | `.home-8-item__h` | NeueHaas 400 (renders 500) | 2.0833vw = 30 / 26.67px | 1em | uppercase | 24px |
| Dev/owner text | `.home-8-item__text` | NeueHaas 500 | 15px | 1.4em = 21px | | 14px / 19.6px |
| Roadmap big day | `.home-10__bottom-day` | NeueHaas **600** | 32.2917vw = 465px | 1em | height 27.2917vw (393px), overflow hidden | hidden |
| Roadmap "Dec" | `.home-10__bottom-date` | Aeonik 400 | 37.5px | 1em | | hidden |
| Roadmap item month | `.roadmap__date` | Aeonik 400 | 1.8519vh = 16.67px @900h | 1em | | hidden |
| Roadmap item day | `.roadmap__date span` | NeueHaas 600 | 9.2593vh = 83.33px | 1em | block | |
| Roadmap item title | `.roadmap__title` | Aeonik 400 | 12px | 1em | | |
| FAQ num | `.accordion__num` | NeueHaas 500 | 1.6667vw = 24px | 18px (inherited) | | hidden |
| FAQ question | `.accordion__h4` | Aeonik 400 | 1.4583vw = 21 / 18.67px | 1.2em | | 20px |
| FAQ answer | `.accordion__text` | NeueHaas 500 | 15px | 1.5em | | 14px |
| Nav link | `.navbar__link` | NeueHaas 500 | 12px | 18px | uppercase | 14px / 21px |
| Button | `.button` | **Arial 400** (UA default) | 1.0417vw = 15 / 13.33px | 1em | uppercase | 16px |
| Footer heading | `.footer__h` | Aeonik 400 | 15px | 18px | uppercase | 18px |
| Footer contact | `.footer-contact__btn` | NeueHaas 500 | .7292vw = 10.5px | 1em | uppercase | 14px |
| Footer copy / by | `.footer__copy`, `.footer__by` | Aeonik 400 | 15px | 1.5em | | 16px |
| Footer legal | `.footer__legal` | Aeonik 400 | .8333vw = 12px | 1.5em | opacity .7 | 14px, opacity 1 |
| Input | `.input` | Aeonik 400 | 16px (all widths) | normal | text-transform none | 16px |
| Input label | `.input-placeholder` | Aeonik 400 | inherits 12px | 18px | uppercase | 14px |
| Input error | `.input-error` | Aeonik 400 | 12px | | red, lowercase, abs, mt 4px | |
| Popup title | `.popup__form-h` | Aeonik 400 | 3.75vw = 54px | 1em | `<legend>` | 36px |
| Loader word | `.loader__item` | NeueHaas 500 | 3.6458vw = 52.5px | 1em | nowrap | |

Letter-spacing is `normal` everywhere. No text-shadow anywhere.

### 0.5 Layout primitives
- `.container`: width 100%, relative, padding-x **5.2083vw** (75px at 1440, 66.67px at 1280). ≤1060: 32px. ≤768: 20px. There is no max-width; content width is 1290px at 1440 and 1146.67px at 1280.
- `.grid`: 12 columns `repeat(12,1fr)`, column-gap **1.0417vw** (15px at 1440; ≤1060: 20px), `grid-auto-flow: column`. ≤460: 4 columns. Column width at 1440 is 93.75px.
- `.section`: padding-top **15.625vw** (225 / 200px). ≤1060: 200px. ≤768: 120px. `.section--nm` sets it to 0. `.section--pb` adds the same value as padding-bottom.
- `.h-line`: 2px tall, accent, full width.
- Radii: nav 12px; rounded-section 20px (0 at ≤768); cards and video use `0 20px 20px` (top-left corner square; ≤1060 `0 10px 10px`); popup 12px; mobile menu 10px; toast 5px.
- z-index: navbar 100; over-revealer panels 3; footer 3; #gl-2 4; loader 1000; popup 5000; toast 10000; app-loader 10001; scrollbar 10000000.

### 0.6 Scroll architecture (desktop >1060)
- `html, body` are 100vh with `overflow: hidden`. Content lives in `#scroll-container` (height 100vh, overflow hidden, scrollbar hidden). A custom smooth scroller (`window.ss`) runs on desktop only:
  - Wheel deltas are clamped to ±120 and multiplied by `stepSize .8` into a target. Each rAF frame applies `current = lerp(current, target, 0.07)`, rounds to 0.01, and sets `#scroll-container.scrollTop`.
  - Keyboard: ↑/↓ ±240px, PageUp/PageDown ±innerHeight, Home/End, Tab scrolls to the focused element.
  - `ss.isFixed = true` locks scrolling (used while the loader and popup are showing).
- Custom scrollbar `.scrollbar`: fixed right 0, width 12px, padding 2px 2px 2px 0. The thumb is 6px wide, `#6b6b6b`, radius 7px, opacity 0. While scrolling it gets `.scrolling` (opacity .7). After 1s of inactivity it hides again. On hover or drag the thumb becomes 10px wide, accent, radius 10px. Transitions: width .2s, opacity/radius/bg .3s ease. Thumb height = vh·(vh/scrollHeight). The thumb is draggable and the track is clickable.
- At ≤1060 the scroller is destroyed and `#scroll-container` becomes `overflow-y: auto` (native scroll). Body stays 100vh.
- The navbar is `position: absolute` relative to `<body>` and sits outside the scroll flow, so it behaves as if fixed.
- `--vh` and `--vw` are set on `body` from window size on resize.

---

## 1. Page structure in DOM order (copy is exact)

Document Y positions are inside `#scroll-container` at 1440x900 (1280x800 in brackets). Total scrollHeight is about 21261 to 21455 [18924]; it changes at runtime as JS sizes the sticky and horizontal wrappers. At 768 it is 12354; at 390 it is 12084.

```
<head>: title "Flashfom: the fastest and easiest way to connect with your customer"  (sic, "Flashfom")
  meta description / og:description / twitter:description:
    "Flashform is an easy in use data sender from a website’s contact form to different messengers and emails: What’s App, Discord, Telegram and etc."
  og:title / twitter:title = title; og:image & twitter:image = /twitter.png (1200x630); favicon /favicon.ico
body
 ├─ .app-grid (debug 12-col overlay, hidden)
 ├─ .loader  (intro, removed after ~5.7s)
 ├─ .app-loader (spinner, only while a form submits)
 ├─ #scroll-container
 │   └─ main
 │       ├─ header.navbar
 │       ├─ .home-1-sticky-wrapper (200vh) > .home-1-sticky (sticky top 0) > section.home-1  [HERO]
 │       ├─ .over-revealer.home-2-over-revealer (margin-top -90vh)
 │       │    ├─ section.home-2  [WHAT DOES IT MEAN]
 │       │    ├─ .sticky-wrapper > [data-section-sticky] > section.rounded-section.home-3  [PURPOSE]
 │       │    ├─ section#why.home-4  [DESIGNED TO MAKE LIFE]
 │       │    └─ section#integration.home-5  [HORIZONTAL HEADLINE + STEPS + SCREENCAST/REVEALER]
 │       └─ .over-revealer.home-6-over-revealer (margin-top -100vh)
 │            ├─ section.home-6  [MESSENGERS + ARROW + CTA]
 │            ├─ section#benefits.home-7  [TICKER + BENEFIT CARDS]
 │            ├─ section.home-8  [RELIEVES THE HEADACHE]
 │            ├─ .sticky-wrapper > … section.rounded-section.home-3  [PROBLEMS THAT WE SOLVE]
 │            ├─ section#roadmap.home-10  [ROADMAP]  (display:none ≤1060)
 │            └─ section#faq.home-11  [FAQ]
 │   └─ footer.footer
 │   └─ .new-form > .popup (Join the beta modal, v-if)
 └─ .toast-container
```

### 1.1 Navbar `header.navbar`
- Position absolute, top **1.0417vw** (15px; ≤1060 20px), left/right 0, z 100. **`mix-blend-mode: difference` at ≥1060**. Because of this the accent text shows as about #a0c73a over the dark bg, and the nav inverts over accent panels.
- Transition `transform .5s ease, opacity .5s ease`. When `body.nav-hidden` is set (and the navbar is not `--fixed`) it moves to `translateY(-100%)` with opacity 0.
- Structure: `.container > .navbar__content`. Content bg rgba(255,255,255,.02), padding **2.0833vw 1.4583vw** (30px 21px; ≤1060 20px), radius 12px, flex space-between center. Measured box at 1440: x75 y15 w1290 h81.
  - Logo: `a.navbar__logo[aria-label=FlashForm][href=/]` with inline SVG `reference/inline-svg/logo.svg` (viewBox 154x28, fill #B1DD40), rendered at **8.125vw x 1.4583vw** (117x21; ≤1060 108x20).
  - `nav.navbar__nav > ul.navbar__ul` (flex, gap 2.0833vw = 30px). Items in order: **"Why flashform"** (#why), **"Integration"** (#integration), **"Benefits"** (#benefits), **"Roadmap"** (#roadmap; hidden ≤1060), **"FAQ"** (#faq), then `button.navbar__link.navbar__link--signin`: **"Join the beta"** plus a 16x16 arrow SVG (`inline-svg/icon-signin-arrow.svg`), gap 8px. The button opens the popup.
  - `button.burger` (only ≤1060). See §7.
- Anchor click: smooth-scrolls to `el.top + scrollTop + innerHeight*0.3`. Note the +30% vh offset. Uses `gsap.to(ss.state, {target, duration: 1})` when innerWidth ≥1024, otherwise `gsap.to(#scroll-container, {scrollTop, duration: 1})`. Default ease is power1.out.
- Hide/show logic: on each rAF, scrolling down adds `body.nav-hidden`; scrolling up removes it. While hidden, a mousemove listener removes it when `event.screenY <= 300`, and the nav stays visible while the mouse remains in that zone.

### 1.2 Hero `section.section.section--nm.home-1` (doc y 0)
- `.home-1-sticky-wrapper` is relative with height **200vh**. `.home-1-sticky` is sticky at top 0. The hero itself is height 100vh, padding-top **7.2917vw** (105px; ≤1060 100px), position relative. In landscape at ≤960 the hero is not sticky and has auto height.
- `.container.home-1__container` (height 100%, z 2):
  - `.home-1__top` (flex, space-between):
    - `h1.h1.home-1__h1[data-a-h]`: `<span class="home-1__h1-first">We <small class="home-1__h1-small">'re</small></span> just sending <span class="h1--i">forms</span>`. Max-width **41.4583vw** (597px; ≤1060 400px). It renders on 3 lines at 1440 and 390 ("We 're just" / "sending" / *forms*) and on 2 lines at 768 ("We 're just" / "sending *forms*"). Box at 1440: x75 y105 w401 h338.
    - `.home-1__right` (flex column, align-end, gap 1.4583vw = 21px, padding-top 1.25vw = 18px; **display:none ≤768**):
      - Globe SVG `inline-svg/icon-globe.svg`, 2.6042vw square (37.5px; ≤1060 20px), `[data-a-o]`. It loops `animation: world 5s linear infinite alternate` (rotateY 0 to 360deg, backface visible).
      - `button.button.home-1__btn[data-a-t]`: **"Try now"**. Opens the popup.
  - `h2.h1.h1--i.home-1__h2[data-a-h]`: **"and that’s all"** (curly apostrophe U+2019). Recife, absolute **right 5.2083vw, bottom 1.0417vw** (≤1060 bottom 20px). Box at 1440: x708.7 y772.5 w656 h112.5.
  - `p.home-1__text.redline-text[data-a-p]`: **"We are not a form builder. We do not seek to solve all problems. We Just send form data to instant messengers and email in the most convenient way"**. Uppercase, line-height 1em, width **29.1667vw** (420px), absolute bottom **2.1875vw** (31.5px). ≤1060: static, 14px, max-width 500px, margin-top 28px.
  - `button.button.home-1__btn.home-1__btn--mobile[data-a-t]`: "Try now", margin-top 40px. **Hidden at ≥768px** (`min-width:768px`). At exactly 768px no Try-now button is visible, because `.home-1__right` is also hidden at ≤768.
- `.home-1__gl`: absolute, centered (`top/left 50%; translate(-50%,-50%)`), z 0, **31.25vw square** (450px; ≤1060 300px). This element is the size and position anchor for the WebGL flower.
- `#gl[data-a-o]`: absolute, top 0, left 0, 100% x 100vh, z 0, pointer-events none. It holds the OGL canvas (1440x900, dpr = devicePixelRatio). See §5.6.

### 1.3 `section.section.home-2[data-in-view="0.4"]` (doc y 990 [880]; bg black)
- `.container.home-2__container`: flex, space-between, align center. ≤960: `column-reverse`, align start.
  - `.home-2__left` (flex 0 1 44.7917vw = 645px) > `.home-2__visual` (36.8229vw square = 530.25px; bg black). It contains `<video src="/1.mp4" autoplay muted loop playsinline>` (1024x1024, 5s) with **`mix-blend-mode: lighten`** and bg black. ≤960 width 60% centered; ≤460 100%.
  - `.home-2__right` (flex 0 1 43.75vw = 630px; ≤960 max-width 70%, margin-bottom 40px; ≤460 100%):
    - `h2.h1.home-2__h[data-a-h]`: **"What does it mean** <span class="h1 h1--i">Flashform?</span>**"**
    - `p.home-2__text.redline-text[data-a-p]`: **"This is a simply-use service, which allows to you configure the sending of contact forms from your website to selected messengers in a few clicks"**. Max-width 29.1667vw (420px), margin-top 2.2917vw (33px), lh 1em. ≤1060: margin-top 28px, max-width none.
- ≤1060: `.home-2` padding-top 60px.

### 1.4 Rounded section #1 "Purpose" (`.rounded-section.home-3[data-section-scale]`, doc y 2024 [1799])
- Wrapper: `.sticky-wrapper` (relative; JS sets its height to the inner content height) > `[data-section-sticky]` (sticky top 0) > `section.rounded-section`.
- `.rounded-section`: `--margin: .62vw` (8.93px; ≤1366 .42vw; ≤1060 10px; ≤768 0), `padding: var(--margin)`, overflow hidden, margin-top 15.625vw (225px; 60.94px at 390 because it has no mobile override), relative. **Initial `transform: scale(.88)` at ≥1060**; it scales to 1 on scroll (§5.4). Any `getBoundingClientRect` inside it reads 0.88x until then, so use the CSS values below.
- `.rounded-section__wrapper`: radius 20px, overflow hidden, **bg accent, color black**. When `.sticky-activated` is set, its height is `calc(var(--vh) - var(--margin)*2)`. ≤768: radius 0, min-height 100vh.
- `.rounded-section__wrapper .container.grid.home-3__container[data-section-sticky-scroller]`: padding **5.2083vw** on all sides (75px), 12-column grid. ≤1060: display block, padding 40px 20px (390: 20.31px 20px).
  - `.home-3__left` (grid-column 1/6): `h2.h1.home-3__h` **"Purpose of using** <span class="h1 h1--i">Flashform</span>**"** (black).
  - `.home-3__right` (grid-column 7/13):
    - Item 1 `.home-3-item`:
      - `.home-3-item__top` (flex, center, gap 1.6667vw = 24px, mb 2.0833vw = 30px): icon `inline-svg/home3-icon-1.svg` (55x45, fill #111606, height **2.34375vw** = 33.75px, width auto) and `h3.home-3-item__h` **"The problem"**.
      - Three `p.home-3-item__text` (consecutive ones have margin-top 1.4583vw = 21px):
        1. "When you build the website, the one of the most popular issue is a sending data from contact form to channel that convenient for you or your client."
        2. "A lot of time is spent on creating the form, integrating it into the website, and making sure that the information from the form reaches the chosen communication channel quickly and consistently"
        3. "We have been constantly faced with this problem for several years as web developers. Every time we made a new site, we spent a lot of time to ensure that the information from the form was quickly sent to a convenient communication channel, and not just to email"
      - `.home-3-item__line` (2px black, margin-top 1.4583vw).
    - Item 2 (margin-top 2.0833vw = 30px):
      - Icon `home3-icon-2.svg` (45x45) and h3 **"Solution"**.
      - p: "Therefore, we have created a web service that allows you to connect your contact form to the chosen messenger or email in a few clicks, without the need to write dozens of lines of code, in a matter of minutes"
      - p: "Thus, when a user fills out the contact form on the site, you instantly receive this information in:"
      - `ul.home-3-item__ul` (margin 2.0833vw 0): six `li`. Each has a 2px black top line, then `.home-3-item-li__content` (flex, space-between, center, padding 1.6667vw 0 = 24px). Name is a `p` at 1.25vw; the icon is an `<img>` with height 1.875vw (27px). After the last li there is one more 2px line.
        - What’sApp → `/icons/whatsapp.svg` (36x32)
        - Email → `/icons/email.svg` (36x36)
        - Telegram → `/icons/telegram.svg`
        - Facebook Messanger (sic) → `/icons/messanger.svg`
        - Discord → `/icons/discord.svg`
        - Etc. → `/icons/plus.svg`
      - No `.home-3-item__line` after item 2.
- Mobile values: icon 28px tall; top gap 24px, margin 28px 0; h3 28px; text 16px, consecutive-text margin 20px; li padding 16px 0; name 20px; icon 24px.

### 1.5 `section#why.section.home-4[data-in-view="0.3"]` (doc y 2999 [2668])
Note that the nav item "Why flashform" scrolls to this section.
- `.container.home-4__container`: flex, space-between, center. ≤960: column, align start.
  - `.home-4__left` (flex 0 1 41.4583vw = 597px):
    - `h2.h1.home-4__h[data-a-h]` **"Designed to make life** <span class="h1 h1--i">{easier}</span>**"** (literal curly braces).
    - `p.home-4__text.redline-text[data-a-p]` **"It is enough to waste time on monotonous activities. We know that whenever you're programming, the least you want to do is customize contact forms"**. Max-width 27.2396vw (392.25px), margin-top 2.2917vw, lh 1em.
  - `.home-4__right` (flex 0 1 42.96875vw = 618.75px, bg black; ≤960 margin-top 40px) > `<video class="home-4__visual" src="/2.mp4" autoplay muted loop playsinline>` (1024x1024). It floats right at width **36.71875vw** (528.75px) with **mix-blend-mode: lighten**. ≤960: 60% wide, centered; ≤460: 100%.

### 1.6 `section#integration.section.section--pb.section--nm.home-5` (doc y 3753 [3338])
- **Horizontal-scroll headline** (desktop): `.wrapper` (JS sets height = `scroller-el.scrollWidth − (innerWidth − innerHeight)`, measured 6270px at 1440) > `.scroller` (sticky top 0, overflow hidden) > `.scroller-el` (flex, nowrap, fit-content; JS translateX) > `.home-5__h-wrapper` (100vh, flex center) > `h2.h1.home-5__h` with innerHTML **"How you can integrate it with your code?"**. Size 26.0417vw (375px), nowrap, lh 1em, rendered width 6860px at 1440. SplitType wraps it into `.word` and `.char` spans; chars start at `translateY(101%)` with opacity 0 (≥1060). See §5.5.
  - ≤1060: no horizontal scroll. The h2 sits in normal flow at 56px with margin-left 32px (≤460: 20px) and wraps.
- `.container.home-5__container[data-in-view]` (default threshold .9):
  - `ul.home-5__items` (margin-top 1.0417vw = 15px; ≤1060 40px). Each `li` has `.home-5-li__line[data-a-l]` (2px accent, scaleX 0 initially) followed by `.home-5-li__content` (padding .8333vw 0 = 12px, flex space-between; ≤1060 column, gap 12px):
    - `span.home-5-li__step[data-a-twrapper] > span[data-a-t]`: **"Step 1"** … **"Step 4"**
    - `p.home-5-li__text[data-a-twrapper] > span[data-a-t]`, uppercase:
      1. **"Create and copy your personal ID link"**
      2. **"Paste it in your HTML form or in fetch as URL"**
      3. **"Choose where you want to send data from form"**
      4. **"Done! The data from your website form is almost here"**
    - The last li has an extra bottom line `[data-a-l]`.
  - `.home-5__sticky-wrapper` (relative, height **200vh**, margin-top **13.0208vw** = 187.5px; ≤1060 mt 0) > `.home-5__sticky` (sticky top 0, 100vh, flex center), which contains:
    - `.home-5__video-wrapper[data-section-scale]`: max-width **74.4792vw** (1072.5px), margin 0 auto, **opacity 0** and scale .88 initially, radius `0 20px 20px`, overflow hidden, max-height 90vh. Inside is `<video src="/screencast.mp4" autoplay muted loop playsinline>` (1680x1050, 30.13s). It renders at 943.8x589.9 at scale .88 and 1072.5x670 at scale 1. ≤1060: max-width 100%, radius 10px, opacity 1, no scale.
    - `#gl-2`: absolute, top 0, left −5.2083vw (≤1060 −32px; ≤460 −20px), 100vw x 100vh, z 4, pointer-events none. Holds the revealer OGL canvas (dpr 1).
    - `.home__revealer`: fixed, 100% x 100% (min 100vh), z 1, pointer-events none. This is the anchor plane for the revealer shader (§5.7).

### 1.7 `.over-revealer.home-6-over-revealer` > `section.section.home-6` (doc y 11583 [10298])
- `.over-revealer`: relative, z 3, bg black, `box-shadow: 0 -16px 44px #b1dd4029`, **margin-top −100vh**. It slides up over the dark revealer.
- `.home-6`: relative, z 3, padding-top **8.3333vw** (120px; ≤1060 100px).
- `.container.home-6__container`: flex column, centered, text-align center.
  - `h2.h1.home-6__h` (uppercase): **"Integration of your form with different** <span class="h1 h1--i">{messengers}</span>**"**. The italic span has `text-transform: none`. It renders on 3 lines at 1440: "INTEGRATION OF YOUR" / "FORM WITH DIFFERENT" / "{messengers}".
  - Arrow SVG `inline-svg/arrow-down-large.svg` at intrinsic 154x220 at every width, margin-top 2.0833vw (30px; ≤1060 24px).
  - `p.home-6__text`: **"Most often, the data that a potential client leaves in the form are sent to email or to the CRM system. But the fact is that a small business does not always use a CRM system, and also does not always have a manager who monitors customer requests via email in real time"**. Uppercase, lh 1em, max-width 27.1875vw (391.5px), margin-top 3.125vw (45px). ≤1060: max-width 70%, mt 36px. ≤768: 100%.
  - `button.button.home-6__btn`: **"Get a beta"**, margin-top 3.125vw (≤1060 40px). Opens the popup.
- There is no reveal animation in this section.

### 1.8 `section#benefits.section.home-7[data-in-view="0.5"]` (doc y 12456 [11098])
- **Ticker** `.ticker` (first child of the section, outside the container): `transform: rotate(-2deg)`, bg rgba(255,255,255,.05), padding .5208vw 0 2.0833vw (7.5px 0 30px; ≤1060 10px 0 20px), overflow hidden, full width.
  - `.ticker__items` (flex, nowrap, fit-content; JS translateX) contains **4** `.ticker__item`s. Each item is Aeonik 150px with lh 93%, margin-left 3.90625vw (56.25px; ≤1060 32px; ≤460 20px), flex center, and contains:
    - Star SVG `inline-svg/icon-ticker-star.svg` (63x60, accent), 3.3333vw square (48px; ≤1060 20px), position relative, top .8333vw (12px). It has `transform: rotate(calc(360deg * var(--dir)))` with `transition: transform 10s linear`.
    - The text node `"   "`.
    - `.ticker__text`: "A few important <span class="h1--i">benefits</span>" (the last word is Recife).
  - Rendered width of `.ticker__items` at 1440: 7063.8px.
- `.container.home-7__container > .home-7__content` (margin-top 8.3333vw = 120px; ≤1060 80px; relative):
  - `.home-7__text-wrapper` (desktop: absolute, top 0, **left 22.65625vw** (326.25px into the content box, so x=401.25 at 1440), max-width 21.6667vw (312px), height 20.3125vw (292.5px), flex column, space-between):
    - Arrow SVG `.home-7__icon[data-a-t]`, 2.5vw x 3.5417vw (36x51). Hidden at ≤1060.
    - `p.home-7__text.redline-text[data-a-p]` (Aeonik, lh 1em): **"Each of these benefits has been tested first-hand by Flashform developers. But what can I say: our product is a symbiosis of practical solutions that were made to facilitate daily work"**.
    - ≤1060: static, margin-bottom 40px.
  - `ul.grid.home-7__items` (row-gap .8333vw = 12px; ≤1060: 2 columns `1fr 1fr`, row-gap 16px, auto-flow row; ≤768: 1 column). Six `li.home-7-item[data-cards-scale]`:
    - Card box: **21.6146vw x 20.3125vw** (311.25 x 292.5px), bg accent, color black, radius **0 20px 20px**, padding **1.25vw 3.3333vw 1.25vw 1.25vw** (18/48/18/18), flex column, space-between. It contains `p.home-7-item__text` (body size) and `h3.home-7-item__title`. ≤1060: padding 20px, height 300px, width auto, radius 0 10px 10px.
    - Desktop placement (grid-column / grid-row): 1 → 1/4, row 1; 2 → 10/13, row 1; 3 → 4/7, row 2; 4 → 7/10, row 2; 5 → 1/4, row 3; 6 → 7/10, row 3.
    - Content in order:
      1. **No-code**: "Yeah, it's almost a no-code decision. This service is like a breath of fresh air: ease in use and functional. You don't need to know programming languages to get a request from a potential client in a convenient place"
      2. **Beautiful and simple**: "You know, we really made a lot of effort to make such a banal at first glance service a pleasure to use. Fresh design with familiar elements. Isn't this happiness? Is the Flashform looks simple? You are all right!"
      3. **One function**: "You understand, nothing extra. We simply take and send data from website contact forms to messengers of your choice. One service — one function. And it does the job as it should, without much fuss"
      4. **To anyone**: "And that, is one of the best features of this product. It is designed both for professional developers who hate routine actions in their work, and for beginners in business who are making their first or second website in their life"
      5. **Who loves quality**: "A business needs a contact form to work properly, right? The flash form will do its main job well — it will send you a messenger message about a new application from the website as soon as someone fills out the form"
      6. **And that’s all**: "With practical experience, the developers of this product have only one goal in mind — to make work life a little easier. No, no less functional (this is important). Namely, it is easier, throwing a lifeline from boring tasks"

### 1.9 `section.section.home-8` (doc y 13880 [12364])
- `.home-8__content[data-in-view="0.4"]`:
  - `.home-8__top` (flex, space-between): `h2.h1.home-8__h.home-8__h--1[data-a-h]` = `<span class="h1--i">Flashform</span> relieves the headache`, max-width 48.4375vw (697.5px).
  - `.home-8__bottom` (≥1060: flex, justify end, align end, margin-top 5.2083vw = 75px; ≤1060 mt 60px): `h2.h1.home-8__h.home-8__h--2[data-a-h]` = `of <span class="h1--i">developers</span> and site <span class="h1--i">owners</span>`, text-align right, max-width 59.1146vw (851.25px).
- `ul.home-8__items[data-in-view]` (margin-top 7.8125vw = 112.5px; ≤1060 72px; li + li margin-top 2.7083vw = 39px; ≤1060 36px). Each li has `.home-8-item__line[data-a-l]` (2px accent) followed by `.grid.home-8-item__content` (margin-top .8333vw = 12px; ≤1060 block):
  - h3 (grid-column 1/5) `span[data-a-t]` **"For developers"**; p (grid-column 7/12) `span[data-a-t]` **"You don't need to write a backend for the form handler. With a service-side API, you only need to insert a unique ID into your HTML, and Flashform will do the rest"**
  - **"For Site owners"** / **"It will be convenient for you to connect the form of your website to Webflow, for example, and send information to several communication channels at once, without programming skills"**
  - ≤1060: text margin-top 16px.
- The CSS defines `.home-8__img` (17.8125vw square), but no such element exists in the DOM. Ignore it.

### 1.10 Rounded section #2 "Problems that we solve" (doc y about 15344; same component as §1.4)
- Left: `h2.h1.home-3__h` **"Problems** <span class="h1 h1--i">that we solve</span>**"**.
- Right, three items, each with an icon, h3, one p, and a 2px black line:
  1. `home3-icon-3.svg` (61x46 stairs): **"Website conversion increases"**: "Data from the form arrives instantly to selected messengers, so you can efficiently process requests from your customers. The speed of order processing affects the potential client's decision to work with you"
  2. `home3-icon-4.svg` (45x45 triangles): **"Less time to set up the form"**: "If you are a developer, you don't need to create a form backend every time in a new project. This will save time on routine things, which can be spent on more pleasant things"
  3. `home3-icon-5.svg` (45x45 clover): **"You don't need to know how to program"**: "If you are not a developer, but are building a site yourself on Webflow or another builder, you can easily connect a form and send data to the messenger of your choice."

### 1.11 `section#roadmap.section.home-10[data-in-view="0.4"]` (doc y 15942, height 3265 at 1440; **display:none at ≤1060**)
- `.container > .home-10__content`:
  - `.home-10__top`:
    - `h2.h1.home-10__h[data-a-h]` "Project <span class="h1--i">roadmap</span>", max-width 41.6667vw (600px).
    - `p.home-10__text[data-a-p]` **"Part of the Flashform is already done, but we continue to work on it to give you the best user experience"**. Max-width 25.2604vw (363.75px), uppercase, lh 1em, margin-top 1.25vw.
  - `.home-10__bottom` (flex, space-between, align end):
    - Arrow `.home-10__bottom-arrow[data-a-t]` (36x51).
    - `.home-10__bottom-date-wrapper` (flex, align end, relative, top 3.125vw = 45px) contains:
      - `small.home-10__bottom-date-description[data-a-o]` **"{Alpha release}"** (10px, rotate(−90deg), relative, right 10.6771vw, top −4.375vw).
      - `span.home-10__bottom-date[data-a-t]` "Dec " + `span.home-10__bottom-day[data-a-h]` **"19"** (465px NeueHaas 600, clipped to 393px tall, top −30px).
- **Horizontal roadmap** (HorizontalScroll wrapper, the same mechanism as §1.6) > `.home-10__roadmap`: height 100vh, **width 312.037vh** (2808px at 900h), flex column, justify center, margin-left 5.2083vw, relative.
  - Curve SVG `inline-svg/roadmap-curve.svg` (viewBox 3370x671, stroke #B1DD40, width 3) at height 62.2222vh (560px), width 100%.
  - `small.roadmap__circle`: absolute, top 18.9vh, left 0, .9259vh dot (8.33px), accent, round.
  - Three `.roadmap__item`s (absolute, opacity 0, `transition: opacity .4s ease`; `.is-visible` sets opacity 1). Each is `span.roadmap__date` "month " + `<span>day</span>` and `p.roadmap__title` "{event}":
    1. bottom 1.8519vh, left 72.6852vh: **jan 19**, **{Beta release}**
    2. top 40.7407vh, left 154.4444vh: **march 03**, **{Hopefully, a release}**
    3. bottom 3.7037vh, left 230.3704vh: **apr 23**, **{Add new messengers}**
- Nav item "Roadmap" is hidden on mobile because this section is hidden there.

### 1.12 `section#faq.section.home-11` (doc y 19207 [17095])
- `h2.h1.home-11__h`: `F<span class="h1--i">A</span>Q`, centered, 26.0417vw (375px; ≤1060 100px).
- `.accordion > .accordion__items` (≤1060 margin-top 20px) starts with an `.h-line`, then 4 `.accordion__item`s. See §7.3. Questions and answers:
  1. **"Is it form builder?"** "No, this is the web service that provide an API for implementing backend function to HTML form. It just send all data from your website form to convinient messengers or other chanels."
  2. **"What I must to do for implementing this to my website form?"** "Just follow these three steps:<br/>1. Create an copy your personal ID link.<br/>2. Paste it in your HTML form or in fetch as URL.<br/>3. Choose where you want to send data from form.<br/>4. Done! The data from your website form is almost here." (rendered via innerHTML with `<br/>`)
  3. **"Are the instructions different for integration with different messengers?"** "Yes, there are certain differences in the instructions for each messenger. But we have done everything so that you as a user do not experience any inconvenience:)"
  4. **"Is FlashForm a paid product?"** "You can use a free account if it is sufficient for your purposes. But if you need more integrations, then for $10 per month you get unlimited access to integrations."
- Numbers display as "01" to "04".

### 1.13 `footer.footer` (doc y 20104 [17892])
- Relative, z 3, bg black, padding-bottom 30px. Contains `.container.footer__container`:
  - `.footer__top`: height **100vh** (≤460 **50vh**) > `#letter-parent` (relative, 100%) holding the matter.js canvas sized to the parent (1290x900 at 1440). At ≤1060 there is also an empty `.letter-over` (absolute center, 40vw square). See §5.9.
  - `.footer__bottom`:
    - `.footer__line` (2px accent, opacity .2).
    - `.grid.footer__content` (margin-top 3.125vw = 45px; ≤1060 40px; ≤1060 flex column, gap 32px):
      - `.foter__item--1` (sic; col 1/3): logo SVG at 8.125vw x 1.4583vw (117x21; ≤1060 156x28).
      - `.foter__item--2` (col 5/7): `h3.footer__h` **"Contact us"** + `ul.footer__contacts` (margin-top .8333vw; ≤1060 16px). Three `li.footer-contact` (margin-top .4167vw = 6px; the 2nd li 1.6667vw = 24px; ≤1060 8px / 28px; lh 1em; uppercase), each an `a.button.footer-contact__btn` (target _blank, rel "noreferer noopener"; underline removed):
        - **hello@emotion-agency.com** → `mailto:hello@emotion-agency.com`
        - **Whatsapp** → `https://wa.me/+380970422959`
        - **Telegram** → `https://t.me/rstetsr`
      - `.foter__item--4` (col 9/13, justify-self end, fit-content): `h3.footer__h` **"Join the beta"** + `form.form.footer__form[novalidate]` (width **29.1667vw** = 420px, margin-top 2.7083vw = 39px; ≤1060 32px, full width). The form has an email input (placeholder label **"Your Email"** + red `abbr` **"*"**) and `button.button.form__btn.input-btn` **"Join"**. See §7.4.
    - `.footer__info` (margin-top 4.5833vw = 66px; ≤1060 60px) > `.grid.footer__info-content` (align baseline; ≤1060 flex column, gap 12px):
      - col 1/3: `small.footer__copy` **"©2022 Flashform"**
      - col 5/7: `a.footer__legal` **"Terms and conditions"** → https://www.termsandconditionsgenerator.com/live.php?token=KqfzIWBkH418WdHEZEWKRACbvJtGFf0j
      - col 7/9: `a.footer__legal` **"Privacy Policy"** → https://www.privacypolicygenerator.info/live.php?token=iEz9YG406khJuP5hPg30r2GlroSf2mmH
      - col 9/13 (justify end): `a.footer__by` **"by emotion"** → https://emotion-agency.com/en/
      - All three links open with target _blank.

### 1.14 Measured boxes (x, y-in-document, w, h)
| element | 1440x900 | 1280x800 | 768x1024 | 390x844 |
|---|---|---|---|---|
| navbar__content | 75,15,1290,81 | 66.7,13.3,1146.7,72 | 20,20,728,62 | 20,20,350,62 |
| home-1__h1 | 75,105,401,338 | 66.7,93.3,356.7,300.5 | 20,100,359.5,112 | 20,100,199.8,168 |
| home-1__h2 | 708.7,772.5,656.3,112.5 | 630,686.7,583.3,100 | 401.3,948,326.7,56 | 43,768,326.7,56 |
| home-1__text | 75,826.5,420,42 | 66.7,733.5,373.3,38.5 | 20,240,500,49.5 | 20,296,350,66 |
| home-1__gl | 495,225,450,450 | 440,200,400,400 | 234,362,300,300 | 45,272,300,300 |
| home-2 | 0,990,1440,755 | 0,880,1280,671 | 0,1126,768,719 | 0,928,390,702 |
| home-2__visual | 75,1215,530.3² | 66.7,1080,471.3² | 165.6,1408,436.8² | 20,1280,350² |
| rounded #1 (scaled .88) | 86.4,2024,1267,792 | 76.8,1799,1126,704 | 0,1965,768,1024 | 0,1691,390,844 |
| home-4 | 0,2999,1440,754 | 0,2668,1280,670 | 0,2997,768,765 | 0,3036,390,762 |
| home-4__visual | 836.3,3224,528.8² | 743.3,2868,470² | 165.6,3325,436.8² | 20,3448,350² |
| home-5 headline wrapper | 0,3753, w6860 | 0,3338, w6098 | flow | flow |
| home-5__items | 75,10038,1290,232 | 66.7,8924,1146.7,207 | 20,4034,728,358 | 20,4182,350,498 |
| home-5 sticky wrapper | 75,10458,1290,1800 | 66.7,9298,1146.7,1600 | 20,4392,728,2048 | 20,4680,350,1688 |
| home-6 | 0,11583,1440,873 | 0,10298,1280,800 | 0,5536,768,646 | 0,5644,390,814 |
| ticker | −2.7,12656,1445,228 | −2.4,11276,1285,202 | −1.1,6289,770,101 | −1.2,6571,392,88 |
| home-7 card 1 | 75,12978,311.3,292.5 | 66.7,11563,276.7,260 | 20,6539,728,300 | 20,6843,350,300 |
| home-8 | 0,13880,1440,1149 | 0,12364,1280,1022 | 0,8419,768,722 | 0,8723,390,893 |
| home-10 | 0,15942,1440,3265 | 0,14193,1280,2902 | hidden | hidden |
| home-11 | 0,19207,1440,897 | 0,17095,1280,798 | 0,10285,768,499 | 0,10521,390,595 |
| footer | 0,20104,1440,1157 | 0,17892,1280,1032 | 0,10784,768,1571 | 0,11115,390,969 |

---

## 2. Responsive changes summary

**1280** (desktop): identical layout to 1440. Every vw value scales by 0.8889. Rounded-section `--margin` is .42vw (5.376px) because ≤1366 applies.

**768:**
- Native scroll; no smooth scroller and no custom scrollbar.
- Nav: logo 108x20, links hidden behind the burger, navbar__content padding 20px.
- Hero: h1 56px on 2 lines; text is static below the h1; **no Try-now button visible** (see §1.2); globe hidden; flower box 300px; "and that’s all" absolute bottom-right at 56px.
- home-2: column-reverse, video 60% width (436.8px) centered.
- Rounded sections: no scale; full-bleed at 768 (`--margin: 0`), radius 0, min-height 100vh, content padding 40px 20px. Their sticky inner-scroll still runs if the content is taller than the viewport.
- home-4: column, video 60% centered.
- home-5 headline: normal flow, 56px, wraps, margin-left 32px. Steps stack (label above text), 16px / 28px. Screencast is full-width with 10px radius and no scale. The revealer canvas still exists.
- home-6: 56px heading on 3 lines.
- Ticker: 48px.
- Cards: 1 column (≤768), 300px tall, 24px titles.
- home-8: headings stack, left-aligned (the second is right-aligned via text-align right, max-width unset).
- Roadmap hidden.
- FAQ: 100px heading; accordion rows are flex with no numbers.
- Footer: letters canvas 100vh; content stacks with gap 32; info stacks with gap 12.

**390:** same as 768 except:
- `.grid` becomes 4 columns at ≤460.
- Hero h1 3 lines; "Try now" mobile button visible (x20 y402, 95.9x16).
- Videos 100% width (350px).
- home-5 headline margin-left 20px.
- Rounded-section margin-top is 60.94px (15.625vw).
- Cards 1 column.
- Footer letters canvas **50vh** (422px).
- Ticker item margin-left 20px.

**Landscape ≤960** (phones): hero is not sticky and has min-height 100vh; `.home-2-over-revealer` margin-top 0 with no shadow.

---

## 3. Colors per section
- Page bg `#111606` with text `#b1dd40` everywhere except accent panels (rounded sections, benefit cards, popup, mobile menu, success toast), which are bg `#b1dd40` with text `#111606`.
- Lines are accent 2px. Inside accent panels the lines are black 2px. The footer line is accent at .2 opacity.
- Video panels use `mix-blend-mode: lighten` over black, so the black video background merges into the page.

---

## 4. Assets (25 downloadable; see `assets-manifest.tsv`)
| URL | local path | format | intrinsic | where |
|---|---|---|---|---|
| /fonts/Aeonik-Regular.woff2 | public/fonts/ | woff2 42,632 B | | |
| /fonts/NeueHaasDisplay-Roman.woff2 | public/fonts/ | woff2 26,524 B | | NeueHaas 500 |
| /fonts/NeueHaasDisplay-Medium.woff2 | public/fonts/ | woff2 27,256 B | | NeueHaas 600 |
| /fonts/RecifeDisplayWeb-BookItalic.woff2 | public/fonts/ | woff2 30,132 B | | Recife 350 |
| /1.mp4 | public/assets/video/1.mp4 | mp4 364 KB | 1024x1024, 5s loop | home-2 |
| /2.mp4 | public/assets/video/2.mp4 | mp4 265 KB | 1024x1024, 5s | home-4 |
| /screencast.mp4 | public/assets/video/screencast.mp4 | mp4 1.15 MB | 1680x1050, 30.13s | home-5 |
| /icons/{whatsapp,email,telegram,messanger,discord,plus}.svg | public/assets/icons/ | svg | 36x36 (whatsapp 36x32) | Purpose list |
| /svg/{s,T,A,Y,I,N,O,U,C,H}.svg | public/assets/letters/ | svg, fill #B1DD40 | s 210x286, T 217x280, A 255x280, Y 247x281, I 35x280, N 217x280, O 268x286, U 215x283, C 252x286, H 215x281 | footer physics. **Note: the S sprite file is lowercase `s.svg`** (`/svg/S.svg` returns 404) |
| /favicon.ico | public/assets/favicon.ico | ico 1,123 B | | `<link rel=icon type=image/x-icon>` |
| /twitter.png | public/assets/og/twitter.png | png 1200x630 | | og:image / twitter:image |

The following are **inline SVGs, not downloadable**. Exact markup is in `reference/inline-svg/`:
- `logo.svg` (154x28; used in nav and footer)
- `icon-signin-arrow.svg` (16x16)
- `icon-burger-close.svg` (10x10, black)
- `icon-globe.svg` (50x51)
- `icon-ticker-star.svg` (63x60)
- `arrow-down-large.svg` (154x220; used in home-6, home-7, home-10)
- `roadmap-curve.svg` (3370x671 stroke)
- `icon-accordion-arrow.svg` (34x34 down arrow)
- `home3-icon-1..5.svg`
- Popup close icon: 28x28 circle-x, path `M14 0C6.2 0 0 6.2 0 14C0 21.8 6.2 28 14 28C21.8 28 28 21.8 28 14C28 6.2 21.8 0 14 0ZM19.4 21L14 15.6L8.6 21L7 19.4L12.4 14L7 8.6L8.6 7L14 12.4L19.4 7L21 8.6L15.6 14L21 19.4L19.4 21Z`, fill #333333, fill-opacity .9.
- Toast close icon: 15x14 X, fill #000000 (white in danger toasts).

There are no raster images on the page other than the og image, and no Lottie files. The two hero/revealer visuals are **WebGL shaders** (§5.6, §5.7), not assets.

---

## 5. Motion inventory

GSAP eases used: `power3.out`, `power4.out` / `power4.in`, `power2.inOut`, `power3.inOut`, `power1.inOut`, `back.out(2)`, `back.in(2)`, `back.inOut(2)`, `back.out(1.2)`, `linear`. CSS ease used everywhere for UI: **`cubic-bezier(.16,1,.3,1)`** (expo-out).

### 5.1 Intro loader (on every load; `.loader`, fixed, full-screen, bg black, color accent, z 1000)
- Markup: 5 flex columns (`.loader__cols`, gap 1.0417vw, space-between), each a column of "Flashform ®" words (`.loader__item`: 3.6458vw = 52.5px, lh 1em, nowrap, opacity 0).
  - Col 1 is absolute, full width, with items centered at left 50vw. It holds 5 items: top (`--ct`), plain, center (`--c`, `data-a-h`), plain, bottom (`--cb`).
  - Cols 2, 4, 5 hold 5 items each.
  - Col 3 holds 2 items, then `--ec` (the "end center"), then 2 items.
  - All except `--c` carry `data-a-p`.
- Timeline (source; times are from mount):
  1. t=0: center word `--c` animates by chars: chars go from `translateY(100%) scaleY(1.5)` opacity 0 to y 0, scaleY 1. Duration .5s (opacity .55s), stagger .07, ease `back.out(2)`.
  2. +1000ms: `--ct` animates by lines (lines from y 100% to 0 over 1s `power4.out`, opacity over 1.2s). +100ms later the same for `--cb`.
  3. +500ms: col-1 items go to `left: 0, translateX(0)` (from the centered position). Duration 1s, `power2.inOut`, stagger .01. When complete, col-1 gets `.done` (static and width auto), so it joins the 5-column grid.
  4. +1000ms: every `.loader__item` animates by lines (duration .9s) with a 20ms·index stagger.
  5. +1000ms: all items except `--ec` fade to opacity 0 over .5s. Then `--ec` goes to **scale 100**, opacity 0, over 1.3s `power3.inOut` (a zoom-through).
  6. +1800ms: the loader unmounts, `ss.isFixed = false`, the hero intro (§5.2) runs, and the Butterfly `onLoad` runs.
- **Measured** (sampled every 150ms): center chars settled by ~0.9s; col-1 `.done` and all items visible at ~3.0s; non-ec items faded by ~4.3s; ec scale 3.2 at 4.6s, 37 at 4.9s, 93 at 5.2s, 100 at 5.5s; loader removed at ~5.7s.

### 5.2 Reveal-on-view system (`[data-in-view]` sections plus the hero after the loader)
- Trigger: on each rAF, a section activates once (adds `.activated`) when `0 < rect.top <= innerHeight * threshold`. `threshold = data-in-view` value, default .9. This is not IntersectionObserver.
- Thresholds: home-2 .4, home-4 .3, home-5 container .9, home-7 .5, home-8__content .4, home-8__items .9, home-10 .4. The hero runs right after the loader.
- On activation, for elements inside the section:
  - `[data-a-l]` (lines; CSS `transform: scaleX(0)`, origin left): to scaleX 1, **1s `power1.inOut`, stagger .1**.
  - `[data-a-t]` (CSS opacity 0, `translateY(100%)`; parent `[data-a-twrapper]` is overflow hidden and inline-block): to opacity 1, y 0, **.7s `power3.out`, stagger .1**.
  - `[data-a-o]` (opacity 0): to opacity 1, **.8s `power3.out`, stagger .1**.
  - `[data-a-h]` headings (heading opacity 0 until split): heading *n* waits **n·300ms**. It is split into chars (SplitType "lines, words, chars", line class `e-line`, inner `.line-inner`). Chars start at `translateY(100%) scaleY(1.5)` opacity 0 and animate to y 0, scaleY 1 over **.5s `back.out(2)`** (opacity .55s). The stagger is **.07s per char, restarting for each line**, so all lines start together.
  - `[data-a-p]` paragraphs: paragraph *n* waits **(n+1)·700ms**. It is split into lines; each `.line-inner` (inside an overflow-hidden `.e-line`) starts at `translateY(100%)` opacity 0 and animates to 0 over **1s `power4.out`** (opacity 1.2s), **stagger .1**.
  - `.redline-text.splitted`: after the split, the first line's `.line-inner` gets margin-left 7.65625vw (86px at ≤1060) instead of text-indent.
- Hero intro: h1 (n=0) and h2 (n=1, +300ms) char-reveal; the paragraph line-reveals at +700ms; the globe and #gl canvas fade in (.8s); the Try-now buttons rise in (.7s).

### 5.3 Over-revealer panels (CSS plus sticky)
- The hero is sticky inside a 200vh wrapper. The next panel (`.home-2-over-revealer`, black, with a glow shadow at its top edge) starts at margin-top −90vh and scrolls up over the pinned hero.
- `.home-6-over-revealer` (margin-top −100vh) scrolls up over the pinned screencast/revealer panel.

### 5.4 SectionScale (`[data-section-scale]`: both rounded sections and the screencast wrapper; only when innerWidth > 960)
- GSAP timeline with ScrollTrigger: `trigger: el, start: "top-=100%"`, `end: "+=" + innerHeight`, `scrub: .1`, `scroller: #scroll-container`. Tweens to scale 1 and opacity 1 with ease linear (from CSS scale .88; the video wrapper also goes from CSS opacity 0).
- **Measured** behavior: progress runs linearly from when the element's top reaches the viewport bottom until it reaches the viewport top.
  - Rounded #1 (top 2024): scale .88 at y≤1124 → .941 at 1500 → .984 at 1800 → 1.0 at 2100.
  - Rounded #2 (top 15344): .908 at 14800 → .965 at 15100.
  - Screencast wrapper (sticky): scale .923 / opacity .355 at y=10200, .974 / .779 at 10500, .998 / .981 at 10800, 1 / 1 at 11100.

### 5.5 HorizontalScroll (home-5 headline and the roadmap; only when screen.width > 1060)
- The wrapper height is set to `scrollerEl.scrollWidth − (innerWidth − innerHeight)`. `.scroller` is sticky top 0. Each rAF (while in view) sets `translateX = clamp(wrapperRect.top, −wrapperHeight + innerHeight, 0)`, so 1px of vertical scroll moves the content 1px horizontally. It writes `matrix3d(...)` and sets `--t`.
- Measured: at scrollTop 4300, translateX −547; at 6000, −2106.5. The wrapper starts at doc y 3753.
- **SplitHeading on `.home-5__h`** (>960): split into words and chars. Each char gets its own ScrollTrigger timeline: `start: "left +=" + innerWidth/2`, `end: "right right-=" + charRect.right + "px"`, `scrub: .01`, to `y: 0, opacity: 1`, ease `back.out(1.2)`, with delay `.02*i` for i>1. Initial CSS is `translateY(101%)`, opacity 0.
- Measured result: chars right of viewport center are pushed down and faded; they settle as they travel left past center, with a slight upward overshoot from back.out. Sampled values as [char, viewport x, translateY px, opacity]:
  - At scrollTop 4300: w −77 −12.9 1 | y 315 −17.9 1 | o 500 1.4 1 | u 718 36 .91 | c 1023 101.4 .73 | a 1228 161.7 .57 | n 1430 233.8 .38
  - At 6000: n −129 −0.4 1 | i 179 −5.2 1 | n 252 −13.3 1 | t 462 −17.4 1 | e 586 −20 1 | g 796 −15.5 1 | r 1020 −8.2 1 | a 1144 9.6 .97 | t 1346 27.4 .93 | e 1470 62.3 .84
  - See `1440-vp-04300-howto-horizontal-a.png`.
- **Roadmap**: same horizontal mechanism. Also, on each rAF with `y = wrapperRect.top / wrapperHeight * 100`:
  - The path is drawn with `strokeDasharray = L` and `strokeDashoffset = clamp(L + y*L/95 − innerHeight, 0, L + innerHeight)`, where L is the total path length.
  - Items get `.is-visible` when −y ≥ 8, 30, and 52 respectively. They fade in over .4s and fade out again when scrolling back.

### 5.6 Hero WebGL "Butterfly" flower (OGL; desktop and mobile)
- Renderer: OGL `Renderer({dpr: devicePixelRatio, alpha: true, antialias: true, premultipliedAlpha: false, webgl: 2})`. The canvas is full-viewport inside `#gl`.
- Camera: perspective with `fov = 2*atan(h/2/800)` in degrees, z 800, near 1, far 1000. Pixel units are 1:1.
- Mesh: a plane (1x1 segments) scaled to `.home-1__gl`'s rect (450px at 1440) and positioned at that rect's center. The scene is scaled **2x**, so the flower visually spans about 900px.
- Shaders: `reference/shaders/butterfly.vert.glsl` and `butterfly.frag.glsl`. Prefix them with `base-vert-webgl2.glsl` + `base-vert-cover-prefix.glsl` (vertex) and `base-frag-webgl2.glsl` (fragment), and add `#version 300 es` at the top. Transparent, no depth test.
- Uniforms:
  - `u_color1 = (165,104,62)`, `u_color2 = (69,114,78)` (0–255; the shader divides by 255).
  - `u_timeOffset = 7.4` initially.
  - `u_time = 1e-4*(Date.now()-start) + timeOffset`. `timeOffset` grows by `(|camX|+|camY|)/30` per frame, where `camX = ((mouseX/innerWidth − .5)*20 − camera.x)*.05` and `camY = ((mouseY/innerHeight − .5)*25 − camera.y)*.05`.
  - `u_mousePosition`: normalized mouse position. It changes the petal count (`3 + mx*3`) and brightness (`1 + (1−my)*.5`).
  - `camera.rotation.z += camY/400 + camX/200` every frame, so the flower slowly spins and responds to the mouse.
- Load-in (called when the loader ends): `camera.rotation.z` from .5 to 0 over **2s `back.inOut(2)`**; `scene.scale` from 0 to 2 over **1.5s `back.out(2)`**. Mouse and touch listeners attach after that.
- The canvas only renders while `#gl` is in view.

### 5.7 Screencast "Revealer" noise dissolve (OGL, `#gl-2`, dpr 1)
- A plane fitted to `.home__revealer` (fixed full-screen) using `revealer.frag.glsl` and `revealer.vert.glsl`.
- Uniforms: `uColor1 = #FFFFFF`, `uColor2 = #000000`, `uClicked` from 0 to 1.
- `progress = smoothstep(t+.1, t−.1, noise(gl_FragCoord.xy*.4))`; `color = mix(vec4(white, progress), vec4(black, 1), progress)`. The effect is noise-shaped blotches that dissolve the screencast to black, with soft whitish edges.
- ScrollTrigger: trigger `.home-5__sticky`, `start: "top+=40%"`, `end: "+=" + innerHeight`, `scrub: .1`, linear. It writes the progress to the `moved` attribute.
- **Measured** `moved`: .313 at y=11100, .647 at 11400, .98 at 11700, 1 at 12000. That is linear over 900px, starting at about y≈10818 (about 35–40% of the 900px sticky panel past the viewport top).

### 5.8 CardsScale (benefit cards, >960)
- Initial inline transform per card index i: `translateY(17*(i*2.4)px) scaleY(1+i*.07)`:
  - i=0: 0, 1
  - i=1: 40.8px, 1.07
  - i=2: 81.6px, 1.14
  - i=3: 122.4px, 1.21
  - i=4: 163.2px, 1.28
  - i=5: 204px, 1.35
- ScrollTrigger: `trigger: card, end: "+=bottom"` (the original's literal string), scrub .1, to y 0 and scaleY 1, linear.
- **Measured** (cards 1 and 5): card 2 (top ≈13028) had progress 38% at y=12300, 79% at 12600, 98.5% at 12900, 100% at 13200. Card 6 (top ≈13790) had 13% at 12900, 64% at 13200, 93% at 13500, 100% at 13800.
- Approximation: progress starts when the card top reaches the viewport bottom and completes about 0.75–0.9 viewport heights later. **Uncertain:** the curve is slightly ease-out-shaped because of how the original string is parsed. Tune against `1440-vp-13100-benefit-cards.png`.

### 5.9 Sticky inner scroll (rounded sections)
- If the inner `.container` is taller than the viewport, the wrapper gets `.sticky-activated`. The panel is then pinned at `100vh − 2·margin` tall, the `.sticky-wrapper` height is set to the content height, and the content is translated by `clamp(wrapperTop, 0, −(contentHeight − innerHeight))`. The text scrolls inside the fixed accent card.

### 5.10 Ticker marquee
- Defaults: duration 80, direction 1, 4 copies.
- Each frame: `time += dir + scrollVelocity/100`, where `scrollVelocity = scrollTop − ss.state.target` while scrolling. `x = itemsWidth * (time/60/80)`, wrapped into [−50%, 0] of the total width (two copies equal one loop).
- Base speed: half the track width per 40s, which is about 88px/s at 1440.
- Direction: idle drift is **rightward** (dir +1). While scrolling down it becomes −1 (leftward). Scrolling up returns it to +1. Scroll velocity adds speed.
- `--dir` is written to `.ticker__items`. Each star SVG has `rotate(calc(360deg*var(--dir)))` with a 10s linear transition, so each direction flip spins the stars 360° over 10s.

### 5.11 CSS keyframe loops
- `@keyframes world` rotateY 0 to 360deg: 5s linear infinite **alternate** (hero globe).
- `@keyframes ticker` translateX 0 to −50%: 4s linear infinite. This runs on every button's hidden hover marquee (`.button__hover-text`, 4 repeats of the label).
- App-loader spinner: `rotate` 2s linear infinite, plus `dash` 1.5s ease-in-out infinite (stroke-dasharray 1,200 → 89,200 → 89,200 with offset 0 → −35 → −124).

### 5.12 Footer physics letters (matter-js 0.18.0)
- Starts 2s after mount. It plays only while `#letter-parent` top is less than `innerHeight/2`, and stops otherwise. The first play triggers the drops.
- Engine, Render (canvas = parent size, pixelRatio 1, bg `#111606`, wireframes off) and Runner.
- Walls: static invisible rectangles (thickness 160) on the floor, left, right, and top.
- `MouseConstraint` with stiffness .02 and angularStiffness .02, so the letters can be dragged.
- Sprite scale `g = 0.2 + 0.4*((innerWidth−375)/1065)`: .6 at 1440, about .206 at 390.
- Each letter is a rectangle of sprite w·g x h·g. Spawn x = `w*g + w*g*indexInTable`, clamped to [w*g, parentWidth], where the table order is s,T,A,Y,I,N,T,O,U,C,H. Spawn y = −160. Angle `random()*0.5`, restitution .07, frictionAir 1e-4. Texture `/svg/<letter>.svg` at xScale/yScale g.
- Drop sequence: "STAY" (one letter every 400ms), "IN" at +2s, "TOUCH" at +3s, then again at +5s: STAY, +2s IN, +3s TOUCH (relative to +5s). That is 26 letters in total.
- Physics positions are non-deterministic. See `1440-vp-20361-footer.png` for a settled example.

### 5.13 Hover and interaction transitions
| element | rest | hover / active | timing |
|---|---|---|---|
| `.button` (all CTAs) | `[` label `]`. Label has a 1px accent underline (`.button__content::after`, bottom 0) | label `translateY(-110%)`; hidden marquee wrapper slides from `translateY(110%)` to 0 and shows the looping 4x label (4s linear); underline goes to `translateY(50px) rotate(10deg)` opacity 0. **Measured** at 1440: text −16.5px, underline matrix(0.985,0.174,−0.174,0.985,0,50) | .5s cubic-bezier(.16,1,.3,1) |
| `.navbar__link`, `.footer__legal`, `.footer__by` | `::after` 2px accent line at bottom, `translateY(20px) rotate(10deg)`, opacity 0 | `translateY(0) rotate(0)`, opacity 1 (the line swings up into place) | .5s cubic-bezier(.16,1,.3,1) |
| `.accordion__item` | `.accordion__overlay` height 0%, radius 50% 50% 0 0, accent at opacity .2, from the bottom | height 100%, radius 0% (a wash rises from the bottom) | height and radius .8s cubic-bezier(.16,1,.3,1) |
| `.scrollbar` hover | thumb 6px gray | 10px accent, radius 10px, opacity .7 | .2s/.3s ease |
| Footer `.footer-contact__btn`, `.input-btn` | same as `.button` but with no underline (`::after` display none) | | |
| `.toast__close svg path` | opacity .7 | (no hover rule in CSS) | .2s ease |
- There are no custom cursors and no focus rings (the reset sets `outline: none` on everything).

---

## 6. Section-specific notes
- `[data-a-h] span:not(.line-inner,.e-line,.char,.word) { display: inline !important }` keeps the italic spans inline after the split.
- `.home-5__h .word { display: inline-block !important }`.
- The navbar is not part of any reveal and is visible immediately (under the loader).

---

## 7. Interactive components

### 7.1 Mobile menu (≤1060)
- Burger `button.navbar__burger.burger[aria-label="Navigation button"]`: flex, gap 20px, padding 8px 0 8px 8px (content-box). Three dots (`.burger__dot`, 6x6, accent, radius 20px, `transition: transform .4s ease`). Dot 2 is absolute at left 12px, 24x24, `scale(.25) rotate(0)`. Its `::before` is an accent circle at 100% size. Its child `.burger__close-icon` holds a 10x10 black X SVG (rendered 8x8) at opacity 0. Measured box at 768: x688 y40 40x22.
- Open state (`.burger--open`):
  - Dot 1 `translateX(10px)` and dot 3 `translateX(-10px)`, both z −1 (they merge under the center).
  - Dot 2 `scale(1) rotate(180deg)`.
  - The `::before` goes to `scale(5)` with opacity 0 (the accent circle bursts out).
  - The close X fades to opacity 1. Measured dot 2 is 24x24 at 700,39.
- Panel `.navbar__nav`: absolute, **top 60px, right 48px**. Closed: `translateY(60px)`, opacity 0, visibility hidden. Open (`.open`): `translateY(0)`, opacity 1, visible. Transition **.5s cubic-bezier(.16,1,.3,1)** on opacity, transform, and visibility.
- `ul` styles: flex column, bg accent, color black, radius 10px, padding 12px, align flex-end, text-align right, gap 2.0833vw (16px at 768). Links are 14px/21px uppercase. Roadmap is hidden; the arrow SVG path becomes black. Measured panel at 768: x575.7 y80 w144.3 h193.
- Clicking any item, or clicking anywhere on the body, closes the menu. The navbar gets `.navbar--fixed` while open, so it is never hidden by `nav-hidden`.

### 7.2 Popup "Join the beta" (opened by "Try now", "Get a beta", and the nav "Join the beta")
- `.popup`: fixed inset 0, z 5000, flex center. Vue transition `popup`: enter-from is opacity 0, visibility hidden, window `translateY(60px)`. Transition `.3s ease` on opacity and visibility (the window animates opacity and transform at .3s ease).
- Opening sets `ss.isFixed = true`, which locks the smooth scroll.
- `.popup__backdrop`: absolute inset 0, rgba(0,0,0,.8). Clicking it closes the popup.
- `.popup__window`: bg accent, color black, padding **2.0833vw** (30px; ≤1060 20px 16px), radius 12px, **max-width 44.2708vw** (637.5px; ≤1060 80%, ≤768 85%, ≤460 90%), width 100%. Measured at 768: 652.8x299 at 57.6,362.5.
- Contents:
  - `button.popup__btn`: absolute, top/right 1.3542vw (19.5px; ≤1060 14px / 12px), with the 28x28 close SVG.
  - `form.form.popup__form[novalidate]` (margin-top 2.7083vw):
    - `legend.popup__form-h` **"Join the beta"** (3.75vw = 54px; ≤1060 36px; Aeonik, lh 1em).
    - Input 1 `#name`: label **"Your Name"**, not required. Margin-top 3.125vw (45px; ≤1060 52px).
    - Input 2 `#email-2`: label **"Your Email"** + red `*`, required, email validation, error text "incorrect email". Margin-top 2.6042vw (37.5px; ≤1060 40px).
    - Popup inputs have a 2px black bottom border and black text.
    - `button.button.popup__form-btn` **"Join"**: margin-top 1.6667vw (24px; ≤1060 28px), margin-left auto (right-aligned), black underline.
- Submitting closes the popup after the request.

### 7.3 FAQ accordion
- Item: relative, cursor pointer, overflow hidden, z 1. Children:
  - `.accordion__overlay` (§5.13).
  - `.grid.accordion__cols` (padding 1.4583vw 0 = 21px; ≤1060 flex space-between, padding 20px 0):
    - `.h3.accordion__num` (col 1/3, row 1/3) showing "01".
    - `h3.h4.accordion__h4` (col 6/12).
    - `.accordion__arrow` (col 11/13, justify-self end, 1.25vw = 18px; ≤1060 16px) with the 34x34 down-arrow SVG, fill accent.
  - `.accordion__text` (innerHTML answer). Height 0; desktop margin-left 38.0208vw (547.5px), width 39.4792vw (568.5px), 15px, lh 1.5em.
  - `.h-line.accordion__line`, absolute at bottom 0.
- Click toggles `.opened`:
  - Text height becomes `calc(var(--h)*100)`, where JS sets `--h = scrollHeight*0.01px` (so the target is the full content height), with margin-bottom 1.4583vw (≤1060 20px). Transition **.45s cubic-bezier(.16,1,.3,1)** on height and margin.
  - Arrow `rotate(180deg)` (.45s same ease).
  - The overlay is forced to height 0.
- Multiple items can be open at once. All start closed.

### 7.4 Forms and inputs (footer and popup share the component)
- `.input-wrapper` (relative) contains the `input.input`, a `label.input-placeholder` acting as the visual placeholder (absolute, top 40%, `translateY(-50%)`, left 0, flex, gap 8px, uppercase), and a required `abbr` that is red with no underline.
- Focus, or a non-empty value, adds `.js-focus`: the label moves to `translateY(-30px)` with font-size **10px** and opacity .7. Transition `.3s ease` on opacity, transform, and font-size. Blur with an empty value reverts it.
- Footer input: Aeonik 16px, accent text, transparent, `border-bottom: 2px solid accent`, padding-bottom .3646vw (5.25px; ≤1060 7px), padding-right 4.1667vw (60px; ≤1060 80px), radius 0. The "Join" button is absolute at right 0, bottom 10px, Aeonik 1.0417vw (≤1060 20px).
- Validation: email regex plus required. An invalid submit focuses the field and shows `small.input-error` "incorrect email" (12px, red, lowercase, absolute, margin-top 4px).
- Submit:
  - `POST https://formspree.io/f/xyyvopzy` with `mode: 'no-cors'` and FormData `{ "From:": "Flashform Website", "Email": <value> }`. The popup also sends `"Name"`.
  - The `.app-loader` spinner shows while waiting: fixed top 30px, centered, white circle 4.1667vw (60px; ≤1060 `calc(46px + 34*((100vw − 375px)/1545))`), with an accent stroke spinner inside. It hides 400ms after the request finishes.
  - Success toast: **"You have successfully registered for the beta"**. Error toast: **"An error has occurred:("**.
  - Fields reset on success.

### 7.5 Toasts
- `.container.toast-container`: fixed, z 10000, top 10%, right-aligned via `margin-left: auto` on each toast.
- `.toast`: 16px, bg black, color white, radius 5px, padding 12px, flex space-between center, cursor pointer, overflow hidden. Consecutive toasts are spaced 10px apart.
  - `--success`: bg accent, text black.
  - `--danger`: bg red.
- A 2px progress bar at the top (white; black on success) grows from width 0 to 100% over **5s linear**, then the toast auto-dismisses. The close button is 16x16 with margin-left 20px.
- Enter and leave use a Vue `fade` transition (out-in). **Uncertain:** the fade CSS is not in the bundle, so duration is unknown; .2s is a reasonable default.

---

## 8. Known gaps and uncertainty
1. **WebGL** (hero flower, revealer) and the **matter.js** footer are canvas-rendered. Their look comes from verbatim shader and physics source (in `reference/shaders/` and §5.12), not from DOM measurement. Physics output is random by nature.
2. **Loader visuals:** viewport screenshots of the loader came back blank because the capture fired before first paint after reload. The timeline in §5.1 comes from source plus 150ms DOM sampling. No pixel reference of the loader exists.
3. **CardsScale** timing (§5.8) is given as measured samples. The original `end: "+=bottom"` string makes the exact curve implementation-specific.
4. **1440 full-page** is stitched from viewport captures of a scroll-jacked page. Use the `1440-vp-*` frames for exact per-position comparisons.
5. **Vue `fade` / `page` transition** CSS for toasts and the app-loader is only partly in the bundle (`.page-enter-active{transition: all .2s}`); the toast fade duration is not defined in CSS.
6. **Button font** is the UA default (measured Arial on Chromium/macOS). Other browsers or OSes may differ; matching Chromium means setting Arial explicitly.
7. **`mix-blend-mode: difference` on the navbar** changes its perceived color depending on what is behind it. Implement the blend; do not hard-code a color.
