# Platform Cleanup: Telegram

## Option A: Manual (Fastest for Channels)
1. Open **Telegram Desktop**.
2. Click the first duplicate post.
3. Hold **Shift** and click the last duplicate.
4. Right-click -> **Delete** -> Check **Delete for everyone**.

## Option B: Bot API (Automated)
If you have the `remote_id` from your logs:
~~~bash
BOT_TOKEN="your_token"
CHAT_ID="your_id"

# Delete single message
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteMessage" \
  -d "chat_id=${CHAT_ID}&message_id=MESSAGE_ID"
~~~
*Note: Bots can only delete messages sent within the last 48 hours.*

[⬅️ Back to Troubleshooting Index](README.md)
