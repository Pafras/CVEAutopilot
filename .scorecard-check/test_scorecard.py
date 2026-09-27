"""
Focused AppTest verification for the Scorecard tab (task #8).
Run from the workspace root:
    python .scorecard-check/test_scorecard.py

All tests run against the real app.py source — ROOT is patched per-test run to
point at an isolated directory with the chosen fixture. Real evidence files are
never mutated; the real results.json is used as-is for the real-data case.
"""

import shutil
import sys
import traceback
from pathlib import Path

HERE      = Path(__file__).parent
WORKSPACE = HERE.parent
FIXTURES  = HERE / "fixtures"
REAL_APP  = WORKSPACE / "app.py"
REAL_JSON = WORKSPACE / "acme-platform" / "remediation" / "results.json"


# ---------------------------------------------------------------------------
# Test-directory builder
# ---------------------------------------------------------------------------

def build_app(fixture_name: str | None, *, use_real_json: bool = False, tag: str = "") -> Path:
    """
    Build an isolated test directory under .scorecard-check/run_<tag|name>/.
    Copies the real app.py into it, rewriting ROOT to point at that directory.

    fixture_name=None + use_real_json=False → no results.json (missing-file case).
    use_real_json=True           → copies the real results.json unchanged.
    tag                          → overrides the directory name suffix (avoids
                                   collisions when two calls share fixture_name=None).
    """
    if tag:
        slug = tag
    elif use_real_json:
        slug = "real"
    else:
        slug = fixture_name.replace(".", "_") if fixture_name else "none"
    test_dir = HERE / f"run_{slug}"

    # Create layout mirroring workspace
    rem_dir = test_dir / "acme-platform" / "remediation"
    rem_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "docs").mkdir(exist_ok=True)
    (test_dir / "acme-platform" / "security").mkdir(parents=True, exist_ok=True)

    # Place results.json
    if use_real_json:
        shutil.copy(REAL_JSON, rem_dir / "results.json")
    elif fixture_name is not None:
        shutil.copy(FIXTURES / fixture_name, rem_dir / "results.json")
    # else: leave absent for missing-file test

    # Copy real app.py, patching ROOT assignment so it resolves inside test_dir
    src = REAL_APP.read_text("utf-8")
    src = src.replace(
        "ROOT = Path(__file__).parent",
        f"ROOT = Path(r'{test_dir}')",
        1,
    )
    app_copy = test_dir / "app.py"
    app_copy.write_text(src)
    return app_copy


def run_test(name: str, app_path: Path, checks):
    try:
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(app_path), default_timeout=20)
        at.run()
        checks(at)
        return True, "PASS"
    except Exception:
        return False, traceback.format_exc()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def metrics(at):
    return {m.label: m.value for m in at.metric}

def tab_labels(at):
    return [t.label for t in at.tabs]

def all_tables(at):
    return list(getattr(at, "table", [])) + list(getattr(at, "dataframe", []))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_real_data():
    """Real results.json: all metric values, table, escalation, no spurious warnings."""
    app = build_app(None, use_real_json=True, tag="real")
    def checks(at):
        assert not at.exception, at.exception
        # Tab order
        assert tab_labels(at) == ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
        m = metrics(at)
        # Advisory scope — AppTest returns metric values as strings for str displays,
        # or the original numeric type for bare int/float.
        assert m["Remediation rate"]       == "89%",    f"got {m['Remediation rate']!r}"
        assert m["Verified by re-scan"]    == "Yes ✓",  f"got {m['Verified by re-scan']!r}"
        assert m["SLA compliance"]         == "100%",   f"got {m['SLA compliance']!r}"
        # _fmt returns int/float scalars; AppTest may preserve type
        assert str(m["Auto-fixed services"]) == "3",    f"got {m['Auto-fixed services']!r}"
        assert str(m["Escalated services"])  == "1",    f"got {m['Escalated services']!r}"
        assert m["Tests changed"]          == "0",      f"got {m['Tests changed']!r}"
        assert m["Time per CVE"]           == "33.6 s", f"got {m['Time per CVE']!r}"
        assert str(m["Bobcoins per CVE"])  == "0.48",   f"got {m['Bobcoins per CVE']!r}"
        # Re-scan scope
        assert str(m["New CVEs found"])            == "2", f"got {m['New CVEs found']!r}"
        assert str(m["Advisory CVEs still open"])  == "1", f"got {m['Advisory CVEs still open']!r}"
        assert str(m["Total open CVEs"])           == "3", f"got {m['Total open CVEs']!r}"
        assert str(m["Escalated services (re-scan)"]) == "1", f"got {m['Escalated services (re-scan)']!r}"
        assert m["Re-scan remediation rate"] == "0%",   f"got {m['Re-scan remediation rate']!r}"
        # Escalation warning present
        assert any("Escalation" in w.value for w in at.warning), "no escalation warning"
        # CVE table has 3 rows with correct IDs
        tbls = all_tables(at)
        assert tbls, "no CVE table rendered"
        df = tbls[0].value
        assert len(df) == 3, f"expected 3 CVE rows, got {len(df)}"
        ids = set(df["CVE ID"].tolist())
        assert ids == {"CVE-2026-25645", "CVE-2026-44432", "CVE-2026-44431"}, f"ids: {ids}"
        # verified_by_rescan=true must NOT fire the NOT-confirmed warning
        assert not any("NOT confirmed" in w.value for w in at.warning), "spurious NOT-confirmed warning"
    return run_test("real_data", app, checks)


def test_missing_file():
    """No results.json → info message, no metrics, all 5 tabs present."""
    app = build_app(None, tag="missing")
    def checks(at):
        assert not at.exception, at.exception
        assert tab_labels(at) == ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
        assert any("Scorecard not generated yet" in i.value for i in at.info), "no info msg"
        assert not list(at.metric), "unexpected metrics"
    return run_test("missing_file", app, checks)


def test_no_scorecard_key():
    """results.json exists but has no scorecard key → info message."""
    app = build_app("no_scorecard.json")
    def checks(at):
        assert not at.exception, at.exception
        assert any("Scorecard not generated yet" in i.value for i in at.info)
        assert not list(at.metric)
    return run_test("no_scorecard_key", app, checks)


def test_malformed_json():
    """Malformed JSON → warning contains 'cannot be parsed', no crash, 5 tabs."""
    app = build_app("malformed.json")
    def checks(at):
        assert not at.exception, at.exception
        assert any("cannot be parsed" in w.value for w in at.warning), \
            f"warnings: {[w.value for w in at.warning]}"
        assert not list(at.metric)
        assert len(tab_labels(at)) == 5
    return run_test("malformed_json", app, checks)


def test_list_root():
    """JSON root is a list (non-dict) → 'cannot be parsed' warning."""
    fixture = FIXTURES / "list_root.json"
    fixture.write_text("[1, 2, 3]")
    app = build_app("list_root.json")
    def checks(at):
        assert not at.exception, at.exception
        assert any("cannot be parsed" in w.value for w in at.warning), \
            f"warnings: {[w.value for w in at.warning]}"
        assert not list(at.metric)
    return run_test("list_root", app, checks)


def test_scalar_scorecard():
    """scorecard key is a scalar (not dict) → info msg as if scorecard absent."""
    fixture = FIXTURES / "scalar_scorecard.json"
    fixture.write_text('{"scorecard": "oops"}')
    app = build_app("scalar_scorecard.json")
    def checks(at):
        assert not at.exception, at.exception
        assert any("Scorecard not generated yet" in i.value for i in at.info)
        assert not list(at.metric)
    return run_test("scalar_scorecard", app, checks)


def test_wrong_shape():
    """advisory_scope and rescan_findings are wrong types → two shape warnings, no crash."""
    app = build_app("wrong_shape.json")
    def checks(at):
        assert not at.exception, at.exception
        warns = [w.value for w in at.warning]
        shape_warns = [w for w in warns if "unexpected shape" in w]
        assert len(shape_warns) == 2, f"wanted 2 shape warnings, got: {warns}"
        assert not list(at.metric)
    return run_test("wrong_shape", app, checks)


def test_invalid_metric_containers():
    """Fields that contain dicts/lists are displayed as 'n/a', not raw Python repr."""
    fixture = FIXTURES / "container_metrics.json"
    fixture.write_text("""{
      "scorecard": {
        "advisory_scope": {
          "cves_found": 9, "cves_closed": 8,
          "remediation_rate_pct": {"nested": true},
          "verified_by_rescan": true,
          "auto_fixed_services": [1, 2],
          "escalated_services": 1,
          "tests_changed": 0,
          "sla_compliant_cves": 8, "sla_compliance_rate_pct": 100,
          "time_per_cve_seconds": 33.6, "bobcoins_per_cve": 0.48
        },
        "rescan_findings": {
          "new_cves_found": 2, "advisory_cves_still_open": 1,
          "open_cves_total": 3, "escalated_services": 1,
          "remediation_rate_pct": 0, "cves": []
        }
      }
    }""")
    app = build_app("container_metrics.json")
    def checks(at):
        assert not at.exception, at.exception
        m = metrics(at)
        # Container values must render as n/a, not Python repr like "{'nested': True}"
        assert m["Remediation rate"] == "n/a",       f"got {m['Remediation rate']!r}"
        assert m["Auto-fixed services"] == "n/a",    f"got {m['Auto-fixed services']!r}"
        # Valid numeric value still renders correctly
        assert str(m["Escalated services"]) == "1",  f"got {m['Escalated services']!r}"
    return run_test("invalid_metric_containers", app, checks)


def test_zero_and_false():
    """tests_changed=0→'0'; verified_by_rescan=False→'No ✗' + warning; escalated=0→0; no policy error."""
    app = build_app("zero_false.json")
    def checks(at):
        assert not at.exception, at.exception
        m = metrics(at)
        assert m["Tests changed"] == "0",              f"got {m['Tests changed']!r}"
        assert m["Verified by re-scan"] == "No ✗",     f"got {m['Verified by re-scan']!r}"
        assert str(m["Escalated services"]) == "0",    f"got {m['Escalated services']!r}"
        assert str(m["Escalated services (re-scan)"]) == "0", \
            f"got {m['Escalated services (re-scan)']!r}"
        # False must fire the NOT-confirmed warning
        assert any("NOT confirmed" in w.value for w in at.warning), \
            "no NOT-confirmed warning for False"
        # tests_changed=0 must NOT fire a policy error
        assert not list(at.error), f"unexpected error: {[e.value for e in at.error]}"
        # escalated_services=0 must NOT fire the escalation-action warning
        assert not any("Escalation —" in w.value for w in at.warning), \
            "spurious escalation warning for 0"
    return run_test("zero_and_false", app, checks)


def test_missing_verification_stays_unknown():
    """verified_by_rescan absent → displayed as n/a, NOT-confirmed warning must NOT fire."""
    fixture = FIXTURES / "no_verified.json"
    fixture.write_text("""{
      "scorecard": {
        "advisory_scope": {
          "cves_found": 5, "cves_closed": 5,
          "remediation_rate_pct": 100,
          "auto_fixed_services": 5, "escalated_services": 0,
          "tests_changed": 0, "sla_compliant_cves": 5,
          "sla_compliance_rate_pct": 100,
          "time_per_cve_seconds": 10.0, "bobcoins_per_cve": 0.1
        },
        "rescan_findings": {
          "new_cves_found": 0, "advisory_cves_still_open": 0,
          "open_cves_total": 0, "escalated_services": 0,
          "remediation_rate_pct": 0, "cves": []
        }
      }
    }""")
    app = build_app("no_verified.json")
    def checks(at):
        assert not at.exception, at.exception
        m = metrics(at)
        assert m["Verified by re-scan"] == "n/a",  f"got {m['Verified by re-scan']!r}"
        # missing is not False — must NOT trigger the NOT-confirmed warning
        assert not any("NOT confirmed" in w.value for w in at.warning), \
            "spurious NOT-confirmed warning for absent verified_by_rescan"
    return run_test("missing_verification_unknown", app, checks)


def test_tests_changed_nonzero():
    """tests_changed=2 → policy error box fired."""
    app = build_app("tests_changed.json")
    def checks(at):
        assert not at.exception, at.exception
        m = metrics(at)
        assert m["Tests changed"] == "2",  f"got {m['Tests changed']!r}"
        errors = [e.value for e in at.error]
        assert any("tests_changed" in e and "policy violation" in e for e in errors), \
            f"no policy error: {errors}"
    return run_test("tests_changed_nonzero", app, checks)


def test_escalation_warning_and_table():
    """escalated_services>0 → warning + action_required info + CVE table."""
    app = build_app("escalation.json")
    def checks(at):
        assert not at.exception, at.exception
        m = metrics(at)
        assert str(m["Escalated services (re-scan)"]) == "1", \
            f"got {m['Escalated services (re-scan)']!r}"
        assert any("Escalation" in w.value for w in at.warning)
        assert any("Action required" in i.value for i in at.info)
        tbls = all_tables(at)
        assert tbls, "no CVE table"
        df = tbls[0].value
        assert "CVE-2099-12345" in df["CVE ID"].tolist(), f"CVE not in table: {df}"
    return run_test("escalation_warning_and_table", app, checks)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    ("real data — metrics match results.json, table, escalation",    test_real_data),
    ("missing file — info msg, no metrics",                           test_missing_file),
    ("no scorecard key — info msg",                                   test_no_scorecard_key),
    ("malformed JSON — warning, no crash",                            test_malformed_json),
    ("list root — cannot-be-parsed warning",                          test_list_root),
    ("scalar scorecard — treated as absent",                          test_scalar_scorecard),
    ("wrong shape — two shape warnings, no metrics",                  test_wrong_shape),
    ("invalid metric containers — displayed as n/a",                  test_invalid_metric_containers),
    ("zero/False — correct display, no false alarms",                 test_zero_and_false),
    ("missing verification — stays n/a, no warning",                  test_missing_verification_stays_unknown),
    ("tests_changed > 0 — policy error",                              test_tests_changed_nonzero),
    ("escalation warning + action info + CVE table",                  test_escalation_warning_and_table),
]


def main():
    try:
        from streamlit.testing.v1 import AppTest  # noqa: F401
    except ImportError as exc:
        print(f"ERROR: streamlit.testing.v1 unavailable — {exc}")
        sys.exit(1)

    passed = failed = 0
    for name, fn in TESTS:
        ok, detail = fn()
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            for line in detail.splitlines():
                print(f"      {line}")
            failed += 1
        else:
            passed += 1

    print(f"\n{passed} passed, {failed} failed / {len(TESTS)} total")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
