![Status](https://img.shields.io/badge/Status-Maintenance--Mode-orange)
![Database](https://img.shields.io/badge/Database-SQLite-003B57)
![Action](https://img.shields.io/badge/Action-Required-red)

---

# 🚨 Flood Posting Remediation

This guide provides an emergency recovery procedure for when the application enters a "flooding" state—where the `post_events` table grows exponentially or the worker script enters an infinite retry loop.

---

## Table of Contents
- [Symptoms](#symptoms)
- [Emergency Shutdown](#emergency-shutdown)
- [Database Surgery](#database-surgery)
- [Root Cause Analysis](#root-cause-analysis)
- [Prevention](#prevention)

---

## Symptoms

- **High CPU Load:** `htop` shows Python/Uvicorn processes consuming 100% CPU.
- **Log Spam:** `journalctl` is flooded with database write errors or API timeout retries.
- **Storage Spike:** The `app.db` file size increases rapidly (megabytes per minute).
- **Ghost Events:** The dashboard shows hundreds of pending events for a post ID that may not even exist.

---

## Emergency Shutdown

Before you can clean the database, you must kill the active worker process to prevent it from re-inserting rows as you delete them.

~~~bash
# 1. Stop the systemd service
sudo systemctl stop social-poster

# 2. Verify no ghost processes are running
ps aux | grep uvicorn
# If a process persists, kill it manually:
# kill -9 <PID>
~~~

---

## Database Surgery

Usually, flooding occurs because a post was deleted from the `posts` table, but its associated events remained in the queue. This is known as an **Orphaned Record Loop**.

### 1. Access the Data Volume
~~~bash
sqlite3 /mnt/data/poster/db/app.db
~~~

### 2. Identify the "Heavy" Post
Find out which ID is causing the event spike:
~~~sql
SELECT post_id, COUNT(*) as cnt 
FROM post_events 
GROUP BY post_id 
ORDER BY cnt DESC 
LIMIT 5;
~~~

### 3. Clear the Backlog (The "Nuclear" Option)
If the system is completely unresponsive, wipe the event queue and the retry queue to reset the application state:
~~~sql
-- Clear the main event queue
DELETE FROM post_events;

-- Clear the exponential backoff retry queue
DELETE FROM retry_queue;

-- Clean up orphans (Events pointing to non-existent posts)
DELETE FROM post_events WHERE post_id NOT IN (SELECT id FROM posts);

-- Shrink the database file back to normal size
VACUUM;
~~~

---

## Root Cause Analysis

| Cause | Logic Failure |
|---|---|
| **Orphaned Post** | A user deleted a post record while the worker was processing it. The worker crashed, never marked the event "done," and retried forever. |
| **Draft Conflict** | A post was created as a `draft` but an event was manually injected into the queue. The worker ignores drafts, fails the dispatch, and triggers a retry. |
| **API Rate Limiting** | Mastodon or Bluesky blocked the IP due to high frequency, triggering the exponential backoff which eventually flooded the RAM. |

---

## Prevention

1. **Check Status Before Deletion:** Never delete a post from the `posts` table if it still has `pending` events in the `post_events` log.
2. **Dry Run Testing:** Always keep `DRY_RUN=true` in your `.env` when testing new formatting or large batches of media.
3. **Foreign Key Integrity:** Ensure your migrations include `ON DELETE CASCADE` if modifying the schema manually.

---

[⬅️ Back to Main README](README.md)
