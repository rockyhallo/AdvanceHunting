# FOFA Research — Avaya IP Office

**Product:** Avaya IP Office, a unified-communications PBX for small and mid-size businesses. It runs as hardware (IP500 V2), on Linux (Server Edition, Application Server, Select) or as a virtual machine.
**Purpose:** Find IP Office assets (call controller, Web Manager, Web Control, one-X Portal, Voicemail Pro, SIP) for attack-surface management and exposure checks.
**Status:** Fingerprints come from public scanner signatures (Nmap service probes, WhatWeb) and Avaya documentation. FOFA was not reachable from the research environment, so **no hit counts are included**. Run each query on fofa.info to check its precision before you rely on it.

> Use these queries only on assets you own or are authorized to assess.

---

## 1. Fingerprint summary

| # | Component | Signal | Where it shows | Confidence |
|---|-----------|--------|----------------|------------|
| 1 | Core / embedded web server | `Server: IPOffice/<version>` | HTTP response header | **High** (Nmap + WhatWeb) |
| 2 | Core redirect | `301` → `Location: /index.html` + body `Redirect to index.html` | HTTP | High (Nmap) |
| 3 | Core malformed request | `400 Bad Request` + body `Parsing error` | HTTP | High (Nmap) |
| 4 | System Status (SSA web) | `<title>IP Office System Status</title>` (`/ssa/index.html`) | HTML title | High (WhatWeb) |
| 5 | About page | `<title>About IP Office <version></title>` | HTML title | High (WhatWeb) |
| 6 | Voicemail Pro SMTP | `220 <host> IP Office Voicemail Pro ... SMTP MAIL Service ready` | SMTP banner | High (Nmap) |
| 7 | Delta Server (legacy) | `WWW-Authenticate: Basic realm="Delta Server Management Interface"`, `Server: Indy/` | HTTP | Medium (legacy) |
| 8 | Web Manager | path `/WebMgmtEE/WebManagement.html` or `/webmanagement/WebManagement.html`, ports 8443 / 7070 | HTTP | Medium (Avaya docs) |
| 9 | one-X Portal | title containing `one-X Portal` / `one-X® Portal`, ports 8080 / 9443 / 8443 | HTML title | Medium (check on FOFA) |
| 10 | SIP | `User-Agent:` / `Server:` containing `IP Office` | SIP OPTIONS response | Medium (check on FOFA) |

---

## 2. FOFA queries

### 2.1 High-precision (core call controller)

```text
header="Server: IPOffice"
```
```text
banner="Server: IPOffice"
```
```text
server="IPOffice"
```
```text
title="IP Office System Status"
```
```text
title="About IP Office"
```
```text
banner="IP Office Voicemail Pro"
```

### 2.2 Combined "all IP Office" query

```text
header="Server: IPOffice" || title="IP Office System Status" || title="About IP Office" || banner="IP Office Voicemail Pro"
```

### 2.3 Built-in FOFA product tag

FOFA has its own app rules. Try these and keep whichever returns results (the rule name may differ):

```text
app="Avaya-IP-Office"
```
```text
app="AVAYA-IP-Office"
```
```text
product="Avaya-IP-Office"
```

### 2.4 Web Manager / Web Control (admin surfaces)

```text
body="WebMgmtEE" || body="WebManagement.html"
```
```text
(title="IP Office" || body="IP Office Web Manager") && (port="8443" || port="7070" || port="7071")
```

### 2.5 one-X Portal

```text
title="one-X Portal" || title="one-X® Portal" || body="one-X Portal for IP Office"
```
```text
(title="one-X Portal" || body="onexportal") && (port="8080" || port="9443" || port="8443")
```

### 2.6 Voicemail Pro / legacy Delta Server

```text
protocol="smtp" && banner="IP Office Voicemail Pro"
```
```text
banner="Delta Server Management Interface"
```

### 2.7 SIP trunk / endpoint registrar

```text
protocol="sip" && banner="IP Office"
```

### 2.8 Version-specific hunting (exposure to known CVEs)

FOFA reads the version from the `Server: IPOffice/<ver>` header. For example:

```text
header="Server: IPOffice/11.0"
```
```text
header="Server: IPOffice/10."  ||  header="Server: IPOffice/9."
```
```text
header="Server: IPOffice/11.1" && !header="Server: IPOffice/11.1.3"
```

> FOFA matches substrings, not version ranges. Export the `header` field and parse the version yourself to see whether a host is below a fixed release.

### 2.9 Scoping modifiers

Add these to any query above:

| Goal | Modifier |
|------|----------|
| One country | `&& country="US"` |
| Your own address space | `&& ip="203.0.113.0/24"` |
| Your own domains | `&& domain="example.com"` / `&& cert="example.com"` |
| Your own ASN | `&& asn="64500"` |
| Only recent data | `&& after="2026-01-01"` |
| Drop honeypots | `&& is_honeypot=false` |

---

## 3. Ports reference (for port-pivoting)

| Port | Proto | Service |
|------|-------|---------|
| 80 / 443 | TCP | Embedded web (index.html, SSA, file server) |
| 8443 | TCP | Web Manager (IP500 V2) / one-X Portal (older docs) |
| 7070 | TCP | Web Manager on Linux (Server Edition) |
| 7071 | TCP | Web Control / platform view (Linux) |
| 8080 / 9443 | TCP | one-X Portal HTTP / HTTPS |
| 5060 / 5061 | UDP/TCP | SIP / SIP-TLS |
| 25 | TCP | Voicemail Pro SMTP |
| 50791 | TCP | Voicemail Pro service |
| 50794–50805 | UDP/TCP | IP Office Manager config / System Status / Monitor / discovery |
| 1719 / 1720 | UDP/TCP | H.323 RAS / signalling |

Port pivot query (use it **with** a fingerprint, never alone):

```text
header="Server: IPOffice" && (port="50802" || port="50804" || port="50805" || port="7071")
```

---

## 4. Vulnerabilities relevant to internet-exposed IP Office

| CVE | Component | Impact | Fixed in |
|-----|-----------|--------|----------|
| CVE-2024-4196 | Web Control | Unauthenticated RCE through a crafted web request (CVSS 9.8–10) | 11.1.3.1 |
| CVE-2024-4197 | one-X Portal | Unrestricted file upload → RCE (CVSS 9.8–9.9) | 11.1.3.1 |
| CVE-2020-7030 | Web Manager / Web Control (7070/7071) | Base64 credentials in URL query string | 10.1.0.8 / 11.0.4.3 |
| CVE-2019-7005 | Web interface | Unauthenticated information disclosure | See Avaya advisory |
| CVE-2018-15610 | one-X Portal | Improper access control | See Avaya advisory |
| CVE-2018-15614 | one-X Portal | XSS | See Avaya advisory |

**Priority hunt.** Hosts that show Web Control (7071) or one-X Portal **and** report a version below 11.1.3.1 are the most exposed, because of CVE-2024-4196 and CVE-2024-4197:

```text
(header="Server: IPOffice" || title="one-X Portal") && (port="7071" || port="9443" || port="8443")
```

---

## 5. Validation checklist (run after the FOFA export)

1. `curl -skI https://<host>/` → look for `Server: IPOffice/<ver>`.
2. `curl -sk https://<host>/ssa/index.html | grep -i "<title>"` → `IP Office System Status`.
3. `nmap -sV -p 80,443,7070,7071,8443,9443,5060,50802-50805 <host>` → Nmap reports `Avaya IP Office VoIP PBX httpd`.
4. Write down the version and map it to the CVE table above.
5. Remove CDN, proxy and honeypot false positives (one IP with many unrelated banners).

---

## 6. Detection / defensive notes

- IP Office admin surfaces (Web Manager, Web Control, Manager ports 5080x) should **never** be reachable from the internet. Restrict them with firewall rules or ACLs, or put them behind a VPN.
- Watch for unexpected uploads to one-X Portal and for crafted requests to Web Control (7071) on unpatched hosts.
- Upgrade to **11.1.3.1 or later** (R12.x recommended).

---

## 7. Sources

- Nmap `nmap-service-probes`: `Server: IPOffice/` HTTP matches, Voicemail Pro SMTP banner, Delta Server realm. <https://github.com/nmap/nmap/blob/master/nmap-service-probes>
- WhatWeb `avaya-ip-office.rb` plugin: `IP Office System Status`, `About IP Office`, `IPOffice/` server header. <https://github.com/urbanadventurer/WhatWeb/blob/master/plugins/avaya-ip-office.rb>
- Avaya IP Office system ports: <https://documentation.avaya.com/en-us/home/bundle/ip-office/IPOfficeSystemMonitor/IP_Office_ports/IP_Office_system_ports.html>
- Avaya Web Manager login (8443 `/WebMgmtEE/WebManagement.html`): <https://ipofficekb.avaya.com/basic/english/tech/webmanager/logging_in.htm>
- NVD CVE-2024-4196: <https://nvd.nist.gov/vuln/detail/CVE-2024-4196>
- CVE-2024-4197: <https://cvefeed.io/vuln/detail/CVE-2024-4197>
- NVD CVE-2020-7030: <https://nvd.nist.gov/vuln/detail/CVE-2020-7030>
- NVD CVE-2019-7005: <https://nvd.nist.gov/vuln/detail/CVE-2019-7005>
