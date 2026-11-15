#!/usr/bin/env python3
"""Build a static, network-free evidence dashboard; never deploys it."""
import hashlib
import html
import json
from pathlib import Path
import shutil
from lab import ROOT


def render(data):
    esc = html.escape
    cards = []
    for run in data['runs']:
        passed = sum(v is True for v in run['checks'].values())
        total = len(run['checks'])
        checks = ''.join(f'<li><span>{"PASS" if v is True else "FAIL"}</span> {esc(k.replace("_", " "))}</li>' for k,v in run['checks'].items())
        seconds = run['metrics']['elapsedSeconds']
        poster = next((m['path'] for m in run['media'] if m['path'].endswith('/result.png')), '')
        hero = f'<img alt="Verified synthetic workbook result" src="{esc(poster, quote=True)}">' if poster else ''
        media = ''.join(f'<video controls preload="metadata" poster="{esc(poster, quote=True)}" src="{esc(m["path"], quote=True)}"></video>' if m['path'].endswith('.webm') else f'<a href="{esc(m["path"], quote=True)}"><img loading="lazy" alt="Synthetic {esc(run["case"], quote=True)} fixture evidence" src="{esc(m["path"], quote=True)}"></a>' for m in run['media'])
        cards.append(f'<article><div class="eyebrow">FIXTURE / {esc(run["fault"])}</div><h2>{esc(run["case"].replace("-", " ").title())}</h2><div class="badge">{esc(run["outcome"]).upper()}</div><div class="metrics"><div><b>{passed}/{total}</b><small>independent checks</small></div><div><b>{seconds:.2f}s</b><small>observed wall time</small></div><div><b>{len(run["media"])}</b><small>evidence files</small></div></div><details><summary>Inspect assertions and provenance</summary><ul>{checks}</ul><p class="mono">{esc(run["runId"])}</p><p>Demo source: <code>{esc(run["parentCommit"])}</code></p></details><div class="media">{hero}</div><details><summary>Open {len(run["media"])} recordings and screenshots</summary><p>Raw clips are brief automated interactions, not real-time human demonstrations.</p><div class="media">{media or "No browser media captured. This is not a successful recording."}</div></details></article>')
    pins = ''.join(f'<li><span>{esc(s["path"])}</span><code>{esc(s["commit"])}</code></li>' for s in data['sources'])
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Runspindle Lab · Evidence</title><style>
:root{color-scheme:dark;--bg:#0c1320;--panel:#131e2f;--line:#2a384c;--muted:#a4b6ca;--accent:#9fe1ca}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#eff5fc;font:16px/1.6 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:32px 28px 70px}nav{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:22px}.brand{font-weight:700;letter-spacing:.08em}a{color:var(--accent)}.eyebrow{color:var(--accent);font-size:12px;font-weight:700;letter-spacing:.15em}header{padding:58px 0 28px}h1{font-size:clamp(36px,6vw,64px);letter-spacing:-.055em;line-height:1.08;max-width:800px;margin:18px 0}header p{max-width:760px;color:var(--muted);font-size:19px}.notice{border-left:3px solid #dfb970;background:#211e20;padding:18px 22px;margin:20px 0 30px}.tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0}.tier,article{border:1px solid var(--line);background:var(--panel);border-radius:16px;padding:24px}.tier strong{display:block}.tier p{color:var(--muted);margin-bottom:0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}h2{margin:8px 0 14px;font-size:27px}.badge{display:inline-block;border:1px solid #526577;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:700}.metrics{display:flex;gap:24px;padding:26px 0}.metrics b{display:block;font-size:25px}.metrics small{color:var(--muted);font-size:11px}details{border-top:1px solid var(--line);padding-top:16px}summary{cursor:pointer}details ul{padding-left:20px;font-size:13px}details li span{color:var(--accent)}.media{display:grid;gap:12px;margin-top:20px}.media video,.media img{width:100%;border-radius:9px;background:#080e16}code,.mono{font-size:11px;overflow-wrap:anywhere;color:var(--muted)}.provenance{border-top:1px solid var(--line);margin-top:38px;padding-top:20px}.provenance li{margin:12px 0}.provenance code{display:block}footer{color:var(--muted);font-size:13px;margin-top:32px}@media(max-width:740px){.grid,.tiers{grid-template-columns:1fr}main{padding:24px 18px}.metrics{gap:20px}header{padding-top:35px}}
</style></head><body><main><nav><span class="brand">RUNSPINDLE / LAB</span><a href="summary.json">Evidence JSON ↗</a></nav><header><div class="eyebrow">PINNED SOURCES · SYNTHETIC DATA · NO FALLBACK</div><h1>Evidence before<br>integration claims.</h1><p>Reference execution of the independent demo suite. Inspect actual assertions, observed timings and recordings while keeping component and product acceptance separate.</p></header><div class="notice"><strong>Scope:</strong> ''' + esc(data['environment']) + '''. These results do not establish Strix or MacBook Pro CI qualification, real product integration, human-time savings or performance baselines.</div><section class="tiers"><div class="tier"><strong>01 / Fixture</strong><p>Reference results below. Scripted synthetic apps, independent persisted-state checks.</p></div><div class="tier"><strong>02 / Component</strong><p>BLOCKED · Business-case adapter not implemented. No fixture substitution.</p></div><div class="tier"><strong>03 / Product</strong><p>BLOCKED · Full integration not implemented. Acceptance remains closed.</p></div></section><p>Contract suite: <strong>''' + esc(data['contractTests']['status'].upper()) + '''</strong>. Reference bundle <code>''' + esc(data['id']) + '''</code>.</p><section class="grid">''' + ''.join(cards) + '''</section><section class="provenance"><h2>Reproducible boundaries</h2><p>Exact source pins for this reference. Media hashes are retained in the JSON; all page assets have a checksum manifest.</p><ul>''' + pins + '''</ul><a href="sha256.json">Verify bundle checksums</a></section><footer>Static preview, not a deployed Pages site. Missing metrics mean unmeasured, never zero. Failed and blocked outcomes remain visible. Media is synthetic fixture evidence.</footer></main></body></html>'''


def build(summary, destination):
    data = json.loads(summary.read_text())
    if data['tier'] != 'fixture' or data['upstreamExecuted'] is not False:
        raise ValueError('Only explicitly synthetic fixture evidence supported')
    destination.mkdir(parents=True, exist_ok=True)
    for run in data['runs']:
        for media in run['media']:
            rel = Path(media['path'])
            if rel.is_absolute() or '..' in rel.parts: raise ValueError('Unsafe media path')
            source = summary.parent / rel
            if hashlib.sha256(source.read_bytes()).hexdigest() != media['sha256']:
                raise ValueError('Media checksum mismatch')
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != target.resolve(): shutil.copyfile(source, target)
    (destination / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
    (destination / 'index.html').write_text(render(data))
    checksums = {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(destination.rglob('*')) if p.is_file() and p.name != 'sha256.json'}
    (destination / 'sha256.json').write_text(json.dumps(checksums, indent=2) + '\n')
    return destination


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('summary', type=Path); p.add_argument('--output', type=Path, default=ROOT/'artifacts/dashboard')
    args = p.parse_args(); print(build(args.summary, args.output))
