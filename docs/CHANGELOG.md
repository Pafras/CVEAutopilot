# Changelog

## [Unreleased] — autopilot/advisory-2026-09

### Security

- **billing** — Bump `PyYAML` 5.3.1 → 6.0.3 (CVE-2020-14343, CRITICAL 9.8).
  Arbitrary code execution via untrusted YAML. Add `Loader=yaml.SafeLoader` to
  `load_invoice_rules()` to satisfy the now-mandatory Loader argument.

- **notifications** — Bump `Jinja2` 2.11.3 → 3.1.6 (CVE-2024-22195, CVE-2024-34064,
  CVE-2025-27516, CVE-2024-56326, MEDIUM). XSS via `xmlattr` filter accepting
  keys with spaces/special characters. Also bump `MarkupSafe` 2.0.1 → 3.0.3.
  Update `renderer.py` to import `Markup`/`escape` from `markupsafe` (removed
  from `jinja2` namespace in 3.x).

- **inventory** — Bump `requests` 2.25.1 → 2.32.5 (CVE-2023-32681, CVE-2024-35195,
  CVE-2024-47081, CVE-2026-25645, MEDIUM). Proxy-Authorization header leak on
  HTTPS redirects; TLS verify persistence; netrc credential leak; zip path
  predictability. Safe bump — no code changes.

## [Unreleased] — autopilot/scan-2026-09

### Security

- **web-gateway** — Bump `axios` 0.21.1 → 0.34.0 (24 GHSAs, highest CVSS 8.6 HIGH).
  Fixes ReDoS, prototype-pollution, SSRF, header injection, and credential-leakage
  vulnerabilities. Safe bump — no code changes. All 9 tests pass. `npm audit` clean.

- **web-gateway** — Bump `lodash` 4.17.20 → 4.18.1 (5 GHSAs, highest CVSS 8.1 HIGH).
  Fixes code injection via `_.template` import keys, command injection, ReDoS, and
  prototype-pollution vulnerabilities. Safe bump — no code changes. All 9 tests pass.

### Escalated (awaiting human decision)

- **reports** — `PyYAML==5.3.1` (CVE-2020-14343, CRITICAL) remains at vulnerable version.
  Safety-brake triggered: PyYAML 6.0 `FullLoader` rejects the `!!python/object` tag
  used in the test fixture; bumping would only pass with `yaml.UnsafeLoader`, which is
  forbidden. Recommended fix: migrate report specs to plain-dict YAML and use `yaml.safe_load`.

- **inventory** — `requests==2.32.5` / `urllib3==2.6.3` (CVE-2026-25645, CVE-2026-44432,
  CVE-2026-44431, MEDIUM) remain unchanged. Fix versions require Python ≥ 3.10;
  service runs Python 3.9. Pre-existing blocker re-confirmed by live scan.
  Recommended fix: upgrade inventory runtime to Python 3.10+.
