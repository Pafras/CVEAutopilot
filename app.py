import html as _html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
_NA = "Not generated yet — run CVE Autopilot"

st.set_page_config(page_title="CVE Autopilot", layout="wide")

# Per-session appearance: switching never changes the shared server config.
_SKILL_URL = (
    "https://github.com/Pafras/CVEAutopilot/blob/main/"
    ".bob/skills/cve-autopilot/SKILL.md"
)
with st.container(key="masthead"):
    title, actions = st.columns([3, 1], vertical_alignment="center")
    with title:
        st.markdown("""
        <div class="cva-hd">
          <h1>CVE Autopilot</h1>
          <p class="tag">Security advisory in. Tested fix and SLA evidence out.</p>
          <p class="intro">An IBM Bob skill for remediation, breaking-change repairs,
          and test verification. Explore the recorded results below.</p>
        </div>
        """, unsafe_allow_html=True)
    with actions:
        appearance = st.segmented_control(
            "Appearance", ["Dark", "Light"], default="Dark", required=True,
            key="appearance", label_visibility="collapsed", width="stretch",
        )
        st.link_button("View the skill", _SKILL_URL, width="stretch")

# The same palette drives the viewer and the embedded evidence document.
if appearance == "Light":
    palette = dict(bg="#f5f7fa", panel="#ffffff", text="#152332", muted="#4b6073",
                   border="#d3dce5", accent="#205aaa", good="#16643c", warn="#865008",
                   bad="#a82b31", good_bg="#eaf5ee", warn_bg="#fff2de", bad_bg="#fcebee",
                   info_bg="#e9f0fa", selected="#183f70", selected_text="#ffffff")
else:
    palette = dict(bg="#101820", panel="#19242e", text="#f2f5f7", muted="#b3c0ca",
                   border="#34434f", accent="#a0c4fa", good="#93dcb4", warn="#f2c277",
                   bad="#ffaaa8", good_bg="#17372b", warn_bg="#3b2d1c", bad_bg="#402629",
                   info_bg="#203345", selected="#a0c4fa", selected_text="#101820")
variables = ";".join(f"--cva-{k.replace('_', '-')}: {v}" for k, v in palette.items())
st.html(f"<style>:root {{{variables}; color-scheme: {appearance.lower()};}}</style>")
st.html("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background:var(--cva-bg); color:var(--cva-text);
}
.block-container { max-width:1240px; padding:4.5rem 2.5rem 4rem; }
.st-key-masthead { padding-bottom:1.5rem; }
.cva-hd h1 { font-size:2.5rem; font-weight:700; letter-spacing:-.03em;
    color:var(--cva-text); padding:0; margin:0 0 .5rem; }
.cva-hd .tag { font-size:1.125rem; color:var(--cva-text); margin:0 0 .5rem; }
.cva-hd .intro { font-size:1rem; color:var(--cva-muted); line-height:1.6; max-width:65ch; margin:0; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color:var(--cva-text); }
.stApp a { color:var(--cva-accent); text-underline-offset:3px; }
.stApp button, .stApp summary, [data-testid="stLinkButton"] a {
    color:var(--cva-text); border-color:var(--cva-border);
}
[data-testid="stBaseButton-secondary"], .stApp button[data-variant="segmented_control"],
[data-testid="stLinkButton"] a { background:var(--cva-panel); color:var(--cva-text); }
.stApp button[data-variant="segmented_control"][aria-checked="true"] {
    background:var(--cva-selected); color:var(--cva-selected-text); border-color:var(--cva-selected);
}
.stApp [data-testid="stTooltipIcon"] button { color:var(--cva-muted); }
.stApp [role="tab"]:focus-visible { outline:2px solid var(--cva-accent); outline-offset:-2px; }
.stApp button:hover, [data-testid="stLinkButton"] a:hover {
    border-color:var(--cva-accent); color:var(--cva-accent);
}
.stApp button:focus-visible, .stApp a:focus-visible, .stApp summary:focus-visible {
    outline:2px solid var(--cva-accent); outline-offset:3px;
}
::selection { background:var(--cva-selected); color:var(--cva-selected-text); }
.stApp, .cva-scroll { scrollbar-color:var(--cva-border) var(--cva-bg); }
.stApp [role="tablist"] { gap:1.75rem; border-bottom:1px solid var(--cva-border); }
.stApp [role="tab"] { font-size:1rem; font-weight:600; padding:.5rem 0 .8rem; color:var(--cva-muted); }
.stApp [role="tab"][aria-selected="true"] { color:var(--cva-text); }
.stApp [role="tab"] .react-aria-SelectionIndicator { background:var(--cva-accent); }
h2.cva-sec { font-size:1.4rem; font-weight:650; letter-spacing:-.015em; padding:0; margin:1.5rem 0 .25rem; }
.cva-badge { display:inline-block; font-size:.9rem; font-weight:600; color:var(--cva-muted); margin-right:.75rem; }
.cva-sr { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin:.25rem 0 .5rem; }
.cva-st, [data-testid="stMetric"] { background:var(--cva-panel); border:1px solid var(--cva-border);
    border-radius:12px; padding:1.15rem 1.25rem !important; }
.cva-st { display:flex; flex-direction:column-reverse; gap:.5rem; }
.cva-st .v { display:block; font-size:2.5rem; font-weight:650; letter-spacing:-.025em;
    font-variant-numeric:tabular-nums; line-height:1.2; color:var(--cva-text); }
.cva-st .l { display:block; font-size:.9375rem; font-weight:500; color:var(--cva-muted); }
.cva-st .v.g { color:var(--cva-good); }
.cva-st .v.a { color:var(--cva-warn); }
.cva-st .v.r { color:var(--cva-bad); }
.cva-na { color:var(--cva-muted); }
[data-testid="stMetricLabel"] p { font-size:.9375rem; font-weight:500; color:var(--cva-muted); }
[data-testid="stMetricValue"] { font-size:2.25rem; font-weight:650; color:var(--cva-text); font-variant-numeric:tabular-nums; }
.cva-dt { width:100%; border-collapse:collapse; font-size:1rem; table-layout:fixed; }
.cva-dt td { padding:.65rem 0; border-bottom:1px solid var(--cva-border);
    color:var(--cva-text); vertical-align:top; overflow-wrap:anywhere; }
.cva-dt tr:last-child td { border-bottom:none; }
.cva-dt .k { width:32%; color:var(--cva-muted); padding-right:1rem; }
.cva-dt .val { width:68%; font-weight:500; font-variant-numeric:tabular-nums; }
.cva-dt .hint { font-size:.875rem; color:var(--cva-muted); font-weight:400; display:block; margin-top:.25rem; }
.cva-ti, .cva-cap { font-size:.9375rem; color:var(--cva-muted); line-height:1.6; max-width:85ch; margin:.5rem 0; }
.cva-n-g, .cva-n-i { padding:.85rem 1rem; font-size:1rem; line-height:1.6; border-radius:8px; }
.cva-n-g { background:var(--cva-good-bg); color:var(--cva-good); }
.cva-n-i { background:var(--cva-info-bg); color:var(--cva-text); }
[data-testid="stAlertContainer"] { color:var(--cva-text); }
[data-testid="stAlertContentWarning"] { color:var(--cva-warn); }
[data-testid="stAlertContentError"] { color:var(--cva-bad); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { background:var(--cva-warn-bg); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { background:var(--cva-bad-bg); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) { background:var(--cva-info-bg); }
[data-testid="stExpander"] details { border-color:var(--cva-border); background:var(--cva-panel); }
[data-testid="stExpander"] summary:hover { color:var(--cva-accent); }
[data-testid="stTable"], .cva-scroll { overflow-x:auto; }
[data-testid="stTable"] th, [data-testid="stTable"] td,
[data-testid="stMarkdownContainer"] th, [data-testid="stMarkdownContainer"] td { border-color:var(--cva-border); color:var(--cva-text); }
[data-testid="stMarkdownContainer"] > table { display:block; max-width:100%; overflow-x:auto; }
[data-testid="stMarkdownContainer"] code { color:var(--cva-text); background:var(--cva-panel); }
[data-testid="stMarkdownContainer"] hr { border-color:var(--cva-border); }
[data-testid="stCaptionContainer"] { color:var(--cva-muted); }
[data-testid="stCode"], [data-testid="stCode"] pre { background:var(--cva-panel); color:var(--cva-text); }
[data-testid="stCode"] code, [data-testid="stCode"] .token { color:var(--cva-text) !important; }
[data-testid="stCode"] .token.coord { color:var(--cva-muted) !important; }
[data-testid="stMarkdownContainer"] blockquote { color:var(--cva-muted); }
[data-testid="stCode"] .token.deleted { color:var(--cva-bad) !important; }
[data-testid="stCode"] .token.inserted { color:var(--cva-good) !important; }
@media(max-width:640px) {
    .block-container { padding:4.5rem 1rem 3rem; }
    .cva-hd h1 { font-size:2rem; }
    .st-key-masthead { padding-bottom:.75rem; }
    .cva-sr { grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; }
    .cva-st { padding:1rem !important; }
    .cva-st .v { font-size:2rem; }
    .cva-st .l { font-size:.875rem; min-height:2.7em; }
    .cva-dt, .cva-dt tbody, .cva-dt tr, .cva-dt td { display:block; width:100% !important; }
    .cva-dt .k { padding-bottom:0; border-bottom:0; font-size:.9rem; }
    .stApp [role="tablist"] { gap:1rem; }
    .stApp [role="tab"] { font-size:.9375rem; }
}
</style>
""")

tab_scorecard, tab_sla, tab_diffs, tab_report, tab_advisory = st.tabs(
    ["Scorecard", "SLA evidence", "Diffs", "Report", "Advisory"]
)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _fmt(d, key, suffix=""):
    v = d.get(key) if isinstance(d, dict) else None
    if v is None or isinstance(v, (dict, list)):
        return None
    return f"{v}{suffix}" if suffix else v


def _metric(col, label, val, *, help=""):
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


def _e(v):
    """HTML-escape any scalar; return 'n/a' span for None/missing."""
    if v is None:
        return '<span class="cva-na">n/a</span>'
    return _html.escape(str(v))


def _scalar(v):
    """Normalise a JSON value to str or None, skipping dicts/lists."""
    if v is None or isinstance(v, (dict, list)):
        return None
    return str(v)


def _join_list(v):
    """Join a list of scalars safely; ignore non-string items."""
    if not isinstance(v, list):
        return None
    parts = [str(i) for i in v if not isinstance(i, (dict, list))]
    return ", ".join(parts) if parts else None


def _stat(label, raw, cls=""):
    c = f' {cls}' if cls else ''
    return (
        f'<div class="cva-st">'
        f'<span class="v{c}">{_e(raw)}</span>'
        f'<span class="l">{_html.escape(label)}</span>'
        f'</div>'
    )


def _dt_row(key, val, hint=""):
    h = f'<span class="hint">{_html.escape(hint)}</span>' if hint else ""
    return (
        f'<tr><td class="k">{_html.escape(key)}</td>'
        f'<td class="val">{_e(val)}{h}</td></tr>'
    )


def _sec(title):
    st.markdown(f'<h2 class="cva-sec">{_html.escape(title)}</h2>', unsafe_allow_html=True)


# ── Scorecard tab ──────────────────────────────────────────────────────────────
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
                st.markdown(
                    '<p class="cva-cap">Recorded values from this demo run. '
                    "SLA compliance, time, and Bobcoins apply to closed CVEs only. "
                    "<em>Verified by re-scan</em> confirms reported closures; "
                    "open CVEs remain.</p>",
                    unsafe_allow_html=True,
                )

                # ── Latest scan ────────────────────────────────────────────
                # scan_scope is a newer field; degrade gracefully when absent
                # or wrong-shaped.
                scan = scorecard.get("scan_scope")
                if scan is not None and not isinstance(scan, dict):
                    st.warning("scan_scope has an unexpected shape — skipping latest scan section.")
                elif isinstance(scan, dict):
                    _sec("Latest scan")

                    run_id   = _scalar(scan.get("run", ""))
                    scan_date = _scalar(scan.get("scan_date", ""))
                    badge = (f'<span class="cva-badge">{_html.escape(run_id)}</span>'
                             if run_id else "")
                    date_txt = _html.escape(scan_date) if scan_date else ""
                    if badge or date_txt:
                        st.markdown(badge + date_txt, unsafe_allow_html=True)

                    # Normalise all numeric fields — raw .get() can return
                    # dicts/lists/bools; _fmt strips non-scalars to None.
                    cf   = _fmt(scan, "cves_found")
                    cc   = _fmt(scan, "cves_closed")
                    esc  = _fmt(scan, "escalated_services")
                    tc   = _fmt(scan, "tests_changed")
                    rate = _fmt(scan, "remediation_rate_pct")

                    # Colour only when value is a genuine numeric literal.
                    # Missing/container values → neutral (no colour class).
                    cf_rv   = scan.get("cves_found")
                    cc_rv   = scan.get("cves_closed")
                    esc_rv  = scan.get("escalated_services")
                    tc_rv   = scan.get("tests_changed")
                    rate_rv = scan.get("remediation_rate_pct")

                    def _num(v):
                        return isinstance(v, (int, float)) and not isinstance(v, bool)

                    # Label uses "Findings" — scan mixes GHSA + CVE identifiers.
                    cells = (
                        _stat(
                            "Findings closed / found",
                            f"{cc}/{cf}" if None not in (cc, cf) else None,
                            "g" if (_num(cc_rv) and _num(cf_rv) and cc_rv >= cf_rv) else "",
                        )
                        + _stat(
                            "Remediation rate",
                            f"{rate}%" if rate is not None else None,
                            "g" if (_num(rate_rv) and rate_rv >= 90) else "",
                        )
                        + _stat(
                            "Services escalated", esc,
                            "a" if (_num(esc_rv) and esc_rv > 0)
                            else ("g" if (_num(esc_rv) and esc_rv == 0) else ""),
                        )
                        + _stat(
                            "Tests changed", tc,
                            "r" if (_num(tc_rv) and tc_rv > 0)
                            else ("g" if (_num(tc_rv) and tc_rv == 0) else ""),
                        )
                    )
                    st.markdown(f'<div class="cva-sr">{cells}</div>', unsafe_allow_html=True)

                    rows = ""
                    svc_s   = _join_list(scan.get("services_scanned"))
                    svc_cl  = _join_list(scan.get("services_clean"))
                    svc_fx  = _join_list(scan.get("services_fixed"))
                    svc_esc = _join_list(scan.get("services_escalated"))
                    if svc_s:   rows += _dt_row("Services scanned",  svc_s)
                    if svc_cl:  rows += _dt_row("Clean (no fix needed)", svc_cl)
                    if svc_fx:  rows += _dt_row("Fixed by Autopilot", svc_fx)
                    if svc_esc: rows += _dt_row("Escalated — requires human action", svc_esc)
                    note = _scalar(scan.get("cves_found_note"))
                    if note: rows += _dt_row(
                        "Finding breakdown",
                        note,
                        "IDs include GHSA (npm) and CVE/PYSEC (Python) identifiers",
                    )
                    rr = _scalar(scan.get("rescan_result"))
                    if rr: rows += _dt_row("Re-scan result", rr)
                    # Normalise numeric detail fields before rendering.
                    sla_s = _fmt(scan, "sla_compliance_rate_pct")
                    tpc_s = _fmt(scan, "time_per_cve_seconds")
                    bpc_s = _fmt(scan, "bobcoins_per_cve")   # show if recorded, n/a stays absent
                    if sla_s is not None:
                        rows += _dt_row("SLA compliance (closed findings)", f"{sla_s}%")
                    if tpc_s is not None:
                        rows += _dt_row("Time per finding (closed)", f"{tpc_s} s")
                    if bpc_s is not None:
                        rows += _dt_row("Bobcoins per finding", str(bpc_s))
                    if rows:
                        with st.expander("Scan details · services, findings and timing"):
                            st.markdown(
                                f'<div class="cva-scroll"><table class="cva-dt">'
                                f'<tbody>{rows}</tbody></table></div>',
                                unsafe_allow_html=True,
                            )

                    esc_notes = scan.get("escalation_notes")
                    if isinstance(esc_notes, dict):
                        for svc, reason in esc_notes.items():
                            st.warning(f"**Escalation — {svc}:** {reason}")

                    # Fix 5: tests_changed > 0 in scan scope → policy error
                    # (tc is already _fmt-normalised; compare numeric raw value)
                    if _num(tc_rv) and tc_rv > 0:
                        st.error(
                            f"tests_changed = {tc} in scan scope — policy violation: "
                            "CVE Autopilot must not modify existing tests."
                        )

                    vr_scan = scan.get("verified_by_rescan")  # bool — not normalised by _fmt
                    if vr_scan is True:
                        st.markdown(
                            '<div class="cva-n-g"><strong>Verified by re-scan</strong>'
                            ' — scan-scope closures confirmed. Open CVEs remain.</div>',
                            unsafe_allow_html=True,
                        )
                    elif vr_scan is False:
                        st.warning(
                            "verified_by_rescan is false — scan-scope closures were "
                            "NOT confirmed by re-scan."
                        )

                # ── Advisory scope ─────────────────────────────────────────
                _sec("Advisory scope")
                adv = scorecard.get("advisory_scope")

                if not isinstance(adv, dict):
                    st.warning("advisory_scope is missing or has an unexpected shape.")
                else:
                    cf, cc = adv.get("cves_found"), adv.get("cves_closed")
                    scope = f"{cc}/{cf} advisory CVEs" if None not in (cf, cc) else "advisory CVEs"
                    sc = adv.get("sla_compliant_cves")
                    sla_scope = (f"{sc} closed CVEs in SLA window"
                                 if sc is not None else "closed CVEs")

                    metric_rows = [
                        [
                            ("Remediation rate",    _fmt(adv, "remediation_rate_pct", "%"),
                             f"cves_closed ÷ cves_found × 100 — {scope}"),
                            ("Verified by re-scan", adv.get("verified_by_rescan"),
                             "Closures confirmed by post-fix re-scan"),
                            ("SLA compliance",      _fmt(adv, "sla_compliance_rate_pct", "%"),
                             f"sla_compliant_cves ÷ cves_closed × 100 — {sla_scope}"),
                        ],
                        [
                            ("Auto-fixed services", _fmt(adv, "auto_fixed_services"),
                             "Fixed without human intervention (may overlap with escalated)"),
                            ("Escalated services",  _fmt(adv, "escalated_services"),
                             "Flagged for human review"),
                            ("Tests changed",       _fmt(adv, "tests_changed"),
                             "Policy requires 0; any non-zero value is a violation"),
                        ],
                        [
                            ("Time per CVE",     _fmt(adv, "time_per_cve_seconds", " s"),
                             "total_time_seconds ÷ cves_closed"),
                            ("Bobcoins per CVE", _fmt(adv, "bobcoins_per_cve"),
                             "bobcoins_total ÷ cves_closed"),
                        ],
                    ]
                    for row in metric_rows:
                        cols = st.columns(len(row))
                        for col, (label, val, hlp) in zip(cols, row):
                            _metric(col, label, val, help=hlp)

                    verified = adv.get("verified_by_rescan")
                    if verified is True:
                        st.markdown(
                            '<div class="cva-n-g"><strong>Verified by re-scan</strong>'
                            ' — advisory-scope closures confirmed.</div>',
                            unsafe_allow_html=True,
                        )
                    elif verified is False:
                        st.warning(
                            "verified_by_rescan is false — reported closures were "
                            "NOT confirmed by re-scan."
                        )

                    tc = adv.get("tests_changed")
                    if isinstance(tc, (int, float)) and tc > 0:
                        st.error(
                            f"tests_changed = {tc} — policy violation: "
                            "CVE Autopilot must not modify existing tests."
                        )

                    if adv.get("note"):
                        st.markdown(
                            f'<div class="cva-n-i">{_html.escape(str(adv["note"]))}</div>',
                            unsafe_allow_html=True,
                        )

                # ── Re-scan findings ───────────────────────────────────────
                _sec("Re-scan findings")
                rescan = scorecard.get("rescan_findings")

                if not isinstance(rescan, dict):
                    st.warning("rescan_findings is missing or has an unexpected shape.")
                else:
                    c1, c2, c3 = st.columns(3)
                    _metric(c1, "New CVEs found",           _fmt(rescan, "new_cves_found"),
                            help="CVEs found during re-scan, outside advisory scope")
                    _metric(c2, "Advisory CVEs still open", _fmt(rescan, "advisory_cves_still_open"),
                            help="Advisory-scope CVEs not yet closed")
                    _metric(c3, "Total open CVEs",          _fmt(rescan, "open_cves_total"),
                            help="new_cves_found + advisory_cves_still_open")

                    c4, c5 = st.columns(2)
                    _metric(c4, "Escalated services (re-scan)", _fmt(rescan, "escalated_services"),
                            help="Services flagged during re-scan")
                    _metric(c5, "Re-scan remediation rate",     _fmt(rescan, "remediation_rate_pct", "%"),
                            help="new CVEs closed ÷ new CVEs found × 100")

                    esc_svc = rescan.get("escalated_services")
                    if esc_svc:
                        st.warning(
                            f"**Escalation — {esc_svc} service(s) require human action.**"
                            f"\n\n{rescan.get('escalation_reason', '')}"
                        )

                    if rescan.get("action_required"):
                        st.info(f"**Action required:** {rescan['action_required']}")

                    cves_list = rescan.get("cves")
                    if isinstance(cves_list, list) and cves_list:
                        _sec("Open CVEs from re-scan")
                        st.table([
                            {
                                "CVE ID":      str(e.get("id",      "")) if isinstance(e, dict) else "",
                                "PYSEC":       str(e.get("pysec",   "")) if isinstance(e, dict) else "",
                                "Package":     str(e.get("package", "")) if isinstance(e, dict) else "",
                                "Fix version": str(e.get("fix",     "")) if isinstance(e, dict) else "",
                            }
                            for e in cves_list
                        ])

# ── SLA evidence tab ───────────────────────────────────────────────────────────
with tab_sla:
    p = ROOT / "acme-platform" / "remediation" / "sla-dashboard.html"
    if p.exists():
        st.markdown(
            '<p class="cva-ti">Self-contained SLA dashboard generated by CVE Autopilot. '
            "Per-CVE: advisory deadline, time to fix, test results before and after. "
            "Source file is the evidence record — not edited.</p>",
            unsafe_allow_html=True,
        )
        # Presentation only: the saved evidence file and every data value stay intact.
        evidence = p.read_text("utf-8")
        for icon in ("📊", "🔍", "✅", "🪙", "⚠", "🛡️", "🛡", "🔎", "⏸"):
            evidence = evidence.replace(icon, "")
        evidence_style = """
        <style>
        :root { --bg:var(--cva-bg); --card:var(--cva-panel); --text:var(--cva-text);
            --muted:var(--cva-muted); --border:var(--cva-border); --green:var(--cva-good);
            --amber:var(--cva-warn); --red:var(--cva-bad); --critical:var(--cva-bad); --medium:var(--cva-warn); }
        body { padding:1rem 0 2rem; font-size:16px; line-height:1.6; overflow-wrap:anywhere; }
        .scorecard, header, footer, .bar-section { max-width:none; }
        .scorecard-scope { background:transparent; border:0; border-radius:0; padding:0; margin-bottom:2rem; }
        .scorecard-scope h2 { font-size:1.35rem; line-height:1.4; }
        .sc-grid { grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
        .sc-tile { background:var(--card); border-color:var(--border) !important; border-radius:12px; padding:1.15rem; }
        .sc-label { font-size:.9375rem; text-transform:none; letter-spacing:0; }
        .sc-value { font-size:2.25rem; font-variant-numeric:tabular-nums; }
        .sc-tile.ok .sc-value { color:var(--text); }
        .sc-tile.warn .sc-value { color:var(--amber); }
        .sc-tile.bad .sc-value { color:var(--red); }
        .sc-sub { font-size:.875rem; line-height:1.5; }
        .sc-bar-track, .bar-track { background:var(--border); }
        .sc-bar-green, .bar-fill { background:var(--green); transition:none; }
        .sc-bar-amber { background:var(--amber); }
        .sc-notice { background:var(--cva-warn-bg); color:var(--amber); border-color:var(--border); font-size:1rem; }
        .sc-notice strong { color:inherit; }
        .grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .card { border-left-width:1px !important; border-color:var(--border) !important; }
        .card-title { font-size:1.2rem; }
        .card-pkg, .status-label, table.info, table.info td:last-child, .per-cve-table,
        .tests, .tests span.label, .reach-evidence, .reach-reachable, .reach-not-reachable,
        .reach-unknown, .bar-labels, footer, [style*="font-size:.78rem"], [style*="font-size:.8rem"] { font-size:.9375rem !important; }
        .badge, .badge-kev, .badge-kev-none, .risk-pill, .cve-pill { font-size:.8125rem; letter-spacing:0; text-transform:none; }
        .badge-critical, .badge-kev, .risk-breaking, [style*="background:#7c1a1a"], [style*="background:#1a0a0a"] {
            background:var(--cva-bad-bg) !important; color:var(--red) !important; border-color:var(--red) !important; }
        .badge-medium { background:var(--cva-warn-bg); }
        .risk-safe { background:var(--cva-good-bg); color:var(--green); }
        .tests { background:var(--bg); color:var(--green); border-color:var(--border); }
        .cve-pill { background:var(--cva-info-bg); color:var(--cva-accent); }
        .per-cve-table td:first-child { color:var(--cva-accent); white-space:normal; }
        .per-cve-table td.reach-reachable, .reach-reachable, [style*="color:#d97706"] { color:var(--amber) !important; }
        [style*="color:#94a3b8"] { color:var(--muted) !important; }
        [style*="color:#dc2626"] { color:var(--red) !important; }
        [style*="color:#22d3ee"] { color:var(--cva-accent) !important; }
        .dot { box-shadow:none; }
        ::selection { background:var(--cva-selected); color:var(--cva-selected-text); }
        html { scrollbar-color:var(--border) var(--bg); }
        @media(max-width:640px) {
            .sc-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; }
            .sc-tile { padding:.85rem; }
            .sc-value { font-size:1.85rem; }
            .sc-label { font-size:.875rem; }
            .grid { grid-template-columns:minmax(0,1fr); }
            .card-header { gap:.5rem; flex-wrap:wrap; }
            .bar-labels { gap:1rem; flex-wrap:wrap; }
            table.info td:last-child { font-family:inherit; }
        }
        </style>
        """
        evidence = evidence.replace(
            "</head>",
            f"<style>:root {{{variables}; color-scheme:{appearance.lower()};}}</style>"
            + evidence_style + "</head>", 1,
        )
        components.html(evidence, height=1400, scrolling=True)
    else:
        st.info(_NA)

# ── Diffs tab ──────────────────────────────────────────────────────────────────
with tab_diffs:
    diff_files = sorted((ROOT / "acme-platform" / "remediation").glob("*.diff"))
    if diff_files:
        st.markdown(
            f'<p class="cva-ti">{len(diff_files)} diff file(s) recorded. '
            "Each shows the exact code changes CVE Autopilot applied.</p>",
            unsafe_allow_html=True,
        )
        for d in diff_files:
            with st.expander(d.name):
                st.code(d.read_text("utf-8"), language="diff")
    else:
        st.info(_NA)

# ── Report tab ─────────────────────────────────────────────────────────────────
with tab_report:
    p = ROOT / "docs" / "REMEDIATION.md"
    if p.exists():
        st.markdown(
            '<p class="cva-ti">Per-CVE remediation report: service, versions, files changed, '
            "test results before and after, risk classification, and time taken.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(p.read_text("utf-8"))
    else:
        st.info(_NA)

# ── Advisory tab ───────────────────────────────────────────────────────────────
with tab_advisory:
    pdf = ROOT / "acme-platform" / "security" / "advisory-2026-09.pdf"
    md  = ROOT / "docs" / "advisory-2026-09.md"
    if pdf.exists() or md.exists():
        st.markdown(
            '<p class="cva-ti">The original advisory that triggered this remediation run. '
            "CVE Autopilot parsed this document in Plan mode to extract findings.</p>",
            unsafe_allow_html=True,
        )
    if pdf.exists():
        st.download_button("Download advisory-2026-09.pdf", pdf.read_bytes(),
                           file_name="advisory-2026-09.pdf", mime="application/pdf")
    else:
        st.info(_NA)
    if md.exists():
        st.markdown(md.read_text("utf-8"))
    else:
        st.info(_NA)
