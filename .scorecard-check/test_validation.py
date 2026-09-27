"""D04 regression checks; Python 3.14, temporary fixtures, no artifact writes.

Run: python3.14 .scorecard-check/test_validation.py
"""
import copy
import json
import re
import shutil

from test_scorecard import REAL_JSON, WORKSPACE, build_app, metrics, run_test, tab_labels


BASE = json.loads(REAL_JSON.read_text())
DELETE = object()
CASES = []


def case(name, changes, expected, conflicts=(), extra=None):
    data = copy.deepcopy(BASE)
    for scope, key, value in changes:
        section = data["scorecard"][scope]
        if value is DELETE:
            section.pop(key, None)
        else:
            section[key] = value
    app = build_app(None, tag="validation", data=data)
    # Keep all other tabs populated so validation failures cannot mask regressions.
    for pattern in ("acme-platform/remediation/*.html", "acme-platform/remediation/*.diff",
                    "docs/REMEDIATION.md", "docs/advisory-2026-09.md",
                    "acme-platform/security/*.pdf"):
        for path in WORKSPACE.glob(pattern):
            shutil.copy(path, app.parent / path.relative_to(WORKSPACE))

    def checks(at):
        assert not at.exception, at.exception
        assert tab_labels(at) == ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
        actual = metrics(at)
        for label, value in expected.items():
            assert actual[label] == value, (label, actual[label], value)
        errors = [e.value for e in at.error if "Evidence inconsistent" in e.value]
        assert bool(errors) == bool(conflicts), errors
        for field in conflicts:
            assert any(field in error for error in errors), (field, errors)
        sla = at.tabs[1]
        assert bool(sla.warning) == bool(conflicts)
        if conflicts:
            assert "historical SLA HTML" in sla.warning[0].value
            elements = list(sla)
            assert next(i for i, e in enumerate(elements) if e.type == "warning") < next(
                i for i, e in enumerate(elements) if e.type == "iframe")
        assert len(sla.get("iframe")) == 1
        assert len(at.tabs[2].code) == len(list(WORKSPACE.glob("acme-platform/remediation/*.diff")))
        # Streamlit strips the trailing newline from Markdown input.
        assert at.tabs[3].markdown[-1].value == (WORKSPACE / "docs/REMEDIATION.md").read_text().strip()
        assert at.tabs[4].markdown[-1].value == (WORKSPACE / "docs/advisory-2026-09.md").read_text().strip()
        if extra:
            extra(at)

    CASES.append((name, app, checks))


ADV = "advisory_scope"
SCAN = "scan_scope"
RESCAN = "rescan_findings"

case("historical snapshot", [], {"Remediation rate": "89%", "SLA compliance": "100%",
     "Total open CVEs": "3", "Time per CVE": "33.6 s", "Bobcoins per CVE": "0.48"})
case("closed exceeds found", [(ADV, "cves_closed", 999)],
     {"Remediation rate": "n/a", "SLA compliance": "n/a", "Time per CVE": "n/a",
      "Bobcoins per CVE": "n/a", "Total open CVEs": "n/a", "Auto-fixed services": "3"},
     ["advisory_scope.cves_closed"])
case("SLA exceeds closed", [(ADV, "sla_compliant_cves", 9)],
     {"SLA compliance": "n/a", "Remediation rate": "89%", "Total open CVEs": "3"},
     ["advisory_scope.sla_compliant_cves"])
case("new closed exceeds found", [(RESCAN, "new_cves_closed", 3)],
     {"Re-scan remediation rate": "n/a", "Total open CVEs": "n/a", "Remediation rate": "89%"},
     ["rescan_findings.new_cves_closed"])

for key, label in (("cves_found", "Remediation rate"), ("cves_closed", "Remediation rate"),
                   ("sla_compliant_cves", "SLA compliance"), ("auto_fixed_services", "Auto-fixed services"),
                   ("escalated_services", "Escalated services"), ("tests_changed", "Tests changed")):
    for bad in (-1, True, "8", 8.0, [], {}):
        case(f"count {key} rejects {bad!r}", [(ADV, key, bad)], {label: "n/a"}, [f"{ADV}.{key}"])

for key, label in (("total_time_seconds", "Time per CVE"), ("bobcoins_total", "Bobcoins per CVE"),
                   ("remediation_rate_pct", "Remediation rate"), ("sla_compliance_rate_pct", "SLA compliance")):
    for bad in (-1, True, "9", float("nan"), float("inf"), -float("inf")):
        case(f"number {key} rejects {bad!r}", [(ADV, key, bad)], {label: "n/a"}, [f"{ADV}.{key}"])

for bad in (1, 0, "true", "false", [], {}):
    case(f"verification rejects {bad!r}", [(ADV, "verified_by_rescan", bad)],
         {"Verified by re-scan": "n/a", "Remediation rate": "89%"}, [f"{ADV}.verified_by_rescan"])

for scope, key, label in ((ADV, "remediation_rate_pct", "Remediation rate"),
                         (ADV, "sla_compliance_rate_pct", "SLA compliance"),
                         (RESCAN, "remediation_rate_pct", "Re-scan remediation rate")):
    case(f"percentage range {scope}.{key}", [(scope, key, 999)], {label: "n/a"}, [f"{scope}.{key}"])
case("contradictory 100 percent", [(ADV, "remediation_rate_pct", 100)],
     {"Remediation rate": "n/a", "SLA compliance": "100%"}, [f"{ADV}.remediation_rate_pct"])
for stored, expected, conflicts in ((49.5, "50%", []), (50.5, "50%", []),
                                    (50.5001, "n/a", [f"{ADV}.remediation_rate_pct"])):
    case(f"half point tolerance {stored}", [(ADV, "cves_found", 16),
         (ADV, "remediation_rate_pct", stored), (RESCAN, "advisory_cves_still_open", 8),
         (RESCAN, "open_cves_total", 10)], {"Remediation rate": expected}, conflicts)

for key, labels in (("cves_found", ["Remediation rate", "Total open CVEs"]),
                    ("cves_closed", ["Remediation rate", "SLA compliance", "Time per CVE", "Bobcoins per CVE"]),
                    ("sla_compliant_cves", ["SLA compliance"]),
                    ("total_time_seconds", ["Time per CVE"]), ("bobcoins_total", ["Bobcoins per CVE"]),
                    ("verified_by_rescan", ["Verified by re-scan"])):
    for missing in (DELETE, None):
        case(f"missing/null {key} remains unknown", [(ADV, key, missing)], dict.fromkeys(labels, "n/a"))

case("zero counts have no defined rates", [(ADV, "cves_found", 0), (ADV, "cves_closed", 0),
     (ADV, "sla_compliant_cves", 0), (RESCAN, "advisory_cves_still_open", 0),
     (RESCAN, "new_cves_found", 0), (RESCAN, "open_cves_total", 0)],
     dict.fromkeys(("Remediation rate", "SLA compliance", "Time per CVE", "Bobcoins per CVE",
                    "Re-scan remediation rate"), "n/a") | {"Total open CVEs": "0"})
case("zero closed", [(ADV, "cves_closed", 0), (ADV, "sla_compliant_cves", 0),
     (ADV, "remediation_rate_pct", 0), (RESCAN, "advisory_cves_still_open", 9),
     (RESCAN, "open_cves_total", 11)], {"Remediation rate": "0%", "SLA compliance": "n/a",
     "Time per CVE": "n/a", "Bobcoins per CVE": "n/a", "Total open CVEs": "11"})
case("zero time and coins", [(ADV, "total_time_seconds", 0), (ADV, "bobcoins_total", 0)],
     {"Time per CVE": "0.0 s", "Bobcoins per CVE": "0.00"})
case("derive absent percentages and ignore stale per-CVE fields", [(ADV, "remediation_rate_pct", DELETE),
     (ADV, "sla_compliance_rate_pct", DELETE), (ADV, "time_per_cve_seconds", 999),
     (ADV, "bobcoins_per_cve", 999)], {"Remediation rate": "89%", "SLA compliance": "100%",
     "Time per CVE": "33.6 s", "Bobcoins per CVE": "0.48"})

case("partially closed new findings", [(RESCAN, "new_cves_closed", 1),
     (RESCAN, "remediation_rate_pct", 50), (RESCAN, "open_cves_total", 2)],
     {"Total open CVEs": "2", "Re-scan remediation rate": "50%"})
case("missing new closed is not zero", [(RESCAN, "new_cves_closed", DELETE)],
     {"Total open CVEs": "n/a", "Re-scan remediation rate": "n/a"},
     extra=lambda at: assert_missing_count_explanation(at))
case("wrong advisory open", [(RESCAN, "advisory_cves_still_open", 2)],
     {"Advisory CVEs still open": "n/a", "Total open CVEs": "n/a"}, [f"{RESCAN}.advisory_cves_still_open"])
for bad in (99, -1, True, "3"):
    case(f"wrong total open {bad!r}", [(RESCAN, "open_cves_total", bad)],
         {"Total open CVEs": "n/a", "Re-scan remediation rate": "0%"}, [f"{RESCAN}.open_cves_total"])
case("derive absent total", [(RESCAN, "open_cves_total", DELETE)], {"Total open CVEs": "3"})


def assert_missing_count_explanation(at):
    assert any("new_cves_closed" in i.value and "not assumed to be zero" in i.value for i in at.info)


def check_scan(at):
    cards = next(m.value for m in at.markdown if 'class="cva-sr"' in m.value)
    assert re.search(r'<span class="v"><span class="cva-na">n/a</span></span>'
                     r'<span class="l">Remediation rate</span>', cards), cards
    assert metrics(at)["Remediation rate"] == "89%"


for key, bad in (("cves_closed", 999), ("cves_found", True), ("remediation_rate_pct", 999),
                 ("remediation_rate_pct", float("nan")), ("remediation_rate_pct", 100)):
    case(f"latest scan validates {key}={bad!r}", [(SCAN, key, bad)], {}, [f"{SCAN}.{key}"], check_scan)
case("latest scan SLA conflict", [(SCAN, "sla_compliant_cves", 30)], {}, [f"{SCAN}.sla_compliant_cves"])
case("latest scan missing cost", [], {}, extra=lambda at: assert_scan_cost(at))


def assert_scan_cost(at):
    details = next(m.value for m in at.markdown if "Bobcoins per finding" in m.value)
    assert 'Bobcoins per finding</td><td class="val"><span class="cva-na">n/a</span>' in details
    assert "13.0 s" in details and "88%" in "".join(m.value for m in at.markdown)


if __name__ == "__main__":
    failed = 0
    for name, app, checks in CASES:
        ok, detail = run_test(name, app, checks)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            failed += 1
            print(detail)
    print(f"{len(CASES) - failed} passed, {failed} failed / {len(CASES)} total")
    raise SystemExit(bool(failed))
