# Reports, media and Pages

`tools/lab.py report` writes a static HTML status page and JSON under `artifacts/site/`. It reports unimplemented lanes as blocked, not green. This generated site is a preview, not a published result.

Future run bundles must carry: lab commit, recursively pinned source revisions, runner identity/OS/tool versions, case and evidence tier, command exit codes, independent assertion results, interruptions and unresolved effects, timestamps, and SHA-256 for every report, screenshot and recording. Fixture/component/product results must remain visibly separate. Blank metrics mean unmeasured, never zero.

Publish only reviewed synthetic evidence. Version media under immutable run/commit paths, with a manifest; never overwrite a prior result or load latest media into an old report. Large recordings should use versioned release assets with checksums rather than unbounded Git history. A Pages index should link versioned run pages and recordings, explicitly distinguishing historical evidence from current pins.

Pages deployment is intentionally absent until audience, evidence review and deployment approval are settled. Do not copy private runner inventory, logs, credentials, profiles, connected-account data or unrelated local files into reports. Public repository visibility alone is not permission to publish arbitrary machine data.
