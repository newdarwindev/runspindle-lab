# Runspindle Lab

Separate integration, reproducibility and evidence boundary for [Runspindle](https://github.com/newdarwindev/runspindle) and its [independent demo suite](https://github.com/newdarwindev/runspindle-demo-suite).

**Initial scaffold. Product integration, browser recordings and dual-host CI qualification are not delivered by this commit.**

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
