# ThreatFlow: SOC Alert Automation & Threat Analysis

An end-to-end SOC (Security Operations Center) automation pipeline that detects file-based threats on a Linux endpoint, enriches them with threat intelligence, and delivers real-time alerts to Email and Discord — with zero manual steps.

Built as a hands-on learning project to understand how a real SOC detection → enrichment → notification pipeline works, using **Wazuh** (SIEM/XDR), **n8n** (workflow automation), and **VirusTotal** (threat intelligence).

---

## Architecture

```
Kali Linux (Agent)
      │  file added/modified in /root
      ▼
Wazuh Manager  ──(File Integrity Monitoring, rules 550/554)──▶  Alert generated
      │
      ▼  (custom integration script, JSON over HTTPS)
n8n Webhook (via ngrok tunnel)
      │
      ▼
Code Node → extracts md5 / sha1 / sha256 from the alert
      │
      ▼
HTTP Request → queries VirusTotal API v3 with the sha256 hash
      │
      ▼
Code Node → summarizes VirusTotal's response (malicious/suspicious counts, status)
      │
      ├──▶ HTML Node → Gmail (formatted "File Threat Summary" email)
      │
      └──▶ Discord Webhook (chat alert)
```

---

## Why this project

As a final-year Cybersecurity student preparing for an L1 SOC Analyst role, I wanted hands-on experience with the tools and workflows a real SOC analyst uses daily: a SIEM (Wazuh), threat intelligence enrichment (VirusTotal), and alert automation (n8n) — rather than just studying the concepts in theory.

---

## Components

| Component | Role |
|---|---|
| **Wazuh Manager** (Ubuntu 22.04 VM) | SIEM — collects agent data, applies detection rules, generates alerts |
| **Wazuh Agent** (Kali Linux VM) | Monitored endpoint — File Integrity Monitoring (FIM) on `/root` |
| **n8n** | Workflow automation — receives, parses, enriches, and routes alerts |
| **ngrok** | Exposes local n8n webhook to a public HTTPS URL (free tier) |
| **VirusTotal API** | Threat intelligence — checks file hash reputation across 60+ AV engines |
| **Gmail (SMTP)** | Email notification channel |
| **Discord Webhook** | Chat notification channel |

---

## How it works

1. **Detection** — Wazuh's File Integrity Monitoring watches `/root` on the Kali agent in real time. When a file is added or modified, Wazuh's manager matches it against rule 550 (checksum changed) or 554 (file added) and generates a JSON alert.
2. **Forwarding** — A custom Wazuh integration script (`custom-n8n`) forwards the raw alert JSON to an n8n webhook, reachable via an ngrok tunnel.
3. **Parsing** — An n8n Code node extracts the file's md5, sha1, and sha256 hashes, along with the file path and agent name.
4. **Enrichment** — The sha256 hash is sent to the VirusTotal API, which returns how many antivirus engines flag the file as malicious.
5. **Summarization** — A second Code node condenses VirusTotal's large response into a short summary (malicious/suspicious/harmless counts, threat label, reputation, and a computed status).
6. **Notification** — The summary is formatted into an HTML report and emailed via Gmail, and a short alert is also posted to a Discord channel — both running in parallel from the same data.

---

## Test case: EICAR

The project is tested using the [EICAR test file](https://www.eicar.org/), an industry-standard, harmless file that every antivirus engine is designed to detect as "malware" — used specifically to safely test detection pipelines without handling real malicious code.

**Result:** VirusTotal flagged the EICAR file as malicious by 66 of 69 engines, and the alert was delivered via both Email and Discord within seconds of the file being downloaded.

---

## Screenshots

| | |
|---|---|
| Wazuh Agent (Active) | ![Agent Active](screenshots/1-agent-active.png) |
| FIM Alert (EICAR detected) | ![FIM Alert](screenshots/2-fim-alert.png) |
| n8n Workflow | ![n8n Workflow](screenshots/3-n8n-workflow.png) |
| Successful Execution | ![Execution Success](screenshots/4-execution-success.png) |
| Email Alert | ![Email Alert](screenshots/5-email-alert.png) |
| Discord Alert | ![Discord Alert](screenshots/6-discord-alert.png) |

---

## Key learnings and design decisions

- **Wazuh's integration scripts come in pairs** — a shell wrapper and a matching Python script with the same name. A default example script (`shuffle`) was adapted, but it reformatted alerts into a different platform's message shape, so a small custom Python script was written to forward the raw alert JSON unmodified instead.
- **n8n's Test webhook only accepts one call** and then deactivates, unsuitable for a live pipeline that must always listen. Switched to a **Production** webhook (published workflow) so alerts are received automatically, at any time, without manual intervention.
- **VirusTotal's free tier is rate-limited** (4 requests/minute) — acceptable for a learning project, but a real SOC deployment would need a paid tier or a caching layer to handle a higher alert volume.
- **ngrok's free tier URL is temporary** and not guaranteed to persist across restarts — fine for a lab environment, but a production setup would use a fixed internal address or a paid static domain.

---

## Limitations (by design, for a learning project)

- Runs in a local VirtualBox lab, not a cloud-hosted or production environment.
- Uses a single test rule set (file-integrity monitoring) rather than a full detection rule library.
- VirusTotal lookups are hash-based only (no dynamic/sandbox analysis).
- Notification channels (Gmail, Discord) are personal accounts, not a SOC ticketing/SOAR platform.

---

## Tech stack

`Wazuh` `n8n` `VirusTotal API` `JavaScript` `JSON` `Python` `Kali Linux` `Ubuntu Server` `VirtualBox` `ngrok`
