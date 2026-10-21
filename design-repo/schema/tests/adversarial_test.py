#!/usr/bin/env python3
"""Adversarial suite: every mutation must be REJECTED (by the expected layer), every control must PASS.

Controls are synthesised generically: for every template in templates/templates.json the suite builds
(a) the full node list and (b) a required-nodes-only page from that template's own node list, so a new or
split template is covered with zero new control code. The bundled generated example (schema/example.generated.pagespec.json,
mode "generated") is the base for the generated-mode controls and mutations: it proves the compliance rules do not
reject legitimate generated pages, and that each generation-safe brand role passes.
REGISTRY_MUTATIONS mutate an in-memory copy of assets/asset-roles.json and must be rejected by the shared pinned /
closed-enum check semantic_validate.availability_errors (the same function verify_all check 11 runs).

Usage: python3 -I schema/tests/adversarial_test.py     (exit 1 on any failed expectation)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'schema'))
import semantic_validate as sv  # noqa: E402

REPO = sv.Repo()
with open(os.path.join(ROOT, 'schema', 'example.pagespec.json'), encoding='utf-8') as f:
    EXAMPLE = json.load(f)


def node(spec, nid):
    return next(n for n in spec['nodes'] if n['id'] == nid)


def drop(spec, *ids):
    spec['nodes'] = [n for n in spec['nodes'] if n['id'] not in ids]


def set_links(spec, hrefs):
    nav = node(spec, 'nav')
    nav['content']['links'] = [l for l in nav['content']['links'] if l['href'] in hrefs]


def brand(spec, role, ref):
    """Set the navbar + footer logo of a spec to {role, ref}."""
    for n in spec['nodes']:
        if n['section'] in ('shell.navbar', 'shell.footer'):
            n['content']['logo'] = {'assetRole': role, 'assetRef': ref}


with open(os.path.join(ROOT, 'schema', 'example.generated.pagespec.json'), encoding='utf-8') as f:
    NEW = json.load(f)  # the bundled generated example (mode generated): the base for every generated-mode mutation


def controls():
    out = [('example.pagespec.json (unmutated)', copy.deepcopy(EXAMPLE)), ('example.generated.pagespec.json (unmutated, mode generated)', copy.deepcopy(NEW))]
    for role, ref in (('brand.placeholder', 'generated:placeholder-logo'), ('brand.user-supplied', 'owner-supplied:logo'), ('brand.generated-mark', 'generated:brand-mark')):
        g = copy.deepcopy(NEW)
        brand(g, role, ref)
        out.append((f'generated mode with {role} ({ref})', g))
    out.append(('reference-mode spec with the real Flashform logo (brand.logo / asset:logo-flashform)', copy.deepcopy(EXAMPLE)))
    by_key = {(n['section'], n.get('variant')): n for n in EXAMPLE['nodes']}
    for tid, t in REPO.templates['templates'].items():
        full = copy.deepcopy(EXAMPLE)
        full['template'] = tid
        full['nodes'] = [copy.deepcopy(by_key[(tn['section'], tn.get('variant'))]) for tn in t['nodes']]
        out.append((f'{tid}: all template nodes', full))
        req = copy.deepcopy(full)
        req_keys = {(tn['section'], tn.get('variant')) for tn in t['nodes'] if tn['required']}
        req['nodes'] = [n for n in req['nodes'] if (n['section'], n.get('variant')) in req_keys]
        anchors = {n.get('anchorId') for n in req['nodes']}
        for n in req['nodes']:
            if n['section'] == 'shell.navbar':
                n['content']['links'] = [l for l in n['content']['links'] if l['href'][1:] in anchors] or None
                if n['content']['links'] is None:
                    # a navbar needs >=1 link (schema minItems 1); point it at the hero via an anchor
                    hero = next(x for x in req['nodes'] if x['section'].startswith('hero.'))
                    hero['anchorId'] = 'top'
                    n['content']['links'] = [{'label': 'Top', 'href': '#top', 'mobileHidden': False}]
        out.append((f'{tid}: required nodes only', req))
    return out


def M(name, expect, fn, base=None, warn_only=False):
    return (name, expect, fn, base, warn_only)


def mut(f):
    return f


def _first_cta_label(s):
    node(s, 'hero')['content']['cta']['label'] = 'x'


MUTATIONS = [
    # ---------------- schema layer
    M('wrong template enum', 'SCHEMA', lambda s: s.__setitem__('template', 'template.home')),
    M('invented section type alias', 'SCHEMA', lambda s: node(s, 'hero').__setitem__('section', 'hero.marketing')),
    M('missing reducedMotionFallback', 'SCHEMA', lambda s: node(s, 'hero')['motion'].pop('reducedMotionFallback')),
    M('wrong reducedMotionFallback for section', 'SCHEMA', lambda s: node(s, 'hero')['motion'].__setitem__('reducedMotionFallback', 'native-vertical-flow')),
    M('invented motion field', 'SCHEMA', lambda s: node(s, 'meaning')['motion'].__setitem__('inventedAnimation', 'spin')),
    M('motion pattern not allowed for section', 'SCHEMA', lambda s: node(s, 'messengers')['motion'].__setitem__('patterns', ['ticker-marquee'])),
    M('invented inView threshold', 'SCHEMA', lambda s: node(s, 'meaning')['motion'].__setitem__('inViewThresholds', [0.7])),
    M('invented assetRole', 'SCHEMA', lambda s: node(s, 'meaning')['content']['media'].__setitem__('assetRole', 'image')),
    M('assetRole wrong for field', 'SCHEMA', lambda s: node(s, 'meaning')['content']['media'].__setitem__('assetRole', 'media.product-screencast')),
    M('benefit cards != 6 (fixed nth-of-type grid)', 'SCHEMA', lambda s: node(s, 'benefits')['content']['cards'].pop()),
    M('roadmap milestones != 3', 'SCHEMA', lambda s: node(s, 'roadmap')['content']['milestones'].pop()),
    M('roadmap title without braces', 'SCHEMA', lambda s: node(s, 'roadmap')['content']['milestones'][0].__setitem__('title', 'Beta release')),
    M('extra content property', 'SCHEMA', lambda s: node(s, 'hero')['content'].__setitem__('subtitle', 'x')),
    M('variant on a variant-less section', 'SCHEMA', lambda s: node(s, 'hero').__setitem__('variant', 'centered')),
    M('missing variant on a variant section', 'SCHEMA', lambda s: node(s, 'meaning').pop('variant')),
    M('anchorId on a shell section', 'SCHEMA', lambda s: node(s, 'footer').__setitem__('anchorId', 'contact')),
    M('invented cta action', 'SCHEMA', lambda s: node(s, 'hero')['content']['cta'].__setitem__('action', 'open-url')),
    M('missing meta', 'SCHEMA', lambda s: s.pop('meta')),
    M('non-https form endpoint', 'SCHEMA', lambda s: s.__setitem__('forms', {'submission': 'owner-endpoint', 'endpoint': 'http://example.com/f'})),
    M('wrong pageSpecVersion', 'SCHEMA', lambda s: s.__setitem__('pageSpecVersion', '2.0.0')),
    M('missing mode', 'SCHEMA', lambda s: s.pop('mode')),
    M('missing mode (generated example)', 'SCHEMA', lambda s: s.pop('mode'), base='new'),
    M('invalid mode value', 'SCHEMA', lambda s: s.__setitem__('mode', 'clone')),
    M('invalid mode value (wrong case)', 'SCHEMA', lambda s: s.__setitem__('mode', 'Generated'), base='new'),
    M('invalid mode value (both modes)', 'SCHEMA', lambda s: s.__setitem__('mode', ['reference', 'generated'])),
    M('footer logo missing', 'SCHEMA', lambda s: node(s, 'footer')['content'].pop('logo'), base='new'),
    M('logo role outside the brand roles', 'SCHEMA', lambda s: node(s, 'nav')['content'].__setitem__('logo', {'assetRole': 'meta.favicon', 'assetRef': 'asset:favicon'}), base='new'),
    M('brand.placeholder with an asset: ref', 'ASSET_REF_POLICY', lambda s: brand(s, 'brand.placeholder', 'asset:logo-flashform'), base='new'),
    M('brand.user-supplied with a generated: ref', 'ASSET_REF_POLICY', lambda s: brand(s, 'brand.user-supplied', 'generated:logo'), base='new'),
    M('brand.generated-mark with an owner-supplied: ref', 'ASSET_REF_POLICY', lambda s: brand(s, 'brand.generated-mark', 'owner-supplied:logo'), base='new'),
    # ---------------- mode rules: the real Flashform logo cannot appear in another generated brand
    M('mode reference but contentProvenance new-content', 'MODE_PROVENANCE_CONSISTENT', lambda s: s.__setitem__('contentProvenance', 'new-content')),
    M('mode generated but contentProvenance original-reference', 'MODE_PROVENANCE_CONSISTENT', lambda s: s.__setitem__('contentProvenance', 'original-reference'), base='new'),
    M('generated mode: the real Flashform logo (nav + footer)', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: brand(s, 'brand.logo', 'asset:logo-flashform'), base='new'),
    M('generated mode: real logo in the navbar only', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: node(s, 'nav')['content'].__setitem__('logo', {'assetRole': 'brand.logo', 'assetRef': 'asset:logo-flashform'}), base='new'),
    M('generated mode: real logo in the footer only (a different section)', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: node(s, 'footer')['content'].__setitem__('logo', {'assetRole': 'brand.logo', 'assetRef': 'asset:logo-flashform'}), base='new'),
    M('generated mode: brand.logo role with an owner-supplied ref', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: brand(s, 'brand.logo', 'owner-supplied:logo'), base='new'),
    M('generated mode: brand.logo role with an AI-generated ref', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: brand(s, 'brand.logo', 'generated:logo'), base='new'),
    M('generated mode: real favicon asset', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: s['meta'].__setitem__('favicon', {'assetRole': 'meta.favicon', 'assetRef': 'asset:favicon'}), base='new'),
    M('generated mode: real OG image asset', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: s['meta'].__setitem__('ogImage', {'assetRole': 'meta.og-image', 'assetRef': 'asset:og-twitter'}), base='new'),
    M("generated mode: the original's video", 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: node(s, 'meaning')['content'].__setitem__('media', {'assetRole': 'media.loop-video-square', 'assetRef': 'asset:video-2'}), base='new'),
    M('generated mode: real logo id smuggled into a text field', 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS', lambda s: node(s, 'footer')['content']['contact']['links'].append({'label': 'asset:logo-flashform', 'href': 'https://example.com/logo'}), base='new'),
    M('generated mode: real logo, and the brand-mark requirement fires too', 'GENERATED_MODE_REQUIRES_BRAND_MARK', lambda s: node(s, 'nav')['content'].__setitem__('logo', {'assetRole': 'brand.logo', 'assetRef': 'owner-supplied:logo'}), base='new'),
    M('invented run style', 'SCHEMA', lambda s: node(s, 'hero')['content']['headline'][0].__setitem__('style', 'bold')),
    # ---------------- structural (template cross-reference)
    M('duplicate one-per-page hero', 'TEMPLATE_NODE_SEQUENCE', lambda s: s['nodes'].insert(2, copy.deepcopy(node(s, 'hero')))),
    M('required navbar removed', 'TEMPLATE_NODE_SEQUENCE', lambda s: drop(s, 'nav')),
    M('required footer removed', 'TEMPLATE_NODE_SEQUENCE', lambda s: drop(s, 'footer')),
    M('reordered sections (purpose before meaning)', 'TEMPLATE_NODE_SEQUENCE', lambda s: s['nodes'].insert(2, s['nodes'].pop(3))),
    M('footer moved mid-page', 'FOOTER_LAST', lambda s: s['nodes'].insert(5, s['nodes'].pop())),
    M('same (section, variant) twice', 'TEMPLATE_NODE_SEQUENCE', lambda s: node(s, 'why').__setitem__('variant', 'media-left')),
    M('panel variants swapped vs template', 'TEMPLATE_NODE_SEQUENCE',
      lambda s: (node(s, 'purpose').__setitem__('variant', 'items-only'), node(s, 'problems').__setitem__('variant', 'with-channel-list'))),
    M('faq moved before roadmap', 'FAQ_PRECEDES_FOOTER', lambda s: s['nodes'].insert(10, s['nodes'].pop(11))),
    M('original-reference on an unreal route', 'ROUTE_ALLOWED', lambda s: s.__setitem__('route', '/pricing')),
    # ---------------- graph rules
    M('nav link to an omitted section', 'NAV_LINKS_RESOLVE', lambda s: drop(s, 'roadmap')),
    M('roadmap link not mobile-hidden', 'DESKTOP_ONLY_LINK_MOBILE_HIDDEN', lambda s: node(s, 'nav')['content']['links'][3].__setitem__('mobileHidden', False)),
    M('duplicate anchorId', 'ANCHOR_IDS_UNIQUE', lambda s: node(s, 'meaning').__setitem__('anchorId', 'why')),
    M('cta without beta popup overlay', 'CTA_REQUIRES_BETA_POPUP', lambda s: s['overlays'].pop('betaPopup')),
    M('form without toasts', 'FORMS_REQUIRE_FEEDBACK', lambda s: s['overlays'].pop('toasts')),
    M('form without submit spinner', 'FORMS_REQUIRE_FEEDBACK', lambda s: s['overlays'].__setitem__('submitSpinner', False)),
    M("original owner's Formspree endpoint", 'FORM_ENDPOINT_NOT_ORIGINAL', lambda s: s.__setitem__('forms', {'submission': 'owner-endpoint', 'endpoint': 'https://formspree.io/f/xyyvopzy'})),
    M('physics word with no sprite letters', 'PHYSICS_LETTERS_IN_GLYPH_SET', lambda s: node(s, 'footer')['content'].__setitem__('physicsWords', ['Hello'])),
    M('superscript outside hero headline', 'SUPERSCRIPT_HERO_HEADLINE_ONLY', lambda s: node(s, 'faq')['content']['heading'][1].__setitem__('style', 'superscript')),
    M('channelList in items-only panel', 'CHANNEL_LIST_VARIANT', lambda s: node(s, 'problems')['content']['items'][0].__setitem__('channelList', copy.deepcopy(node(s, 'purpose')['content']['items'][1]['channelList']))),
    M('with-channel-list panel lost its list', 'CHANNEL_LIST_VARIANT', lambda s: node(s, 'purpose')['content']['items'][1].pop('channelList')),
    M('AI-generated logo', 'ASSET_REF_POLICY', lambda s: node(s, 'nav')['content'].__setitem__('logo', {'assetRole': 'brand.logo', 'assetRef': 'generated:logo'})),
    M('AI-generated third-party messenger icon', 'ASSET_REF_POLICY', lambda s: node(s, 'purpose')['content']['items'][1]['channelList'][0].__setitem__('icon', {'assetRole': 'icon.third-party-channel', 'assetRef': 'generated:whatsapp'})),
    M('registered asset under the wrong role', 'ASSET_REF_POLICY', lambda s: node(s, 'purpose')['content']['items'][0].__setitem__('icon', {'assetRole': 'icon.feature-glyph', 'assetRef': 'asset:icon-whatsapp'})),
    M('owner-supplied ref for a must-reuse-exact shader', 'ASSET_REF_POLICY', lambda s: node(s, 'hero')['content'].__setitem__('visual', {'assetRole': 'shader.hero-flower', 'assetRef': 'owner-supplied:flower'})),
    M('unregistered asset id', 'ASSET_REF_POLICY', lambda s: node(s, 'meaning')['content']['media'].__setitem__('assetRef', 'asset:video-9')),
    M('maxWords overflow: hero paragraph', 'MAX_WORDS', lambda s: node(s, 'hero')['content'].__setitem__('paragraph', node(s, 'hero')['content']['paragraph'] + ' and then some more extra words here')),
    M('maxWords overflow: benefit card text', 'MAX_WORDS', lambda s: node(s, 'benefits')['content']['cards'][0].__setitem__('text', ' '.join(['word'] * 60))),
    M('maxWords overflow: page meta title', 'MAX_WORDS', lambda s: s['meta'].__setitem__('title', ' '.join(['word'] * 20))),
    M('maxWords overflow: horizontal headline', 'MAX_WORDS', lambda s: node(s, 'integration')['content'].__setitem__('headline', ' '.join(['word'] * 11))),
    # ---------------- compliance rules on new-content pages (base = the passing new-content control)
    M('new-content reuses agency email', 'ORIGINAL_CONTACTS_NOT_REUSED',
      lambda s: node(s, 'footer')['content']['contact']['links'].__setitem__(0, {'label': 'Email', 'href': 'mailto:hello@emotion-agency.com'}), base='new'),
    M('new-content reuses personal WhatsApp', 'ORIGINAL_CONTACTS_NOT_REUSED',
      lambda s: node(s, 'footer')['content']['contact']['links'].append({'label': 'Whatsapp', 'href': 'https://wa.me/+380970422959'}), base='new'),
    M('new-content reuses original paragraph verbatim', 'ORIGINAL_COPY_NOT_REUSED',
      lambda s: node(s, 'hero')['content'].__setitem__('paragraph', EXAMPLE['nodes'][1]['content']['paragraph']), base='new'),
    M("new-content reuses the original's video", 'ASSET_REF_POLICY',
      lambda s: node(s, 'meaning')['content'].__setitem__('media', {'assetRole': 'media.loop-video-square', 'assetRef': 'asset:video-1'}), base='new'),
    M("new-content reuses the original's OG image", 'ASSET_REF_POLICY',
      lambda s: s['meta'].__setitem__('ogImage', {'assetRole': 'meta.og-image', 'assetRef': 'asset:og-twitter'}), base='new'),
    # ---------------- warn-severity (must warn, must NOT error)
    M('adjacent scroll stages (warn only)', 'NO_ADJACENT_SCROLL_STAGES',
      lambda s: (drop(s, 'messengers', 'benefits', 'relief', 'problems'), set_links(s, {'#why', '#integration', '#roadmap', '#faq'})), warn_only=True),
    M('brand name in new-content (warn only)', 'BRAND_NAME_IN_NEW_CONTENT',
      lambda s: node(s, 'hero')['content'].__setitem__('paragraph', 'Flashform routes every form entry to your chat'), base='new', warn_only=True),
]


def _reg(path, value):
    """Return a mutator that sets doc[...path] = value on an asset-roles document."""
    def f(doc):
        o = doc
        for p in path[:-1]:
            o = o[p]
        o[path[-1]] = value
    return f


def _asset(doc, aid):
    return next(a for r in doc['roles'].values() for a in r['assets'] if a['id'] == aid)


REGISTRY_MUTATIONS = [
    ('real-logo role availability -> generation-safe (valid but wrong)', _reg(('roles', 'brand.logo', 'availability'), 'generation-safe')),
    ('real-logo role availability -> blocked-in-generated (valid but not the pin)', _reg(('roles', 'brand.logo', 'availability'), 'blocked-in-generated')),
    ('real-logo role availability -> invalid value', _reg(('roles', 'brand.logo', 'availability'), 'semi-safe')),
    ('real-logo role availability removed', lambda d: d['roles']['brand.logo'].pop('availability')),
    ('real-logo asset availability -> generation-safe', lambda d: _asset(d, 'asset:logo-flashform').__setitem__('availability', 'generation-safe')),
    ('real-logo role AND its pin map both changed (pin in code holds)', lambda d: (d['roles']['brand.logo'].__setitem__('availability', 'generation-safe'), d['pinnedAvailability'].__setitem__('brand.logo', 'generation-safe'))),
    ('real favicon asset availability -> generation-safe', lambda d: _asset(d, 'asset:favicon').__setitem__('availability', 'generation-safe')),
    ('a role without availability (unclassified)', lambda d: d['roles']['icon.generic-channel'].pop('availability')),
    ('a role with an invalid availability', _reg(('roles', 'icon.generic-channel', 'availability'), 'public')),
    ('protected role asset without explicit availability', lambda d: _asset(d, 'asset:og-twitter').pop('availability')),
    ('generation-safe asset inside a reference-only role', lambda d: _asset(d, 'asset:logo-flashform').__setitem__('availability', 'generation-safe')),
    ('brand mark role loses its generation guidance', lambda d: d['roles']['brand.generated-mark'].pop('generationGuidance')),
]


def total_mutations():
    return len(MUTATIONS) + len(REGISTRY_MUTATIONS)


def run():
    fails = 0
    print('CONTROLS (must pass with 0 errors)')
    for name, spec in controls():
        errs, warns = sv.validate(spec, REPO)
        ok = not errs and not warns
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + ('' if ok else f'  -> {errs + warns}'))
    print('MUTATIONS (must be rejected by the expected layer)')
    for name, expect, fn, base, warn_only in MUTATIONS:
        spec = copy.deepcopy(NEW if base == 'new' else EXAMPLE)
        fn(spec)
        errs, warns = sv.validate(spec, REPO)
        if warn_only:
            ok = not errs and any(w.startswith(expect + ':') for w in warns)
            got = warns if ok else errs + warns
        else:
            ok = any(e.startswith(expect + ':') or (expect == 'SCHEMA' and e.startswith('SCHEMA')) for e in errs)
            got = errs
        fails += not ok
        first = next((g for g in got if g.startswith(expect)), got[0] if got else 'nothing')
        print(f"  {'REJECTED' if ok and not warn_only else 'WARNED  ' if ok else 'MISSED  '}  [{expect}] {name}  :: {first[:110]}")
    print('REGISTRY MUTATIONS (the pinned / closed-enum availability check must reject them)')
    control_errs = sv.availability_errors(REPO.assets)
    ok = not control_errs
    fails += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  control: the real asset-roles.json passes the availability check" + ('' if ok else f'  -> {control_errs}'))
    for name, fn in REGISTRY_MUTATIONS:
        doc = copy.deepcopy(REPO.assets)
        fn(doc)
        errs = sv.availability_errors(doc)
        ok = bool(errs)
        fails += not ok
        print(f"  {'REJECTED' if ok else 'MISSED  '}  [AVAILABILITY] {name}  :: {(errs or ['nothing'])[0][:110]}")
    n_c = len(controls()) + 1
    print(f'\n{total_mutations()} mutations, {n_c} controls, {fails} failed expectation(s)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(run())
