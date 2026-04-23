# Flood Post Remediation: Overview

A runbook for diagnosing, stopping, and recovering from accidental mass duplicate posting incidents.

## 🚨 Immediate Response Checklist
When a flood is in progress, speed is critical. Perform these steps in order:

1. **Stop the service immediately:** `sudo systemctl stop pnwc-poster`
2. **Identify the offending post ID:** Run the SQL diagnostic below.
3. **Clear the retry queue:** Remove entries for that specific post.
4. **Force status to 'sent':** Prevent the post from being eligible for re-dispatch.
5. **Verify and Restart:** Only restart once the retry queue is empty.

## 🔍 Database Diagnostics (SQLite)
Access your database: `sqlite3 /mnt/data/pnwc/db/pnwc.db`

### Identify the Culprit
~~~sql
SELECT post_id, COUNT(*) as count 
FROM post_events 
GROUP BY post_id 
ORDER BY count DESC LIMIT 5;
~~~

### Clean the Backlog
Replace `POST_ID` with the ID found above:
~~~sql
-- Remove from retry logic
DELETE FROM retry_queue WHERE post_id = POST_ID;

-- Mark as finished
UPDATE posts SET status = 'sent' WHERE id = POST_ID;

-- Clean orphaned events
DELETE FROM post_events WHERE post_id NOT IN (SELECT id FROM posts);
~~~

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

## Repository Documentation
| File | Description |
| :--- | :--- |
| [**Flood Remediation: Overview**](flood_remediation.md) | Emergency steps to clear a jammed event queue |
| [**Security**](../security.md) | Policy on vulnerability reporting and hardening |
| [**Contributing**](../contributing.md) | Guidelines for adding new platform connectors |
| [**Changelog**](../changelog.md) | History of bug fixes and new features |

---

[⬅️ Back to Troubleshooting Index](README.md)
[⬅️ Back to Main README](../README.md)



