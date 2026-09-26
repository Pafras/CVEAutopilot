# CVE Autopilot

**Security advisory in. Tested fix out.** Built with IBM Bob 2.0 for the
[lablab.ai IBM Bob 2.0 Hackathon](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon).

CVE Autopilot turns a security advisory into a tested, ready-to-merge fix. IBM Bob 2.0 reads the
advisory, finds every affected service, and runs parallel subagents that upgrade dependencies,
repair breaking changes and verify with tests.

## Repo layout
- `acme-platform/` — sample monorepo with real vulnerable dependencies (the remediation target)
- `acme-platform/security/advisory-2026-09.md` — the security scan report Bob reads
- `bob_sessions/` — exported IBM Bob task session reports (required for submission)

## Why a plain version bump is not enough
| Service | CVE | Plain bump | After Autopilot |
|---|---|---|---|
| billing | PyYAML CVE-2020-14343 | ❌ `TypeError` | ✅ |
| notifications | Jinja2 CVE-2024-22195 / CVE-2024-34064 | ❌ `ImportError` | ✅ |
| inventory | requests CVE-2023-32681 | ✅ | ✅ |

## How it works

See [`docs/architecture.md`](docs/architecture.md) for the full Mermaid flowchart.

In short: Bob reads the advisory PDF in **Plan mode** (extract CVEs, pip-audit cross-check, find usages,
mark unaffected services), waits for human approval, then switches to **Agent mode** and runs one
subagent per affected service in parallel. Each subagent baselines tests, bumps the dependency, fixes
any breaking changes, and rolls back on failure. Bob then writes `REMEDIATION.md`, a `CHANGELOG.md`
entry, PR description, and a self-contained SLA dashboard. The Streamlit app displays all outputs.

## Run the demo

1. Open the repo root as your workspace in Bob IDE (the CVE Autopilot mode lives in `.bob/` at the root).
2. Select the **CVE Autopilot** custom mode.
3. Select the **CVE Autopilot mode** and paste the prompt below. Bob stops once for plan approval, then executes.

```
Mode: CVE Autopilot. Remediate acme-platform/security/advisory-2026-09.pdf end to end.
Follow the full playbook, steps 1-9. Plan first and wait for my approval. Then run the three affected services
(billing, notifications, inventory) as parallel subagents. Done = PRD.md requirements R1-R9 all met.
Finish with a checklist of R1-R9 marked pass/fail and the total wall-clock time.
```

After the run, verify tests were not modified:

```bash
git diff main --stat -- acme-platform/services/*/tests
```

Then open `acme-platform/remediation/sla-dashboard.html` in a browser.

## Data sources

- [NVD](https://nvd.nist.gov) (nvd.nist.gov) — US gov, public domain.
- [GitHub Advisory Database](https://osv.dev) via OSV.dev — CC-BY 4.0. Raw records in `acme-platform/security/sources/`.
- Package changelogs (PyYAML, Jinja2/MarkupSafe, requests) — used for migration notes only.
- Regulation: EU Commission CRA reporting page; PCI DSS v4.0.1 (req. 6.3.3). Stats: Verizon DBIR 2026, Veracode SoSS 2025/2026.

## Security
Based on the [IBM hackathon template](https://github.com/watsonxhackathon/ibm-hackathon-template):
`.gitignore` and `.bobignore` keep credentials out of git and Bob session logs.
Copy `.env.example` to `.env` for any keys, and read [SECURITY.MD](SECURITY.MD) before committing.

## License
MIT
