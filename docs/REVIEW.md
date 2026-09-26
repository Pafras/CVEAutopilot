# Security Review — advisory-2026-09

Branch: `autopilot/advisory-2026-09` vs `main`  
Reviewer: IBM Bob (Agent mode)
Date: 2026-09-26

---

## Check Results

| # | Check | Result |
|---|-------|--------|
| 1 | CVE-2020-14343 (PyYAML): fixed at or above 5.4 — bumped to 6.0.3 | PASS |
| 2 | CVE-2024-22195 (Jinja2): fixed at or above 3.1.4 — bumped to 3.1.6 | PASS |
| 3 | CVE-2024-34064 (Jinja2): fixed at or above 3.1.4 — bumped to 3.1.6 | PASS |
| 4 | CVE-2023-32681 (requests): fixed at or above 2.31.0 — bumped to 2.32.5 | PASS |
| 5 | No test files under acme-platform/services/*/tests were changed | PASS |
| 6 | Unaffected auth service was not changed | PASS |
| 7 | Code fixes are minimal and keep behaviour — billing: added `Loader=yaml.SafeLoader` to existing `yaml.load` call only; notifications: moved `Markup`/`escape` imports from `jinja2` to `markupsafe` only; inventory: requirements-only bump, no code change | PASS |

---

## Notes

- The advisory (docs/advisory-2026-09.md) lists 4 CVEs across 3 packages. The PR description enumerates 9 CVEs (1 Critical, 8 Medium) by including additional CVEs in the same version ranges fixed by each bump; all fall within the fixed versions confirmed above.
- `yaml.load(f, Loader=yaml.SafeLoader)` is the correct minimal fix for CVE-2020-14343 (PyYAML 6.x makes the `Loader` argument mandatory).
- Importing `Markup`/`escape` from `markupsafe` instead of `jinja2` is the only required code change for the Jinja2 3.x migration; `autoescape=True` on the Environment was already present and is unchanged.
- No public function signatures were altered in any service.
