# CVE Autopilot — Build Plan

> **Current plan (Sat 26 Sep evening):** read the **"DECIDED: upgrade breakdown"** section and the two
> **"Rebalanced"** notes at the bottom, and the GitHub issues (each has the ready-to-paste Bob prompt).
> Sections above them are earlier drafts kept for history.

**Build window: Sep 25, 23:00 → Sep 27, 23:00 WITA (48h).** Bob access arrives at kickoff.
Spec, scope and acceptance criteria are in [PRD.md](PRD.md). Point Bob there instead of re-explaining.

## What we demo
Pitch frame: **patch-SLA compliance evidence** (EU CRA Art. 14 reporting live since 11 Sep 2026, PCI DSS 6.3.3),
not "AI saves dev time". See PRD §1.

`security/advisory-2026-09.pdf` goes in → Bob reads the PDF → **Plan mode** proposes the plan, dev approves →
**Agent mode**: one subagent per affected service runs **in parallel** → each bumps the dependency, runs tests,
fixes the breaking code (rolls back failed attempts), re-runs tests → Bob merges results into one remediation
branch + `REMEDIATION.md` + CHANGELOG + PR text + **`sla-dashboard.html`** (Bob's HTML report).

Proof point (already verified):
| Service | CVE | Plain version bump | After Autopilot |
|---|---|---|---|
| billing | PyYAML CVE-2020-14343 (Critical) | ❌ `TypeError: load() missing Loader` | ✅ |
| notifications | Jinja2 CVE-2024-22195/34064 | ❌ `ImportError: cannot import name 'Markup'` | ✅ |
| inventory | requests CVE-2023-32681 | ✅ (safe bump) | ✅ |

## Deliverables (built WITH Bob during event)
1. **Autopilot mode** — Bob custom mode holding the playbook, also packaged as a Bob Skill if supported (format per Bob 2.0 docs at kickoff).
2. **`REMEDIATION.md`** — per CVE: service, old → new version, files changed, test result before/after, risk (safe bump vs breaking fix), time taken.
3. **SLA dashboard** (`remediation/sla-dashboard.html`) — Bob-generated HTML: per-CVE deadline vs time to fix, green/amber/red.
4. **Streamlit app** (`app.py`) — embeds the SLA dashboard, shows diffs, report and advisory. Deploy on Streamlit Community Cloud = "Application URL" (lablab wants Streamlit, Replit or Vercel).
5. **Bob task session summary screenshots** of ALL tasks, from EVERY member — REQUIRED.
   Bob IDE → Tasks → open task → click task header → screenshot (PNG) → `bob_sessions/`,
   named `diapers_<member>_taskNN_<desc>_summary.png`. Budget: 40 Bobcoins per member, no top-up.
   **Required for eligibility:** after EVERY Bob task, screenshot its summary as PNG into `bob_sessions/`
   (Bob chat → Tasks → select task → click task header). Name: `diapers_taskNN_<topic>_summary.png`.
6. **Public** GitHub repo — a private repo lowers the score.

## Autopilot playbook + Bob prompts
See [BOB_PROMPTS.md](BOB_PROMPTS.md): mode instructions (M), tasks T1–T4, fallbacks, coin log.

## Bobcoin budget (40 total, no top-ups)
Rough guess; real cost per task unknown until kickoff. Check Settings → General after each task and re-plan.
| Step | Coins |
|---|---|
| Create Autopilot mode + dry run on billing | 8 |
| Full parallel run, all 3 services | 12 |
| Playbook fixes + one clean re-run for the video | 8 |
| Streamlit `app.py` (embeds Bob's HTML, tiny) | 4 |
| Reserve (fallbacks, or stretch hook) | 8 |
If coins run out: finish by hand or with watsonx. Never re-run the full demo just to tidy output.

## Timeline (48h, WITA)
| When | Task |
|---|---|
| Fri 23:00–00:00 | Accept `ibm-hackathon-xxxx` invite (check spam). Switch Bob to `ibm-coding-challenge-uat` / `us-east`. Read Bob guide: custom modes, Skills, Plan mode, subagents, parallel tasks, rollback, hooks. |
| Sat 00:00–02:00 | Create Autopilot mode from playbook. Dry run on billing only. Screenshot → `bob_sessions/`. Sleep. |
| Sat 09:00–13:00 | Full run, 3 services in parallel. Plan mode → Agent mode. Check PRD R1–R9, open SLA dashboard. Check `git diff` on tests. Time it. Screenshot. |
| Sat 13:00–17:00 | Bob builds Streamlit `app.py` (PRD R10). Push public repo, deploy on Streamlit Community Cloud. |
| Sat 17:00–20:00 | Clean re-run for the video, screen-recorded. Fill impact numbers in deck + PITCH.md. |
| Sun 09:00–14:00 | Record + edit video (≤5 min). Export deck PDF. Export Bob report → `bob-report/`. Check `bob_sessions/` is complete. |
| Sun 14:00–17:00 | Fill lablab form (checklist in PITCH.md). **Submit.** |
| Sun 17:00–23:00 | Buffer only. |

## Pre-kickoff checklist (do now)
- [x] Register on lablab.ai
- [x] GitHub repo (public, MIT)
- [x] Target repo `acme-platform/` with real CVEs, tests verified
- [x] Pitch text, video script, submission checklist (PITCH.md)
- [ ] Slide deck: update to compliance frame (CRA/PCI on slide 2, competition table on slide 9); numbers after demo
- [x] Cover image (`assets/cover.png`)
- [x] PRD (PRD.md)
- [x] `bob_sessions/` folder
- [x] Advisory PDF (`acme-platform/security/advisory-2026-09.pdf`) + OSV source records
- [x] Bob prompts (BOB_PROMPTS.md)
- [ ] IBMid created (same email as lablab registration)
- [ ] Bob IDE installed, **v2.0.2 or later** (v1.0.3 / v2.0.0 stop working Sep 30)
- [ ] Skim Bob guide
- [ ] Push `acme-platform/`, `assets/`, PRD, PLAN to GitHub
- [ ] Streamlit Community Cloud account, linked to GitHub
- [ ] Screen recorder ready (QuickTime ok, export MP4)

## Stretch (only if time left)
- Bob hook: new advisory PDF in `security/` starts Autopilot (BOB_PROMPTS.md stretch).
- Add a 4th service in Node to show multi-language.

## Upgrade options (Sat 26 Sep, NOT decided yet — pick later)
Coins left ≈ Pafras 34.6, Erin ~40, Dyan ~40. Product type: developer tool inside Bob IDE (not web/mobile);
Streamlit web app is only the viewer / Application URL. Categories: Developer Tools, DevSecOps, AI Agents.

| # | Upgrade | Why judges care | Who | Coins |
|---|---|---|---|---|
| U1 | Node.js service (e.g. `web-gateway` with old lodash/axios) + `npm audit` in playbook | Proves it is not Python-only | Pafras | ~8 |
| U2 | Package playbook as Bob Skill `cve-autopilot` | Reusable in any repo; deeper Bob feature use | Pafras | ~2 |
| U3 | Bob Hook: auto-run Autopilot when a new advisory PDF lands in `security/` | "Drop a PDF, it fixes itself" demo moment | Pafras | ~3 |
| U4 | GitHub Action: scheduled pip-audit/npm audit → opens issue on new CVEs | Full loop detect → fix → evidence → PR | Dyan (after T4) | ~3 |
| U5 | `COMPLIANCE.md` evidence pack mapping the run to PCI DSS 6.3.3 / CRA Art. 14 | Makes SLA evidence auditor-ready | Erin (after E2) | ~2 |

If chosen: Sunday T3 = final recorded run with 4 services, 2 languages, triggered by the hook.
Check Bob docs for Skills + Hooks before writing prompts.

## Idea-strengthening options V1–V7 (Sat 26 Sep, NOT decided yet)
| # | Option | Why it strengthens the idea | Criterion | Coins |
|---|---|---|---|---|
| V1 | Exploitability priority: match each CVE to CISA KEV (public known-exploited list) + Bob checks if the vulnerable function is actually reachable in our code | "This one is exploitable in YOUR code, fix first" — beyond plain scanners | Originality | ~3 |
| V2 | Safety-brake demo: add a case where the upgrade forces a behaviour change → Autopilot stops, rolls back, asks a human (rule R8) | Shows the agent knows when NOT to act; addresses fear of AI changing code | Originality / trust | ~4 |
| V3 | Measure real manual time: one person fixes 1 service without Bob, with a stopwatch | Replaces the `<X> hours` placeholder with measured data | Business value | 0 |
| V4 | ROI per CVE: 3.84 Bobcoins for 9 CVEs vs developer hours | Data-backed business model slide | Business value | 0 |
| V5 | SBOM before/after via `pip-audit -f cyclonedx-json` | Standard compliance evidence (CRA) | Business value | ~1 |
| V6 | "Why you can trust it" slide: .bobignore, never edits tests, 2 human gates, everything via PR | Answers the biggest AI-agent objection | Presentation | 0 |
| V7 | Real user quote: ask 1–2 developer/security friends how long CVE patching takes (must be real, never invented) | Problem validation | Presentation | 0 |

Recommended if time is short: V1 + V2 + V3, combined with U1 into one final recorded run on Sunday.

## Scorecard + automation options (Sat 26 Sep, NOT decided yet)
| # | Option | Why | Coins |
|---|---|---|---|
| S1 | **Scorecard** at top of SLA dashboard + in results.json / Streamlit: remediation rate, verified-by-rescan, auto-fix rate, breaking changes repaired, test integrity (0 tests changed), SLA compliance, **Bobcoins per CVE** (T2: 3.84/9 ≈ 0.43), time per CVE (~30 s) | Sellable numbers; efficiency per coin, not more coin use | ~2 (with S2) |
| S2 | **Post-fix re-scan**: run pip-audit again after fixes, must show 0 known vulns remaining; add as playbook step | Strongest proof the fix worked | incl. above |
| C  | **Bob Shell in GitHub Actions** (fully automatic fix + PR, no IDE) | Vision only → "What's next" slide. NOT for this hackathon: needs IBM/Bob credentials in CI (suspension risk) + unattended coin spend | 0 |

Notes:
- Honesty: 100% rates are from ONE demo repo → always say "on our demo run". With V2 a mixed result
  (e.g. "8 auto-fixed, 1 safely escalated") is more credible than 100%.
- "Bob recommends Autopilot": U2 Skill description ("use when dependencies have CVEs / advisory arrives /
  pip-audit or npm audit reports vulns") so Bob picks it up by itself; U3 hook suggests it when requirements change.
- V2 concrete example: a service that intentionally uses `yaml.load` with `!!python/object` tags. Safe fix
  (SafeLoader) changes behaviour → Autopilot must roll back, stop and ask a human (rule R8).
- Automation recommendation: A (Bob IDE hook, U3) + B (GitHub Action detection, U4). Detection automatic,
  fix one approval away. Bob Hooks docs page 404'd — check events directly in Bob Settings → Hooks.
- My overall priority if time allows: S1+S2, V1, V2, V3, U1, then U2/U3.

## DECIDED: upgrade breakdown (Sat 26 Sep ~18:00 WITA) — tracked as GitHub issues
Deadline for all upgrades: **Sun 12:00 WITA**; anything unfinished is dropped (current version is already submittable).
File ownership (avoid push conflicts): Pafras = `.bob/`, `acme-platform/services/`, `acme-platform/security/` ·
Erin = `docs/`, `README.md`, slides/video content · Dyan = `app.py`, root `requirements.txt`, `.github/workflows/`.

| Who | Issue | Plan ref | Coins |
|---|---|---|---|
| Pafras | #9 Post-fix re-scan + Scorecard | S1+S2 | ~2 |
| Pafras | #10 CISA KEV priority + reachability | V1 | ~3 |
| Pafras | #11 Node.js web-gateway + npm support | U1 | ~4 |
| Pafras | #12 Safety-brake reports service + escalation rule | V2 | ~3 |
| Pafras | #13 T3 final recorded run (Sun morning, scan-driven, 5 services) | T3 | ~8–10 |
| Pafras | #14 Optional Bob Skill + Hook (only if done by Sun 10:00) | U2+U3 | ~5 |
| Erin | #15 Measure manual fix time (no Bob) | V3 | 0 |
| Erin | #16 SBOM before/after | V5 | ~1 |
| Erin | #17 docs/COMPLIANCE.md + README fix | U5 | ~2 |
| Erin | #18 Real user quotes | V7 | 0 |
| Erin | #19 ROI line + trust slide content | V4+V6 | 0 |
| Erin | #3 slides, #4 video (ongoing) | — | 0 |
| Dyan | #6 Streamlit app + deploy (critical path) | T4 | ~4 |
| Dyan | #7 GitHub Action scheduled scan | U4 | ~3 |
| Dyan | #8 Scorecard tab in app (after #9) | S1 | ~1 |

Order for Pafras: #9 → #10 → #11 → #12 → (Sun) #14 optional → #13.
T3 story: day 2, no advisory, live scan finds Node + reports CVEs; Node auto-fixed, reports safely escalated,
all services re-scanned clean. Not in scope: C (Bob Shell in CI) → "What's next" slide only.
Closed: #1 (E1), #2 (E2). PR #5 merged 367e9e1.

### Rebalanced (Sat ~18:10): Erin focuses on video + slides
- Moved to Dyan: #15 V3 manual timing, #16 V5 SBOM, #17 U5 COMPLIANCE.md + README fix.
- Erin keeps presentation work only: #3 slides, #4 video, #18 user quotes, #19 ROI + trust slide content.
- File ownership update: Dyan now also owns `docs/COMPLIANCE.md`, `README.md`, `acme-platform/remediation/sbom/`.
- Dyan order: #6 Streamlit (critical) → #8 scorecard tab (after #9) → #16 SBOM → #17 COMPLIANCE → #7 GitHub Action → #15 manual timing.
  Anything not done by Sun 12:00 is dropped; #6 is the only must-have.

### Rebalanced again (Sat ~18:15): Dyan only app work, Pafras takes the rest
- Moved to Pafras: #15 V3 (low priority), #16 V5 SBOM, #17 U5 COMPLIANCE.md + README fix.
- Dyan: #6 Streamlit (must) → #8 scorecard tab → #7 GitHub Action. Keeps his own Bob screenshots.
- Erin: #3 slides, #4 video, #18 quotes, #19 ROI + trust content.
- Pafras order tonight: #9 → #16 → #17 → #10 → #11 → #12 → (#15 if time). Sunday: #14 optional → #13 recorded run.
- Pafras coin estimate ≈ 2+1+2+3+4+3+10 (+5 optional) ≈ 25–30 of ~34.6 left.
