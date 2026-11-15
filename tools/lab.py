#!/usr/bin/env python3
"""Offline lab scaffold. No tier substitution and no implicit dependency acquisition."""
import argparse
import hashlib
import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ('bakery-prep', 'bookkeeper-deposit')
TIERS = ('fixture', 'component', 'product')


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def check(root=ROOT):
    lock = json.loads((root / 'sources.lock.json').read_text())
    expected = {'sources/runspindle', 'sources/demo-suite'}
    sources = lock['sources']
    if {s['path'] for s in sources} != expected or len(sources) != 2:
        raise ValueError('Exactly two named source gitlinks are required')
    for s in sources:
        entry = git('ls-files', '--stage', '--', s['path'], cwd=root).split()
        if len(entry) != 4 or entry[:3] != ['160000', s['commit'], '0']:
            raise ValueError(f"Gitlink disagrees with lock: {s['path']}")
        if git('rev-parse', 'HEAD', cwd=root / s['path']) != s['commit']:
            raise ValueError(f"Checkout disagrees with lock: {s['path']}")
        url = git('config', '-f', '.gitmodules', f"submodule.{s['path']}.url", cwd=root)
        if url != s['url']:
            raise ValueError(f"Submodule URL disagrees with lock: {s['path']}")
        if git('status', '--porcelain', cwd=root / s['path']):
            raise ValueError(f"Dirty source checkout: {s['path']}")
    return sources


def blocked(case, tier):
    if case not in CASES or tier not in TIERS:
        raise ValueError('Unknown case or tier')
    return {'case': case, 'tier': tier, 'status': 'blocked',
            'reason': 'Lab case adapter not implemented; no fallback permitted',
            'measurements': None, 'media': [], 'productAcceptance': False}


def report(root=ROOT):
    sources = check(root)
    try:
        commit = git('rev-parse', 'HEAD', cwd=root)
    except subprocess.CalledProcessError:
        commit = None
    data = {'schema_version': 1, 'labCommit': commit,
            'labDirty': bool(git('status', '--porcelain', cwd=root)),
            'scope': 'scaffold status only, no executed business cases',
            'sources': sources,
            'runs': [blocked(case, tier) for case in CASES for tier in TIERS],
            'ciQualification': {'strix': 'not verified', 'macbook-pro': 'not verified'}}
    out = root / 'artifacts' / 'site'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'status.json').write_text(json.dumps(data, indent=2) + '\n')
    cards = ''.join(f'<li><strong>{html.escape(x["case"])} / {x["tier"]}</strong>: '
                    f'{x["status"]}. {html.escape(x["reason"])}</li>' for x in data['runs'])
    (out / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Runspindle Lab status</title><style>body{font:18px system-ui;max-width:900px;'
        'margin:48px auto;padding:0 24px;background:#101925;color:#eef4ff}li{margin:20px 0}'
        'a{color:#a6d8ff}</style><h1>Runspindle Lab</h1><p>Initial scaffold. No product '
        'acceptance, recordings or qualified dual-host CI are claimed.</p><ul>' + cards +
        '</ul><p>Source pins and exact status: <a href="status.json">JSON report</a>.</p></html>')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [out / 'index.html', out / 'status.json']}
    (out / 'sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'report', 'fixture-contracts', 'run'])
    parser.add_argument('--case', choices=CASES, default=CASES[0])
    parser.add_argument('--tier', choices=TIERS, default='product')
    args = parser.parse_args()
    if args.command == 'run':
        print(json.dumps(blocked(args.case, args.tier), indent=2))
        return 78
    if args.command == 'check':
        print(json.dumps({'sourcePins': check(), 'scope': 'top-level pins only'}, indent=2))
    elif args.command == 'report':
        print(report())
    else:
        check()
        demo = ROOT / 'sources' / 'demo-suite'
        status = git('submodule', 'status', '--recursive', cwd=demo)
        if any(line.startswith(('-', '+', 'U')) for line in status.splitlines()):
            raise ValueError('Demo child pins must be initialized and exact before fixture contracts')
        print('FIXTURE CONTRACT TESTS ONLY. No component/product acceptance.', flush=True)
        return subprocess.run([sys.executable, 'tools/demo.py', 'test'], cwd=demo).returncode
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Lab blocked or failed: {exc}', file=sys.stderr)
        sys.exit(1)
