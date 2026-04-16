# Flood Post Remediation Guide

A runbook for diagnosing, stopping, and recovering from accidental mass duplicate posting across social media platforms.

---

## Table of Contents

- [What Is a Flood Post Incident](#what-is-a-flood-post-incident)
- [Immediate Response Checklist](#immediate-response-checklist)
- [Diagnosing the Cause](#diagnosing-the-cause)
- [Stopping an Active Flood](#stopping-an-active-flood)
- [Platform Cleanup](#platform-cleanup)
  - [Mastodon](#mastodon)
  - [Bluesky](#bluesky)
  - [Telegram](#telegram)
  - [LinkedIn](#linkedin)
  - [Facebook](#facebook)
- [Handling Platform Warnings and Suspensions](#handling-platform-warnings-and-suspensions)
- [After Cleanup](#after-cleanup)
- [Prevention](#prevention)

---

## What Is a Flood Post Incident

A flood post incident occurs when automation posts the same content to one or more platforms repeatedly and unintentionally. Common symptoms:

- Dozens or hundreds of identical posts appearing in rapid succession
- Platform spam warnings or account suspensions
- `429 Too Many Requests` errors flooding the event log
- Retry queue growing without bound
- Followers reporting spam

### Known root causes in pnwc-poster

| Cause | Description | Fixed in version |
|---|---|---|
| Retry queue re-dispatching all targets | `dispatch_post()` called instead of `dispatch_single()` — every retry re-posted to all platforms including already-successful ones | 1.0.1 |
| Post status never updated | Posts stuck in `draft`/`queued` state were eligible for repeated dispatch | 1.0.1 |
| No idempotency guard | Dispatch endpoint had no protection against double-calls | 1.0.1 |

---

## Immediate Response Checklist

When you notice a flood in progress, work through these steps in order. Speed matters — every second the service is running adds more duplicate posts.

```
[ ] 1. Stop the service immediately
[ ] 2. Identify the offending post ID from the event log
[ ] 3. Clear the retry queue for that post
[ ] 4. Force the post status to 'sent'
[ ] 5. Verify retry queue is empty before restarting
[ ] 6. Restart the service
[ ] 7. Monitor the event log for 5 minutes to confirm no new activity
[ ] 8. Begin platform cleanup
[ ] 9. Respond to any platform warnings
```

---

## Diagnosing the Cause

### 1. Check the event log for the pattern

A flood always shows as many events with the same `post_id` in a short time window. In the dashboard, filter by the affected platform and look for the repeating post ID.

### 2. Check the retry queue

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT post_id, platform, attempts, next_retry FROM retry_queue ORDER BY post_id;"
```

A post with high `attempts` and a short `next_retry` is actively flooding.

### 3. Check post status

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT id, status, created_at, updated_at FROM posts ORDER BY created_at DESC LIMIT 20;"
```

Posts stuck in `draft`, `queued`, or `partial` status after a dispatch are eligible to be re-dispatched.

### 4. Check service logs

```bash
sudo journalctl -u pnwc-poster -n 100 --no-pager | grep -E "dispatch|retry|ERROR"
```

---

## Stopping an Active Flood

### Step 1 — Stop the service

```bash
sudo systemctl stop pnwc-poster
```

Do not skip this step. Every second the service is running with an active retry queue adds more posts.

### Step 2 — Identify the offending post ID

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT post_id, COUNT(*) as count FROM post_events GROUP BY post_id ORDER BY count DESC LIMIT 5;"
```

The post ID with the highest event count is the culprit.

### Step 3 — Clear its retry queue entries

Replace `POST_ID` with the actual ID:

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db "DELETE FROM retry_queue WHERE post_id = POST_ID;"
```

### Step 4 — Force the post status to sent

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db "UPDATE posts SET status = 'sent' WHERE id = POST_ID;"
```

### Step 5 — Verify before restarting

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db "SELECT id, status FROM posts WHERE id = POST_ID;"
sqlite3 /mnt/data/pnwc/db/pnwc.db "SELECT COUNT(*) FROM retry_queue WHERE post_id = POST_ID;"
```

Expected output:
```
POST_ID|sent
0
```

Only restart the service after seeing `0` retry queue entries.

### Step 6 — Restart and monitor

```bash
sudo systemctl start pnwc-poster
```

Watch the event log in the dashboard for 5 minutes. No new entries for the offending post ID means you are clean.

---

## Platform Cleanup

### Mastodon

Mastodon has a well-documented REST API that supports bulk deletion via script.

#### Prerequisites

Create a dedicated app token with `read:statuses` and `write:statuses` scopes:

1. Log into your instance → **Settings → Development → New Application**
2. App name: anything (e.g. `cleanup-tool`)
3. Scopes: check `read:statuses` and `write:statuses` only
4. Submit and copy the **access token** shown at the bottom

> **Important:** Even if you already have an app token, create a new one for this purpose. Existing tokens may lack `read:statuses` and cannot list your posts for deletion.

#### Bulk delete script

Save this as `delete_mastodon_posts.py` and replace the token and instance values:

```python
#!/usr/bin/env python3
"""
Mastodon Bulk Post Deleter
Deletes all posts from your account using the Mastodon REST API.
Handles rate limiting automatically.
"""
import time
import urllib.request
import urllib.error
import json

MASTODON_INSTANCE = "https://mastodon.social"   # Change to your instance
ACCESS_TOKEN = "YOUR_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

def api_request(url, method="GET"):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if method == "GET":
                return json.loads(resp.read().decode())
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 429:
            print("  Rate limited — waiting 60 seconds...")
            time.sleep(60)
            return api_request(url, method)
        print(f"  HTTP {e.code} error on {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def get_account_id():
    data = api_request(f"{MASTODON_INSTANCE}/api/v1/accounts/verify_credentials")
    if data:
        print(f"Logged in as: @{data['username']}")
        print(f"Total posts reported: {data['statuses_count']}")
        return data["id"]
    return None

def fetch_statuses(account_id, max_id=None):
    url = f"{MASTODON_INSTANCE}/api/v1/accounts/{account_id}/statuses?limit=40&exclude_reblogs=false"
    if max_id:
        url += f"&max_id={max_id}"
    return api_request(url)

def delete_all_posts():
    account_id = get_account_id()
    if not account_id:
        print("Failed to get account info. Check your token.")
        return

    total_deleted = 0
    total_skipped = 0
    max_id = None

    print("\nStarting deletion...\n")

    while True:
        statuses = fetch_statuses(account_id, max_id)

        if not statuses:
            print("\nNo more posts found.")
            break

        for status in statuses:
            post_id = status["id"]
            created = status["created_at"][:10]
            content = status.get("content", "").replace("<p>", "") \
                           .replace("</p>", "").replace("<br>", " ")[:60]

            result = api_request(
                f"{MASTODON_INSTANCE}/api/v1/statuses/{post_id}",
                method="DELETE"
            )

            if result is None:
                print(f"  SKIP  [{created}] {post_id} — already gone")
                total_skipped += 1
            else:
                print(f"  DEL   [{created}] {post_id} — {content}")
                total_deleted += 1

            max_id = post_id
            time.sleep(0.3)

    print(f"\nDone.")
    print(f"  Deleted:  {total_deleted}")
    print(f"  Skipped:  {total_skipped}")
    print(f"  Total:    {total_deleted + total_skipped}")

if __name__ == "__main__":
    delete_all_posts()
```

Run it:

```bash
python3 delete_mastodon_posts.py
```

Rate limiting is handled automatically — the script pauses 60 seconds when it hits a 429 and resumes. At 0.3 seconds per deletion expect approximately 1 minute per 200 posts plus any rate limit pauses.

#### Mastodon rate limits

| Limit | Value |
|---|---|
| DELETE requests | ~30 per 5 minutes on most instances |
| mastodon.social specifically | More aggressive — expect 60-second pauses |

---

### Bluesky

Bluesky uses the AT Protocol. Posts (called "records") are deleted via `com.atproto.repo.deleteRecord`.

#### Bulk delete script

Save as `delete_bluesky_posts.py`:

```python
#!/usr/bin/env python3
"""
Bluesky Bulk Post Deleter
Deletes all posts from your account via the AT Protocol.
"""
import time
import urllib.request
import urllib.error
import json

BLUESKY_HANDLE = "yourhandle.bsky.social"
BLUESKY_APP_PASSWORD = "your-app-password"
PDS_HOST = "https://bsky.social"

def create_session():
    url = f"{PDS_HOST}/xrpc/com.atproto.server.createSession"
    payload = json.dumps({
        "identifier": BLUESKY_HANDLE,
        "password": BLUESKY_APP_PASSWORD
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def list_posts(did, access_token, cursor=None):
    url = (f"{PDS_HOST}/xrpc/com.atproto.repo.listRecords"
           f"?repo={did}&collection=app.bsky.feed.post&limit=100")
    if cursor:
        url += f"&cursor={cursor}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def delete_post(did, access_token, rkey):
    url = f"{PDS_HOST}/xrpc/com.atproto.repo.deleteRecord"
    payload = json.dumps({
        "repo": did,
        "collection": "app.bsky.feed.post",
        "rkey": rkey
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={"Authorization": f"Bearer {access_token}",
                                           "Content-Type": "application/json"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  Rate limited — waiting 60 seconds...")
            time.sleep(60)
            return delete_post(did, access_token, rkey)
        print(f"  HTTP {e.code} on {rkey}")
        return False

def delete_all_posts():
    print("Authenticating...")
    session = create_session()
    did = session["did"]
    access_token = session["accessJwt"]
    print(f"Logged in as: {BLUESKY_HANDLE} ({did})")

    total_deleted = 0
    cursor = None

    print("\nStarting deletion...\n")

    while True:
        data = list_posts(did, access_token, cursor)
        records = data.get("records", [])

        if not records:
            print("\nNo more posts found.")
            break

        for record in records:
            rkey = record["uri"].split("/")[-1]
            text = record.get("value", {}).get("text", "")[:60]
            result = delete_post(did, access_token, rkey)
            if result:
                print(f"  DEL   {rkey} — {text}")
                total_deleted += 1
            time.sleep(0.5)

        cursor = data.get("cursor")
        if not cursor:
            break

    print(f"\nDone. Deleted: {total_deleted}")

if __name__ == "__main__":
    delete_all_posts()
```

Run it:

```bash
python3 delete_bluesky_posts.py
```

#### Bluesky rate limits

| Limit | Value |
|---|---|
| Writes per 5 minutes | 3,000 |
| Writes per day | 35,000 |

Bluesky is generally more lenient than Mastodon for bulk operations.

---

### Telegram

Telegram does not support bulk deletion via API for channel posts. Options:

#### Option A — Telegram desktop app (recommended for large floods)

1. Open Telegram Desktop
2. Go to your channel
3. Click the first duplicate post
4. Scroll to the last duplicate while holding **Shift** and click it
5. Right-click → **Delete** → check **Delete for everyone**

This is the fastest method for large numbers of posts.

#### Option B — Bot API deletion (if you know the message IDs)

The Telegram Bot API `deleteMessage` endpoint deletes one message at a time and requires the exact `message_id`. Your pnwc-poster event log contains `remote_id` for every successful Telegram post — use those:

```bash
# Get all Telegram remote_ids for a specific post
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT remote_id FROM post_events WHERE post_id = POST_ID AND platform = 'telegram' AND success = 1;"
```

Then delete each one:

```bash
BOT_TOKEN="your_bot_token"
CHAT_ID="your_chat_id"

# For each message_id from the query above:
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteMessage" \
  -d "chat_id=${CHAT_ID}&message_id=MESSAGE_ID"
```

#### Telegram limits

- Bots can only delete messages sent within the last 48 hours via API
- For older messages, use Telegram Desktop

---

### LinkedIn

LinkedIn does not provide a bulk deletion API. Posts must be deleted individually.

#### Via the LinkedIn website

1. Go to your LinkedIn profile
2. Click **Posts** tab
3. Click the three dots `...` on each post → **Delete post**

For large numbers of posts this is tedious. LinkedIn has no official bulk delete tool.

#### Via the API (if you have post URNs)

If your event log captured `remote_id` values for the flood posts:

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT remote_id FROM post_events WHERE post_id = POST_ID AND platform = 'linkedin' AND success = 1;"
```

Then delete each URN:

```bash
ACCESS_TOKEN="your_linkedin_token"

curl -s -X DELETE \
  "https://api.linkedin.com/v2/ugcPosts/ENCODED_URN" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "X-Restli-Protocol-Version: 2.0.0"
```

Note: The URN must be URL-encoded. `urn:li:ugcPost:1234567890` becomes `urn%3Ali%3AugcPost%3A1234567890`.

#### LinkedIn rate limits

LinkedIn enforces strict daily limits. If you hit them during cleanup, wait 24 hours and continue.

---

### Facebook

Facebook Page posts can be deleted via the Graph API.

#### Get all flood post IDs from the event log

```bash
sqlite3 /mnt/data/pnwc/db/pnwc.db \
  "SELECT remote_id FROM post_events WHERE post_id = POST_ID AND platform = 'facebook' AND success = 1;"
```

#### Delete each post

```bash
PAGE_TOKEN="your_page_access_token"

curl -s -X DELETE \
  "https://graph.facebook.com/v25.0/POST_ID?access_token=${PAGE_TOKEN}"
```

#### Bulk delete script

Save as `delete_facebook_posts.py` and replace credentials:

```python
#!/usr/bin/env python3
"""
Facebook Page Bulk Post Deleter
Deletes all recent posts from a Facebook Page via the Graph API.
"""
import time
import urllib.request
import urllib.error
import json

PAGE_ID = "your_page_id"
PAGE_ACCESS_TOKEN = "your_page_access_token"
API_VERSION = "v25.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"

def get_posts(after=None):
    url = f"{BASE}/{PAGE_ID}/posts?access_token={PAGE_ACCESS_TOKEN}&limit=100"
    if after:
        url += f"&after={after}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def delete_post(post_id):
    url = f"{BASE}/{post_id}?access_token={PAGE_ACCESS_TOKEN}"
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  Rate limited — waiting 60 seconds...")
            time.sleep(60)
            return delete_post(post_id)
        print(f"  HTTP {e.code} on {post_id}")
        return False

def delete_all_posts():
    total_deleted = 0
    after = None

    print("Starting deletion...\n")

    while True:
        data = get_posts(after)
        posts = data.get("data", [])

        if not posts:
            print("\nNo more posts found.")
            break

        for post in posts:
            post_id = post["id"]
            message = post.get("message", "")[:60]
            result = delete_post(post_id)
            if result:
                print(f"  DEL   {post_id} — {message}")
                total_deleted += 1
            time.sleep(0.5)

        paging = data.get("paging", {})
        after = paging.get("cursors", {}).get("after")
        if not after:
            break

    print(f"\nDone. Deleted: {total_deleted}")

if __name__ == "__main__":
    delete_all_posts()
```

---

## Handling Platform Warnings and Suspensions

### Mastodon spam warning

If your instance sends a spam warning:

1. Reply to the warning email explaining the situation — automated posting bug, now resolved
2. Provide the approximate time window of the flood
3. Confirm you have deleted all duplicate posts
4. Most instance admins are understanding about genuine automation bugs

### Bluesky

Bluesky has automated rate limiting but does not typically issue manual warnings for single incidents. If your account is temporarily restricted, it will self-clear after the rate limit window resets (shown in the `ratelimit-reset` header in your event log).

### LinkedIn

LinkedIn's `APPLICATION_AND_MEMBER DAY` limit resets at midnight UTC. If you hit it during a flood, cleanup may need to be spread across multiple days. Contact LinkedIn Support only if the account is suspended, not just rate-limited.

### Facebook

Facebook Page publishing limits reset every 24 hours. A flood that triggers the spam detection system may temporarily restrict Page posting. Submit a review request via the Facebook Business Help Center if the restriction persists after 24 hours.

---

## After Cleanup

Once all duplicate posts are removed and platforms are clean, run the full verification test suite to confirm pnwc-poster is healthy before making any new posts:

```bash
cd ~/pnwc-poster && ~/pnwc-poster/venv/bin/pytest -v
```

All 19 tests passing confirms the service is safe to use.

Then make one test post with `dry_run=true` from the dashboard, verify it appears in the event log as `sent`, and confirm no duplicates appear before switching back to live posting.

---

## Prevention

The following measures are already implemented in pnwc-poster v1.0.1 and prevent recurrence:

| Measure | Implementation |
|---|---|
| Single-platform retry | `dispatch_single()` in `dispatcher.py` — retries only the failed platform |
| Post status tracking | `update_post_status()` — marks posts `sent`/`partial`/`failed` after dispatch |
| Idempotency guard | `POST /api/posts/{id}/dispatch` returns `409` if post is already `sent` |
| Max retry cap | `MAX_ATTEMPTS = 5` in `queue.py` — drops permanently failing posts after 5 tries |

### Additional recommended practices

- Always keep `DRY_RUN=true` in `.env` when testing new post formats or connector changes
- Run `pytest -v` after any code change before re-enabling live posting
- Monitor the event log after every new post for the first 2 minutes
- Keep the verification test suite up to date as new platforms are added
- Never manually trigger dispatch on the same post twice — use the dashboard's status indicator to confirm `sent` before moving on
