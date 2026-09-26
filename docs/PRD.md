# CVE Autopilot — PRD

**Status:** v2, pre-kickoff · **Team:** Diapers · **Deadline:** Sep 27, 23:00 WITA
**Challenge fit:** Maintenance + Release readiness ("review dependencies, summarise risks").
**Positioning:** patch-SLA compliance evidence, not "AI saves developer time". Autopilot closes the CVE,
fixes the code the upgrade breaks, and produces the evidence an auditor asks for.

## 1. Problem
A security scan flags vulnerable dependencies. A developer then spends hours on manual work:
read the advisory, find which services use the package, bump it, find out the bump breaks the code,
fix it, re-run tests, write the PR. Across many services this takes days, and critical CVEs stay open
past policy deadlines. Dependabot/Renovate open the bump PR; **fixing what the bump breaks is still manual.**

**Why now: patch deadlines are becoming law and audit items.**
- **EU Cyber Resilience Act, Art. 14** — since **11 Sep 2026**, manufacturers of products with digital elements
  must report actively exploited vulnerabilities to ENISA/CSIRT: early warning in 24h, notification in 72h,
  final report within 14 days after a fix is available. CRA vulnerability-handling duties (Annex I) apply from 11 Dec 2027.
- **PCI DSS v4.0.1, req. 6.3.3** — critical security patches installed within one month of release.
- Median time to remediate a known-exploited vulnerability is **43 days** (Verizon DBIR 2026).

Proof (verified on `acme-platform/`): plain safe-version bump breaks 2 of 3 services.

| Service | CVE | Plain bump |
|---|---|---|
| billing | PyYAML CVE-2020-14343 (Critical) | ❌ `TypeError: load() missing 1 required positional argument: 'Loader'` |
| notifications | Jinja2 CVE-2024-22195, CVE-2024-34064 | ❌ `ImportError: cannot import name 'Markup'` |
| inventory | requests CVE-2023-32681 | ✅ safe bump |

## 2. Users
Platform, DevOps and AppSec engineers who maintain many services on open-source dependencies,
in regulated industries with patch SLAs (payments/PCI, EU product makers/CRA, finance, health).
Secondary: the compliance/audit owner who needs proof that SLAs were met.

## 3. Goal
Security advisory PDF in → tested fix + SLA evidence out, in minutes.

## 4. Scope
**In**
- Input: advisory PDF at `acme-platform/security/advisory-2026-09.pdf` (markdown copy at `docs/advisory-2026-09.md` for GitHub readers).
- Target: `acme-platform/` (4 Python services, pytest). 3 are affected; `auth` is not and must stay unchanged.
- Bob **custom mode** "CVE Autopilot", playbook packaged as a **Bob Skill** if supported (see docs/BOB_PROMPTS.md).
- Bob features shown on screen: **Plan mode → Agent mode**, **document understanding** (PDF),
  **parallel subagents**, **rollback** of failed fix attempts, **HTML report**.
- Outputs: remediation branch, `docs/REMEDIATION.md`, `docs/CHANGELOG.md` entry, PR description,
  `remediation/sla-dashboard.html` (Bob-generated), `remediation/results.json` + diffs.
- Streamlit app, deployed, that embeds the SLA dashboard.

**Stretch** (only with coins/time left)
- Bob hook that starts Autopilot when a new advisory lands in `security/`.

**Non-goals** (do not build)
- Running Bob from the Streamlit app. The app only shows results of a finished run.
- Building our own scanner. We reuse pip-audit (PyPA) to cross-check the advisory or as input when no advisory exists.
- Filing real CRA/ENISA reports. We produce the evidence, a human files.
- Languages other than Python, CI integration, auto-merge, opening real GitHub PRs.
- Auth, database, multi-user anything.

## 5. User flow
1. Dev opens `acme-platform/` in Bob IDE, CVE Autopilot mode, points it at the advisory PDF.
2. **Plan mode:** Bob reads the PDF, extracts findings, finds usages, proposes a remediation plan. Dev approves.
3. **Agent mode:** one subagent per affected service **in parallel**: baseline tests → bump → tests → fix → tests.
   A failed attempt is **rolled back** before the next try.
4. Bob merges the results: report, changelog, PR text, SLA dashboard.
5. Bob stops and asks the dev before any behaviour or public API change.
6. Dev / auditor reviews the SLA dashboard (Streamlit URL) and merges.

## 6. Requirements + acceptance criteria
| # | Requirement | Done when |
|---|---|---|
| R1 | Parse advisory PDF | Bob outputs a table of all 4 CVEs: package, installed ver, fixed ver, severity, service. Matches the PDF exactly. |
| R1b | Scan cross-check | pip-audit runs per service; each CVE marked confirmed / only in advisory / only in scan. Without an advisory, pip-audit output is the input. |
| R2 | Find usages | Every import/call site of PyYAML, Jinja2, requests in `acme-platform/services/` listed with file path. |
| R2b | Plan first | Plan mode produces the remediation plan; Agent mode executes it after approval. Both visible on video. |
| R3 | Parallel fix | 3 subagents run at the same time (visible in Bob, captured on video). |
| R4 | Fix loop rules | Pins bumped to fixed version or later; breaking code fixed with minimal change; **no test deleted, skipped or weakened**; failed attempt rolled back; max 3 attempts, else flag for human. |
| R5 | Green tests | `pytest` passes in all 3 services after the run. Before/after results recorded. |
| R6 | `docs/REMEDIATION.md` | Per CVE: service, old → new version, files changed, tests before/after, risk (safe bump / breaking fix), time taken. |
| R6b | Viewer data | `acme-platform/remediation/results.json` + one `<service>.diff` per service. |
| R7 | Changelog + PR text | `docs/CHANGELOG.md` entry and PR description, fixes ordered by severity. |
| R8 | Human gate | Playbook tells Bob to stop and ask before behaviour/public-API changes. |
| R9 | SLA dashboard | Single self-contained `remediation/sla-dashboard.html` from Bob: per CVE, advisory date, policy deadline (Critical 24h, Medium 14d), fixed-at time, status green/amber/red, time-to-fix vs 43-day industry median, tests before/after, links to diffs. |
| R10 | Streamlit app | Public URL embeds the SLA dashboard and shows the advisory, diffs and `docs/REMEDIATION.md`. Reads committed files only; no secrets, no Bob calls. |

## 7. Success metrics (for the pitch)
- **Time:** manual estimate (triage + 3 upgrades + 2 breaking fixes + tests + PR ≈ 4–8 h) vs Autopilot wall-clock minutes. Measured on the real run.
- **SLA:** Critical fixed well inside its 24h policy window, against a 43-day industry median.
- **Correctness:** 3/3 affected services green, 4/4 CVEs closed, 0 tests weakened, unaffected `auth` left untouched.
- **Effort:** developer actions needed = 1 prompt + 1 plan approval + 1 review.

## 8. Competition
| Tool | Bumps version | Fixes code the bump breaks | Proves with tests | SLA evidence |
|---|---|---|---|---|
| Dependabot / Renovate | ✅ | ❌ | CI only | ❌ |
| Snyk Fix PRs | ✅ | ❌ | CI only | partial (dashboards) |
| OpenRewrite / Moderne | ✅ | ✅ for known recipes | ❌ | ❌ |
| **CVE Autopilot** | ✅ | ✅ any change, reads migration notes | ✅ before/after | ✅ |

## 9. Constraints
- **Bob IDE is the core component.** All solution code is Bob-assisted.
- **40 Bobcoins per member (3 members), no top-ups.** Few, large, well-specified tasks. Point Bob to this PRD instead of re-explaining.
- **Evidence:** PNG task-summary screenshot per Bob task, from every member, in `bob_sessions/` (`diapers_<member>_taskNN_<topic>_summary.png`).
- **Data:** no client/confidential/personal/social-media data. `acme-platform/` is our own sample code.
  CVE data from public sources that allow commercial use (see §11).
- Repo public, MIT license.

## 10. Risks
| Risk | Mitigation |
|---|---|
| Coins run out mid-build | Budget in docs/PLAN.md; Streamlit app last and tiny (embeds Bob's HTML); watsonx or manual as fallback. |
| Bob subagents/parallel/Skills work differently than assumed | Read Bob 2.0 guide first hour; adapt playbook, keep the demo flow. |
| Fix loop goes wrong (weakens tests) | Explicit rule in playbook; check `git diff tests/` before accepting. |
| Overclaiming regulation | CRA = reporting duty, PCI = patch window. Say "helps meet", never "makes you compliant". |
| Streamlit Cloud deploy issues | App is plain static viewer; deploy early (Sat afternoon). |

## 11. Data sources
- NVD (nvd.nist.gov) — US gov, public domain.
- GitHub Advisory Database via OSV.dev — CC-BY 4.0. Raw records in `acme-platform/security/sources/`.
- Package changelogs (PyYAML, Jinja2/MarkupSafe, requests) — used for migration notes only.
- Regulation: EU Commission CRA reporting page; PCI DSS v4.0.1 (req. 6.3.3). Stats: Verizon DBIR 2026, Veracode SoSS 2025/2026.
