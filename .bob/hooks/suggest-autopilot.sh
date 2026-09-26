#!/usr/bin/env bash
# PostToolUse hook: suggest CVE Autopilot when a dependency or advisory file changes.
# Reads the Bob hook JSON from stdin, extracts the edited file path, and prints a
# one-line advisory when the path matches requirements.txt, package.json, or */security/*.pdf.
# Always exits 0 (PostToolUse output is added to model context; it cannot block).
# No network calls.

set -euo pipefail

raw=$(cat)

# Extract tool_input.path using pure bash + sed (no jq required).
# Bob write tools all carry the target path in tool_input.path.
path=$(printf '%s' "$raw" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('path', ''))
" 2>/dev/null || true)

if [[ -z "$path" ]]; then
    exit 0
fi

# Match: ends with requirements.txt, ends with package.json, or matches */security/*.pdf
if [[ "$path" == */requirements.txt || "$path" == *requirements.txt ]] || \
   [[ "$path" == */package.json    || "$path" == *package.json    ]] || \
   [[ "$path" == */security/*.pdf                                  ]]; then
    echo "Dependency or advisory changed: $path. Run CVE Autopilot (pip-audit / npm audit) before merging."
fi

exit 0
