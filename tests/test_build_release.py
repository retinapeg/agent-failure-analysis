import hashlib
import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "scripts" / "build_release.py"


def test_release_zip_contents_and_determinism(tmp_path):
    r1 = subprocess.run([sys.executable, str(BUILD), "--out", str(tmp_path / "a")], capture_output=True, text=True)
    assert r1.returncode == 0, r1.stderr
    r2 = subprocess.run([sys.executable, str(BUILD), "--out", str(tmp_path / "b")], capture_output=True, text=True)
    assert r2.returncode == 0, r2.stderr
    za = next((tmp_path / "a").glob("*.zip"))
    zb = next((tmp_path / "b").glob("*.zip"))
    assert za.read_bytes() == zb.read_bytes(), "zip is not byte-stable"
    with zipfile.ZipFile(za) as zf:
        names = zf.namelist()
        assert all(n.startswith("agent-failure-analysis/") for n in names)
        assert "agent-failure-analysis/SKILL.md" in names
        assert "agent-failure-analysis/scripts/trace_tools.py" in names
        assert "agent-failure-analysis/INSTALL.md" in names
        assert "agent-failure-analysis/MANIFEST.txt" in names
        assert not any("evaluation" in n or "tests" in n or "__pycache__" in n for n in names)
        manifest = zf.read("agent-failure-analysis/MANIFEST.txt").decode()
        for line in manifest.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            digest, arc = line.split("  ", 1)
            assert hashlib.sha256(zf.read(arc)).hexdigest() == digest, arc
    side = (tmp_path / "a" / (za.name + ".sha256")).read_text().split()[0]
    assert side == hashlib.sha256(za.read_bytes()).hexdigest()


def test_secret_scan_blocks_packaging(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("build_release", BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    bad = tmp_path / "leak.md"
    bad.write_text("token: AKIAABCDEFGHIJKLMNOP\n", encoding="utf-8")
    hits = mod.scan_secrets([bad])
    assert hits and "AKIA" in hits[0]
