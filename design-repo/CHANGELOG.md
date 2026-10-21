# Changelog

## 1.1.0 (2026-10-21): generation-safe brand handling

Review item: generated sites must not be able to reuse the real Flashform trademark. Verified first against the
repo: `brand.logo` (`must-not-fabricate`) was the only role the navbar/footer `logo` field accepted, and the
validator accepted `asset:logo-flashform` in a `new-content` page (only owner-supplied-only media was blocked there),
so a page generated for another brand could carry the real logo. `asset:favicon` was likewise accepted. This was a
real gap, not a stale claim.

### Added
- **PageSpec `mode`** (required, closed enum `reference | generated`), `pageSpecVersion` 1.1.0. `reference` is clone /
  fidelity validation of the source brand; `generated` is a new site for another brand. It must agree with the
  existing `contentProvenance` (`reference` <-> `original-reference`, `generated` <-> `new-content`); the existing
  new-content rules now key on `mode`.
- **`availability`** on every role in `assets/asset-roles.json` (`generation-safe | reference-only |
  blocked-in-generated`) and on each registered asset of a protected role. `brand.logo` is `reference-only`;
  the registered favicon, OG image and the original's videos/screencast are `blocked-in-generated`.
  Pinned: `brand.logo` -> `reference-only`, `asset:logo-flashform` -> `reference-only`, `asset:favicon` ->
  `blocked-in-generated`, both in the file and in `semantic_validate.py` (a change to a different but still valid
  value is rejected).
- **Roles `brand.placeholder`, `brand.user-supplied`, `brand.generated-mark`** (generation-safe, with
  `generationGuidance` and `allowedRefKinds`). Navbar and footer `logo` accept these four brand roles; the real
  one is only valid in reference mode.
- **Rules** `MODE_PROVENANCE_CONSISTENT`, `GENERATED_MODE_BLOCKS_REFERENCE_ASSETS`,
  `GENERATED_MODE_REQUIRES_BRAND_MARK` (graph + validator, 24 -> 27 rules).
- **`schema/example.generated.pagespec.json`**: a generated page for a fictional brand using `brand.placeholder`.
- **Adversarial coverage** (57 -> 91 mutations incl. 12 registry mutations; 4 -> 9 controls): generated spec with the
  real logo (nav, footer, either alone, any ref kind), real favicon / OG image / video, the real logo id smuggled
  into a text field, missing / invalid mode, mode vs provenance mismatch, real-logo availability changed to another valid
  value; controls: both examples, each generation-safe brand role, a reference-mode spec with the real logo.
- **verify_all**: every `example*.pagespec.json` is schema- and semantically validated; check 11 adds availability
  (closed enum, every role classified, protected assets explicit, pins); new check 15 `modes` (schema enum == validator ==
  asset-roles, logo role enums == brand roles, example/generated-example consistency, manifest lists both). The drift test
  gains 18 injected drifts (15 -> 33), each proven caught on a scratch copy.

### Changed
- `allowlistVersion` 1.1.0 (machine-checked), `pageSpecVersion` 1.1.0, `repositoryVersion` 1.1.0 (documentation-only).
  Manifest `counts` and the README counts block were recomputed from the files, not hand-bumped.
- The README / manifest / measured-values said the clone folder is not a git repository. It is one now (remote
  Riiyotta/flashform); `design-repo.zip` is gitignored and untracked. Corrected.

### Not changed, on purpose (stated so it is not mistaken for coverage)
- Other roles (UI glyphs, shaders, the physics letter sprites, the commercial fonts, the third-party messenger marks)
  keep their policy and are classified `generation-safe`. That means "may appear in a generated page under its existing
  policy" (the messenger marks only as unmodified official marks, the fonts only with a licence), not that they are
  free of third-party rights.
- Status stays `design-review-pending`, `productionApproved: false`.

## 1.0.0 (2026-10-16): initial build

This repo was built from scratch, bottom-up: tokens → primitives → components → sections → template →
compatibility graph → schema → example → semantic validator → adversarial tests → manifest/allowlist/docs.

### Built
- Tokens in DTCG `$value`/`$type` form. Each token carries `$extensions.measuredFrom` citations that include an
  `expect` snippet. The colour palette matches the 1440 computed-style histogram of the live original exactly.
- Section contracts for each distinct section type, with closed content schemas, word budgets, per-section closed
  motion (locked `reducedMotionFallback`), structured responsive changes cited to real CSS, and accessibility notes.
- One template (`template.single-page-landing`) with structured nodes, mapped 1:1 to the only route `/`.
- A compatibility graph whose rule ids match the validator's `RULES` one-to-one; severity is read from the graph at
  runtime.
- A closed asset-role vocabulary. Each role has a generation policy, licensing guidance and pinned policies for the
  legally weighty roles.
- A `contentProvenance` mechanism. The bundled example is the real page (`original-reference`); generated pages
  (`new-content`) have the original copy, contacts and proprietary media rejected.
- `verify_all.py` (all checks), `drift_test.py` (proves those checks catch drift) and the adversarial suite.

### Groundwork claims found wrong or stale, and corrected
The groundwork was a strong first draft. These claims did not hold against the original bundle, the QA
measurements, or the current src. Each correction is recorded in `extraction/measured-values.json` under
`supersedes`:
- **Loader length:** CLONE_SPEC §5.1 says the loader is removed at ~5.7s. Playwright QA of the live original shows
  it first observed at 296ms and removed at 6368ms, which is **~6.07s from first paint**. The original awaits Nuxt
  hydration and dynamic module imports before its timeline. When this build started, the clone's timeline ran 5.4s
  from React mount. During the build, the animation-fix pass added a `MOUNT_AT = 800ms` offset, which brings the
  clone to ~6.2s (see the drift section below).
- **"linear" eases:** CLONE_SPEC §5.4, §5.7 and §5.8 describe SectionScale, the Revealer and CardsScale as
  "linear". The original passes `"linear.none"`, which GSAP does not register, so the **effective ease is
  power1.out**. Confirmed in the original `SectionScale-*.js`, `CardsScale-*.js` and `Revealers-*.js`. The token
  `motion.ease.gsap-scrub-effective` records the effective value.
- **Hero `u_mousePosition`:** CLONE_SPEC §5.6 says it tracks the normalised mouse position and changes the petal
  count. In the original `Butterfly-*.js` the inertia objects are overwritten with plain numbers, so
  `new Vec2(x.value, y.value)` is **(0,0) on every frame**: always 3 petals, always x1.5 brightness.
- **Braced italic copy:** the original HTML renders `" {easier} "` and `" {messengers} "` with surrounding spaces.
  The example follows the original HTML. At build time `src/components/Why.jsx` had the spaces (the pixel-audit
  agent added them mid-build) and `Messengers.jsx` did not.
- **Undocumented quirk:** `.ticker__item` sets `color: var(--main)`, and `--main` is never defined anywhere. The
  colour therefore resolves through inheritance to the accent.
- **Column-1 loader hold until ~2.5s:** this figure was reported by the QA pass, but no field in the copied QA JSON
  records it. It is recorded as `reported-not-re-verified`, not as a measured value.

### Decisions (not measured values; stated so they are not mistaken for evidence)
- `maxWords = observed + max(1, ceil(observed × 0.2))`, applied uniformly.
- Template requiredness: the navbar, hero and footer are required; the other 10 nodes are optional but keep their
  order. The observed page contains all of them.
- `NO_ADJACENT_SCROLL_STAGES` has severity `warn`. It is rhythm guidance derived from the single observed
  composition, not a measured breakage.
- Item maxima equal the observed counts (for example FAQ ≤ 4 and audience rows ≤ 2). Benefit cards (exactly 6) and
  roadmap milestones (exactly 3) are fixed because the CSS places them by `nth-of-type`.

### Source drift observed during this build (the clone was being edited concurrently)
`src/` was snapshotted when the build started (12:30) and diffed again immediately before packaging. The builder
resolves every citation by searching for its quoted snippet, so line shifts were absorbed automatically. Afterwards
`verify_all.py` re-checked all ~540 `expect` snippets against the current source. These changes affected the repo's
claims:
- `src/anim/core.js` + `src/anim/loader.js` + `src/App.jsx`: the new `MOUNT_AT = 800`. The loader timeline and
  `initPage()` are now deferred to 800ms after navigation start, so the clone loader ends at ~6.2s instead of
  5.4s, and every staged ScrollTrigger is now staged from that mount. Added the token
  `motion.loader.clone-mount-offset-ms`, and updated `loader.clone-duration` and `scrolltriggers.staged` in
  measured-values.
- `src/components/Why.jsx`: the italic span changed from `{easier}` to ` {easier} `, matching the original HTML.
  After packaging, `src/components/Messengers.jsx` (`{messengers}` → ` {messengers} `) and `src/components/Meaning.jsx`
  (`Flashform?` → ` Flashform? `) were changed the same way, so all three braced/italic spans now match the original
  HTML. Re-measured at 1440: `.home-2__h` 630×338 and `.home-6__h` 1290×338 on both sites. The example already
  followed the original, and no citation moved.
- `src/index.css`: two blocks were appended (`button{...:revert}`, `svg,canvas{display:inline}`) and all later lines
  shifted. These are preflight-undo fixes that make UA button fonts and inline SVGs match the original. They do not
  change any token value.
- `src/anim/smoothScroll.js` + `src/App.jsx`: the custom scrollbar is now created and removed by SmoothScroll, as in
  the original `CreateScrollbar`, instead of being static markup. No token changed.
- `src/components/Toasts.jsx`, `BetaPopup.jsx`, `Input.jsx`, `Benefits.jsx`: markup fidelity fixes (the real
  15x14 toast-close path, `toast__message`, `popup__close-icon`, `form__input`, and `--dir` no longer inline). No
  contract value changed.
- `tailwind.config.js`: unchanged.
