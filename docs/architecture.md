# CVE Autopilot — Architecture

```mermaid
flowchart TD
    A([Advisory PDF]) --> B

    subgraph PLAN ["Bob — Plan mode"]
        B["Extract CVEs<br>(package · version · severity · service)"]
        B --> C["pip-audit scan cross-check<br>(confirmed / advisory-only / scan-only)"]
        C --> D["Find import & call sites<br>per affected package (file:line)"]
        D --> E["Mark auth service:<br>'not affected — no change'"]
        E --> F["Write remediation plan<br>(ordered by severity)"]
    end

    F --> G{{"Human approval"}}
    G --> H

    subgraph AGENT ["Bob — Agent mode"]
        H["Create branch<br>autopilot/advisory-2026-09"]
        H --> PAR

        subgraph PAR ["3 parallel subagents"]
            direction TB
            S1["billing<br>PyYAML CVE-2020-14343"]
            S2["notifications<br>Jinja2 CVE-2024-22195<br>CVE-2024-34064"]
            S3["inventory<br>requests CVE-2023-32681"]
        end

        S1 & S2 & S3 --> LOOP

        subgraph LOOP ["Each subagent — fix loop (max 3 attempts)"]
            direction LR
            L1["Baseline pytest"] --> L2["Bump to safe version"]
            L2 --> L3["Reinstall & run pytest"]
            L3 -- pass --> L4["Record: risk, files, time"]
            L3 -- fail --> L5["Read migration notes<br>Apply minimal code fix"]
            L5 --> L6["Run pytest"]
            L6 -- pass --> L4
            L6 -- fail --> L7["Roll back attempt"]
            L7 -- "attempt < 3" --> L5
            L7 -- "attempt = 3" --> L8[/"Flag for human"/]
        end

        L4 --> AGG["Aggregate results"]
    end

    AGG --> OUT1["docs/REMEDIATION.md"]
    AGG --> OUT2["docs/CHANGELOG.md entry"]
    AGG --> OUT3["docs/PR_DESCRIPTION.md"]
    AGG --> OUT4["remediation/sla-dashboard.html<br>(inline, self-contained)"]
    AGG --> OUT5["remediation/results.json<br>+ one .diff per service"]

    OUT1 & OUT2 & OUT3 & OUT4 & OUT5 --> ST(["Streamlit viewer<br>(public URL)"])
```

## Notes

- **Plan mode** covers playbook steps 1–3 (read advisory, scan, find usages, write plan).  
  No files are changed until the human approves.
- **Agent mode** covers steps 4–9: branch, parallel subagents, aggregate, commit.
- **auth** is scanned but never modified; it appears in step 2 as "not affected — no change".
- The fix loop hard rules: no test deleted, skipped, or weakened; no public API changed without asking; `.venv/` never committed.
- Outputs feed the Streamlit app directly from committed files; the app makes no Bob or network calls.
