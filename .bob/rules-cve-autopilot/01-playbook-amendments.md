# CVE Autopilot — playbook amendments (after dry run T1)

These rules refine the playbook in the mode instructions. Where they differ, these win.

1. **Pick exact target versions in the plan (step 3).** For each package, run
   `pip3 index versions <package>` and choose the highest published release that is at or above the
   advisory's fixed version, preferring the newest major. Write the exact `package==version` in the plan,
   so the human approves the concrete target. Do not ask again at bump time.
2. **Always show the break before the fix (step 5c).** After bumping the pin, reinstall and run
   `pytest -q` BEFORE changing any code, even if you already know the fix. Show the failing output
   (error type and message). Only then apply the code fix and retest. If the bump passes on its own,
   record risk = "safe bump" and make no code change.
3. **Python interpreter:** use `python3` unless the service has a `.python-version` file.
4. **Per-service result:** whether a subagent or you run a service, end each service with the step 5e
   report (files changed, before/after pytest summary, risk, fixed-at time from `date -u`).
