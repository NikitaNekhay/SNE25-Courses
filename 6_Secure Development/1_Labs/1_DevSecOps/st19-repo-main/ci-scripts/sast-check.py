#!/usr/bin/env python3
"""Parse Semgrep JSON report and enforce quality gate.
Gate policy: fail if any ERROR-severity finding exists outside known-accepted list.
"""
import json, sys

# Findings accepted after review (rule_id + file pattern)
ACCEPTED = {
    "javascript.browser.security.insufficient-postmessage-origin-validation.insufficient-postmessage-origin-validation",
}

with open(sys.argv[1]) as f:
    data = json.load(f)

results = data.get("results", [])
blocking = []
accepted = []

for r in results:
    sev = r.get("extra", {}).get("severity", "?")
    path = r.get("path", "")
    line = r.get("start", {}).get("line", "?")
    rule = r.get("check_id", "")
    msg = r.get("extra", {}).get("message", "")[:100]
    print(f"  [{sev}] {path}:{line} - {msg}")
    if sev.upper() == "ERROR" and rule not in ACCEPTED:
        blocking.append(r)
    elif rule in ACCEPTED:
        accepted.append(r)

print(f"\nTotal findings: {len(results)}")
print(f"Blocking (ERROR, not accepted): {len(blocking)}")
print(f"Accepted/waived: {len(accepted)}")

if len(blocking) > 0:
    print("SAST GATE FAILED!")
    sys.exit(1)
else:
    print("SAST gate passed.")
    sys.exit(0)
