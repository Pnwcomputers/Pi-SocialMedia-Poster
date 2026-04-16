# Contributing to Pi Social Poster

Thanks for your interest in contributing. This is a self-hosted tool built for reliability — contributions that improve stability, add platform support, or fix bugs are very welcome.

---

## What we're looking for

- Bug fixes
- New platform connectors (Reddit, Threads, Pixelfed, etc.)
- Instagram connector (once Meta business account linking is documented)
- LinkedIn Company Page posting
- Scheduled posts UI
- Post templates
- Performance improvements
- Documentation improvements

---

## Getting started

### 1. Fork and clone

```bash
git clone https://github.com/your_username/Pi-SocialMedia-Poster.git
cd Pi-SocialMedia-Poster
```

### 2. Set up the dev environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a .env file

Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

Set `DRY_RUN=true` while developing — this prevents any live posts during testing.

### 4. Run the app locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## Adding a new platform connector

Each platform needs three things:

### 1. Formatter — `app/formatters/yourplatform.py`

```python
from app.formatters.base import strip_extra_whitespace, extract_hashtags

MAX_CHARS = 500

def format_yourplatform(post: dict) -> str:
    body = strip_extra_whitespace(post.get("body_long") or "")
    hashtags = extract_hashtags(post.get("hashtags") or [])
    # shape content for your platform
    return body[:MAX_CHARS]
```

### 2. Connector — `app/connectors/yourplatform.py`

```python
from app.connectors.base import BaseConnector, ConnectorResult

class YourPlatformConnector(BaseConnector):
    platform = "yourplatform"

    async def post(self, content, dry_run: bool = True, media_paths: list[str] = []) -> ConnectorResult:
        if dry_run:
            return ConnectorResult(platform=self.platform, success=True, dry_run=True,
                                   remote_id="dry-run", remote_url="dry-run")
        # implement live posting here
        ...
```

### 3. Wire it up

- Add formatter to `app/formatters/__init__.py`
- Add connector to `app/connectors/__init__.py`
- Add to `CONNECTORS` dict in `app/dispatcher.py`
- Add to `allowed` set in `app/schemas.py`
- Add button to `app/dashboard/templates/index.html`
- Add credentials to `app/config.py` and `.env.example`

---

## Code style

- Follow existing patterns — each connector and formatter follows the same interface
- Keep connectors responsible only for HTTP/auth — content shaping belongs in formatters
- Always handle both `dry_run=True` and `dry_run=False` paths
- Return a `ConnectorResult` — never raise exceptions from a connector
- Add credentials to `config.py` as typed fields with empty string defaults
- Never hardcode credentials or tokens

---

## Pull request process

1. Branch from `main`: `git checkout -b feature/your-feature-name`
2. Keep PRs focused — one feature or fix per PR
3. Test with `DRY_RUN=true` before submitting
4. Update `CHANGELOG.md` under `[Unreleased]`
5. Update `README.md` if you add a new platform or change setup steps
6. Open a PR with a clear description of what changed and why

---

## Reporting bugs

Open an issue at https://github.com/Pnwcomputers/Pi-SocialMedia-Poster/issues with:

- What you were doing
- What you expected to happen
- What actually happened
- Relevant logs (`journalctl -u social-poster --no-pager | tail -30`)
- Your OS and Python version

---

## Questions

Open a discussion or issue — happy to help get things working.
