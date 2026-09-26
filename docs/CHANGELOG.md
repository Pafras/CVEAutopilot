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
