# Platform Cleanup: LinkedIn

## Manual Cleanup
1. Go to your LinkedIn Profile/Page.
2. Click **Posts**.
3. Click the three dots `...` on each post -> **Delete post**.

## API Cleanup
If you have the URNs (e.g., `urn:li:ugcPost:12345`):
~~~bash
ACCESS_TOKEN="your_token"

curl -s -X DELETE \
  "https://api.linkedin.com/v2/ugcPosts/ENCODED_URN" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "X-Restli-Protocol-Version: 2.0.0"
~~~
*Note: The URN must be URL-encoded (e.g., `:` becomes `%3A`).*

[⬅️ Back to Troubleshooting Index](README.md)
