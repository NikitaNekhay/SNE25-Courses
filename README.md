# Security and Network Engineering Courses

Open-sourced Labs and Reports from my masters degree in Networking, Security and DevOps in Innopolis University 2026-2027.

Here I want to thank our friend Ahmed N. for inspiration to create such a repository.

[Читать на русском](README.ru.md)

---

## Description of the program

The curriculum is based on System and Network Engineering program of the University of Amsterdam — the best Master's program (Computer Science) in the ranking of the Keuzegids Masters 2018.

The program focuses on applied network engineering and computer security concepts in order to master real industry problem-solving skills.

__The language of instruction is English.__

---

## Masters Coursework

> Currently pursuing Masters in Security and Network Engineering

Every course folder has its own README with a lab-by-lab table. All reports are written in Markdown and keep their original screenshots next to them.

| # | Course | Contents |
|---|--------|----------|
| 1 | [Security of Systems and Networks](./1_Security%20of%20Systems%20and%20Networks/README.md) | labs on classical cryptography, UEFI secure boot, OpenSSL, and OpenVPN. Project work on TLS/SSL attack & defense. |
| 2 | [Computer Systems and Networks](./2_Computer%20Systems%20and%20Networks/README.md) | labs on system architecture, IPC, network reconnaissance, systemd/crontab, and SAST tools. Project works on Tor Browser forensics and WireGuard VPN with Samba AD DC. |
| 3 | [Networks Engineering](./3_Networks%20Engineering/README.md) | practical network configuration tasks in GNS3 with virtual MikroTiK and Cisco equipment. Topics include IP, STP, VLAN, LACP, OSPF, QoS, and BGP. |
| 4 | [Unix-Based Internet Applications](./4_Unix-Based%20Internet%20Applications/README.md) | installing and configuring tools for network boot (dnsmasq), name server (BIND), mail agent (Postfix/Dovecot), and web server (Nginx). Project work on a production secure email server. |
| 5 | [DevOps](./5_DevOps/README.md) | labs on Docker, Ansible, Terraform, GitLab CI, Kubernetes and LLMs in pipelines. Project work on a DevSecOps AI GitLab bot. |
| 6 | [Secure Development](./6_Secure%20Development/README.md) | labs on DevSecOps pipelines, secure coding, fuzzing, SIEM, AppArmor/SELinux, and penetration testing. |
| 7 | [Computer Forensics and Incident Response](./7_Computer%20Forensics%20and%20Incident%20Response/README.md) | labs on data acquisition, file system forensics, sandboxing and malware analysis, and SIEM deployment. Project work on secure DevOps in cyber forensics. |
| 8 | [Offensive Technologies](./8_Offensive%20Technologies/README.md) | labs on binary disassembly/exploitation, software vulnerabilities and malware analysis. Project work on an IoT deception honeypot network. |
| 9 | [Financial Management in Digital Products](./9_Financial%20Management%20in%20Digital%20Products/README.md) | unit economics, financial statements, financial ratios and a digital habits case. |
| 10 | [Industrial Project — Flexible Platform](./10_Industrial%20Project/README.md) | team-built cyber-range scenario constructor for client Innostage: visual multi-stage attack-chain editor on Sliver C2 + MITRE ATT&CK Atomic Red Team. My role — frontend and team lead. |

---

## Skills acquired

<https://new.innopolis.university/en/masters/securityandnetworkengineering/>

- Debugging, disassembling, tracing and interpreting system call commands
- Ensuring availability, integrity and confidentiality at the network level
- Monitoring and analysis of network traffic and network devices
- Working with various types of vulnerabilities in the field of memory exploitation and web applications
- Working on code security analysis and writing appropriate exploits
- Working with tools for finding vulnerabilities and exploiting software (scanners, fuzzers, MSF and others)
- Secure IT infrastructure creation, support and monitoring
- Predicting and searching for cyber threats, detecting and deterring computer attacks development, integration and monitoring of software development life cycle systems (DevOps)

<https://apply.innopolis.university/masters/securityandnetworkengineering/>

- Install, configure and maintain enterprise-level IT infrastructure in a secure manner
- Install, configure and maintain virtualized/containerized infrastructure at large scale
- Work with continuous integration and continuous deployment technologies
- Work with backup, logging, performance monitoring and disaster recovery systems
- Collect and extract data from various sources
- Classify the main types of threats, vulnerabilities and attackers
- Test systems for vulnerabilities
- Work with the main methods and means of technical information protection in operating systems, networks and application software
- Collect and analyse digital evidence, investigate computer incidents, predict and hunt cyber threats, detect and contain computer attacks

---

## Tools, technologies and techniques

Everything below appears in the labs and projects of this repository. Grouped by
the domains of the speciality rather than by course, since most of them recur
across several courses.

### Networking and routing

| | |
|---|---|
| **Protocols** | IPv4 · IPv6 · TCP · UDP · ICMP · ARP · OSPF (multi-area) · BGP / eBGP · STP · VLAN (802.1Q) · LACP · DHCP · DNS · NAT / masquerading · QoS · SNMP |
| **Platforms** | GNS3 · MikroTik RouterOS / CHR · Cisco 7200 · Cisco IOSvL2 · pfSense |
| **Analysis** | Wireshark · tshark · tcpdump · nmap · ncat · netcat · socat · powercat · curl · Netplan · iproute2 |
| **Techniques** | Subnetting and addressing plans · L2 bridging · link redundancy and fault tolerance · spanning-tree convergence · route redistribution and static routes · traffic shaping and prioritisation · packet capture and artifact extraction |

### Virtualization, containers and orchestration

| | |
|---|---|
| **Hypervisors** | QEMU/KVM (Linux KVM) · libvirt · virt-manager · VirtualBox · VMware · Hyper-V · Citrix Hypervisor · XenServer |
| **Containers** | Docker Engine · Dockerfile · Docker Compose · Docker Hub · Docker Swarm · containerd |
| **Orchestration** | Kubernetes · minikube · k3s · Helm · pods, deployments, services and manifests |
| **Techniques** | Multi-container environments · bind mounts and volumes · image tagging by commit SHA · L7 load balancing with weighted round-robin · isolated and segmented lab networks |

### Unix internet services

| | |
|---|---|
| **Boot and naming** | PXE · TFTP · dnsmasq · BIND9 · forward and reverse zones · primary / secondary / delegated name servers |
| **Mail** | Postfix (MTA) · Dovecot (IMAP) · SMTP · IMAP · POP3 · SASL · STARTTLS · virtual mailboxes · SpamAssassin · SPF · DKIM · DMARC |
| **Web** | nginx · Apache · HAProxy · virtual hosts · building a webserver from source · GeoIP · Let's Encrypt · certbot |
| **Techniques** | Network installation of an OS · MBR and GPT partitioning · zone delegation · mail authentication alignment verified against external providers · spam classification |

### Cryptography, PKI and VPN

| | |
|---|---|
| **Tools** | OpenSSL · easy-rsa · OpenVPN · WireGuard · IPsec · sslyze · testssl.sh · mitmproxy |
| **Standards** | RSA · X.509 · TLS 1.2 / 1.3 · HTTPS · HSTS · UEFI Secure Boot (PK / KEK / db / dbx) |
| **Techniques** | Key generation, encryption, decryption and signature verification · certificate authority and client certificate issuance · certificate pinning · MITM demonstration in an isolated lab · secure boot chain and kernel signing · classical ciphers (Vigenère, Nihilist) and cryptanalysis |

### CI/CD, infrastructure as code and automation

| | |
|---|---|
| **Pipelines** | GitLab CE (self-hosted) · GitLab Runner · GitLab CI · GitHub Actions · Jenkins · Git · GitOps |
| **Configuration management** | Ansible · Ansible AWX · Terraform · Puppet · Chef · SaltStack |
| **Techniques** | Multi-stage pipelines with enforced security gates · runner registration and shell executors · masked CI variables and secret managers · artifact publishing · automated deployment to remote hosts · LLM-assisted code review, failure triage and merge-request generation (OpenRouter / OpenAI) |

### Application and code security

| | |
|---|---|
| **SAST / SCA / secrets** | Semgrep · Trivy · Gitleaks · SonarQube · Snyk · Deepsource · Bandit · cppcheck |
| **Dynamic analysis** | AFL++ · afl-fuzz · Valgrind · AddressSanitizer · Burp Suite · sqlmap · dirb |
| **Frameworks** | CWE Top 25 · OWASP Top 10 · CVE · CVSS |
| **Techniques** | Vulnerability classification and remediation · crash triage from fuzzing corpora · compiler hardening (`-fstack-protector-strong`, `_FORTIFY_SOURCE`, `-Wformat=2`) · dependency upgrade and lockfile regeneration · release blocking on policy violation |

### Monitoring, SIEM and threat detection

| | |
|---|---|
| **Platforms** | Wazuh (manager / indexer / dashboard) · OpenSearch · Kibana · Filebeat · Grafana · Prometheus · Zabbix · Splunk |
| **Detection** | Snort · Suricata · YARA · osquery · Sigma · MITRE ATT&CK |
| **Techniques** | Agent enrolment on Linux and Windows · custom detection rules and decoders · log rotation · alert correlation and behaviour classification · dashboard-driven investigation |

### Offensive security

| | |
|---|---|
| **Reverse engineering** | GDB · Ghidra · radare2 · IDA · objdump · readelf · strace · ltrace · Immunity Debugger |
| **Exploitation** | Metasploit Framework · Hydra · Hashcat · Nessus · smbclient |
| **Concepts** | ASLR · NX · stack canaries · PIE · GOT and PLT · ROP · shellcode · NOP sleds |
| **Techniques** | Stripped-binary analysis · breakpoint mechanics · local stack buffer overflow to root shell · pivoting through a compromised host · privilege escalation · full engagement against a target machine |

### Digital forensics and malware analysis

| | |
|---|---|
| **Acquisition** | CAINE · dcfldd · dd · Guymager · Disk Image Mounter |
| **Analysis** | Autopsy · The Sleuth Kit · PhotoRec · foremost · binwalk · Volatility · log2timeline / plaso · mactime · RegRipper |
| **Sandboxing** | CAPEv2 · Cuckoo · PE analysis |
| **Techniques** | Forensically sound imaging · MD5 / SHA-256 pre- and post-acquisition hashing · write blocking and evidence integrity · file system and platform identification · timeline creation · Windows artefact analysis · static and dynamic malware analysis · reporting and chain of custody |

### Hardening and access control

| | |
|---|---|
| **Mandatory access control** | AppArmor · SELinux · profiles and policy modes |
| **Host hardening** | auditd · fail2ban · ufw · iptables · nftables · GRUB kernel parameters · CIS Benchmarks |
| **System administration** | systemd units · crontab · journalctl · sudo policy · SSH key authentication and hardening |
| **Identity** | Kerberos · LDAP · Samba Active Directory DC · SSSD |

### Deception and honeypots

Cowrie (SSH / Telnet) · Mosquitto MQTT broker · decoy service stubs · fake device fingerprints · intentional weak credentials · attacker engagement logging

### Languages, formats and data stores

| | |
|---|---|
| **Languages** | C · Python · Bash · PowerShell · JavaScript / Node.js · PHP · SQL |
| **Formats** | YAML · JSON · Makefile |
| **Data stores** | MySQL · MariaDB · PostgreSQL · MongoDB · Redis · SQLite · CassandraDB |
| **Distributed storage** | GlusterFS · HDFS · CephFS · Hadoop · DRBD |

Reference for the official programme tool list:
<https://apply.innopolis.university/masters/securityandnetworkengineering/>

---

## Further career paths

**DevOps Engineer**
Automates development, testing and deployment processes, sets up CI/CD pipelines, manages infrastructure as code (IaC), ensures monitoring and uninterrupted system operation.

**DevSecOps Engineer**
Integrates security practices into DevOps processes, automates security checks in CI/CD pipelines, ensures infrastructure compliance with security requirements at every stage of development.

**Software Security Engineer**
Audits code, tests applications for vulnerabilities, develops and implements protection mechanisms, ensures security across the whole software development lifecycle.

**Penetration Testing Specialist**
Conducts controlled attacks on systems to identify vulnerabilities, models the behaviour of attackers, prepares reports and recommendations for strengthening defenses.

**Computer Systems and Networks Security Engineer**
Designs and implements network infrastructure protection systems, configures firewalls, intrusion detection and prevention systems, ensures secure data transmission.

**Systems Engineer**
Designs, deploys and maintains IT infrastructure, ensures integration of various systems, optimizes performance and fault tolerance of complex solutions.

**Systems Analyst**
Analyses business requirements, designs the architecture of secure IT solutions.

**System Administrator**
Ensures the operability of servers and network equipment, manages access rights, performs backups, maintains IT infrastructure in accordance with security policies.

---

## Materials for the labs (images, zip files)

Link to private folder: https://drive.google.com/drive/u/3/folders/1Ne7hnJypXBD23rPkegLQe4ZmAoveMpMc

---

## License

See [LICENSE](LICENSE).
