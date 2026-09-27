"""D05: actual download bytes + AppTest, using Python 3.14 and temporary fixtures.

Run: python3.14 .scorecard-check/test_evidence.py
"""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from unittest.mock import patch
from zipfile import ZipFile

import streamlit as st
from streamlit.testing.v1 import AppTest

from test_scorecard import WORKSPACE, build_app, metrics, tab_labels


REM = "acme-platform/remediation/"
CORE = {REM + "results.json", REM + "sla-dashboard.html", "docs/REMEDIATION.md"}
FINDING = {
    "service": "billing", "package": "demo", "cves": ["CVE-example-A", "CVE-example-B"],
    "old": "1", "new": "2", "baseline": "2 passed", "after": "1 passed, 1 failed",
    "risk": "ESCALATED: human review", "status": "mixed", "fixed_at": None,
}
DATA = {
    "findings": [FINDING, FINDING | {"service": "reports"}, FINDING],
    "scorecard": {"advisory_scope": {"cves_found": 7, "cves_closed": 4,
        "total_time_seconds": 123.5, "breaking_changes_repaired": 3},
        "scan_scope": {"cves_found": 5, "cves_closed": 2,
            "total_time_seconds": 75, "breaking_changes_repaired": 0}},
}


def write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def run(app):
    downloads = {}
    original = st.download_button

    def capture(label, data, **kwargs):
        downloads[kwargs["file_name"]] = (data, kwargs)
        return original(label, data, **kwargs)

    before = datetime.now(timezone.utc)
    with patch("streamlit.download_button", side_effect=capture):
        at = AppTest.from_file(str(app), default_timeout=20).run()
    after = datetime.now(timezone.utc)
    assert not at.exception, at.exception
    assert tab_labels(at) == ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
    content, options = downloads["cve-autopilot-evidence.zip"]
    assert options["mime"] == "application/zip"
    with ZipFile(io.BytesIO(content)) as archive:
        assert archive.testzip() is None
        manifest = json.loads(archive.read("MANIFEST.json"))
        exported = datetime.fromisoformat(manifest["exported_at"])
        assert exported.utcoffset().total_seconds() == 0
        assert before <= exported <= after
        names = archive.namelist()
        assert len(names) == len(set(names))
        files = {n: archive.read(n) for n in names if n != "MANIFEST.json"}
        assert set(files) == {item["path"] for item in manifest["files"]}
        for item in manifest["files"]:
            path = PurePosixPath(item["path"])
            assert not path.is_absolute() and ".." not in path.parts and "\\" not in str(path)
            original_bytes = (app.parent / path).read_bytes()
            assert files[str(path)] == original_bytes
            assert item["size_bytes"] == len(original_bytes)
            assert item["sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert set(manifest["missing_core"]) == CORE - set(files)
    assert options["disabled"] == (not files)
    assert not (app.parent / "MANIFEST.json").exists()
    assert not (app.parent / "cve-autopilot-evidence.zip").exists()
    assert len([d for d in at.get("download_button") if d.proto.label == "Download evidence ZIP"]) == 1
    return at, files, manifest


def test_full_pack():
    app = build_app(None, tag="evidence-full", data=DATA)
    root = app.parent
    expected = {REM + "results.json": (root / (REM + "results.json")).read_bytes(),
        REM + "sla-dashboard.html": b"<html><head></head><body>Recorded SLA</body></html>",
        REM + "billing.diff": b"--- old\n+++ new\n-old\n+new\n",
        REM + "sbom/billing-before.cdx.json": b'{"before": true}',
        REM + "sbom/billing-after.cdx.json": b'{"after": true}',
        REM + "sbom/README.md": b"# SBOM", "docs/REMEDIATION.md": b"# Report",
        "docs/COMPLIANCE.md": b"# Compliance", "docs/advisory-2026-09.md": b"# Advisory",
        "acme-platform/security/advisory-2026-09.pdf": b"%PDF-synthetic fixture"}
    for name, content in expected.items():
        write(root, name, content)
    # Synthetic secrets only. None of these paths is in the allowlist.
    for name in (".env", REM + ".env", "docs/secret.txt", REM + "raw.log",
                 REM + "nested/hidden.diff", REM + "sbom/unrelated.json"):
        write(root, name, b"SYNTHETIC EXCLUDED DATA")
    at, files, manifest = run(app)
    assert files == expected
    assert not manifest["missing_optional"] and not manifest["warnings"]
    assert not any("Partial evidence pack" in w.value for w in at.warning)
    m = metrics(at)
    assert m["Advisory CVEs closed / found"] == "4/7"
    assert m["Recorded time (advisory)"] == "123.5 s"
    assert m["Breaking changes repaired (advisory)"] == "3"
    assert m["Recorded time (scan)"] == "75 s" and m["Open findings (scan)"] == "3"
    assert m["Breaking changes repaired (scan)"] == "0"
    assert any(t.value == "billing, reports" for t in at.text)
    captions = " ".join(c.value for c in at.caption)
    assert "Run identity / scan timestamp not recorded in structured data" in captions
    assert "historical authenticity" in captions and "not the complete scanned scope" in captions
    entries = [e for e in at.expander if e.label.startswith("Finding ")]
    assert len(entries) == 3
    first = " ".join(m.value for m in entries[0].markdown)
    for value in ("CVE-example-A, CVE-example-B", "1 → 2", "2 passed", "1 passed, 1 failed",
                  "mixed", "Not recorded", "ESCALATED"):
        assert value in first
    assert entries[0].code[0].value == expected[REM + "billing.diff"].decode().strip()
    assert entries[0].warning and entries[1].info and not entries[1].code
    print("PASS: full ZIP, exact bytes/hashes, allowlist, live metrics, grouped/mixed/escalated findings")


def test_untrusted_and_unreadable():
    app = build_app(None, tag="evidence-unsafe", data={"findings": [
        FINDING | {"service": "../outside"}, {"service": "<script>bad</script>", "cves": [{}]},
        None, FINDING | {"service": ["invalid"], "baseline": {}},
    ]})
    root = app.parent
    outside = write(root.parent, "outside.diff", b"SYNTHETIC OUTSIDE DATA")
    (root / (REM + "outside.diff")).symlink_to(outside)
    local = write(root, REM + "billing.diff", b"safe diff")
    (root / (REM + "alias.diff")).symlink_to(local)
    write(root, REM + "nested/invisible.diff", b"not direct")
    (root / (REM + "directory.diff")).mkdir()
    # A directory symlink must be rejected before globbing/reading its contents.
    (root / (REM + "sbom")).symlink_to(root.parent, target_is_directory=True)
    write(root.parent, "leak-before.cdx.json", b"SYNTHETIC OUTSIDE SBOM")
    unreadable = write(root, "docs/REMEDIATION.md", b"unreadable fixture")
    original = Path.read_bytes

    def read(path):
        if path.resolve() == unreadable.resolve():
            raise PermissionError("synthetic denied")
        assert not path.is_symlink() and path.resolve() != outside.resolve()
        return original(path)

    with patch.object(Path, "read_bytes", read):
        at, files, manifest = run(app)
    assert set(files) == {REM + "results.json", REM + "billing.diff"}
    assert "docs/REMEDIATION.md" in manifest["missing_core"]
    assert any("synthetic denied" in w for w in manifest["warnings"])
    assert any("symlink" in w for w in manifest["warnings"])
    assert any("Partial evidence pack" in w.value for w in at.warning)
    assert any("Finding 3: unexpected shape" in w.value for w in at.warning)
    entries = [e for e in at.expander if e.label.startswith("Finding ")]
    assert all(not e.code for e in entries)
    assert "&lt;script&gt;" in entries[1].markdown[0].value
    # Also reject a symlinked parent of a core artifact, even when its target is inside root.
    app2 = build_app(None, tag="evidence-parent-link")
    (app2.parent / "docs").rmdir()
    write(app2.parent, "internal/REMEDIATION.md", b"symlinked parent")
    (app2.parent / "docs").symlink_to(app2.parent / "internal", target_is_directory=True)
    _, files2, _ = run(app2)
    assert not files2
    print("PASS: traversal names, symlink files/parents, unreadable evidence and malformed finding fields")


def test_partial_and_invalid():
    app = build_app(None, tag="evidence-core-only", data=DATA)
    write(app.parent, REM + "sla-dashboard.html", b"<html><head></head><body>SLA</body></html>")
    write(app.parent, "docs/REMEDIATION.md", b"# Report")
    at, files, manifest = run(app)
    assert set(files) == CORE and not manifest["missing_core"] and manifest["missing_optional"]
    assert any("Partial evidence pack" in w.value for w in at.warning)
    for value in (None, b"", b"{bad json", b"[]", b"\xff", b'{"findings": {}}',
                  b'{"findings": [], "scorecard": {}}'):
        app = build_app(None, tag="evidence-partial")
        if value is not None:
            write(app.parent, REM + "results.json", value)
        at, files, _ = run(app)
        assert len(files) == (value is not None)
        assert any("Partial evidence pack" in w.value for w in at.warning)
    data = {"scorecard": {"advisory_scope": {
        "cves_found": 1, "cves_closed": 2, "total_time_seconds": True,
        "breaking_changes_repaired": -1}}, "findings": [FINDING]}
    at, _, _ = run(build_app(None, tag="evidence-invalid-metrics", data=data))
    for label in ("Advisory CVEs closed / found", "Recorded time (advisory)",
                  "Breaking changes repaired (advisory)"):
        assert metrics(at)[label] == "n/a"
    assert at.error
    app = build_app(None, tag="evidence-invalid-text")
    for name in (REM + "sla-dashboard.html", REM + "billing.diff", "docs/REMEDIATION.md",
                 "docs/advisory-2026-09.md"):
        write(app.parent, name, b"\xff")
    at, files, _ = run(app)
    assert len(files) == 4 and sum("invalid UTF-8" in w.value for w in at.warning) == 4
    print("PASS: empty/missing/malformed/partial input, disabled empty download, invalid metrics/text")


if __name__ == "__main__":
    test_full_pack()
    test_untrusted_and_unreadable()
    test_partial_and_invalid()
    at, files, manifest = run(WORKSPACE / "app.py")
    print(f"PASS: actual workspace ZIP ({len(files)} evidence files), missing core: {manifest['missing_core']}")
