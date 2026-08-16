# Team project “TLS/SSL Sec Attack/Defense (Team Project)”

Name of report: Final_Project_TLS_SSL_Team
Course: Security of Systems and Networks
Performed by Nikita Niakhai and MGBEMENA MMESOMACHUKWU CHUKWUEMEKA (MESO)

---

README.MD

- **Prepare lab:** Create an isolated VM network with client, server, and attacker/proxy machines.
- **Install tools:** Install and verify `sslyze`, `testssl.sh`, `openssl`, `nmap`, `wireshark/tshark`, `mitmproxy`, and `burpsuite`.
- **Generate certs & server:** Create a test CA and certif icates, then configure HTTPS on your server (nginx/apache).
- **Baseline scans:** Run `sslyze`, `testssl.sh`, and `nmap --script ssl-enum-ciphers` against the server and save outputs.
- **Passive capture:** Capture TLS handshakes with `tshark`/Wireshark and save annotated pcap files.
- **Controlled MITM demo:** In the isolated lab use `mitmproxy` to present a test cert and record the client’s behavior.
- **Enable defenses & retest:** Enable TLS 1.3, add HSTS, implement client pinning, then repeat scans and captures.
- **Document deliverables:** Produce a short PDF report, 6–8 slide deck, raw logs, and a 2–4 minute recorded demo showing before/after evidence.

- `openssl`- is installed by default on KALI
- `nginx`- is installed via sudo apt install
- `bettercup` - is installed via sudo apt install
- `Burp Suite` -
- `ssl` -
- `testssl` - is installed via sudo apt install
- `sslyze` - is installed via sudo apt install

`pinned_client.py`

1. Open a TLS connection to `HOST:PORT` without verifying the certificate.
2. Download the server's X.509 certificate in DER format.
3. Use OpenSSL to extract the public key and compute its SHA256 hash.
4. If OpenSSL fails, fall back to hashing the entire certificate DER.
5. Compare the observed hash to `EXPECTED_HEX`; abort on mismatch (possible MITM).
6. If the pin matches, fetch the HTTPS page and print the first 1024 bytes.

`pinned_client_mitm.py`

1. Issues HTTP CONNECT to proxy, then negotiates TLS through that proxy to target.
2. Retrieves the server's DER certificate from the proxied TLS handshake.
3. Uses OpenSSL to extract public-key DER and compute SHA256 fingerprint.
4. Fallback: if OpenSSL unavailable, hash whole certificate DER instead.
5. Compares observed hash to `EXPECTED_HEX`; mismatch indicates intercepting proxy or MITM.
6. If pin matches, performs HTTPS GET via proxy or direct and prints first 1024 bytes.

TLS/SSL Defenses provided vs MITM:

- PFS (Perfect Forward Security) prevents long-term key exposure from decrypting past sessions. It ensures (ephemeral enc. key inside alghorithm like Defie Helman) that past session of TLS are not decrypted even if a server’s private key is stolen.
- AEAD (Authentication Encryption with Associated Data) provides combined confidentiality+integrity preventing trivial modification. Binds processes of encryption and authentication.
- Shorter, simpler handshake reduces attack surface.

HSTS:

- Site is accessed only for defined a time window
- Browser refuses any HTTP-to-HTTPS downgrade — it will not even allow a click-through for an insecure redirect.
- Does **not** stop a MITM who can present a valid certificate the browser trusts (unless pinning is used).

Nik 1,3, (last slide HSTS) ,6

Meso 2,4,5
