import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
_NA = "Not generated yet — run CVE Autopilot"

st.title("CVE Autopilot")
st.caption("Security advisory in. Tested fix and SLA evidence out.")

tab_scorecard, tab_sla, tab_diffs, tab_report, tab_advisory = st.tabs(
    ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
)


def _fmt(d, key, suffix=""):
    """Return formatted scalar from dict d[key], or None if missing/non-scalar."""
    v = d.get(key) if isinstance(d, dict) else None
    if v is None or isinstance(v, (dict, list)):
        return None
    return f"{v}{suffix}" if suffix else v


def _metric(col, label, val, *, help=""):
    """Render st.metric with a safe display value."""
    if val is None:
        display = "n/a"
    elif isinstance(val, bool):
        display = "Yes ✓" if val else "No ✗"
    elif isinstance(val, (int, float)):
        display = val
    elif isinstance(val, (dict, list)):
        display = "n/a"
    else:
        display = str(val)
    col.metric(label, display, help=help)


with tab_scorecard:
    results_path = ROOT / "acme-platform" / "remediation" / "results.json"

    if not results_path.exists():
        st.info("Scorecard not generated yet — run CVE Autopilot")
    else:
        try:
            data = json.loads(results_path.read_text("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("root is not a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            st.warning(f"results.json cannot be parsed: {exc}")
            data = None

        if data is not None:
            scorecard = data.get("scorecard")
            if not isinstance(scorecard, dict):
                st.info("Scorecard not generated yet — run CVE Autopilot")
            else:
                st.caption(
                    "Recorded values from this demo run. "
                    "SLA compliance, time, and Bobcoins apply to closed CVEs only. "
                    "Verified by re-scan confirms reported closures; open CVEs remain."
                )

                # ── Advisory scope ─────────────────────────────────────────
                st.subheader("Advisory scope")
                adv = scorecard.get("advisory_scope")

                if not isinstance(adv, dict):
                    st.warning("advisory_scope is missing or has an unexpected shape.")
                else:
                    cf, cc = adv.get("cves_found"), adv.get("cves_closed")
                    scope = f"{cc}/{cf} advisory CVEs" if None not in (cf, cc) else "advisory CVEs"
                    sc = adv.get("sla_compliant_cves")
                    sla_scope = f"{sc} closed CVEs in SLA window" if sc is not None else "closed CVEs"

                    metric_rows = [
                        [
                            ("Remediation rate",  _fmt(adv, "remediation_rate_pct", "%"), f"cves_closed ÷ cves_found × 100 — {scope}"),
                            ("Verified by re-scan", adv.get("verified_by_rescan"),         "Closures confirmed by post-fix re-scan"),
                            ("SLA compliance",    _fmt(adv, "sla_compliance_rate_pct", "%"), f"sla_compliant_cves ÷ cves_closed × 100 — {sla_scope}"),
                        ],
                        [
                            ("Auto-fixed services", _fmt(adv, "auto_fixed_services"),  "Fixed without human intervention (may overlap with escalated)"),
                            ("Escalated services",  _fmt(adv, "escalated_services"),   "Flagged for human review"),
                            ("Tests changed",       _fmt(adv, "tests_changed"),        "Policy requires 0; any non-zero value is a violation"),
                        ],
                        [
                            ("Time per CVE",      _fmt(adv, "time_per_cve_seconds", " s"), "total_time_seconds ÷ cves_closed"),
                            ("Bobcoins per CVE",  _fmt(adv, "bobcoins_per_cve"),            "bobcoins_total ÷ cves_closed"),
                        ],
                    ]
                    for row in metric_rows:
                        cols = st.columns(len(row))
                        for col, (label, val, hlp) in zip(cols, row):
                            _metric(col, label, val, help=hlp)

                    verified = adv.get("verified_by_rescan")
                    if verified is False:
                        st.warning("verified_by_rescan is false — reported closures were NOT confirmed by re-scan.")

                    tc = adv.get("tests_changed")
                    if isinstance(tc, (int, float)) and tc > 0:
                        st.error(f"tests_changed = {tc} — policy violation: CVE Autopilot must not modify existing tests.")

                    if adv.get("note"):
                        st.caption(f"ℹ️ {adv['note']}")

                # ── Re-scan findings ───────────────────────────────────────
                st.subheader("Re-scan findings")
                rescan = scorecard.get("rescan_findings")

                if not isinstance(rescan, dict):
                    st.warning("rescan_findings is missing or has an unexpected shape.")
                else:
                    c1, c2, c3 = st.columns(3)
                    _metric(c1, "New CVEs found",           _fmt(rescan, "new_cves_found"),           help="CVEs found during re-scan, outside advisory scope")
                    _metric(c2, "Advisory CVEs still open", _fmt(rescan, "advisory_cves_still_open"), help="Advisory-scope CVEs not yet closed")
                    _metric(c3, "Total open CVEs",          _fmt(rescan, "open_cves_total"),          help="new_cves_found + advisory_cves_still_open")

                    c4, c5 = st.columns(2)
                    _metric(c4, "Escalated services (re-scan)", _fmt(rescan, "escalated_services"),     help="Services flagged during re-scan")
                    _metric(c5, "Re-scan remediation rate",     _fmt(rescan, "remediation_rate_pct", "%"), help="new CVEs closed ÷ new CVEs found × 100")

                    esc_svc = rescan.get("escalated_services")
                    if esc_svc:
                        st.warning(f"**Escalation — {esc_svc} service(s) require human action.**\n\n{rescan.get('escalation_reason', '')}")

                    if rescan.get("action_required"):
                        st.info(f"**Action required:** {rescan['action_required']}")

                    cves_list = rescan.get("cves")
                    if isinstance(cves_list, list) and cves_list:
                        st.markdown("**Open CVEs from re-scan:**")
                        st.table([
                            {
                                "CVE ID":      str(e.get("id",      "")) if isinstance(e, dict) else "",
                                "PYSEC":       str(e.get("pysec",   "")) if isinstance(e, dict) else "",
                                "Package":     str(e.get("package", "")) if isinstance(e, dict) else "",
                                "Fix version": str(e.get("fix",     "")) if isinstance(e, dict) else "",
                            }
                            for e in cves_list
                        ])

with tab_sla:
    p = ROOT / "acme-platform" / "remediation" / "sla-dashboard.html"
    components.html(p.read_text("utf-8"), height=900, scrolling=True) if p.exists() else st.info(_NA)

with tab_diffs:
    diff_files = sorted((ROOT / "acme-platform" / "remediation").glob("*.diff"))
    if diff_files:
        for d in diff_files:
            with st.expander(d.name):
                st.code(d.read_text("utf-8"), language="diff")
    else:
        st.info(_NA)

with tab_report:
    p = ROOT / "docs" / "REMEDIATION.md"
    st.markdown(p.read_text("utf-8")) if p.exists() else st.info(_NA)

with tab_advisory:
    pdf = ROOT / "acme-platform" / "security" / "advisory-2026-09.pdf"
    md  = ROOT / "docs" / "advisory-2026-09.md"
    if pdf.exists():
        st.download_button("Download advisory-2026-09.pdf", pdf.read_bytes(),
                           file_name="advisory-2026-09.pdf", mime="application/pdf")
    else:
        st.info(_NA)
    st.markdown(md.read_text("utf-8")) if md.exists() else st.info(_NA)
