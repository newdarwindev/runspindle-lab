"""Restore an exact, runner-provisioned Lab submodule closure when available."""

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path("/home/runner/preparation/lab-checkout")

def git(repo, *args, bare=False):
    location = [f"--git-dir={repo}"] if bare else ["-C", str(repo)]
    return subprocess.check_output(
        ["git", "-c", "core.hooksPath=/dev/null", *location, *map(str, args)],
        text=True,
    )

def gitlinks(repo, *, bare=False):
    for entry in git(repo, "ls-tree", "-rz", "--full-tree", "HEAD", bare=bare).split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, _, revision = metadata.split()
        if mode == "160000":
            yield name, revision

def plan(root, cache):
    pins = cache / "pins.tsv"
    if not pins.is_file():
        return None
    available = {}
    for row in pins.read_text().splitlines():
        number, relative, revision = row.split("\t")
        path = Path(relative)
        if (not number.isdecimal() or path.is_absolute() or ".." in path.parts
                or relative in available or not re.fullmatch("[0-9a-f]{40}", revision)):
            raise ValueError("Invalid offline cache pin")
        available[relative] = (cache / f"{number}.git", revision)
    entries = []
    pending = [(root, "", False)]
    while pending:
        repo, prefix, bare = pending.pop()
        for name, revision in gitlinks(repo, bare=bare):
            relative = f"{prefix}{name}"
            entry = available.get(relative)
            if entry is None or entry[1] != revision:
                return None
            source = entry[0]
            if source.resolve(strict=True) != source or git(source, "rev-parse", "HEAD", bare=True).strip() != revision:
                raise ValueError("Offline checkout cache object differs from its recorded pin")
            entries.append((name, relative, source, revision))
            pending.append((source, relative + "/", True))
    if len(entries) != len(available.keys() - {"."}):
        return None
    return sorted(entries, key=lambda entry: (len(Path(entry[1]).parts), entry[1]))

def restore(root=ROOT, cache=CACHE):
    entries = plan(root, cache)
    if entries is None:
        return False
    for name, relative, source, revision in entries:
        destination = root / relative
        owner = destination
        for _ in Path(name).parts:
            owner = owner.parent
        if destination.resolve() != destination or (destination.exists() and any(destination.iterdir())):
            raise ValueError("Offline checkout destination is not empty and canonical")
        git(owner, "submodule", "init", "--", name)
        git(owner, "-c", "protocol.file.allow=always", "clone", "--quiet",
            "--no-hardlinks", "--no-tags", source, destination)
        if git(destination, "rev-parse", "HEAD").strip() != revision:
            raise ValueError("Offline checkout restored the wrong revision")
    if any(line[:1] != " " for line in git(root, "submodule", "status", "--recursive").splitlines()):
        raise ValueError("Offline checkout did not restore clean gitlinks")
    return True

if __name__ == "__main__":
    restored = restore()
    if restored:
        print("Restored exact Lab submodules from the runner checkout cache")
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        output.write(f"restored={str(restored).lower()}\n")
