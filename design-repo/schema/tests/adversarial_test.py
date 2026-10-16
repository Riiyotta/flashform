#!/usr/bin/env python3
"""Adversarial suite: every mutation must be REJECTED (by the expected layer), every control must PASS.

Controls are synthesised generically: for every template in templates/templates.json the suite builds
(a) the full node list and (b) a required-nodes-only page from that template's own node list, so a new or
split template is covered with zero new control code. A hand-written new-content control proves the
compliance rules do not reject legitimate generated pages.

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


def new_content_control():
    """A legitimate generated page: no original copy, owner-supplied media, the owner's own links, stubbed forms."""
    s = copy.deepcopy(EXAMPLE)
    s['contentProvenance'] = 'new-content'
    s['route'] = '/launch'
    s['meta'] = {'title': 'Route every form to your team chat', 'description': 'Send website form entries straight to the chat apps your team already reads.',
                 'ogImage': {'assetRole': 'meta.og-image', 'assetRef': 'owner-supplied:og-card'},
                 'favicon': {'assetRole': 'meta.favicon', 'assetRef': 'owner-supplied:favicon'}}
    s['overlays']['introLoader'] = {'word': 'Formline'}
    keep = ['nav', 'hero', 'meaning', 'benefits', 'faq', 'footer']
    drop(s, *[n['id'] for n in s['nodes'] if n['id'] not in keep])
    set_links(s, {'#benefits', '#faq'})
    for n in s['nodes']:
        if n['id'] in ('nav', 'footer'):
            n['content']['logo'] = {'assetRole': 'brand.logo', 'assetRef': 'owner-supplied:logo'}
    h = node(s, 'hero')['content']
    h['headline'] = [{'text': 'Forms that ', 'style': 'roman'}, {'text': 'arrive', 'style': 'italic'}]
    h['subheadline'] = [{'text': 'in seconds', 'style': 'italic'}]
    h['paragraph'] = 'Paste one link into your form and every new entry lands in the chat you already use'
    h['cta'] = {'label': 'Start free', 'action': 'open-beta-popup'}
    m = node(s, 'meaning')['content']
    m['heading'] = [{'text': 'One link, ', 'style': 'roman'}, {'text': 'every channel', 'style': 'italic'}]
    m['paragraph'] = 'Connect a contact form to chat apps and email without writing a backend'
    m['media'] = {'assetRole': 'media.loop-video-square', 'assetRef': 'owner-supplied:loop-a'}
    b = node(s, 'benefits')['content']
    b['ticker'] = [{'text': 'Why teams ', 'style': 'roman'}, {'text': 'switch', 'style': 'italic'}]
    b['intro'] = 'Six reasons small teams route their website forms through one simple service'
    b['cards'] = [{'title': f'Reason {i}', 'text': f'Short supporting sentence number {i} about the benefit.'} for i in range(1, 7)]
    fq = node(s, 'faq')['content']
    fq['items'] = [{'question': 'Do I need a backend?', 'answerLines': ['No. Point your form at your personal link and choose a channel.']}]
    ft = node(s, 'footer')['content']
    ft['contact']['links'] = [{'label': 'Email us', 'href': 'mailto:team@example.com'}]
    ft['legal'] = {'copyright': '©2026 Formline', 'links': [{'label': 'Terms', 'href': 'https://example.com/terms'}], 'credit': {'label': 'Studio', 'href': 'https://example.com/'}}
    s['overlays']['toasts'] = {'success': 'You are on the list', 'error': 'Something went wrong'}
    return s


NEW = new_content_control()


def controls():
    out = [('example.pagespec.json (unmutated)', copy.deepcopy(EXAMPLE)), ('new-content control', copy.deepcopy(NEW))]
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
    n_c = len(controls())
    print(f'\n{len(MUTATIONS)} mutations, {n_c} controls, {fails} failed expectation(s)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(run())
