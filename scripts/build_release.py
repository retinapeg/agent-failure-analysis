#!/usr/bin/env python3
"""Build a release ZIP of the skill: one top-level folder, a manifest, install/remove instructions.

Usage: python3 scripts/build_release.py [--out dist]

Refuses to package caches, evaluation answer keys, or files that look like secrets.
Timestamps inside the ZIP are fixed so the archive is byte-stable for identical inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "skills" / "agent-failure-analysis"
SKILL_NAME = "agent-failure-analysis"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
SECRET_PATTERNS = [
    re.compile(p) for p in (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bsk-[A-Za-z0-9]{20,}\b",
        r"\bghp_[A-Za-z0-9]{36}\b",
        r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    )
]
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def skill_version() -> str:
    text = (SKILL_DIR / "scripts" / "trace_tools.py").read_text(encoding="utf-8")
    m = re.search(r'^SKILL_VERSION = "([^"]+)"', text, re.M)
    if not m:
        raise SystemExit("could not find SKILL_VERSION in trace_tools.py")
    return m.group(1)


def collect_files() -> list[Path]:
    files = []
    for p in sorted(SKILL_DIR.rglob("*")):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(SKILL_DIR).parts):
            continue
        if p.suffix in EXCLUDE_SUFFIXES or p.name in EXCLUDE_DIRS:
            continue
        files.append(p)
    return files


def scan_secrets(files: list[Path]) -> list[str]:
    hits = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                shown = p.relative_to(REPO) if p.is_relative_to(REPO) else p
                hits.append(f"{shown}: matches {pat.pattern}")
    return hits


def install_text(version: str) -> str:
    return f"""# Installing agent-failure-analysis {version}

This ZIP contains one top-level folder, `{SKILL_NAME}/`, holding the skill.
Nothing is installed until you copy that folder into a skills directory.

## Claude Code (verified against code.claude.com/docs/en/skills on 2026-09-23)

Personal (all projects on this machine):

    unzip {SKILL_NAME}-{version}.zip -d ~/.claude/skills/

Project (this repository only, can be committed):

    unzip {SKILL_NAME}-{version}.zip -d .claude/skills/

Check discovery: start `claude`, type `/skills`, and look for `{SKILL_NAME}`.

Remove:

    rm -rf ~/.claude/skills/{SKILL_NAME}
    rm -rf .claude/skills/{SKILL_NAME}

## Codex (per learn.chatgpt.com/docs/build-skills on 2026-09-23; format-compatible, untested)

Repository level:

    unzip {SKILL_NAME}-{version}.zip -d .agents/skills/

User level:

    unzip {SKILL_NAME}-{version}.zip -d ~/.agents/skills/

Restart Codex after adding or removing a skill. Remove by deleting the folder,
or disable it in `~/.codex/config.toml`:

    [[skills.config]]
    path = "/path/to/{SKILL_NAME}/SKILL.md"
    enabled = false

## Requirements

Python 3.11 or newer on PATH as `python3`. No packages. No network.

## Data handling

The package makes no outbound requests. The host model you run it in still
processes the trace under that host's data handling terms. Do not analyse
sensitive logs in a host you would not paste them into.
"""


def build(out_dir: Path) -> Path:
    version = skill_version()
    files = collect_files()
    if not files or SKILL_DIR / "SKILL.md" not in files:
        raise SystemExit("skill folder is missing SKILL.md")
    hits = scan_secrets(files)
    if hits:
        raise SystemExit("refusing to package: possible secrets found:\n  " + "\n  ".join(hits))
    for p in files:
        rel = p.relative_to(REPO)
        if "evaluation" in rel.parts or "tests" in rel.parts:
            raise SystemExit(f"refusing to package evaluation or test material: {rel}")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{SKILL_NAME}-{version}.zip"
    manifest_lines = []
    entries: list[tuple[str, bytes]] = []
    for p in files:
        data = p.read_bytes()
        arc = f"{SKILL_NAME}/{p.relative_to(SKILL_DIR).as_posix()}"
        entries.append((arc, data))
        manifest_lines.append(f"{hashlib.sha256(data).hexdigest()}  {arc}")
    install = install_text(version).encode("utf-8")
    entries.append((f"{SKILL_NAME}/INSTALL.md", install))
    manifest_lines.append(f"{hashlib.sha256(install).hexdigest()}  {SKILL_NAME}/INSTALL.md")
    manifest = ("# agent-failure-analysis release manifest\n"
                f"# version {version}\n# sha256  path\n" + "\n".join(manifest_lines) + "\n").encode("utf-8")
    entries.append((f"{SKILL_NAME}/MANIFEST.txt", manifest))

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arc, data in sorted(entries):
            info = zipfile.ZipInfo(arc, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 << 16)
            zf.writestr(info, data)
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (out_dir / f"{zip_path.name}.sha256").write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    print(f"wrote {zip_path} ({zip_path.stat().st_size} bytes)")
    print(f"sha256 {digest}")
    print(f"{len(entries)} entries")
    return zip_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(REPO / "dist"))
    args = ap.parse_args(argv)
    build(Path(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
