# Changelog

All notable changes to Pi Social Poster are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-04-15

### Added
- Initial release
- FastAPI application with SQLite (WAL mode) backend
- Simultaneous posting to Mastodon, Bluesky, Telegram, LinkedIn, and Facebook
- Per-platform formatters with character limits and content shaping
- Image upload with automatic compression (Bluesky 2MB limit handled transparently)
- Dry run mode for safe testing before going live
- Retry queue with exponential backoff (15-minute intervals, 5 max attempts)
- APScheduler-based retry runner (15-minute polling cycle)
- Web dashboard — post composer with platform selector
- Web dashboard — event log with platform/status filters and expandable error details
- Dashboard login authentication (JWT cookie, bcrypt password)
- Dispatch button with inline result feedback
- Media upload area with image preview and remove option
- LinkedIn OAuth 2.0 flow with SSH tunnel support
- Facebook Page token verification and long-lived token guide
- systemd service with `network-online.target` dependency
- Tailscale remote access support
- UFW firewall configuration
- fail2ban installation
- Automatic security updates via unattended-upgrades
- DNS stability via /etc/hosts entries for platform APIs
- NVMe boot migration guide (SD card → SSD 1)
- Dedicated data drive setup (SSD 2 for database and media)
- Pironman 5 Max software installation (OLED, fans, RGB, safe shutdown)
- Overclock settings for Pironman 5 Max (2800MHz CPU / 933MHz GPU)

### Platform support
| Platform | Text | Images | Notes |
|---|---|---|---|
| Mastodon | ✅ | ✅ | |
| Bluesky | ✅ | ✅ | Auto-compressed to <2MB |
| Telegram | ✅ | ✅ | HTML parse mode |
| LinkedIn | ✅ | — | Personal profile only |
| Facebook | ✅ | ✅ | Page posts |
| Instagram | ⏳ | ⏳ | Pending business account link |

---

## [1.0.1] — 2026-04-16
### Fixed
- **Critical:** Retry queue was calling `dispatch_post()` instead of a single-platform
  dispatcher, causing all targets (including already-successful ones) to be re-posted
  on every retry cycle — root cause of the Mastodon flood incident
- Post status never updated after successful dispatch — posts remained in `draft`/`queued`
  state permanently; all posts now transition to `sent`, `partial`, or `failed`
- `dispatch_single` import was located inside the retry for-loop body instead of at
  module level — moved to top-level imports
- Abstract `BaseConnector.post()` signature was missing the `media_paths` parameter,
  causing a `TypeError` on any connector that did not override the signature
- Duplicate imports in `main.py` (`RedirectResponse`, `Cookie`, `Form`, `datetime`)
  introduced during incremental development — consolidated to top-level imports
- `python-jose` was installed in the venv but absent from `requirements.txt` — pinned
  at confirmed version 3.5.0

### Added
- `update_post_status()` function in `database.py` — updates `posts.status` and
  `posts.updated_at` atomically after each dispatch
- `dispatch_single()` function in `dispatcher.py` — dispatches to one platform only,
  used exclusively by the retry queue to prevent cross-platform re-posting
- Idempotency guard on `POST /api/posts/{id}/dispatch` — returns `409 Conflict` if
  the post status is already `sent`, preventing duplicate dispatches from double-clicks
  or network retries
- Verification test suite (`tests/test_verification.py`) — 19 tests across 6 classes
  covering service health, post creation, dry-run dispatch, status updates, idempotency,
  and event logging; runs against the live service with `dry_run=True`

### Security
- `python-jose==3.5.0` pinned in `requirements.txt` to ensure JWT authentication
  dependency is included in all future venv rebuilds

---

## [Unreleased]

### Planned
- Instagram connector (pending Meta Business account link)
- LinkedIn Company Page posting (pending Marketing Developer Platform approval)
- Scheduled posts UI
- Post templates for recurring content formats
- Grafana dashboard over the SQLite event log
- Facebook token expiry monitoring
- Multi-account support per platform
