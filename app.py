from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
_NA = "Not generated yet — run CVE Autopilot"

st.title("CVE Autopilot")
st.caption("Security advisory in. Tested fix and SLA evidence out.")

tab_sla, tab_diffs, tab_report, tab_advisory = st.tabs(
    ["SLA evidence", "Diffs", "Report", "Advisory"]
)

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
    md = ROOT / "docs" / "advisory-2026-09.md"
    if pdf.exists():
        st.download_button("Download advisory-2026-09.pdf", pdf.read_bytes(),
                           file_name="advisory-2026-09.pdf", mime="application/pdf")
    else:
        st.info(_NA)
    st.markdown(md.read_text("utf-8")) if md.exists() else st.info(_NA)
