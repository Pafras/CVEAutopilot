# CVE Autopilot

**Security advisory in. Tested fix out.** Built with IBM Bob 2.0 for the
[lablab.ai IBM Bob 2.0 Hackathon](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon).

CVE Autopilot turns a security advisory into a tested, ready-to-merge fix. IBM Bob 2.0 reads the
advisory, finds every affected service, and runs parallel subagents that upgrade dependencies,
repair breaking changes and verify with tests.

## Repo layout
- `acme-platform/` — sample monorepo with real vulnerable dependencies (the remediation target)
- `acme-platform/security/advisory-2026-09.md` — the security scan report Bob reads
- `bob_sessions/` — exported IBM Bob task session reports (required for submission)

## Why a plain version bump is not enough
| Service | CVE | Plain bump | After Autopilot |
|---|---|---|---|
| billing | PyYAML CVE-2020-14343 | ❌ `TypeError` | ✅ |
| notifications | Jinja2 CVE-2024-22195 / CVE-2024-34064 | ❌ `ImportError` | ✅ |
| inventory | requests CVE-2023-32681 | ✅ | ✅ |

## Security
Based on the [IBM hackathon template](https://github.com/watsonxhackathon/ibm-hackathon-template):
`.gitignore` and `.bobignore` keep credentials out of git and Bob session logs.
Copy `.env.example` to `.env` for any keys, and read [SECURITY.MD](SECURITY.MD) before committing.

## License
MIT
