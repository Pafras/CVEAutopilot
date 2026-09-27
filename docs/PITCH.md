# CVE Autopilot — Pitch Kit

Follows https://lablab.ai/delivering-your-hackathon-solution

## Project title
CVE Autopilot — Patch-SLA Evidence, From Advisory to Tested Fix in Minutes

## Short description (224 / 255 chars)
CVE Autopilot turns a security advisory PDF into a tested fix plus patch-SLA evidence. IBM Bob plans the fix, runs parallel subagents that upgrade each service, repair what the upgrade breaks and prove it with passing tests.

## Long description (≥100 words)
**Problem.** Patch deadlines are now law and audit items. Since 11 September 2026 the EU Cyber Resilience Act
requires manufacturers to report actively exploited vulnerabilities within 24 hours, and PCI DSS 6.3.3 requires
critical patches within one month. Yet the median time to fix a known-exploited vulnerability is 43 days
(Verizon DBIR 2026). The slow part is manual: read the advisory, find affected services, upgrade, discover the
upgrade breaks the code, fix it, re-test, write the PR, then prove to an auditor it was done in time.
In our sample monorepo, upgrading PyYAML and Jinja2 to their safe versions breaks 2 of 3 services.

**Solution.** CVE Autopilot is an IBM Bob workflow that runs the whole remediation, not just code suggestions:
- **Document understanding** — Bob reads the advisory PDF and extracts package, CVE, severity, fix version and policy deadline.
- **Plan mode → Agent mode** — Bob proposes a remediation plan; after human approval it executes.
- **Parallel subagents** — one per service: upgrade, run tests, fix breaking changes, roll back failed attempts, retest until green.
- **HTML report** — Bob produces a patch-SLA dashboard: each CVE's deadline vs actual time to fix, with test evidence and diffs.
- **Human gate** — Bob stops before any behaviour change and never weakens a test.

**Who it is for.** Platform, DevOps and AppSec teams in regulated industries (payments, EU product makers,
finance, health), and the compliance owners who must show patch SLAs were met.

**Why it is different.** Dependabot, Renovate and Snyk open version-bump PRs, and GitHub can now hand a
Dependabot alert to a coding agent that drafts a PR. CVE Autopilot packages an IBM Bob workflow across services:
it shows each break and its fix with tests, re-scans to verify the closure, and stops for human review when a
secure fix would change supported behaviour.

**Impact.** On our sample monorepo, the advisory run closed 8 of 9 CVEs in 4 min 29 s and escalated the 9th;
a day-2 live scan closed 29 of 33 advisories in 6 min 18 s and escalated 4, including one the safety brake stopped.
Every closure landed inside our internal policy windows (24 h Critical, 14 days Medium), and no existing test was
changed. The DBIR 43-day median describes the size of the problem; it is not a like-for-like comparison.
CVE Autopilot helps teams meet these deadlines; it does not by itself make anyone compliant.

## Tags
IBM Bob 2.0, AI Agents, DevSecOps, Security, Compliance, Application Maintenance, Python, Streamlit

## Industry stats (for slide 2 Problem and slide 7 Impact)
Cite these as sources on the slide. Checked 2026-09-25.
- **43 days** median to remediate a known-exploited vulnerability, up from 32; 60–70% still open at day 7.
  Exploitation is now the #1 breach entry point (31% of initial access). — Verizon DBIR 2026, via
  [watchTowr summary](https://watchtowr.com/resources/verizon-dbir-2026-vulnerability-exploitation/)
- **252 days** average time to fix flaws (+47% in 5 years). **70%** of critical security debt comes from
  third-party open-source code; third-party flaws take ~12 months to fix vs 8 months for first-party. —
  [Veracode SoSS 2025](https://www.veracode.com/blog/breaking-free-from-security-debt/)
- **82%** of organizations carry security debt, **60%** carry critical debt. —
  [Veracode SoSS 2026](https://www.veracode.com/blog/2026-state-of-software-security-report-risky-security-debt/)

- **EU Cyber Resilience Act, Art. 14:** since 11 Sep 2026, manufacturers must report actively exploited
  vulnerabilities (24h early warning, 72h notification, final report 14 days after a fix is available). —
  [EU Commission](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting)
- **PCI DSS v4.0.1, req. 6.3.3:** critical security patches within one month of release. —
  [TrustedSec explainer](https://trustedsec.com/blog/pci-dss-vulnerability-management-the-most-misunderstood-requirement-part-3)
  Wording differs between v4.0 (critical + high) and v4.0.1 (critical); say "critical".

Line for the video: "Teams take a median of 43 days to patch vulnerabilities attackers are already using. On our sample repo, Autopilot fixed, tested and re-scanned in minutes, and stopped for a human when a fix was unsafe."
Positioning line (from the audit): "CVE Autopilot uses IBM Bob to repair dependency upgrades across services, verify the results, and stop for human review when a secure fix would change supported behavior."
Do not say: "all CVEs fixed", "43 days → 4 minutes", "only we fix code", "not reachable" (say "no path found in the checked code"), "CRA requires patching in 24 h" (CRA is about reporting; the 24 h patch window is our internal policy), "the hook auto-remediates" (it is a reminder).

## Real results from the T2 run (use these numbers)
Source: `docs/REMEDIATION.md`, `acme-platform/remediation/results.json`, PR #5.
- **4 min 29 s** total, advisory to tested fix, 3 affected services fixed **in parallel** by 3 Bob subagents
- **8 of 9 CVEs** closed (1 Critical, 7 Medium); pip-audit found CVEs the advisory PDF missed (e.g. Jinja2 CVE-2025-27516, CVE-2024-56326)
- Post-fix re-scan caught the 9th: requests 2.32.5 does not fix CVE-2026-25645 (fix 2.33.0 needs Python ≥ 3.10) → escalated to a human, not forced. Re-scan also found 2 new urllib3 CVEs (escalated). None of the 11 is in CISA KEV.
- SBOM: 16 known vulnerabilities before, 3 after (all escalated; no call path found in the checked code, not proof they are unexploitable)
- Critical PyYAML CVE fixed in **3 min 28 s** vs a 24 h policy window (0.24% of the window used)
- Plain bump broke 2 of 3 services (`TypeError`, `ImportError`); Autopilot showed each failure, fixed it, all 6 tests green
- 0 tests changed, unaffected `auth` service untouched
- Industry median to patch a known-exploited vulnerability: **43 days** (Verizon DBIR 2026)
- Bob cost: 3.84 Bobcoins for the T2 remediation task (re-scan, KEV, SBOM and compliance were later tasks)

## Real results from the T3 run (day 2, live scan, PR #22)
- No advisory: `pip-audit` + `npm audit` across all 6 services; plan approved by a human before any change
- **web-gateway fixed:** axios 0.21.1 → 0.34.0, lodash 4.17.20 → 4.18.1 (29 advisories), tests 9/9 → 9/9, no code change, post-fix `npm audit`: 0
- **reports stopped by the safety brake:** PyYAML 6.0 breaks the `!!python/object` tag the service relies on; the only way to pass was `UnsafeLoader`, which is forbidden → escalated, service untouched
- **inventory escalated:** fixes need Python ≥ 3.10, service runs 3.9
- auth, billing, notifications clean → untouched
- Scorecard: 33 found · 29 closed · 4 escalated · 88% · 0 tests changed · CISA KEV: 0 matches
- 6 min 18 s remediation run, 8.13 Bobcoins for the task
- The developer steered Bob 4 times (use the real test suite, skip PyYAML 5.4.x which does not build on Python 3.9, exclude node_modules, merge rather than overwrite the KEV file)
- Team Diapers: Pafras, Erin, Dyan

## Slides (PDF export of the deck, 11 slides, 2–3 sentences each)
Deck: https://claude.ai/artifact/91kaPpY5fSrBV9UtyXFbrE → download as PDF.
1. Cover  2. Problem  3. Proof (bump breaks 2 of 3)  4. Solution flow  5. Bob 2.0 features
6. Live run  7. Impact  8. Market (TAM/SAM)  9. Competition / USP  10. Business model  11. What's next

Market sources: DevSecOps ≈ $10B in 2025 (Fortune Business Insights); software composition analysis
≈ $0.4B in 2025, ~20% CAGR (Straits Research). SCA estimates vary widely by analyst.

## Video (MP4, max 5 min — target 4:00)
lablab wants: intro → walk through the PDF slides → show the product working.
- **0:00–0:20 Intro.** Who we are, one line: "Security advisory in. Tested fix out."
- **0:20–1:40 Slides.** Problem (slide 2), proof with real errors (3), solution flow (4), Bob features (5).
- **1:40–3:20 Demo (screen recording).** Open Bob, run CVE Autopilot on the advisory: CVEs extracted, usages
  found, 3 subagents in parallel, breaking code fixed, tests green. Then open the Streamlit app with the report.
- **3:20–4:00 Business.** Impact number (7), market (8), competition (9), business model (10), next steps (11).

## Submission checklist
- [ ] Project title
- [ ] Short and long descriptions
- [ ] Technology and category tags
- [ ] Cover image (`assets/cover.png`, 16:9 PNG)
- [ ] Video presentation (MP4, ≤5 min)
- [ ] Slide presentation (PDF)
- [ ] Public GitHub repo, incl. Bob-assisted code AND Bob task-summary screenshots from every member in `bob_sessions/`
- [ ] Application URL (Streamlit Community Cloud)
