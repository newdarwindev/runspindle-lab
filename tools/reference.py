#!/usr/bin/env python3
"""Bounded synthetic reference execution. Does not start persistent services."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
from lab import ROOT, check, git


def execute():
    sources = check()
    demo = ROOT / 'sources/demo-suite'
    if any(line.startswith(('-', '+', 'U')) for line in git('submodule', 'status', '--recursive', cwd=demo).splitlines()):
        raise ValueError('Initialize exact demo child pins before reference execution')
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = ROOT / 'artifacts/reference' / stamp
    out.mkdir(parents=True)
    data = {'schema_version': 1, 'id': stamp, 'tier': 'fixture', 'upstreamExecuted': False,
            'labCommit': git('rev-parse', 'HEAD'), 'sources': sources,
            'environment': 'cloud development container, not Strix or Mac CI',
            'contractTests': {'status': 'not-run'}, 'runs': [],
            'limitations': ['Synthetic scripted browser fixture, not product integration.',
                            'Human operator time and savings are unmeasured.',
                            'This run does not qualify either local CI host.']}
    tests = subprocess.run([sys.executable, 'tools/demo.py', 'test'], cwd=demo,
                           capture_output=True, text=True, timeout=120)
    (out / 'contract-tests.log').write_text(tests.stdout + tests.stderr)
    data['contractTests'] = {'status': 'passed' if tests.returncode == 0 else 'failed',
                             'exitCode': tests.returncode,
                             'logSha256': hashlib.sha256((tests.stdout + tests.stderr).encode()).hexdigest()}
    server = None
    try:
        # Do not attach to or kill an unrelated existing service.
        import socket
        ports = [4300 + i for i in range(len(json.loads((demo/'contracts/apps.json').read_text())))]
        reservations = []
        try:
            for port in ports:
                sock = socket.socket(); reservations.append(sock); sock.bind(('127.0.0.1', port))
        finally:
            for sock in reservations: sock.close()
        with (out / 'server.log').open('w') as log:
            server = subprocess.Popen([sys.executable, 'tools/demo.py', 'up'], cwd=demo, stdout=log, stderr=log)
            for _ in range(100):
                if server.poll() is not None: raise RuntimeError('Fixture server exited')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:4300/health', timeout=1) as response:
                        if response.status == 200: break
                except OSError: time.sleep(.1)
            else: raise RuntimeError('Fixture server did not become ready')
            for case, fault in [('bakery-prep', 'normal'), ('bookkeeper-deposit', 'expired')]:
                before = set((demo / 'artifacts').glob('*/manifest.json'))
                result = subprocess.run([sys.executable, 'tools/demo.py', 'record', case, '--fault', fault],
                                        cwd=demo, capture_output=True, text=True, timeout=180)
                (out / f'{case}.log').write_text(result.stdout + result.stderr)
                created = set((demo / 'artifacts').glob('*/manifest.json')) - before
                if len(created) != 1: raise RuntimeError('Expected exactly one new manifest')
                manifest = json.loads(next(iter(created)).read_text())
                run_dir = next(iter(created)).parent
                record = {k: manifest[k] for k in ['runId','case','fault','parentCommit','childCommits',
                           'executionMode','upstreamExecuted','outcome','metrics','checks','limitations']}
                record['exitCode'] = result.returncode
                record['media'] = []
                for filename in manifest['media']['clips'] + manifest['media']['screenshots']:
                    source = run_dir / filename
                    if Path(filename).name != filename: raise ValueError('Invalid media path')
                    target = out / manifest['runId'] / filename
                    target.parent.mkdir(exist_ok=True)
                    shutil.copyfile(source, target)
                    record['media'].append({'path': str(target.relative_to(out)),
                                            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                                            'bytes': target.stat().st_size})
                data['runs'].append(record)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        data['executionBlocker'] = type(exc).__name__  # raw host diagnostics stay local
    finally:
        if server is not None:
            server.terminate()
            try: server.wait(timeout=10)
            except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=5)
        (out / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
    print(out / 'summary.json')
    return 0 if tests.returncode == 0 and len(data['runs']) == 2 and all(x['outcome']=='verified' for x in data['runs']) else 78


if __name__ == '__main__':
    sys.exit(execute())
