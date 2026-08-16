#!/usr/bin/env python3
"""Parse Trivy image scan JSON report and enforce container security gate.
Policy: fail on CRITICAL vulnerabilities, warn on HIGH.
"""
import json, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

critical = 0
high = 0
medium = 0
low = 0
all_vulns = []

for result in data.get("Results", []):
    target = result.get("Target", "unknown")
    for vuln in result.get("Vulnerabilities", []):
        sev = vuln.get("Severity", "UNKNOWN")
        vid = vuln.get("VulnerabilityID", "?")
        pkg = vuln.get("PkgName", "?")
        installed = vuln.get("InstalledVersion", "?")
        fixed = vuln.get("FixedVersion", "n/a")
        title = vuln.get("Title", "")[:80]
        all_vulns.append((sev, vid, pkg, installed, fixed, target, title))
        if sev == "CRITICAL":
            critical += 1
        elif sev == "HIGH":
            high += 1
        elif sev == "MEDIUM":
            medium += 1
        else:
            low += 1

# Print top findings (limit output)
for sev, vid, pkg, installed, fixed, target, title in sorted(all_vulns)[:30]:
    print(f"  [{sev}] {vid} {pkg}@{installed} (fix: {fixed}) [{target}]")

if len(all_vulns) > 30:
    print(f"  ... and {len(all_vulns) - 30} more")

print(f"\nImage Scan Summary: {critical} CRITICAL, {high} HIGH, {medium} MEDIUM, {low} LOW")
print(f"Total vulnerabilities: {len(all_vulns)}")

if critical > 0:
    print("IMAGE GATE FAILED: Critical vulnerabilities found!")
    sys.exit(1)
else:
    print("Image security gate passed.")
    sys.exit(0)
