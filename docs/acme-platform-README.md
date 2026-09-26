# acme-platform

Sample monorepo used as the target for CVE Autopilot. Five services: `billing`, `notifications` and `inventory` have outdated,
vulnerable dependencies (see `docs/advisory-2026-09.md`); `auth` uses only the standard library
and must stay untouched. `web-gateway` is a Node.js service with known-vulnerable npm dependencies.

Run a service's tests from the repository root:

    cd acme-platform/services/billing && pip install -r requirements.txt pytest && pytest -q

Run the Node.js gateway service (Node, requires Node.js ≥ 18):

    cd acme-platform/services/web-gateway && npm ci --ignore-scripts && npm test
