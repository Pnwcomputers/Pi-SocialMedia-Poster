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

## [Unreleased]

### Planned
- Instagram connector (pending Meta Business account link)
- LinkedIn Company Page posting (pending Marketing Developer Platform approval)
- Scheduled posts UI
- Post templates for recurring content formats
- Grafana dashboard over the SQLite event log
- Facebook token expiry monitoring
- Multi-account support per platform
