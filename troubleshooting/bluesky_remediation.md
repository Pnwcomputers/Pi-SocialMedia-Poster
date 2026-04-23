# Platform Cleanup: Bluesky

## Bulk Delete Script
Uses the AT Protocol. Save as `delete_bluesky_posts.py`.

~~~python
import time, urllib.request, json

HANDLE = "your.bsky.social"
PASSWORD = "app-password"

def create_session():
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    data = json.dumps({"identifier": HANDLE, "password": PASSWORD}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def delete_all():
    sess = create_session()
    token, did = sess["accessJwt"], sess["did"]
    
    while True:
        url = f"https://bsky.social/xrpc/com.atproto.repo.listRecords?repo={did}&collection=app.bsky.feed.post&limit=100"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as resp:
            records = json.loads(resp.read().decode())["records"]
        if not records: break
        for r in records:
            rkey = r["uri"].split("/")[-1]
            del_url = "https://bsky.social/xrpc/com.atproto.repo.deleteRecord"
            del_data = json.dumps({"repo": did, "collection": "app.bsky.feed.post", "rkey": rkey}).encode()
            req = urllib.request.Request(del_url, data=del_data, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req)
            print(f"Deleted: {rkey}")
            time.sleep(0.5)

if __name__ == "__main__":
    delete_all()
~~~

[⬅️ Back to Troubleshooting Index](README.md)
