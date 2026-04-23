![Security](https://img.shields.io/badge/Security-Hardened-success)
![Status](https://img.shields.io/badge/Audit-Passed-blue)

# Security Policy

This document outlines the security procedures for the **Pi-SocialMedia-Poster**. We take the security of your social media credentials and your hardware seriously.

---

## 🛡️ Vulnerability Reporting

If you discover a security vulnerability within this project, please **do not** open a public GitHub issue. Publicly disclosing a vulnerability can put other users' hardware and social media accounts at risk.

### Reporting Process
1. **Private Disclosure:** Please report vulnerabilities via [GitHub Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-fixing-security-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository.
2. **Response Time:** You can expect an acknowledgment of your report within **48 hours**.
3. **Coordinated Disclosure:** We will work with you to fix the issue and release a patch. We request that you wait until a patch is released before discussing the vulnerability publicly.

---

## 🔒 System Hardening (Raspberry Pi 5)

Because this application handles sensitive API tokens and is often exposed to the web via Tailscale or port forwarding, we recommend the following hardening steps for your Pi.

### 1. Account Security
* **Retire the 'pi' User:** Never use the default `pi` username. Create a custom user and remove the default account.
* **Sudo Protection:** Ensure `sudo` requires a password.
  ~~~bash
  # Remove the 'nopasswd' config if it exists
  sudo rm /etc/sudoers.d/010_pi-nopasswd
  ~~~

### 2. Network Defense
* **UFW (Uncomplicated Firewall):** Strictly limit incoming traffic.
  ~~~bash
  sudo ufw default deny incoming
  sudo ufw allow ssh
  sudo ufw allow in on tailscale0 to any port 8080
  sudo ufw enable
  ~~~
* **Fail2Ban:** Protect against brute-force attempts on SSH or the dashboard.
  ~~~bash
  sudo apt install fail2ban -y
  ~~~

### 3. Application Isolation
* **Environment Files:** Your `.env` file contains sensitive API keys. Always ensure its permissions are locked down:
  ~~~bash
  chmod 600 .env
  ~~~
* **Database Location:** If using the Pironman 5 Max, keep your database on the secondary data drive (`/mnt/data/`) to prevent OS corruption if the database grows rapidly during a flood event.

---

## 🛠️ Safe Maintenance

### Preventing "Flood" Loops
Security also involves system stability. To prevent the application from self-denial-of-service (DoS) via database flooding:
1. **Never delete a post** directly from the database while the service is active.
2. Use the **[Flood Post Remediation Guide](flood_remediation.md)** if you notice high CPU usage.
3. Keep **Dry Run** enabled (`DRY_RUN=true`) when testing new features or large batches.

---

## 📦 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v1.1.x  | ✅ YES             |
| v1.0.x  | ❌ NO (Upgrade)    |
| < v1.0  | ❌ NO              |

---

[⬅️ Back to Main README](README.md)
