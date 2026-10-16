#!/usr/bin/env python3
"""One-shot verification for this design-repo. Exit 1 on any FAIL.

Checks (each one is proven to catch drift by extraction/drift_test.py, which mutates a scratch copy):
  1  json        every *.json parses
  2  schema      pagespec.schema.json is valid Draft-07 and example.pagespec.json has 0 schema errors
  3  semantic    semantic_validate.py reports 0 errors / 0 warnings on the example
  4  adversarial schema/tests/adversarial_test.py: every mutation rejected, every control passes
  5  allowlist   parity: files on disk <-> tokens/llm/component-allowlist.json <-> pagespec.schema.json
  6  contracts   each section's content.schema == schema definitions; template nodes reference real sections/variants
  7  graph       compatibility/graph.json rule ids == semantic_validate.RULES ids (both directions)
  8  versions    manifest.allowlistVersion == allowlist.version (machine-checked); other version fields are doc-only
  9  counts      manifest.counts recomputed from the files
 10  citations   every measuredFrom/cites entry resolves (path exists, range within file, `expect` text inside the range).
                 Paths with @repo/ are inside this folder and always checked; others are relative to the sibling clone
                 project (the parent folder) and are WARN-skipped when that project is absent (standalone copy).
 11  assets      asset roles closed + pinned policies unchanged + schema/allowlist roles agree
 12  tokens      every {token.ref} resolves; theme resolves every colour role; policy keys are real catalog keys
 13  manifest    entryPoints exist and are inside design-repo/
 14  paths       no absolute local machine paths in any text file
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # design-repo/
PROJECT = os.path.dirname(ROOT)
SIBLING = os.path.isfile(os.path.join(PROJECT, 'src', 'App.jsx')) and os.path.isfile(os.path.join(PROJECT, 'CLONE_SPEC.md'))
sys.path.insert(0, os.path.join(ROOT, 'schema'))
sys.path.insert(0, os.path.join(ROOT, 'schema', 'tests'))

RESULTS = []


def check(name):
    def deco(fn):
        def run():
            fails, warns, info = [], [], []
            try:
                fn(fails, warns, info)
            except Exception as e:  # a crashing check is a failing check
                fails.append(f'{type(e).__name__}: {e}')
            RESULTS.append((name, fails, warns, info))
        run.__name__ = fn.__name__
        CHECKS.append(run)
        return run
    return deco


CHECKS = []


def load(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return json.load(f)


def json_files():
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith('.json'):
                yield os.path.relpath(os.path.join(d, f), ROOT)


def ids_in(folder):
    return sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, folder)) if f.endswith('.json'))


@check('1 json')
def c_json(F, W, I):
    n = 0
    for rel in json_files():
        try:
            load(rel)
            n += 1
        except Exception as e:
            F.append(f'{rel}: {e}')
    I.append(f'{n} json files parse')


@check('2 schema')
def c_schema(F, W, I):
    import jsonschema
    s = load('schema/pagespec.schema.json')
    jsonschema.Draft7Validator.check_schema(s)
    errs = list(jsonschema.Draft7Validator(s).iter_errors(load('schema/example.pagespec.json')))
    for e in errs:
        F.append(f"{'/'.join(map(str, e.absolute_path))}: {e.message[:150]}")
    I.append(f'Draft-07 meta-schema OK; example.pagespec.json: {len(errs)} schema error(s)')


@check('3 semantic')
def c_semantic(F, W, I):
    import semantic_validate as sv
    errs, warns = sv.validate(load('schema/example.pagespec.json'))
    F.extend(errs)
    F.extend(f'(warning on the example) {w}' for w in warns)
    I.append(f'example: {len(errs)} error(s), {len(warns)} warning(s)')


@check('4 adversarial')
def c_adv(F, W, I):
    import io
    import contextlib
    import adversarial_test as at
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = at.run()
    last = buf.getvalue().strip().splitlines()[-1]
    if rc != 0:
        F.append(last)
        F.extend(l.strip() for l in buf.getvalue().splitlines() if l.strip().startswith(('FAIL', 'MISSED')))
    I.append(last)


@check('5 allowlist')
def c_allow(F, W, I):
    a = load('tokens/llm/component-allowlist.json')
    s = load('schema/pagespec.schema.json')
    for kind, folder in (('sections', 'sections'), ('primitives', 'primitives'), ('components', 'components')):
        listed = {e['id']: e['file'] for e in a[kind]}
        disk = ids_in(folder)
        for i in sorted(set(listed) - set(disk)):
            F.append(f'phantom allowlist {kind} entry with no contract file: {i}')
        for i in sorted(set(disk) - set(listed)):
            F.append(f'contract file with no allowlist entry: {folder}/{i}.json')
        for i, f in listed.items():
            if i in disk and f != f'{folder}/{i}.json':
                F.append(f'allowlist file path wrong for {i}: {f}')
    for e in a['sections']:
        d = s['definitions'].get(f"content.{e['id']}")
        m = s['definitions'].get(f"motion.{e['id']}")
        if d is None:
            F.append(f"schema has no content.{e['id']}")
            continue
        if sorted(d['properties']) != e['settableProperties']:
            F.append(f"{e['id']}: allowlist settableProperties {e['settableProperties']} != schema {sorted(d['properties'])}")
        if sorted(m['properties']) != e['motionFields']:
            F.append(f"{e['id']}: allowlist motionFields != schema motion properties")
        sec = load(f"sections/{e['id']}.json")
        if sec['variants'] != e['variants']:
            F.append(f"{e['id']}: allowlist variants {e['variants']} != contract {sec['variants']}")
    if sorted(s['definitions']['node']['properties']) != a['nodeProperties']:
        F.append('allowlist nodeProperties != schema node properties')
    if sorted(s['properties']) != a['pageProperties']:
        F.append('allowlist pageProperties != schema top-level properties')
    if sorted(s['definitions']['node']['properties']['section']['enum']) != sorted(e['id'] for e in a['sections']):
        F.append('schema node.section enum != allowlist sections')
    I.append(f"{len(a['sections'])} sections, {len(a['primitives'])} primitives, {len(a['components'])} components in parity with disk + schema")


@check('6 contracts')
def c_contracts(F, W, I):
    s = load('schema/pagespec.schema.json')
    t = load('templates/templates.json')
    secs = {i: load(f'sections/{i}.json') for i in ids_in('sections')}
    for i, d in secs.items():
        if d['id'] != i:
            F.append(f'sections/{i}.json declares id {d["id"]}')
        if d['content']['schema'] != s['definitions'].get(f'content.{i}'):
            F.append(f'{i}: content.schema differs from pagespec.schema.json definitions.content.{i}')
        mot = s['definitions'][f'motion.{i}']['properties']['reducedMotionFallback'].get('const')
        if mot != d['motion']['reducedMotionFallback']:
            F.append(f'{i}: schema reducedMotionFallback const {mot} != contract {d["motion"]["reducedMotionFallback"]}')
        for b in d['content']['wordBudgets']:
            if b['maxWords'] < b['observedMaxWords']:
                F.append(f'{i}.{b["path"]}: maxWords below the observed real copy')
    used = set()
    for tid, tt in t['templates'].items():
        for n in tt['nodes']:
            used.add(n['section'])
            if n['section'] not in secs:
                F.append(f'{tid}: node {n["key"]} references missing section {n["section"]}')
            elif n.get('variant') and n['variant'] not in secs[n['section']]['variants']:
                F.append(f'{tid}: node {n["key"]} variant {n["variant"]} not in {n["section"]} variants')
    for i in set(secs) - used:
        W.append(f'section {i} is not used by any template')
    routes = [r['path'] for r in t['routes']]
    if len(routes) != len(set(routes)):
        F.append('a route is assigned to more than one template')
    for r in t['routes']:
        if r['template'] not in t['templates'] or r['path'] not in t['templates'][r['template']]['routes']:
            F.append(f'route {r["path"]} -> {r["template"]} is not declared by that template')
    I.append(f'{len(secs)} section contracts match the schema; {len(t["templates"])} template(s), {len(routes)} route(s) mapped 1:1')


@check('7 graph')
def c_graph(F, W, I):
    import semantic_validate as sv
    g = {r['id'] for r in load('compatibility/graph.json')['rules']}
    v = set(sv.RULES)
    for r in sorted(g - v):
        F.append(f'graph rule {r} has no validator implementation')
    for r in sorted(v - g):
        F.append(f'validator rule {r} is not declared in compatibility/graph.json')
    for r in load('compatibility/graph.json')['rules']:
        if r['severity'] not in ('error', 'warn'):
            F.append(f'{r["id"]}: severity {r["severity"]}')
    I.append(f'{len(g)} graph rules <-> {len(v)} validator rules')


@check('8 versions')
def c_versions(F, W, I):
    m = load('registry.manifest.json')
    a = load('tokens/llm/component-allowlist.json')
    if m['allowlistVersion'] != a['version']:
        F.append(f"manifest allowlistVersion {m['allowlistVersion']} != allowlist version {a['version']}")
    s = load('schema/pagespec.schema.json')
    if m['pageSpecVersion'] != s['properties']['pageSpecVersion']['const']:
        F.append('manifest pageSpecVersion != schema pageSpecVersion const')
    I.append(f"allowlistVersion {a['version']} matches (machine-checked); repositoryVersion is documentation-only")


def count_tokens(layer):
    n = 0

    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            if '$value' in o:
                n += 1
                return
            for k, v in o.items():
                if not k.startswith('$'):
                    walk(v)
    d = os.path.join(ROOT, 'tokens', layer)
    for f in sorted(os.listdir(d)):
        walk(load(f'tokens/{layer}/{f}'))
    return n


def recount():
    import adversarial_test as at
    t = load('templates/templates.json')
    roles = load('assets/asset-roles.json')['roles']
    return {
        'tokensFoundation': count_tokens('00-foundation'), 'tokensSemantic': count_tokens('10-semantic'),
        'tokensComponent': count_tokens('20-component'), 'tokensLayout': count_tokens('30-layout'),
        'primitives': len(ids_in('primitives')), 'components': len(ids_in('components')), 'sections': len(ids_in('sections')),
        'templates': len(t['templates']), 'routes': len(t['routes']), 'assetRoles': len(roles),
        'assetRolesSettable': sum(1 for r in roles.values() if r['settableInPageSpec']),
        'graphRules': len(load('compatibility/graph.json')['rules']),
        'adversarialMutations': len(at.MUTATIONS), 'themes': len(os.listdir(os.path.join(ROOT, 'tokens', 'themes'))),
    }


@check('9 counts')
def c_counts(F, W, I):
    m = load('registry.manifest.json')['counts']
    real = recount()
    for k, v in real.items():
        if m.get(k) != v:
            F.append(f'manifest counts.{k} = {m.get(k)} but files say {v}')
    for k in set(m) - set(real):
        F.append(f'manifest counts.{k} is not recomputed by verify_all')
    with open(os.path.join(ROOT, 'README.md'), encoding='utf-8') as f:
        txt = f.read()
    blk = re.search(r'<!-- counts:start -->(.*?)<!-- counts:end -->', txt, re.S)
    if not blk:
        F.append('README.md has no counts block')
    else:
        rd = dict(re.findall(r'^- (\w+): (\d+)$', blk.group(1), re.M))
        for k, v in real.items():
            if rd.get(k) != str(v):
                F.append(f'README counts {k} = {rd.get(k)} but files say {v}')
    I.append(', '.join(f'{k}={v}' for k, v in real.items()))


CITE_KEYS = {'measuredFrom', 'cites', 'supersedes', 'frameworkCitation'}
CITE_RE = re.compile(r'^(?P<path>.+):(?P<a>\d+)(?:-(?P<b>\d+))?$')


def citations():
    for rel in json_files():
        if rel.startswith(os.path.join('extraction', 'evidence')):
            continue
        stack = [load(rel)]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in CITE_KEYS and isinstance(v, list):
                        for c in v:
                            yield rel, c
                    else:
                        stack.append(v)
            elif isinstance(o, list):
                stack.extend(o)


_FILES = {}


def file_lines(full):
    if full not in _FILES:
        with open(full, encoding='utf-8') as f:
            _FILES[full] = f.read().split('\n')
    return _FILES[full]


@check('10 citations')
def c_cites(F, W, I):
    n_int = n_ext = n_skip = n_expect = 0
    for rel, c in citations():
        ref, expect = (c, None) if isinstance(c, str) else (c.get('cite'), c.get('expect'))
        m = CITE_RE.match(ref or '')
        if not m:
            F.append(f'{rel}: malformed citation {ref!r}')
            continue
        path, a, b = m.group('path'), int(m.group('a')), int(m.group('b') or m.group('a'))
        if path.startswith('@repo/'):
            full, n_int = os.path.join(ROOT, path[6:]), n_int + 1
        else:
            if os.path.isabs(path) or '..' in path.split('/'):
                F.append(f'{rel}: citation path must be project-relative: {ref}')
                continue
            if not SIBLING:
                n_skip += 1
                continue
            full, n_ext = os.path.join(PROJECT, path), n_ext + 1
        if not os.path.isfile(full):
            F.append(f'{rel}: cited file missing: {path}')
            continue
        L = file_lines(full)
        if a < 1 or b < a or b > len(L):
            F.append(f'{rel}: {ref} out of range (file has {len(L)} lines)')
            continue
        if expect is not None:
            n_expect += 1
            if expect not in '\n'.join(L[a - 1:b]):
                F.append(f'{rel}: {ref} does not contain the expected text {expect[:60]!r} (cited code moved or changed)')
    if not SIBLING:
        W.append(f'sibling clone project not found next to design-repo/: {n_skip} external citation(s) skipped (expected for a standalone copy)')
    I.append(f'{n_int} internal + {n_ext} external citations resolved, {n_expect} with expected-text checks' + (f', {n_skip} skipped' if n_skip else ''))


@check('11 assets')
def c_assets(F, W, I):
    sys.path.insert(0, ROOT)
    doc = load('assets/asset-roles.json')
    roles = doc['roles']
    pol = set(doc['policies'])
    for k, r in roles.items():
        if r['generationPolicy'] not in pol:
            F.append(f'{k}: policy {r["generationPolicy"]} not in the closed policy set')
    for k, v in doc['pinnedPolicies'].items():
        if k not in roles:
            F.append(f'pinned role {k} missing')
        elif roles[k]['generationPolicy'] != v:
            F.append(f'PINNED policy drift: {k} is {roles[k]["generationPolicy"]!r}, must be {v!r}')
    settable = sorted(k for k, r in roles.items() if r['settableInPageSpec'])
    s = load('schema/pagespec.schema.json')
    if sorted(s['definitions']['assetRole']['enum']) != settable:
        F.append('schema definitions.assetRole enum != settable asset roles')
    if load('tokens/llm/component-allowlist.json')['assetRoles'] != settable:
        F.append('allowlist assetRoles != settable asset roles')
    used = set()

    def walk(o):
        if isinstance(o, dict):
            ar = o.get('properties', {}).get('assetRole')
            if isinstance(ar, dict):
                used.update(ar.get('enum', [ar['const']] if 'const' in ar else []))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk({k: v for k, v in s['definitions'].items() if k != 'assetRole'})
    walk(s['properties'])
    for r in sorted(used - set(settable)):
        F.append(f'schema field uses non-settable/unknown role {r}')
    for r in sorted(set(settable) - used):
        W.append(f'settable role {r} is not used by any schema field')
    ids = [a['id'] for r in roles.values() for a in r['assets']]
    if len(ids) != len(set(ids)):
        F.append('duplicate asset ids')
    missing = 0
    if SIBLING:
        for r in roles.values():
            for a in r['assets']:
                if not os.path.isfile(os.path.join(PROJECT, a['source'])):
                    F.append(f"asset source missing: {a['source']}")
                    missing += 1
    I.append(f'{len(roles)} roles ({len(settable)} settable), {len(doc["pinnedPolicies"])} pinned policies hold, {len(ids)} assets' + ('' if SIBLING else ' (sources not checked: no sibling project)'))


def token_tree():
    tree = {}
    for layer in ('00-foundation', '10-semantic', '20-component', '30-layout'):
        for f in sorted(os.listdir(os.path.join(ROOT, 'tokens', layer))):
            tree.update(load(f'tokens/{layer}/{f}'))
    return tree


def resolve(tree, ref):
    parts = ref.split('.')
    for i in range(len(parts), 0, -1):  # top-level keys may contain dots (component.button)
        top = '.'.join(parts[:i])
        if top in tree:
            node = tree[top]
            for p in parts[i:]:
                if not isinstance(node, dict) or p not in node:
                    return None
                node = node[p]
            return node
    return None


@check('12 tokens')
def c_tokens(F, W, I):
    tree = token_tree()
    n = 0
    for layer in ('10-semantic', '20-component', '30-layout'):
        for f in os.listdir(os.path.join(ROOT, 'tokens', layer)):
            for ref in re.findall(r'\{([a-z0-9][a-z0-9.-]*)\}', json.dumps(load(f'tokens/{layer}/{f}'))):
                n += 1
                if resolve(tree, ref) is None:
                    F.append(f'tokens/{layer}/{f}: unresolved token reference {{{ref}}}')
    th = load('tokens/themes/flashform-dark.json')
    roles = []

    def walk(o, p):
        for k, v in o.items():
            if k.startswith('$'):
                continue
            if isinstance(v, dict) and '$value' in v:
                roles.append(p + k)
            elif isinstance(v, dict):
                walk(v, p + k + '.')
    walk(tree['color-roles'], 'color-roles.')
    for r in roles:
        e = th['resolves'].get(r)
        tgt = resolve(tree, resolve(tree, r)['$value'].strip('{}'))
        if e is None:
            F.append(f'theme does not resolve {r}')
        elif tgt is None or e['value'] != tgt['$value']:
            F.append(f'theme value for {r} ({e["value"]}) != foundation ({tgt and tgt["$value"]})')
    cat = load('tokens/llm/token-catalog.json')['categories']
    for k in load('tokens/llm/token-policy.json')['rawValueRestrictions']:
        if k not in cat:
            F.append(f'token-policy key {k!r} is not a real catalog category')
    total = sum(len(v) for v in cat.values())
    leaves = sum(count_tokens(l) for l in ('00-foundation', '10-semantic', '20-component', '30-layout'))
    if total != leaves:
        F.append(f'token-catalog lists {total} tokens but token files hold {leaves}')
    I.append(f'{n} token references resolve; theme resolves {len(roles)} colour roles; catalog {total} tokens')


@check('13 manifest')
def c_manifest(F, W, I):
    m = load('registry.manifest.json')
    eps = m['entryPoints']
    flat = [p for v in eps.values() for p in (v if isinstance(v, list) else [v])]
    for p in flat:
        if os.path.isabs(p) or p.startswith('..') or '/../' in p:
            F.append(f'entryPoint outside design-repo: {p}')
        elif not os.path.exists(os.path.join(ROOT, p)):
            F.append(f'entryPoint missing: {p}')
    for k in ('repositoryId', 'status', 'productionApproved', 'defaultTheme', 'schemaValidatedThemes', 'versionFieldNote'):
        if k not in m:
            F.append(f'manifest missing {k}')
    if m.get('productionApproved') is not False:
        F.append('productionApproved must stay false until human design review')
    I.append(f'{len(flat)} entry points, all inside design-repo/')


@check('14 paths')
def c_paths(F, W, I):
    pats = ['/' + 'Users/', '/' + 'private/tmp', '/' + 'home/', 'C:' + '\\\\']
    n = 0
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            full = os.path.join(d, f)
            try:
                txt = open(full, encoding='utf-8').read()
            except (UnicodeDecodeError, OSError):
                continue
            n += 1
            for p in pats:
                if p in txt:
                    F.append(f'{os.path.relpath(full, ROOT)} contains an absolute local path ({p})')
    I.append(f'{n} text files scanned')


def main():
    for c in CHECKS:
        c()
    bad = 0
    print(f"verify_all  (repo: design-repo/, sibling clone project: {'present' if SIBLING else 'ABSENT - standalone mode'})")
    for name, F, W, I in RESULTS:
        status = 'FAIL' if F else ('WARN' if W else 'PASS')
        bad += bool(F)
        print(f'[{status}] {name:13s} {"; ".join(I)}')
        for x in F:
            print(f'        FAIL  {x}')
        for x in W:
            print(f'        warn  {x}')
    print(f'\n{len(RESULTS) - bad}/{len(RESULTS)} checks passed')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
