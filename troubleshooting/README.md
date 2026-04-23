![Status](https://img.shields.io/badge/Status-Troubleshooting-orange)
![Platforms](https://img.shields.io/badge/Platforms-Mastodon%20%7C%20Bluesky%20%7C%20Telegram%20%7C%20LinkedIn%20%7C%20Facebook-blue)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-green)

---

# 🛠 General Troubleshooting

This guide covers common issues and maintenance procedures for the `Pi-SocialMedia-Poster`. If you are dealing with a critical database backup or infinite posting loop, please see the specialized remediation guide below.

> 🚨 **Critical Database Issues?** If your database is flooding with events or the script is stuck in a retry loop, refer immediately to the [Flood Remediation: Overview](flood_remediation.md).

---

## Table of Contents
- [Service Management](#service-management)
- [Log Inspection](#log-inspection)
- [Common API Failures](#common-api-failures)
- [Database Maintenance](#database-maintenance)
- [Hardware & Cooling](#hardware--cooling)
- [Automated Testing](#automated-testing)
- [Platform Specific Remediation](#platform-specific-remediation)

---

## Service Management

If the web dashboard is not responding or posts aren't being dispatched, check the status of the background service.

~~~bash
# Check if the service is running
sudo systemctl status social-poster

# Restart the service (required after .env changes)
sudo systemctl restart social-poster

# Stop the service for maintenance
sudo systemctl stop social-poster
~~~

---

## Log Inspection

The application logs provide specific error codes from the various social media APIs.

~~~bash
# View recent application logs
journalctl -u social-poster -n 50 --no-pager

# Follow logs in real-time to debug a post dispatch
journalctl -u social-poster -f
~~~

---

## Common API Failures

| Platform | Error | Solution |
| :--- | :--- | :--- |
| **Mastodon** | `401 Unauthorized` | Regenerate your Access Token in Development settings. |
| **Bluesky** | `Invalid Identifier` | Ensure you are using your full handle (e.g., `user.bsky.social`) and an App Password, not your master password. |
| **Telegram** | `403 Forbidden` | Ensure the bot is an Administrator in the target channel/group. |
| **LinkedIn** | `Expired Token` | LinkedIn tokens typically expire every 60 days. Re-run the OAuth flow. |

---

## Database Maintenance

Over time, the SQLite database may benefit from optimization, especially after large batches of media uploads or a flood event.

~~~bash
# Open the production database
sqlite3 /mnt/data/poster/db/app.db

# Optimization commands
sqlite> VACUUM;   -- Reclaims unused space and defragments the file
sqlite> ANALYZE;  -- Updates statistics for the query planner
~~~

---

## Hardware & Cooling

Because this project often runs on a Raspberry Pi 5 with overclocking enabled, hardware stability is a common troubleshooting factor.

* **Check Temperature:** `vcgencmd measure_temp` (Keep under 70°C).
* **Check Throttling:** `vcgencmd get_throttled`. A result other than `0x0` indicates power or heat issues.
* **NVMe Health:** If the database becomes "Read-Only," check the health of your M.2 drive in the Pironman 5 Max case.

---

## Automated Testing

Before opening a GitHub issue, run the built-in verification suite to ensure your local environment is configured correctly.

~~~bash
# Run the integration test suite
cd ~/social-poster
./venv/bin/pytest tests/test_verification.py -v
~~~

---

## Platform Specific Remediation

Use these guides to perform bulk deletions and clean up platform-specific spam caused by automation errors.

| Platform | Guide |
| :--- | :--- |
| **🐘 Mastodon** | [Mastodon Remediation](mastodon_remediation.md) |
| **🦋 Bluesky** | [Bluesky Remediation](bluesky_remediation.md) |
| **✈️ Telegram** | [Telegram Remediation](telegram_remediation.md) |
| **👥 Facebook** | [Facebook Remediation](facebook_remediation.md) |
| **💼 LinkedIn** | [LinkedIn Remediation](linkedin_remediation.md) |

---

[⬅️ Back to Main README](../README.md)
