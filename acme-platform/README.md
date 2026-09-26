# acme-platform

Sample monorepo used as the target for CVE Autopilot. Three services, each with outdated,
vulnerable dependencies (see `security/advisory-2026-09.md`).

Run a service's tests:

    cd services/billing && pip install -r requirements.txt pytest && pytest -q
