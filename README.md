# Flashform clone

A local React 18 + Vite + Tailwind v3 replica of https://www.flshfrm.com/.

```bash
npm install
npm run dev      # http://localhost:5181
npm run build
```

## Information architecture

`ia.json` is the only IA file to edit by hand. `IA.md` and `matrix.csv` are generated from it and get overwritten on every build. After changing `ia.json`, rerun:

```bash
node validate.mjs && node build.mjs
```

### What the data shows

- **1 route, 1 template, 19 sections.** The site is a single scrolling page. The nav links are in-page anchors (`#why`, `#integration`, `#benefits`, `#roadmap`, `#faq`), and every footer link goes off-site. The 19 sections are 15 that appear in page order and 4 shell pieces: the beta popup, the scrollbar, the toasts and the spinner.
- **Sharing across templates tells you nothing here.** With one template, every section is "single-use" by definition, so `validate.mjs` reports `0 shared` and that isn't a problem. The reuse that matters is between components. `RoundedSection.jsx` renders both green scaling panels (`story.purpose`, `value.problems`). The same reveal, scale and horizontal-scroll code in `src/anim/` drives several sections.
- **The width differences are within the one route.** At ≤1060px the burger menu replaces the navbar links, the custom scrollbar goes away, and `roadmap.timeline` is hidden.

### Validator notes to leave as they are

`validate.mjs` flags `1060` in four `scope` strings as not matching the computed route count (`1`). That number is the breakpoint in pixels, not a route count, so don't change the text to say "1".

## Things to know

- **Forms are switched off.** `FORM_ENDPOINT = null` in `src/components/submitForm.js`, so submitting shows the success toast but sends nothing. Put your own endpoint there to collect signups.
- **The copy, videos, fonts and icons come from the original site.**
  - Copy, videos and the OG image: Flashform's own content.
  - Fonts (Aeonik, Recife Display, Neue Haas Display): commercial typefaces.
  - Messenger icons: third-party trademarks.

  Check the licences before publishing any of these.
- `CLONE_SPEC.md` and `reference/` hold the measurements and screenshots taken from the live site.
