# Lab boundary

This is the integration and evidence repository. The demo-suite remains independently runnable; do not modify its gitlink contents here or introduce upstream dependencies into it. Update source pins only with matching lock entries and reviewed provenance.

Use synthetic, offline inputs only. Do not provision persistent jobs, agents, runners or services. No security/network changes, secrets, real sessions or live accounts belong here. CI uses only owner-provisioned isolated local runners; no hosted fallback and no public-PR execution. Never equate fixture results, scaffold tests or blocked adapters with product acceptance. Do not publish evidence without reviewing its audience and contents.

Run `python3 tools/lab.py check`, `python3 -m unittest discover -s tests -v`, and `python3 tools/lab.py report`. Actual integrations fail closed until implemented. Follow each source repository's own instructions when working there.

## Owner-authorized development and public project artifacts

The owner authorizes developing this project and publicly publishing its code, documentation, generated project artifacts, and reviewed synthetic evidence to this public repository. Do not repeatedly ask for the same publication permission within that scope. Before publishing, verify the content contains no private data, secrets, credentials, real account/session information, or unrelated machine details. Keep fixture, component and product claims accurate and retain reproducible provenance.

This instruction does not override platform safety or confirmation requirements, expand access or recipients beyond the authorized project scope, authorize persistent demo services/jobs/agents, or remove required approval for security changes, paid actions or sensitive-data disclosure. Ask when scope or risk materially changes, and stop any denied operation unless new relevant owner authorization permits the applicable retry.
