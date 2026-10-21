# Flashform design-repo

An AI-ready, machine-validated design system extracted from the Flashform clone (the sibling React 18 + Vite 5 +
Tailwind 3 project that reproduces https://www.flshfrm.com/). A generator composes a **PageSpec** from the sections
here, and the validators reject anything off-brand, out of order, over budget, or non-compliant.

**Status: `design-review-pending`, `productionApproved: false`.** This is a private reference build of a real,
live company's site. Do not publish it or make the repository public.

## Read this first: constraints that are load-bearing

1. **Forms are stubbed on purpose.** The clone sets `FORM_ENDPOINT = null` (`src/components/submitForm.js`). The
   original posts to a third-party Formspree endpoint (`formspree.io/f/xyyvopzy`) owned by the original site's owner.
   A PageSpec declares `forms.submission: "stub"` or an owner-supplied `https://` endpoint. The original endpoint is
   rejected by rule `FORM_ENDPOINT_NOT_ORIGINAL`.
2. **Real company, proprietary content.** The copy, the videos (`1.mp4`, `2.mp4`, `screencast.mp4`), the OG image
   (`twitter.png`), the logo and the favicon belong to the original owner. The footer also links real people's
   contact channels: an agency email, a personal WhatsApp number and a Telegram handle.
   `schema/example.pagespec.json` reproduces all of it verbatim as a fidelity reference only
   (`mode: "reference"`, `contentProvenance: "original-reference"`). A page generated for any other brand must be
   `mode: "generated"` (`contentProvenance: "new-content"`). For those pages the validator rejects the real Flashform
   logo and every other registered source-brand asset (see "Modes" below), the original copy (any 6+-word string), the
   original contacts, and the original's proprietary media.
3. **Commercial fonts.** Aeonik, Recife Display and Neue Haas Display are self-hosted from the original. Recife is
   the BookItalic cut but is declared `font-style: normal`; never add `font-style: italic` to it. A licence is
   required for any new deployment; otherwise use the declared fallback stack. See
   `tokens/00-foundation/typography.json` → `$extensions.licensing`.
4. **Third-party brand marks.** The WhatsApp, Telegram, Messenger and Discord icons are third-party trademarks. Their
   role `icon.third-party-channel` is pinned to `must-not-fabricate`.
5. **No AI generation of real logos, real people, or the original's proprietary content.** This is enforced by the
   closed asset-role contract in `assets/asset-roles.json`. Its `pinnedPolicies` and `pinnedAvailability` are
   drift-checked by `verify_all.py`.
6. **There is one route and one template.** `/` is the only route. Nav items are in-page anchors (`#why`,
   `#integration`, `#benefits`, `#roadmap`, `#faq`) plus the "Join the beta" popup. All footer links are external.
   The layout has one breakpoint at 1060px, and desktop sizes are vw on a 1440 design width. At exactly 768px the
   hero shows **no** "Try now" button.
7. **Motion quirks are kept on purpose** (ported line for line from the original bundle):
   - `ease: "linear.none"` is not a registered GSAP ease, so it falls back to `power1.out`.
   - ScrollTriggers are created at staged times: the Revealer on the 2nd frame, scroll effects at +1000ms, and the
     physics letters at +2000ms.
   - The page reloads on resize above 768px.
   - The hero shader's `u_mousePosition` is effectively always `(0,0)`.
8. **The clone folder is a git repository.** `design-repo.zip` is gitignored and no zip is tracked. Regenerate it
   fresh, last, after validation, and never commit it.

## Modes: reference vs generated (brand handling)

Every PageSpec carries a required, closed `mode` (schema `properties.mode`, enum `reference | generated`, PageSpec
`1.1.0`):

| mode | purpose | `contentProvenance` | real Flashform roles |
|---|---|---|---|
| `reference` | clone / fidelity validation of the source brand | must be `original-reference` | allowed: `brand.logo` + `asset:logo-flashform`, `asset:favicon`, `asset:og-twitter`, the original's videos |
| `generated` | a new site for any other brand | must be `new-content` | **rejected** (error `GENERATED_MODE_BLOCKS_REFERENCE_ASSETS`) |

**The exact rule.** In `mode: "generated"`, no field of any node or of `meta` may reference an asset role whose
`availability` is `reference-only` or `blocked-in-generated` (any ref kind), nor a registered asset id whose
availability is not `generation-safe`; no text field may mention such an id. The navbar and footer logo must use a
generation-safe brand mark role (`GENERATED_MODE_REQUIRES_BRAND_MARK`), so a generated page never needs the real
Flashform trademark. `mode` and `contentProvenance` must agree (`MODE_PROVENANCE_CONSISTENT`). In `reference` mode the
real roles stay allowed.

`assets/asset-roles.json` gives every role an explicit `availability` (`generation-safe`, `reference-only`,
`blocked-in-generated`; vocabulary in `availabilityVocabulary`). The protected registered assets (logo, favicon, OG
image, the original's videos) carry their own. `brand.logo` is `reference-only` and **pinned**: its role, `asset:logo-flashform` (`reference-only`) and
`asset:favicon` (`blocked-in-generated`) are pinned both in the file (`pinnedAvailability`, `pinnedAssetAvailability`)
and in `semantic_validate.py`; `verify_all.py` (check 11) fails if either drifts.

Generation-safe brand roles (all settable in the navbar and footer `logo` field):

| role | assetRef | guidance |
|---|---|---|
| `brand.placeholder` | `generated:<slot>` | neutral text wordmark of the page's own brand name; no artwork |
| `brand.user-supplied` | `owner-supplied:<slot>` | the page owner's own logo; the slot is left for the owner to fill |
| `brand.generated-mark` | `generated:<slot>` | a new abstract geometric mark; must not resemble the Flashform logo or flower mark |

`schema/example.pagespec.json` is the reference example; `schema/example.generated.pagespec.json` is a generated
example for a fictional brand ("Fernwick Demo") that uses `brand.placeholder`. Both must validate with 0 errors and 0
warnings. Roles that are not Flashform's brand mark (shaders, UI glyphs, the third-party messenger marks, the
commercial fonts and the physics letter sprites) keep their previous policy and are classified `generation-safe`; see the
CHANGELOG for what that classification does and does not mean.

## Layout

```
design-repo/
  README.md  CHANGELOG.md  registry.manifest.json
  tokens/00-foundation/   color typography radius spacing breakpoint elevation icon-size motion
  tokens/10-semantic/     color-roles typography-roles motion-roles
  tokens/20-component/    button navbar input card rounded-panel accordion popup toast ticker
  tokens/30-layout/       container grid section-spacing z-index
  tokens/themes/          flashform-dark (the only theme; resolves every colour role)
  tokens/llm/             token-catalog  token-policy  component-allowlist
  primitives/             primitive contracts
  components/             component contracts
  sections/               section contracts (content schema, word budgets, motion, responsive, a11y, citations)
  templates/templates.json        templates + routes, structured nodes {section, variant, required, repeatable}
  compatibility/graph.json        rules, each with severity error|warn
  assets/asset-roles.json         closed roles, policies, licensing, modes, availability, pinned policies/availability
  schema/pagespec.schema.json     Draft-07 machine contract
  schema/example.pagespec.json    the real page, verbatim (mode reference, original-reference)
  schema/example.generated.pagespec.json  a generated page for a fictional brand (mode generated, brand.placeholder)
  schema/semantic_validate.py     what JSON Schema cannot express
  schema/tests/adversarial_test.py
  extraction/measured-values.json citation ledger + corrections to the groundwork
  extraction/evidence/            Playwright QA JSON + colour/type histogram, copied in so the repo is self-contained
  extraction/verify_all.py        all checks in one run
  extraction/drift_test.py        proves verify_all catches drift
```

<!-- counts:start -->
- tokensFoundation: 137
- tokensSemantic: 40
- tokensComponent: 36
- tokensLayout: 18
- primitives: 8
- components: 20
- sections: 11
- templates: 1
- routes: 1
- assetRoles: 16
- assetRolesSettable: 13
- graphRules: 27
- adversarialMutations: 91
- themes: 1
<!-- counts:end -->

This block is checked against the files by `verify_all.py` (check 9).

## Sections (retrieval units)

| id | variants | purpose |
|---|---|---|
| `shell.navbar` | - | brand, anchors, "Join the beta" |
| `hero.sticky-statement` | - | pinned one-line promise over the WebGL flower |
| `split.media-statement` | `media-left`, `media-right` | mixed-italic heading + redline paragraph + blend-lighten video |
| `panel.rounded-sticky` | `with-channel-list`, `items-only` | accent card that scales in and pins while its column scrolls |
| `scroll.horizontal-steps` | - | sideways headline, 4 steps, screencast dissolving to black |
| `statement.centered-cta` | - | centred uppercase pitch + "Get a beta" |
| `grid.ticker-benefit-cards` | - | tilted marquee + exactly 6 staggered accent cards |
| `statement.audience-rows` | - | two-line heading + ruled audience rows |
| `timeline.horizontal-roadmap` | - | giant numeral + drawn curve with exactly 3 milestones (desktop only) |
| `faq.accordion` | - | 375px "FAQ" + multi-open accordion |
| `shell.footer` | - | physics "STAY IN TOUCH" letters, contacts, beta form, legal |

## How a generator uses this

0. Choose `mode`: `generated` for any brand other than Flashform (use a `brand.*` generation-safe logo role), `reference`
   only to reproduce the Flashform page itself.
1. Read `tokens/llm/component-allowlist.json` to see the closed set of sections and their settable properties.
2. Read `templates/templates.json`. PageSpec nodes must be an **ordered subsequence** of the template's nodes. The
   navbar, hero and footer are required. Content sections may be omitted, but never reordered or repeated. When you
   omit a section, remove its nav link (`NAV_LINKS_RESOLVE`).
3. Fill each node's `content` within the section's `wordBudgets`. For each media field, use an allowed `assetRole`
   and an `assetRef` the role's policy permits (`asset:`, `owner-supplied:`, or `generated:` only where the role is
   `may-generate-new`).
4. Copy each section's `motion` (`patterns`, `reducedMotionFallback`, and thresholds where relevant). The schema
   locks the fallback per section.
5. Validate the result: `python3 -I schema/semantic_validate.py my-page.json`.

The PageSpec has **no** per-instance style or token override field. Styling is owned entirely by the
section/component contracts (`tokens/llm/token-policy.json` → `enforced`).

## Verify

Requires Python 3.8+ with `jsonschema`. Run every command with `-I`.

```
python3 -I extraction/verify_all.py          # all checks; standalone copies warn-skip external citations
python3 -I schema/tests/adversarial_test.py  # mutations rejected, controls pass
python3 -I extraction/drift_test.py          # proves the checks catch injected drift
python3 -I schema/semantic_validate.py       # validates every bundled example (reference + generated)
```

Citations are `path:line[-line]` plus an `expect` snippet that must appear in the cited range. Paths starting
with `@repo/` are inside this folder. All other paths are relative to the sibling clone project (`src/`,
`reference/`, `CLONE_SPEC.md`, `index.html`, `package.json`). If that project is absent, those citations warn and
are skipped, and the checks do not fail.

## Evidence priority

1. Playwright QA of the live original (`extraction/evidence/qa-*.json`).
2. The original's CSS/JS (`reference/original-entry.319c9ada.pretty.css`, the bundle).
3. The clone source `src/`.
4. `CLONE_SPEC.md` prose.

Where they disagree, `extraction/measured-values.json` records the correction under `supersedes`.
