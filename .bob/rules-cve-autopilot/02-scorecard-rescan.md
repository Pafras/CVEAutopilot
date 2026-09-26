# CVE Autopilot — scorecard & re-scan rules

These rules extend the playbook. Where they differ from earlier rules, these win.

## 1. Post-fix re-scan (mandatory)

After all service fixes are applied, re-run the appropriate scanner in **every fixed service**:

- **Python services**: `pip-audit -r requirements.txt --format json` (inside a temporary venv; delete the venv afterwards).
- **Node services**: `npm audit --json` (in the service directory).

Record remaining known vulnerabilities per service.
**Any remaining vulnerability means the run is not done.** Either fix it (follow the same per-service subagent flow) or escalate it as a human-review item. Do not mark the run complete until every fixed service has 0 remaining vulnerabilities or an explicit human escalation.

## 2. Scorecard computation

After the re-scan, compute a **Scorecard** object with the following fields:

| Field | How to compute |
|---|---|
| `cves_found` | Total distinct CVEs identified in the advisory / initial scan |
| `cves_closed` | CVEs confirmed fixed by re-scan (0 remaining) |
| `remediation_rate` | `cves_closed / cves_found` as a percentage |
| `verified_by_rescan` | `true` / `false` — were all closures confirmed by a re-scan? |
| `auto_fixed_services` | Count of services fixed without human intervention |
| `escalated_services` | Count of services flagged for human review |
| `breaking_changes_repaired` | Count of service-code fixes needed after a dependency bump broke tests |
| `tests_changed` | Must be 0; any non-zero value is a policy violation |
| `sla_compliant_cves` | Count of CVEs fixed inside their policy window |
| `sla_compliance_rate` | `sla_compliant_cves / cves_closed` as a percentage |
| `total_time_seconds` | Wall-clock seconds from branch creation to final commit |
| `time_per_cve_seconds` | `total_time_seconds / cves_closed` |
| `bobcoins_per_cve` | Ask the human for the task's total Bobcoins; divide by `cves_closed`. If unknown write `"n/a"` |

## 3. Scorecard in output artefacts

**`remediation/results.json`** — add a top-level `"scorecard"` key whose value is the Scorecard object.

**`remediation/sla-dashboard.html`** — prepend a **Scorecard section** as the very first visible section of the page, before the per-CVE cards. It must:
- Be self-contained (inline CSS, no external requests).
- Display every field from the Scorecard as a labelled metric tile or table row.
- Highlight `tests_changed > 0` in red.
- Highlight `verified_by_rescan = false` in amber.
- Show `remediation_rate` and `sla_compliance_rate` as bold percentages with a small inline bar.
