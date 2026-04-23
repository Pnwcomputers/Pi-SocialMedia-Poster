# Troubleshooting: Event Flooding & Ghost Posts

If you notice your Raspberry Pi social media poster is hammering the database with thousands of events or getting stuck in a loop, follow this guide to clear the backlog and fix the root cause.

## 🚩 Symptoms
- High CPU usage by Python processes.
- The `post_events` table contains hundreds or thousands of rows for the same `post_id`.
- Errors in logs like `Parse error: no such column` or foreign key constraints.
- Posts that have been deleted from the UI still appear to be "processing" in the background.

---

## 🛠️ Phase 1: Stop the Runaway Process
Before cleaning the database, you must stop the worker script from creating new entries.

~~~bash
# Check for running poster scripts
ps aux | grep python

# Kill any process that looks like 'python3 poster.py'
# Replace <PID> with the actual process ID found above
kill -9 <PID>

# If using systemd
sudo systemctl stop host-name.service
~~~

---

## 🧹 Phase 2: Database Surgery (SQLite)
Usually, flooding happens because a post was deleted but its associated "To-Do" events remained in the queue.

1. **Access the database:**
   ~~~bash
   sqlite3 ./host-name/database.db
   ~~~

2. **Identify the "Ghost" Post:**
   Find out which `post_id` is causing the flood:
   ~~~sql
   SELECT post_id, COUNT(*) as cnt FROM post_events GROUP BY post_id ORDER BY cnt DESC;
   ~~~

3. **Clear the Backlog (The "Nuclear Option"):**
   If the system is completely stuck, wipe all pending events to start fresh:
   ~~~sql
   -- Clear the main event queue
   DELETE FROM post_events;

   -- Clear the retry queue
   DELETE FROM retry_queue;

   -- Clean up orphans (events pointing to non-existent posts)
   DELETE FROM post_events WHERE post_id NOT IN (SELECT id FROM posts);

   -- Reclaim disk space
   VACUUM;
   ~~~

4. **Verify the Fix:**
   ~~~sql
   SELECT COUNT(*) FROM post_events;
   -- Should return 0
   ~~~

---

## 🔍 Phase 3: Root Cause Prevention

### 1. Orphaned Records
The most common cause is deleting a post from the `posts` table while the worker is currently trying to post it. Because the `post_id` no longer exists, the worker crashes and never marks the event as "complete."
**Solution:** Always check `post_events` before manually deleting rows from `posts`.

### 2. Status Conflicts
If a post is in `draft` status but has entries in `post_events`, the worker may loop indefinitely.
**Solution:** Ensure your logic only creates events when a post status changes to `published` or `scheduled`.

### 3. API Failures
If one platform (e.g., Telegram) is failing while others (Mastodon, Bluesky) succeed, the event might stay "Pending" for the failed platform and keep retrying.
**Solution:** Check your `.env` credentials and ensure all target platforms are reachable from your Pi.

---

## 📜 Useful Maintenance Queries
Check the status of your current posts:
~~~sql
SELECT id, title, targets, status FROM posts;
~~~

Check how many events are queued per platform:
~~~sql
SELECT platform, status, COUNT(*) FROM post_events GROUP BY platform, status;
~~~
