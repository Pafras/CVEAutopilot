# Bob prompts — CVE Autopilot

Budget: 40 Bobcoins PER MEMBER (3 × 40), no top-ups. Rules for every task:
- Account = hackathon enterprise plan (Settings → General shows Budget 40.00) before the first prompt.
- One prompt = one Bob task. Paste as-is. Don't chat back and forth; if stuck, use F1/F2.
- After each task: Tasks → select task → click header → PNG to
  `bob_sessions/orphane_<member>_taskNN_<topic>_summary.png` (member = pafras / erin / dyan).
- Check coin usage in Settings → General after each task; write it in the log at the bottom.
- Never paste API keys, passwords or tokens into a prompt.

## Who runs what (Sat 26 – Sun 27 Sep, submit by Sun 21:00 WITA, hard deadline Sun 23:00)
| Member | Tasks | Est. coins | Output |
|---|---|---|---|
| **Pafras** | M setup, T1, T2, (T3) | ~20–28 | Autopilot mode, remediation branch, REMEDIATION.md, SLA dashboard, run time |
| **Dyan** | T4 (start early, app tolerates missing files), deploy | ~4–8 | Streamlit URL |
| **Erin** | E1 architecture diagram + README, E2 Bob code review of the branch; slides + video | ~6–10 | README, diagram, review notes, PDF deck, MP4 |

**Saturday = build. Sunday = polish, record, submit.**
| When | Pafras | Dyan | Erin |
|---|---|---|---|
| Sat morning | Push repo, create mode M, T1 dry run billing | Clone, T4 app | Clone, E1 diagram + README |
| Sat afternoon | T2 full run (practice run, note the time) | Deploy on Streamlit Cloud | Put diagram in deck, draft video script |
| Sat evening | Merge branch, push | Check live app shows real data | E2 Bob review of branch |
| Sun morning | T3 clean re-run **screen-recorded** (only if T2 was messy), screenshots | Screenshots, app polish without Bob | Fill deck placeholders with real numbers |
| Sun afternoon | Record demo part | Help video | Record + edit video (MP4 ≤5 min) |
| Sun evening | Submit form by 21:00 | Final checks | Deck → PDF, upload |


---

## M — Autopilot mode instructions
Paste into a Bob custom mode named **CVE Autopilot** (exact setup per Bob 2.0 guide). If Bob supports
Skills, also save it as a Skill named `cve-autopilot` and have the mode load it; that's the "deep Bob use"
the May winner (Pedigree) was praised for. If custom modes aren't available, paste this block at the top of T1/T2.

```
You are CVE Autopilot. You turn a security advisory into a tested fix plus patch-SLA evidence.
Spec and acceptance criteria: PRD.md (sections 4-6). Target repo: acme-platform/.

Playbook:
1. Read the advisory PDF. Output a table per finding: package, installed version, CVE IDs, severity,
   fixed version, service. Cross-check fixed versions against acme-platform/security/sources/*.json.
   Also extract the policy deadlines from the PDF (Critical 24h, Medium 14 days).
1b. Live scan cross-check: in each service run `pip install pip-audit` (in a temp venv) and
   `pip-audit -r requirements.txt --format json`. Compare with the advisory table: mark each CVE
   "confirmed by scan", "only in advisory" or "only in scan". Add "only in scan" findings to the plan.
   If no advisory file was given, use the pip-audit results as the input instead.
2. Search acme-platform/services/ for every import and call of each package. List file:line.
   List every service with no affected package as "not affected, no change"; never modify it.
3. Write a remediation plan (order by severity, one line per service, expected risk). Wait for my
   approval before changing anything. (Run steps 1-3 in Plan mode, the rest in Agent mode.)
4. Create git branch autopilot/advisory-2026-09 from main. Record start time (date -u).
5. One subagent per affected service, run in parallel. Each subagent, inside its service dir:
   a. python3 -m venv .venv, install requirements.txt + pytest, run pytest -q -> save as baseline.
   b. Bump the vulnerable pin to the latest release in the safe line named by the advisory.
   c. Reinstall, run pytest -q. If it fails: read the error and the package's migration notes,
      apply the smallest code fix in the service code.
   d. If the attempt still fails, roll back that attempt (Bob rollback / checkpoint) before trying again.
      Max 3 attempts, then stop and flag for a human.
   e. Report: files changed, before/after pytest summary lines, risk = "safe bump" or "breaking fix",
      fixed-at time (date -u).
6. Hard rules: never delete, skip, xfail or weaken a test. Never edit files under tests/.
   Never change a public function signature or behaviour; if a fix needs that, stop and ask me.
   Never commit .venv/.
7. Aggregate: write acme-platform/REMEDIATION.md (per CVE: service, old -> new version, files changed,
   tests before/after, risk, time taken), append acme-platform/CHANGELOG.md, write
   acme-platform/PR_DESCRIPTION.md. Order everything by severity, Critical first.
8. Save output for the viewer:
   - acme-platform/remediation/<service>.diff  (git diff main -- services/<service>)
   - acme-platform/remediation/results.json:
     [{"service","package","cves":[],"severity","old","new","baseline","after","risk","files":[],
       "deadline_hours","fixed_at","minutes_to_fix"}]
   - acme-platform/remediation/sla-dashboard.html: one self-contained HTML file (inline CSS, no
     external requests). Header "Patch SLA evidence — advisory-2026-09". One card per CVE: severity,
     policy deadline, time to fix, status green (inside SLA) / amber (<25% of window left) / red (missed),
     tests before -> after, files changed. A bar comparing our total time to the 43-day industry median
     (Verizon DBIR 2026). Footer: generated by IBM Bob, timestamp, branch name.
9. Commit on the branch with message "fix(security): remediate advisory-2026-09". Record end time.
   Print total wall-clock time.
```

---

## T1 — Dry run, billing only, **Pafras** (~8 coins) → `orphane_pafras_task01_dry_run_billing_summary.png`
```
Mode: CVE Autopilot. Dry run on ONE service only to test the playbook.
Advisory: acme-platform/security/advisory-2026-09.pdf. Only handle the billing service (PyYAML).
Run playbook steps 1-3, 5 and 6 for billing, no subagents needed. Skip step 4 (no branch) and steps 7-9.
At the end tell me: what worked, what in the playbook was unclear or slow, and one concrete
suggested edit to the mode instructions. Do not commit.
```
After: apply the suggested edit to mode M by hand (no coins). `git checkout -- acme-platform && git clean -fd acme-platform` to reset (acme-platform must be committed on main first).

---

## T2 — Full run, all services in parallel, **Pafras** (~12 coins) → `orphane_pafras_task02_full_parallel_run_summary.png`
Start in **Plan mode**. Approve the plan, then let Bob switch to Agent mode.
```
Mode: CVE Autopilot. Remediate acme-platform/security/advisory-2026-09.pdf end to end.
Follow the full playbook, steps 1-9. Plan first and wait for my approval. Then run the three affected services
(billing, notifications, inventory) as parallel subagents. Done = PRD.md requirements R1-R9 all met.
Finish with a checklist of R1-R9 marked pass/fail and the total wall-clock time.
```
After, check by hand (no coins):
```bash
git diff main --stat -- acme-platform/services/*/tests
```
Must print nothing (tests untouched). Then run pytest in each service yourself and open
`acme-platform/remediation/sla-dashboard.html` in a browser.

---

## T3 — Clean re-run for the video, **Pafras** (~8 coins, only if T2 was messy) → `orphane_pafras_task03_demo_run_summary.png`
Reset to baseline, start screen recording, paste T2 unchanged. Skip T3 if T2 was clean and recorded.
On video, make sure these are visible: PDF being read, Plan → Agent switch, 3 subagents running,
a rollback (if one happens), the SLA dashboard at the end.

---

## T4 — Streamlit app, **Dyan** (~4 coins) → `orphane_dyan_task01_streamlit_app_summary.png`
Run on `main` early; T2's output arrives later, so the app must handle missing files.
```
Build a small Streamlit app for CVE Autopilot results. PRD.md requirement R10.
- One file: app.py at repo root. requirements.txt at repo root with only streamlit (pinned).
- Reads committed files only, no network calls, no secrets.
- Any file below may not exist yet: show st.info("Not generated yet — run CVE Autopilot") instead of failing.
- Tab 1 "SLA evidence": embed acme-platform/remediation/sla-dashboard.html with
  st.components.v1.html (scrolling, height ~900).
- Tab 2 "Diffs": one expander per acme-platform/remediation/*.diff, shown with st.code(diff, "diff").
- Tab 3 "Report": acme-platform/REMEDIATION.md via st.markdown.
- Tab 4 "Advisory": offer acme-platform/security/advisory-2026-09.pdf with st.download_button and
  show the markdown copy.
- Title "CVE Autopilot", caption "Security advisory in. Tested fix and SLA evidence out."
- Keep it under 60 lines. Run it locally with streamlit run app.py to check it loads.
```
Then push to main and deploy on Streamlit Community Cloud (no Bob). After T2 is merged, the app shows real data on its own.

---

## E1 — Architecture diagram + README, **Erin** (~3 coins) → `orphane_erin_task01_architecture_readme_summary.png`
Ask mode is enough for reading; Agent mode to save files.
```
Read PRD.md and BOB_PROMPTS.md (mode M). Do two things:
1. Create docs/architecture.md with one Mermaid flowchart of CVE Autopilot: advisory PDF -> Bob Plan mode
   (extract CVEs, find usages, plan) -> human approval -> Agent mode -> 3 parallel subagents
   (billing, notifications, inventory: baseline -> bump -> test -> fix -> rollback on failure -> retest)
   -> REMEDIATION.md, CHANGELOG, PR text, SLA dashboard -> Streamlit viewer.
2. Update README.md: add sections "How it works" (link docs/architecture.md), "Run the demo"
   (open acme-platform in Bob IDE, select the CVE Autopilot mode, paste the T2 prompt), and
   "Data sources" (copy PRD.md section 11). Keep existing sections. Plain, short English.
Do not change any other file.
```

## E2 — Bob code review of the remediation, **Erin** (~4 coins) → `orphane_erin_task02_code_review_summary.png`
After Pafras pushes branch `autopilot/advisory-2026-09`. Use Bob's built-in **Review** workflow on the branch diff vs main.
```
Review the diff of branch autopilot/advisory-2026-09 against main as a security reviewer.
Check: every CVE in acme-platform/security/advisory-2026-09.md is fixed at or above the fixed version;
no test under acme-platform/services/*/tests was changed; code fixes are minimal and keep behaviour.
Write findings to acme-platform/remediation/REVIEW.md (pass/fail per check, one line each). Change nothing else.
```

---

## Stretch — advisory hook (only if ≥6 coins left)
Ask Bob to set up a hook that starts CVE Autopilot when a new `*.pdf` lands in `acme-platform/security/`.
Exact prompt depends on Bob 2.0 hooks docs; decide at kickoff.

---

## Fallback prompts (reserve ~6 coins)
**F1 — stuck subagent**
```
The <service> subagent failed after 3 attempts. Error: <paste last pytest error>.
Read the package migration notes and propose the smallest fix in service code only. Do not touch tests.
```
**F2 — report only** (if code is done but reporting steps 7-8 didn't run)
```
Code fixes on branch autopilot/advisory-2026-09 are done and tests pass. Only do playbook steps 7-9.
```

---

## Coin log
| Member | Task | Coins used | Running total | Notes |
|---|---|---|---|---|
| Pafras | T1 | | | |
| Pafras | T2 | | | |
| Pafras | T3 | | | |
| Dyan | T4 | | | |
| Erin | E1 | | | |
| Erin | E2 | | | |
