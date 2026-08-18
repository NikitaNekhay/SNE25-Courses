# Industrial Project — Flexible Platform

> A browser-based **cyber-range scenario constructor**: design a multi-stage attack chain (Initial Access → Execution → Persistence → Lateral Movement → Credential Access) visually, then execute it against live Linux and Windows victims with one click — no hands on the underlying C2 command line.

**Program:** Security and Network Engineering — Innopolis University · SNE25-26
**Client:** Innostage (Cyberpolygon commercial cyber range)
**Performed by:** Nikita Niakhai (M25-SNE-01) in a team of 5 students and 2 mentors.

**Team workspace repo** (backend + lab, frontend as submodule): [`sliver-orchestrator`](https://github.com/lcensies/sliver-orchestrator)

**Frontend repo** : [`sliver-orchestrator-frontend`](https://github.com/NikitaNekhay/flexible-platform)


---

## Context

Innostage runs a **cyberpolygon** — a training range that simulates an enterprise network for Red vs Blue exercises, SOC-analyst training and incident-response drills. Attack chains used to be executed by hand, one operator per scenario. The client wanted to **automate Red Team scenarios**: a mentor clicks a button and a predefined kill chain runs automatically across the target machines.

We delivered a platform where mentors build and launch those chains from a web UI, on top of [BishopFox Sliver](https://github.com/BishopFox/sliver) C2 and the [MITRE ATT&CK Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) library.

---

## My role

Security-tooling engineer on the platform — owning the operator-facing app and its integration with the offensive backend — plus **team lead / client liaison** for an international team of 7.

| Area | Contribution |
|---|---|
| **Offensive-security tooling** | Built the operator web app that drives the whole platform: a React Flow **DAG editor** for composing multi-stage ATT&CK kill chains, an Atomic Red Team browser over 340 atomics, live implant-session views, and an execution viewer that streams step output in real time |
| **Backend / API integration** | Designed the data and state layer against the Go `sliver-orchestrator` **REST `/api/v1` + Server-Sent Events** API (RTK Query) — wiring chain validation, per-step session targeting, output capture and `{{variable}}` substitution end-to-end into the **Sliver C2 (gRPC)** execution flow |
| **Security domain** | Hands-on with **BishopFox Sliver C2**, the **MITRE ATT&CK Atomic Red Team** library, and the kill-chain model (Initial Access → Execution → Persistence → Lateral Movement → Credential Access) against live Linux and Windows victims |
| **Lab / DevOps** | Ran the reproducible multi-VM cyber range — Docker single-host and **Vagrant** multi-hop across a segmented **C2 / pivot / target** network (VirtualBox nested in VMware); operated the **git-submodule** workspace architecture |
| **Team management** | Divided responsibilities and roles across the team, tracked tasks in Notion |
| **Client communication** | Led calls and delivery with the client; bridged foreign team members in English (calls, AI translation and transcription) |

**Stack I worked across:** TypeScript · React 18 · Vite · Redux Toolkit + RTK Query · React Flow · SSE · REST `/api/v1` · Go / Sliver gRPC integration · Docker · Vagrant · VirtualBox · Git submodules · Mantine · i18next · Vitest

The operator app I built (`flexible-platform`) is published as its own repository and consumed as a **git submodule** inside the team workspace repo — see [Links](#links).

---

## System overview

Two integrated components against reproducible lab environments:

| Component | Stack | Role |
|---|---|---|
| **flexible-platform** (frontend) | React 18, TypeScript, Vite, Mantine, Redux Toolkit + RTK Query, React Flow, i18next | Visual scenario editor, atomics browser, live sessions, execution viewer |
| **sliver-orchestrator** (backend) | Go, REST `/api/v1`, SSE, Sliver gRPC, SQLite + GORM | Defines, validates and executes multi-stage chains against live implant sessions |

**Key capabilities:** DAG chain engine with topological validation (rejects cycles and missing dependencies) · output capture and variable substitution (`{{VarName}}`) · conditional gating · per-step session targeting across multiple victims · 340 ATT&CK atomics resolvable by GUID, name or index · five action types (`command`, `atomic`, `upload`, `binary`, `sliver_rpc`) · live SSE streaming · reproducible labs via Docker (single-host) and Vagrant (multi-hop, auto-recovers across reboots).

Full technical documentation — architecture, network segments, attack chains, REST API, CLI and setup — is in **[README_FINAL_CHAIN.md](README_FINAL_CHAIN.md)**.

---

## Stack at a glance

| Layer | Technologies |
|---|---|
| **Frontend** | React 18 · TypeScript · Vite · Mantine · Redux Toolkit · RTK Query · React Flow · i18next · Vitest |
| **Backend** | Go · REST `/api/v1` · Server-Sent Events · Sliver gRPC · SQLite · GORM |
| **Offensive tooling** | BishopFox Sliver C2 · MITRE ATT&CK Atomic Red Team (340 atomics) |
| **Lab & infra** | Docker Compose · Vagrant · VirtualBox · VMware Workstation · Kali Linux · Ubuntu pivot · Windows 10 target |
| **Process** | Git · GitHub (multi-repo + submodule) · Notion · Telegram |

---

## Reports

| Document | Description |
|---|---|
| [Final_Report.pdf](Final_Report.pdf) | Graded academic report (final version) |
| [README_FINAL_CHAIN.md](README_FINAL_CHAIN.md) | Full technical system documentation |

---

## Team

Industrial Project · SNE25-26 · Client: Innostage

Nikita Niakhai · Mark Chausov · Hasib Al Tahsin · Khalid Maina · Victor Adekanye · Albert Avkhadeev · Alisa Evdosenko

---

Back to the [degree overview](../README.md) · [обзор на русском](../README.ru.md)
