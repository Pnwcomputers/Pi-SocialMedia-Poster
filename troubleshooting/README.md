![Platforms](https://img.shields.io/badge/Platforms-Mastodon%20%7C%20Bluesky%20%7C%20Telegram%20%7C%20LinkedIn%20%7C%20Facebook-blue)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-green)
![Status](https://img.shields.io/badge/Status-Troubleshooting-orange)

---

# 🛠 General Troubleshooting

This guide covers common issues encountered while running the Pi-SocialMedia-Poster on a Raspberry Pi 5. If you are experiencing high CPU usage or database flooding, please see the specialized guide below.

> 🚨 **Critical Issue?** If your database is flooding or the application is stuck in an infinite posting loop, refer immediately to the [Flood Posting Remediation Guide](post_que_issues.md).

---

## Table of Contents
- [Service Status](#service-status)
- [Log Inspection](#log-inspection)
- [Common API Errors](#common-api-errors)
- [Database Maintenance](#database-maintenance)
- [Hardware & Cooling](#hardware--cooling)

---

## Service Status

If the dashboard is inaccessible, verify the status of the FastAPI service:

~~~bash
# Check if the service is active
sudo systemctl status social-poster

# Restart the service after config changes
sudo systemctl restart social-poster
~~~

---

## Log Inspection

Logs are the first place to look for platform-specific errors (e.g., invalid tokens or network timeouts).

~~~bash
# View the last 50 lines of the application log
journalctl -u social-poster -n 50 --no-pager

# Follow logs in real-time
journalctl -u social-poster -f
~~~

---

## Common API Errors

### 🐘 Mastodon / 🦋 Bluesky
- **401 Unauthorized:** Your access token or app password has expired. Regenerate them in the platform settings.
- **429 Too Many Requests:** You have hit the platform's rate limit. The application will automatically move the post to the `retry_queue`.

### ✈️ Telegram
- **403 Forbidden:** The bot was removed from the channel or does not have admin permissions to post.
- **400 Bad Request:** Usually indicates the `TELEGRAM_CHAT_ID` in your `.env` is incorrect.

---

## Database Maintenance

The application uses SQLite for lightweight, reliable storage. Over time, or after a flood event, you may need to optimize the database file.

~~~bash
# Access the DB
sqlite3 /mnt/data/poster/db/app.db

# Within the SQLite prompt:
sqlite> VACUUM; -- Reclaim unused space
sqlite> REINDEX; -- Rebuild indexes for performance
~~~

---

## Hardware & Cooling

Because this application involves consistent background processing and overclocking (if configured), temperature management is vital.

- **Throttling Check:** Run `vcgencmd get_throttled`. If it returns anything other than `0x0`, your Pi is overheating or under-volted.
- **Temp Monitoring:** Run `vcgencmd measure_temp`. For a Pi 5 in a Pironman 5 Max case, it should ideally stay under 65°C.

---

## Repository Guides
| Guide | Purpose |
|---|---|
| [**Flood Remediation**](post_que_issues.md) | Steps to clear a jammed database and stop posting loops |
| [**Security Hardening**](security.md) | UFW, Fail2Ban, and SSH security configurations |
| [**Changelog**](changelog.md) | Track updates and version-specific fixes |

---

[⬅️ Back to Main README](README.md)
