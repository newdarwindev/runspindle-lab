# Runspindle Lab

Separate integration, reproducibility and evidence boundary for [Runspindle](https://github.com/newdarwindev/runspindle) and its [independent demo suite](https://github.com/newdarwindev/runspindle-demo-suite).

**Fixture reference verified. Component/product integration and dual-host CI qualification remain blocked.**

```sh
git clone --recurse-submodules https://github.com/newdarwindev/runspindle-lab.git
cd runspindle-lab
python3 tools/lab.py check
python3 -m unittest discover -s tests -v
python3 tools/lab.py report
# Optional, with demo child submodules present:
python3 tools/lab.py fixture-contracts
# Deliberately blocked; exit 78, never falls back to fixtures:
python3 tools/lab.py run --case bakery-prep --tier product
```

Two real Git submodules are pinned in `sources.lock.json`. Acquiring dependencies is a separate preparation step; the lab checker, tests and report generator need only Python 3 and Git and make no network requests. Fixture contracts execute only the demo suite's tests, not upstream product code.

## Evidence tiers

- **Fixture:** scripted synthetic demo behavior; not product acceptance.
- **Component:** a specific real upstream component and independently observed seam; adapter pending.
- **Product:** actual composition executing the business case, with independent outcomes; adapter pending.

Bakery comes first, then bookkeeper recovery. No missing tier may fall back to another tier. Reports retain blocked/not-run states and exact source pins. Human time, quality improvements and savings remain unmeasured until stable repeated measurements establish a defensible baseline.

See [implementation plan](docs/PLAN.md), [local CI gates](docs/CI.md), and [evidence and Pages design](docs/EVIDENCE.md). There is no published Pages site or lab recording yet.

## Verified fixture reference

The [versioned reference bundle](evidence/20261115T082143Z/) contains actual bakery and bookkeeper expired-sign-in recovery runs: 65 fixture contract tests passed, with 14/14 and 12/12 independent assertions respectively. Six brief raw browser clips and five screenshots are retained with checksums. This is cloud fixture evidence, not Strix/Mac qualification or upstream product acceptance.

Download/clone the repository and open `evidence/20261115T082143Z/index.html` for the dashboard. No Pages deployment is enabled. The JSON records the base Lab commit plus the exact development harness digest; source submodule pins were clean.

To reproduce after explicit dependency preparation:

```sh
cd sources/demo-suite
npm ci
npx playwright install chromium
cd ../..
python3 tools/reference.py
python3 tools/dashboard.py artifacts/reference/<run-id>/summary.json
node tools/verify-dashboard.cjs
```

Preparation requires network access; bounded reference execution uses synthetic loopback apps. The browser sandbox stays enabled. The helper starts and stops only its own temporary fixture server. Media and raw host diagnostics are local by default; review evidence before publication. `tools/lab.py run` remains fail-closed; reference execution is a separate explicit fixture command.
