# Platform Cleanup: Mastodon

## Prerequisites
1. Log into your instance -> Settings -> Development -> New Application.
2. Scopes: Check `read:statuses` and `write:statuses`.
3. Copy the **Access Token**.

## Bulk Delete Script
Save as `delete_mastodon_posts.py`. Replace `MASTODON_INSTANCE` and `ACCESS_TOKEN`.

~~~python
import time, urllib.request, json

MASTODON_INSTANCE = "https://mastodon.social"
ACCESS_TOKEN = "YOUR_TOKEN"

HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

def api_request(url, method="GET"):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode()) if method == "GET" else True
    except Exception as e:
        print(f"Error: {e}")
        return None

def delete_all_posts():
    user = api_request(f"{MASTODON_INSTANCE}/api/v1/accounts/verify_credentials")
    if not user: return
    
    while True:
        statuses = api_request(f"{MASTODON_INSTANCE}/api/v1/accounts/{user['id']}/statuses?limit=40")
        if not statuses: break
        for s in statuses:
            api_request(f"{MASTODON_INSTANCE}/api/v1/statuses/{s['id']}", "DELETE")
            print(f"Deleted: {s['id']}")
            time.sleep(0.3)

if __name__ == "__main__":
    delete_all_posts()
~~~

[⬅️ Back to Troubleshooting Index](README.md)
