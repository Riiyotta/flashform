#!/usr/bin/env python3
"""Prove verify_all.py actually catches drift (not just that it passes on a correct repo).

For each mutation: copy design-repo/ into a fresh scratch directory, inject one defect, run verify_all.py there
with `python -I`, and require that it FAILS on the expected check. Two controls must PASS unmutated:
a standalone copy (no sibling project: external citations warn-skip) and a copy placed next to a mirror of the
sibling clone project (external citations fully checked).

The mirror symlinks the clone project's files except src/, which is COPIED so one mutation can shift a source
file's lines and prove the expected-text check notices cited code that moved.

Usage: python3 -I extraction/drift_test.py [--workdir DIR]     (default: a new tempfile.mkdtemp())
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.dirname(ROOT)
HAS_SIBLING = os.path.isfile(os.path.join(PROJECT, 'src', 'App.jsx'))


def jload(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def jsave(p, o):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(o, f, indent=2, ensure_ascii=False)


def make(base, name, with_sibling):
    d = os.path.join(base, name)
    os.makedirs(d)
    if with_sibling:
        for item in os.listdir(PROJECT):
            if item in ('design-repo', 'design-repo.zip', 'node_modules', 'dist') or item.startswith('.'):
                continue
            src = os.path.join(PROJECT, item)
            if item == 'src':
                shutil.copytree(src, os.path.join(d, item))
            else:
                os.symlink(src, os.path.join(d, item))
    repo = os.path.join(d, 'design-repo')
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
    return d, repo


def run_verify(repo):
    p = subprocess.run([sys.executable, '-I', os.path.join(repo, 'extraction', 'verify_all.py')], capture_output=True, text=True)
    failed = [l.split(']', 1)[1].strip().split()[0:2] for l in p.stdout.splitlines() if l.startswith('[FAIL]')]
    return p.returncode, [' '.join(x) for x in failed], p.stdout


def m_phantom_allowlist(r, proj):
    p = os.path.join(r, 'tokens/llm/component-allowlist.json')
    a = jload(p)
    a['primitives'].append({'id': 'divider', 'file': 'primitives/divider.json', 'instantiableInPageSpec': False})
    jsave(p, a)


def m_orphan_contract(r, proj):
    jsave(os.path.join(r, 'primitives/badge.json'), {'id': 'badge', 'kind': 'primitive'})


def m_internal_cite_out_of_range(r, proj):
    p = os.path.join(r, 'compatibility/graph.json')
    g = jload(p)
    g['rules'][0]['measuredFrom'][0]['cite'] = '@repo/templates/templates.json:99999'
    jsave(p, g)


def m_internal_cite_wrong_code(r, proj):
    p = os.path.join(r, 'compatibility/graph.json')
    g = jload(p)
    g['rules'][0]['measuredFrom'][0]['expect'] = 'text that is not on that line'
    jsave(p, g)


def m_external_cite_out_of_range(r, proj):
    p = os.path.join(r, 'sections/hero.sticky-statement.json')
    s = jload(p)
    s['measuredFrom'][0]['cite'] = 'src/components/Hero.jsx:5000'
    jsave(p, s)


def m_source_lines_shift(r, proj):
    p = os.path.join(proj, 'src', 'index.css')
    with open(p, encoding='utf-8') as f:
        txt = f.read()
    with open(p, 'w', encoding='utf-8') as f:
        f.write('/* inserted */\n/* lines */\n' + txt)


def m_wrong_count(r, proj):
    p = os.path.join(r, 'registry.manifest.json')
    m = jload(p)
    m['counts']['sections'] += 1
    jsave(p, m)


def m_allowlist_version(r, proj):
    p = os.path.join(r, 'registry.manifest.json')
    m = jload(p)
    m['allowlistVersion'] = '9.9.9'
    jsave(p, m)


def m_pinned_policy(r, proj):
    p = os.path.join(r, 'assets/asset-roles.json')
    a = jload(p)
    a['roles']['icon.third-party-channel']['generationPolicy'] = 'may-generate-new'  # different but still a valid enum value
    jsave(p, a)


def m_graph_rule_unimplemented(r, proj):
    p = os.path.join(r, 'compatibility/graph.json')
    g = jload(p)
    g['rules'].append({'id': 'NO_TWO_ACCENT_PANELS', 'severity': 'error', 'description': 'drift', 'measuredFrom': []})
    jsave(p, g)


def m_absolute_path(r, proj):
    with open(os.path.join(r, 'README.md'), 'a', encoding='utf-8') as f:
        f.write('\nsee ' + '/' + 'Users/someone/design-repo\n')


def m_entrypoint_outside(r, proj):
    p = os.path.join(r, 'registry.manifest.json')
    m = jload(p)
    m['entryPoints']['spec'] = '../CLONE_SPEC.md'
    jsave(p, m)


def m_contract_schema_divergence(r, proj):
    p = os.path.join(r, 'sections/faq.accordion.json')
    s = jload(p)
    s['content']['schema']['properties']['items']['maxItems'] = 9
    jsave(p, s)


def m_theme_drift(r, proj):
    p = os.path.join(r, 'tokens/themes/flashform-dark.json')
    t = jload(p)
    t['resolves']['color-roles.text.default']['value'] = '#00ff00'
    jsave(p, t)


def m_adversarial_regression(r, proj):
    # weaken the validator: drop the template cross-reference rule body -> adversarial suite must notice
    p = os.path.join(r, 'schema/semantic_validate.py')
    with open(p, encoding='utf-8') as f:
        src = f.read()
    src = src.replace("def r_template_node_sequence(spec, repo, emit):\n", "def r_template_node_sequence(spec, repo, emit):\n    return\n", 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(src)


def _roles(r):
    p = os.path.join(r, 'assets/asset-roles.json')
    return p, jload(p)


def _asset(doc, aid):
    return next(a for ro in doc['roles'].values() for a in ro['assets'] if a['id'] == aid)


def m_avail_invalid(r, proj):
    p, d = _roles(r)
    d['roles']['icon.generic-channel']['availability'] = 'semi-safe'  # not in the closed availability set
    jsave(p, d)


def m_avail_unclassified(r, proj):
    p, d = _roles(r)
    del d['roles']['icon.generic-channel']['availability']
    jsave(p, d)


def m_logo_role_avail(r, proj):
    p, d = _roles(r)
    d['roles']['brand.logo']['availability'] = 'generation-safe'  # a valid enum value, but the real logo is pinned reference-only
    jsave(p, d)


def m_logo_role_and_pin_map(r, proj):
    p, d = _roles(r)
    d['roles']['brand.logo']['availability'] = 'generation-safe'
    d['pinnedAvailability']['brand.logo'] = 'generation-safe'  # the in-file pin map is edited too: the pin in code must still hold
    jsave(p, d)


def m_logo_asset_avail(r, proj):
    p, d = _roles(r)
    _asset(d, 'asset:logo-flashform')['availability'] = 'generation-safe'
    jsave(p, d)


def m_favicon_asset_avail(r, proj):
    p, d = _roles(r)
    _asset(d, 'asset:favicon')['availability'] = 'generation-safe'
    jsave(p, d)


def m_protected_asset_unclassified(r, proj):
    p, d = _roles(r)
    del _asset(d, 'asset:og-twitter')['availability']
    jsave(p, d)


def m_validator_pin_changed(r, proj):
    p = os.path.join(r, 'schema/semantic_validate.py')
    with open(p, encoding='utf-8') as f:
        src = f.read()
    src = src.replace("PINNED_ROLE_AVAILABILITY = {'brand.logo': 'reference-only'}", "PINNED_ROLE_AVAILABILITY = {'brand.logo': 'generation-safe'}", 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(src)


def m_schema_mode_enum(r, proj):
    p = os.path.join(r, 'schema/pagespec.schema.json')
    s = jload(p)
    s['properties']['mode']['enum'].append('hybrid')
    jsave(p, s)


def m_gen_example_no_mode(r, proj):
    p = os.path.join(r, 'schema/example.generated.pagespec.json')
    e = jload(p)
    del e['mode']
    jsave(p, e)


def m_gen_example_wrong_mode(r, proj):
    p = os.path.join(r, 'schema/example.generated.pagespec.json')
    e = jload(p)
    e['mode'] = 'reference'
    jsave(p, e)


def m_ref_example_wrong_mode(r, proj):
    p = os.path.join(r, 'schema/example.pagespec.json')
    e = jload(p)
    e['mode'] = 'generated'
    jsave(p, e)


def m_gen_example_real_logo(r, proj):
    p = os.path.join(r, 'schema/example.generated.pagespec.json')
    e = jload(p)
    e['nodes'][0]['content']['logo'] = {'assetRole': 'brand.logo', 'assetRef': 'asset:logo-flashform'}
    jsave(p, e)


def m_gen_example_mentions_brand(r, proj):
    p = os.path.join(r, 'schema/example.generated.pagespec.json')
    e = jload(p)
    e['meta']['description'] = 'A demo that mentions Flashform.'
    jsave(p, e)


def m_logo_enum_contract(r, proj):
    p = os.path.join(r, 'schema/pagespec.schema.json')
    s = jload(p)
    s['definitions']['content.shell.navbar']['properties']['logo']['properties']['assetRole']['enum'].remove('brand.placeholder')
    jsave(p, s)


def m_manifest_lacks_example(r, proj):
    p = os.path.join(r, 'registry.manifest.json')
    m = jload(p)
    del m['entryPoints']['exampleGenerated']
    jsave(p, m)


def m_graph_mode_rule_removed(r, proj):
    p = os.path.join(r, 'compatibility/graph.json')
    g = jload(p)
    g['rules'] = [x for x in g['rules'] if x['id'] != 'GENERATED_MODE_BLOCKS_REFERENCE_ASSETS']
    jsave(p, g)


def m_validator_mode_rule_noop(r, proj):
    p = os.path.join(r, 'schema/semantic_validate.py')
    with open(p, encoding='utf-8') as f:
        src = f.read()
    src = src.replace("def r_generated_mode_blocks_reference_assets(spec, repo, emit):\n", "def r_generated_mode_blocks_reference_assets(spec, repo, emit):\n    return\n", 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(src)


MUTATIONS = [
    ('phantom allowlist entry', '5 allowlist', m_phantom_allowlist, False),
    ('contract file with no allowlist entry', '5 allowlist', m_orphan_contract, False),
    ('internal citation out of range', '10 citations', m_internal_cite_out_of_range, False),
    ('internal citation in range but wrong code', '10 citations', m_internal_cite_wrong_code, False),
    ('external citation out of range', '10 citations', m_external_cite_out_of_range, True),
    ('cited source lines shifted (sibling edited)', '10 citations', m_source_lines_shift, True),
    ('manifest count drift', '9 counts', m_wrong_count, False),
    ('allowlistVersion drift', '8 versions', m_allowlist_version, False),
    ('pinned asset policy drift to another valid value', '11 assets', m_pinned_policy, False),
    ('graph rule without validator implementation', '7 graph', m_graph_rule_unimplemented, False),
    ('absolute local path injected', '14 paths', m_absolute_path, False),
    ('entryPoint outside design-repo', '13 manifest', m_entrypoint_outside, False),
    ('section contract diverges from schema', '6 contracts', m_contract_schema_divergence, False),
    ('theme value drift', '12 tokens', m_theme_drift, False),
    ('validator loses its template cross-reference', '4 adversarial', m_adversarial_regression, False),
    # ---- reference/generated mode + generation-safe brand (availability, pins, examples, schema/contract enums)
    ('availability outside the closed enum', '11 assets', m_avail_invalid, False),
    ('role without an availability (unclassified)', '11 assets', m_avail_unclassified, False),
    ('real-logo role availability -> another valid value', '11 assets', m_logo_role_avail, False),
    ('real-logo role AND its in-file pin map changed (pin in code holds)', '11 assets', m_logo_role_and_pin_map, False),
    ('real-logo asset availability -> generation-safe', '11 assets', m_logo_asset_avail, False),
    ('real favicon asset availability -> generation-safe', '11 assets', m_favicon_asset_avail, False),
    ('protected-role asset without explicit availability', '11 assets', m_protected_asset_unclassified, False),
    ('validator pin for the real logo changed', '11 assets', m_validator_pin_changed, False),
    ('schema mode enum gains a value', '15 modes', m_schema_mode_enum, False),
    ('generated example loses mode', '2 schema', m_gen_example_no_mode, False),
    ('generated example flipped to mode reference', '15 modes', m_gen_example_wrong_mode, False),
    ('reference example flipped to mode generated', '15 modes', m_ref_example_wrong_mode, False),
    ('generated example carries the real Flashform logo', '3 semantic', m_gen_example_real_logo, False),
    ('generated example mentions the source brand', '15 modes', m_gen_example_mentions_brand, False),
    ('schema logo role enum loses a brand role (contract divergence)', '15 modes', m_logo_enum_contract, False),
    ('manifest stops listing the generated example', '15 modes', m_manifest_lacks_example, False),
    ('graph loses a mode rule', '7 graph', m_graph_mode_rule_removed, False),
    ('validator mode rule becomes a no-op', '4 adversarial', m_validator_mode_rule_noop, False),
]


def main(argv):
    work = argv[argv.index('--workdir') + 1] if '--workdir' in argv else tempfile.mkdtemp(prefix='flashform-drift-')
    work = os.path.join(work, 'drift-run')
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    fails = 0
    print('CONTROLS (unmutated copies must PASS)')
    for name, sib in (('standalone copy (no sibling)', False), ('copy next to sibling mirror', True)):
        if sib and not HAS_SIBLING:
            print(f'  SKIP  {name}: no sibling clone project next to this design-repo')
            continue
        _, repo = make(work, 'control-' + ('sib' if sib else 'solo'), sib)
        rc, failed, out = run_verify(repo)
        ok = rc == 0
        fails += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + ('' if ok else f' -> failed checks {failed}'))
    print('MUTATIONS (verify_all must FAIL on the expected check)')
    for i, (name, expect, fn, sib) in enumerate(MUTATIONS):
        if sib and not HAS_SIBLING:
            print(f'  SKIP  {name}: needs the sibling clone project')
            continue
        proj, repo = make(work, f'm{i:02d}', sib)
        fn(repo, proj)
        rc, failed, out = run_verify(repo)
        ok = rc != 0 and expect in failed
        fails += not ok
        detail = next((l.strip() for l in out.splitlines() if l.strip().startswith('FAIL') and l.strip() != 'FAIL'), '')
        print(f"  {'CAUGHT' if ok else 'MISSED'}  [{expect}] {name}  :: {detail[:120]}")
    shutil.rmtree(work)
    print(f'\n{len(MUTATIONS)} drift mutations, {fails} failed expectation(s)')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
