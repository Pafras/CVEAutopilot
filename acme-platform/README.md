# acme-platform

Sample monorepo used as the target for CVE Autopilot. Four services: `billing`, `notifications` and `inventory` have outdated,
vulnerable dependencies (see `security/advisory-2026-09.md`); `auth` uses only the standard library
and must stay untouched.

Run a service's tests:

    cd services/billing && pip install -r requirements.txt pytest && pytest -q
