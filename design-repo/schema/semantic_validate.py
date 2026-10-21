#!/usr/bin/env python3
"""Semantic validator for Flashform PageSpecs.

Enforces what JSON Schema cannot: template node-sequence cross-reference, rhythm/position rules, compliance
rules (form endpoint, original contacts/copy, asset-ref policy), the reference/generated MODE rules (the real
Flashform logo and every registered source-brand asset are rejected in mode "generated"; a generation-safe brand mark
is required there) and per-instance maxWords budgets.

Every rule id in compatibility/graph.json has exactly one implementation in RULES below, and the severity
used at runtime is READ FROM THE GRAPH (one source of truth). extraction/verify_all.py checks the two sets
of ids match both ways.

Usage:  python3 -I schema/semantic_validate.py [pagespec.json ...]   (default: every schema/example*.pagespec.json)
Exit code 1 if any error-severity finding. Requires the `jsonschema` package for the Draft-07 layer.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # design-repo/

MODES = ('reference', 'generated')
MODE_PROVENANCE = {'reference': 'original-reference', 'generated': 'new-content'}
AVAILABILITY = ('generation-safe', 'reference-only', 'blocked-in-generated')
# Pinned: the real Flashform logo carries legal weight (a real trademark), so its availability is pinned in CODE as well as
# in assets/asset-roles.json (pinnedAvailability / pinnedAssetAvailability). Membership in AVAILABILITY is not enough.
PINNED_ROLE_AVAILABILITY = {'brand.logo': 'reference-only'}
PINNED_ASSET_AVAILABILITY = {'asset:logo-flashform': 'reference-only', 'asset:favicon': 'blocked-in-generated'}


def availability_errors(doc):
    """Closed-enum + classification + pinned-value checks on an asset-roles document. Returns a list of messages.
    Used by verify_all (check 11) and by the adversarial suite's registry mutations (one implementation, two callers)."""
    errs = []
    roles = doc['roles']
    protected = ('must-not-fabricate', 'owner-supplied-only')
    for k, r in roles.items():
        av = r.get('availability')
        if av is None:
            errs.append(f'{k}: role has no availability (every role must be classified)')
        elif av not in AVAILABILITY:
            errs.append(f'{k}: availability {av!r} is not in the closed set {list(AVAILABILITY)}')
        for a in r['assets']:
            aav = a.get('availability')
            if aav is None and r.get('generationPolicy') in protected:
                errs.append(f"{a['id']}: registered asset of protected role {k} has no explicit availability")
            elif aav is not None and aav not in AVAILABILITY:
                errs.append(f"{a['id']}: availability {aav!r} is not in the closed set {list(AVAILABILITY)}")
            elif aav == 'generation-safe' and av in ('reference-only', 'blocked-in-generated'):
                errs.append(f"{a['id']}: asset is generation-safe inside the {av} role {k}")
        if r.get('brandMark') and av == 'generation-safe':
            if not r.get('generationGuidance') or not r.get('allowedRefKinds'):
                errs.append(f'{k}: generation-safe brand mark needs generationGuidance and allowedRefKinds')
    for k, want in PINNED_ROLE_AVAILABILITY.items():
        if k not in roles:
            errs.append(f'PINNED role {k} missing')
        elif roles[k].get('availability') != want:
            errs.append(f"PINNED availability drift: {k} is {roles[k].get('availability')!r}, must be {want!r}")
    by_id = {a['id']: a for r in roles.values() for a in r['assets']}
    for k, want in PINNED_ASSET_AVAILABILITY.items():
        if k not in by_id:
            errs.append(f'PINNED asset {k} missing')
        elif by_id[k].get('availability') != want:
            errs.append(f"PINNED availability drift: {k} is {by_id[k].get('availability')!r}, must be {want!r}")
    if doc.get('pinnedAvailability') != PINNED_ROLE_AVAILABILITY:
        errs.append('assets/asset-roles.json pinnedAvailability != the validator pin')
    if doc.get('pinnedAssetAvailability') != PINNED_ASSET_AVAILABILITY:
        errs.append('assets/asset-roles.json pinnedAssetAvailability != the validator pin')
    return errs


def _load(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return json.load(f)


class Repo:
    def __init__(self):
        self.schema = _load('schema/pagespec.schema.json')
        self.templates = _load('templates/templates.json')
        self.graph = _load('compatibility/graph.json')
        self.assets = _load('assets/asset-roles.json')
        self.sections = {}
        for fn in sorted(os.listdir(os.path.join(ROOT, 'sections'))):
            if fn.endswith('.json'):
                d = _load(f'sections/{fn}')
                self.sections[d['id']] = d
        self.rules = {r['id']: r for r in self.graph['rules']}
        self.asset_ids = {}
        self.asset_availability = {}
        for role, r in self.assets['roles'].items():
            for a in r['assets']:
                self.asset_ids[a['id']] = role
                self.asset_availability[a['id']] = a.get('availability', r.get('availability'))
        self._orig_strings = None

    def original_strings(self, min_words):
        """Long strings from the original-reference example (the original's proprietary copy)."""
        if self._orig_strings is None:
            ex = _load('schema/example.pagespec.json')
            out = set()
            for s in iter_text(ex):
                if len(s.split()) >= min_words:
                    out.add(norm(s))
            self._orig_strings = out
        return self._orig_strings


def is_generated(spec):
    return spec.get('mode') == 'generated'


def iter_strings(obj, skip=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip:
                yield from iter_strings(v, skip)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v, skip)
    elif isinstance(obj, str):
        yield obj


def norm(s):
    return ' '.join(s.lower().split())


def iter_text(obj, key=None):
    """Yield human-visible strings (joined runs count as one string)."""
    skip = {'assetRole', 'assetRef', 'href', 'section', 'variant', 'id', 'anchorId', 'template', 'route', 'theme', 'action', 'style',
            'contentProvenance', 'mode', 'pageSpecVersion', 'submission', 'endpoint', 'reducedMotionFallback', 'patterns', 'revealTargets'}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip or k == 'motion':
                continue
            yield from iter_text(v, k)
    elif isinstance(obj, list):
        if obj and all(isinstance(x, dict) and set(x) == {'text', 'style'} for x in obj):
            yield ''.join(x['text'] for x in obj)
        else:
            for v in obj:
                yield from iter_text(v, key)
    elif isinstance(obj, str):
        yield obj


def words_at(content, path):
    """Word counts for every value addressed by a budget path such as items[].paragraphs[]."""
    def go(v, parts):
        if not parts:
            if isinstance(v, list) and v and isinstance(v[0], dict) and 'text' in v[0]:
                yield ''.join(r['text'] for r in v)
            elif isinstance(v, list):
                yield ' '.join(x for x in v if isinstance(x, str))
            elif isinstance(v, str):
                yield v
            return
        p, rest = parts[0], parts[1:]
        if p.endswith('[]'):
            seq = v.get(p[:-2]) if isinstance(v, dict) else None
            for item in seq or []:
                yield from go(item, rest)
        elif isinstance(v, dict) and p in v:
            yield from go(v[p], rest)
    return [(s, len(s.split())) for s in go(content, path.split('.'))]


def walk_media(obj, where=''):
    if isinstance(obj, dict):
        if 'assetRole' in obj and 'assetRef' in obj:
            yield where, obj
        for k, v in obj.items():
            yield from walk_media(v, f'{where}.{k}' if where else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_media(v, f'{where}[{i}]')


# ------------------------------------------------------------------ rules
def r_template_node_sequence(spec, repo, emit):
    t = repo.templates['templates'].get(spec.get('template'))
    if t is None:
        emit(f"unknown template {spec.get('template')!r}")
        return
    tnodes = t['nodes']
    index = {}
    for i, tn in enumerate(tnodes):
        index.setdefault((tn['section'], tn.get('variant')), []).append(i)
    last = -1
    seen = set()
    for n in spec['nodes']:
        key = (n['section'], n.get('variant'))
        cand = [i for i in index.get(key, [])]
        if not cand:
            emit(f"node {n['id']!r}: ({n['section']}, variant={n.get('variant')}) is not a node of {spec['template']}")
            continue
        nxt = [i for i in cand if i > last]
        if not nxt:
            if any(i in seen for i in cand) and not any(tnodes[i]['repeatable'] for i in cand):
                emit(f"node {n['id']!r}: ({n['section']}, {n.get('variant')}) repeated, but the template node is not repeatable")
            else:
                emit(f"node {n['id']!r}: ({n['section']}, {n.get('variant')}) is out of template order")
            continue
        last = nxt[0]
        seen.add(last)
    for i, tn in enumerate(tnodes):
        if tn['required'] and i not in seen:
            emit(f"required template node {tn['key']!r} ({tn['section']}) is missing")


def r_mode_provenance_consistent(spec, repo, emit):
    want = MODE_PROVENANCE.get(spec.get('mode'))
    if want != spec.get('contentProvenance'):
        emit(f"mode {spec.get('mode')!r} requires contentProvenance {want!r}, got {spec.get('contentProvenance')!r}")


def r_generated_mode_blocks_reference_assets(spec, repo, emit):
    """In mode 'generated' nothing that is reference-only / blocked-in-generated may appear: not the real logo role (any ref),
    not a registered source-brand asset id, in any field of any node or in meta."""
    if not is_generated(spec):
        return
    roles = repo.assets['roles']
    for where, m in walk_media(spec):
        role, ref = m['assetRole'], m['assetRef']
        av = roles.get(role, {}).get('availability')
        if av != 'generation-safe':
            emit(f'{where}: assetRole {role!r} is {av}; the real {role} must not appear in a generated page (use a generation-safe brand role)')
        if ref.startswith('asset:') and repo.asset_availability.get(ref) not in (None, 'generation-safe'):
            emit(f"{where}: {ref!r} is {repo.asset_availability[ref]}; a registered source-brand asset must not appear in a generated page")
    blocked = sorted(i for i, a in repo.asset_availability.items() if a != 'generation-safe')
    for s in iter_strings(spec, skip=('assetRef',)):  # assetRef values are checked structurally above
        for i in blocked:
            if i in s:
                emit(f'a text field mentions {i!r}, a source-brand asset that is {repo.asset_availability[i]}')


def r_generated_mode_requires_brand_mark(spec, repo, emit):
    """A generated page must supply a generation-safe brand mark role where a brand mark is required (navbar + footer logo)."""
    if not is_generated(spec):
        return
    roles = repo.assets['roles']
    for n in spec['nodes']:
        if n['section'] in ('shell.navbar', 'shell.footer'):
            role = n['content'].get('logo', {}).get('assetRole')
            r = roles.get(role, {})
            if not (r.get('brandMark') and r.get('availability') == 'generation-safe'):
                emit(f"node {n['id']!r}: logo role {role!r} is not a generation-safe brand mark "
                     f"({', '.join(sorted(k for k, v in roles.items() if v.get('brandMark') and v.get('availability') == 'generation-safe'))})")


def r_route_allowed(spec, repo, emit):
    t = repo.templates['templates'].get(spec.get('template'))
    if t and spec.get('mode') == 'reference' and spec.get('route') not in t['routes']:
        emit(f"reference-mode page must use a real route of its template {t['routes']}, got {spec.get('route')!r}")


def _secs(spec):
    return [n['section'] for n in spec['nodes']]


def r_one_hero(spec, repo, emit):
    if spec.get('template') in repo.rules['ONE_HERO'].get('exemptTemplates', []):
        return
    k = sum(1 for s in _secs(spec) if s.startswith('hero.'))
    if k != 1:
        emit(f'expected exactly one hero node, found {k}')


def r_nav_first(spec, repo, emit):
    if not spec['nodes'] or spec['nodes'][0]['section'] != 'shell.navbar':
        emit('first node must be shell.navbar')


def r_hero_follows_nav(spec, repo, emit):
    s = _secs(spec)
    for i, x in enumerate(s):
        if x.startswith('hero.') and (i == 0 or s[i - 1] != 'shell.navbar'):
            emit('hero must immediately follow shell.navbar')


def r_footer_last(spec, repo, emit):
    if not spec['nodes'] or spec['nodes'][-1]['section'] != 'shell.footer':
        emit('last node must be shell.footer')


def r_faq_precedes_footer(spec, repo, emit):
    s = _secs(spec)
    for i, x in enumerate(s):
        if x == 'faq.accordion' and (i + 1 >= len(s) or s[i + 1] != 'shell.footer'):
            emit('faq.accordion must immediately precede shell.footer')


def r_section_max_per_page(spec, repo, emit):
    counts, pairs = {}, {}
    for n in spec['nodes']:
        counts[n['section']] = counts.get(n['section'], 0) + 1
        k = (n['section'], n.get('variant'))
        pairs[k] = pairs.get(k, 0) + 1
    for sid, k in counts.items():
        c = repo.sections.get(sid, {}).get('constraints', {})
        if k > c.get('maxPerPage', 1):
            emit(f'{sid} appears {k}x (maxPerPage {c.get("maxPerPage", 1)})')
        if c.get('variantsUniquePerPage'):
            for (s2, v), m in pairs.items():
                if s2 == sid and m > 1:
                    emit(f'{sid} variant {v!r} appears {m}x; repeats must use distinct variants')


def r_no_adjacent_scroll_stages(spec, repo, emit):
    cats = set(repo.rules['NO_ADJACENT_SCROLL_STAGES']['categories'])
    s = [repo.sections[x]['category'] if x in repo.sections else None for x in _secs(spec)]
    for i in range(1, len(s)):
        if s[i] in cats and s[i - 1] in cats:
            emit(f'nodes {spec["nodes"][i - 1]["id"]!r} and {spec["nodes"][i]["id"]!r} are adjacent scroll stages')


def r_anchor_ids_unique(spec, repo, emit):
    seen = set()
    for n in spec['nodes']:
        a = n.get('anchorId')
        if a:
            if a in seen:
                emit(f'duplicate anchorId {a!r}')
            seen.add(a)


def _nav(spec):
    for n in spec['nodes']:
        if n['section'] == 'shell.navbar':
            return n
    return None


def r_nav_links_resolve(spec, repo, emit):
    nav = _nav(spec)
    if not nav:
        return
    anchors = {n.get('anchorId') for n in spec['nodes'] if n.get('anchorId')}
    for l in nav['content'].get('links', []):
        if l['href'][1:] not in anchors:
            emit(f"nav link {l['label']!r} -> {l['href']} has no node with that anchorId")


def r_desktop_only_link_mobile_hidden(spec, repo, emit):
    nav = _nav(spec)
    if not nav:
        return
    desk = {n.get('anchorId') for n in spec['nodes'] if n.get('anchorId') and repo.sections.get(n['section'], {}).get('constraints', {}).get('desktopOnly')}
    for l in nav['content'].get('links', []):
        if l['href'][1:] in desk and not l.get('mobileHidden'):
            emit(f"nav link {l['href']} targets a desktopOnly section and must set mobileHidden: true")


def _ctas(obj):
    if isinstance(obj, dict):
        if set(obj) == {'label', 'action'}:
            yield obj
        for v in obj.values():
            yield from _ctas(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _ctas(v)


def r_cta_requires_beta_popup(spec, repo, emit):
    if any(c['action'] == 'open-beta-popup' for c in _ctas(spec['nodes'])) and 'betaPopup' not in spec.get('overlays', {}):
        emit("a cta opens the beta popup but overlays.betaPopup is missing")


def r_forms_require_feedback(spec, repo, emit):
    ov = spec.get('overlays', {})
    has_form = 'betaPopup' in ov or any(n['section'] == 'shell.footer' for n in spec['nodes'])
    if has_form and ('toasts' not in ov or ov.get('submitSpinner') is not True):
        emit('page has a form: overlays.toasts and overlays.submitSpinner=true are required')


def r_form_endpoint_not_original(spec, repo, emit):
    ep = spec.get('forms', {}).get('endpoint', '')
    for bad in repo.rules['FORM_ENDPOINT_NOT_ORIGINAL']['denylist']:
        if bad in ep:
            emit(f"forms.endpoint reuses the original owner's endpoint ({bad})")


def r_original_contacts_not_reused(spec, repo, emit):
    if not is_generated(spec):
        return
    deny = repo.rules['ORIGINAL_CONTACTS_NOT_REUSED']['denylist']

    def hrefs(o):
        if isinstance(o, dict):
            if 'href' in o:
                yield o['href']
            for v in o.values():
                yield from hrefs(v)
        elif isinstance(o, list):
            for v in o:
                yield from hrefs(v)
    for h in hrefs(spec['nodes']):
        for d in deny:
            if d in h:
                emit(f"link {h!r} reuses an original contact/legal channel ({d})")


def r_original_copy_not_reused(spec, repo, emit):
    if not is_generated(spec):
        return
    mw = repo.rules['ORIGINAL_COPY_NOT_REUSED']['minWords']
    orig = repo.original_strings(mw)
    for s in iter_text(spec):
        if len(s.split()) >= mw and norm(s) in orig:
            emit(f"text reproduces original copy verbatim: {s[:60]!r}...")


def r_brand_name_in_new_content(spec, repo, emit):
    if not is_generated(spec):
        return
    term = repo.rules['BRAND_NAME_IN_NEW_CONTENT']['term']
    if any(term in s.lower() for s in iter_text(spec)):
        emit("new-content page mentions the brand name 'Flashform'")


def r_physics_letters_in_glyph_set(spec, repo, emit):
    glyphs = set(repo.assets['roles']['physics.letter-sprite']['glyphSet'])
    for n in spec['nodes']:
        if n['section'] == 'shell.footer':
            for w in n['content'].get('physicsWords', []):
                bad = sorted({c for c in w.upper() if c not in glyphs})
                if bad:
                    emit(f"physicsWords {w!r} uses letters without a sprite: {bad}")


def r_superscript_hero_headline_only(spec, repo, emit):
    def runs(o, where):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from runs(v, f'{where}.{k}')
        elif isinstance(o, list):
            if o and all(isinstance(x, dict) and set(x) == {'text', 'style'} for x in o):
                yield where, o
            else:
                for i, v in enumerate(o):
                    yield from runs(v, f'{where}[{i}]')
    for n in spec['nodes']:
        for where, rs in runs(n['content'], n['id']):
            if any(r['style'] == 'superscript' for r in rs) and not (n['section'].startswith('hero.') and where == f"{n['id']}.headline"):
                emit(f'superscript run outside the hero headline at {where}')


def r_channel_list_variant(spec, repo, emit):
    for n in spec['nodes']:
        has = any('channelList' in it for it in n['content'].get('items', [])) if isinstance(n.get('content'), dict) else False
        if n['section'] != 'panel.rounded-sticky':
            continue
        if n.get('variant') == 'with-channel-list' and not has:
            emit(f"node {n['id']!r}: variant with-channel-list needs a channelList")
        if n.get('variant') != 'with-channel-list' and has:
            emit(f"node {n['id']!r}: channelList only allowed in variant with-channel-list")


def r_asset_ref_policy(spec, repo, emit):
    roles = repo.assets['roles']
    for where, m in walk_media(spec):
        role, ref = m['assetRole'], m['assetRef']
        r = roles.get(role)
        if r is None or not r['settableInPageSpec']:
            emit(f'{where}: assetRole {role!r} is not a settable role')
            continue
        pol = r['generationPolicy']
        kind = ref.split(':', 1)[0]
        if r.get('allowedRefKinds') and kind not in r['allowedRefKinds']:
            emit(f"{where}: {role} accepts only {r['allowedRefKinds']} refs, got {kind!r}")
            continue
        if kind == 'asset':
            if repo.asset_ids.get(ref) != role:
                emit(f'{where}: {ref!r} is not a registered {role} asset')
            elif pol == 'owner-supplied-only' and is_generated(spec):
                emit(f"{where}: {ref!r} is the original's proprietary media ({role} is owner-supplied-only); use owner-supplied:<slot>")
        elif kind == 'generated' and pol != 'may-generate-new':
            emit(f'{where}: {role} is {pol}; AI-generated refs are forbidden')
        elif kind == 'owner-supplied' and pol == 'must-reuse-exact':
            emit(f'{where}: {role} is must-reuse-exact; reference the registered asset')


def r_max_words(spec, repo, emit):
    t = repo.templates['templates'].get(spec.get('template'), {})
    for b in t.get('pageWordBudgets', []):
        for s, w in words_at(spec, b['path']):
            if w > b['maxWords']:
                emit(f"{b['path']}: {w} words > maxWords {b['maxWords']}")
    for n in spec['nodes']:
        sec = repo.sections.get(n['section'])
        if not sec:
            continue
        for b in sec['content']['wordBudgets']:
            for s, w in words_at(n['content'], b['path']):
                if w > b['maxWords']:
                    emit(f"node {n['id']!r} {b['path']}: {w} words > maxWords {b['maxWords']}")


def r_reduced_motion_fallback(spec, repo, emit):
    for n in spec['nodes']:
        sec = repo.sections.get(n['section'])
        want = sec['motion']['reducedMotionFallback'] if sec else None
        got = (n.get('motion') or {}).get('reducedMotionFallback')
        if not got:
            emit(f"node {n['id']!r}: motion.reducedMotionFallback missing")
        elif want and got != want:
            emit(f"node {n['id']!r}: reducedMotionFallback {got!r} != section's {want!r}")


RULES = {
    'TEMPLATE_NODE_SEQUENCE': r_template_node_sequence,
    'MODE_PROVENANCE_CONSISTENT': r_mode_provenance_consistent,
    'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS': r_generated_mode_blocks_reference_assets,
    'GENERATED_MODE_REQUIRES_BRAND_MARK': r_generated_mode_requires_brand_mark,
    'ROUTE_ALLOWED': r_route_allowed,
    'ONE_HERO': r_one_hero,
    'NAV_FIRST': r_nav_first,
    'HERO_FOLLOWS_NAV': r_hero_follows_nav,
    'FOOTER_LAST': r_footer_last,
    'FAQ_PRECEDES_FOOTER': r_faq_precedes_footer,
    'SECTION_MAX_PER_PAGE': r_section_max_per_page,
    'NO_ADJACENT_SCROLL_STAGES': r_no_adjacent_scroll_stages,
    'ANCHOR_IDS_UNIQUE': r_anchor_ids_unique,
    'NAV_LINKS_RESOLVE': r_nav_links_resolve,
    'DESKTOP_ONLY_LINK_MOBILE_HIDDEN': r_desktop_only_link_mobile_hidden,
    'CTA_REQUIRES_BETA_POPUP': r_cta_requires_beta_popup,
    'FORMS_REQUIRE_FEEDBACK': r_forms_require_feedback,
    'FORM_ENDPOINT_NOT_ORIGINAL': r_form_endpoint_not_original,
    'ORIGINAL_CONTACTS_NOT_REUSED': r_original_contacts_not_reused,
    'ORIGINAL_COPY_NOT_REUSED': r_original_copy_not_reused,
    'BRAND_NAME_IN_NEW_CONTENT': r_brand_name_in_new_content,
    'PHYSICS_LETTERS_IN_GLYPH_SET': r_physics_letters_in_glyph_set,
    'SUPERSCRIPT_HERO_HEADLINE_ONLY': r_superscript_hero_headline_only,
    'CHANNEL_LIST_VARIANT': r_channel_list_variant,
    'ASSET_REF_POLICY': r_asset_ref_policy,
    'MAX_WORDS': r_max_words,
    'REDUCED_MOTION_FALLBACK': r_reduced_motion_fallback,
}


def schema_errors(spec, repo):
    try:
        import jsonschema
    except ImportError:
        return ['SCHEMA: jsonschema package not installed (pip install jsonschema)']
    v = jsonschema.Draft7Validator(repo.schema)
    return [f"SCHEMA {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message[:200]}" for e in sorted(v.iter_errors(spec), key=lambda e: list(e.absolute_path))]


def validate(spec, repo=None):
    """Return (errors, warnings). Schema errors short-circuit the semantic layer (it assumes a well-formed spec)."""
    repo = repo or Repo()
    errors = schema_errors(spec, repo)
    warnings = []
    if errors:
        return errors, warnings
    for rid, fn in RULES.items():
        sev = repo.rules[rid]['severity']
        sink = errors if sev == 'error' else warnings
        fn(spec, repo, lambda msg, rid=rid: sink.append(f'{rid}: {msg}'))
    return errors, warnings


def example_paths():
    d = os.path.join(ROOT, 'schema')
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.startswith('example') and f.endswith('.pagespec.json')]


def main(argv):
    paths = argv or example_paths()
    repo = Repo()
    bad = 0
    for p in paths:
        with open(p, encoding='utf-8') as f:
            spec = json.load(f)
        errs, warns = validate(spec, repo)
        name = os.path.relpath(p, ROOT) if os.path.abspath(p).startswith(ROOT) else os.path.basename(p)
        print(f'{name}: {len(errs)} error(s), {len(warns)} warning(s)')
        for e in errs:
            print('  ERROR', e)
        for w in warns:
            print('  warn ', w)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
