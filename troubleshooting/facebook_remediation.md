# Platform Cleanup: Facebook

## Bulk Delete Script
Save as `delete_fb_posts.py`. Requires Page Access Token.

~~~python
import time, urllib.request, json

PAGE_ID = "your_page_id"
TOKEN = "your_page_token"

def delete_all():
    while True:
        url = f"https://graph.facebook.com/v25.0/{PAGE_ID}/posts?access_token={TOKEN}&limit=100"
        with urllib.request.urlopen(url) as resp:
            posts = json.loads(resp.read().decode())["data"]
        if not posts: break
        for p in posts:
            del_url = f"https://graph.facebook.com/v25.0/{p['id']}?access_token={TOKEN}"
            req = urllib.request.Request(del_url, method="DELETE")
            urllib.request.urlopen(req)
            print(f"Deleted: {p['id']}")
            time.sleep(0.5)

if __name__ == "__main__":
    delete_all()
~~~

[⬅️ Back to Troubleshooting Index](README.md)
