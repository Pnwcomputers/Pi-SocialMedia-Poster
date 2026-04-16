# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.x | ✅ Yes |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue**.

Instead, report it privately by opening a [GitHub Security Advisory](https://github.com/Pnwcomputers/Pi-SocialMedia-Poster/security/advisories/new) or emailing the maintainer directly.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

You can expect a response within 7 days.

## Security notes for self-hosters

- Never commit your `.env` file — it is in `.gitignore` by default
- The `.env` file should be `chmod 600` and owned by your service user
- Keep `DRY_RUN=true` until you have verified all credentials work correctly
- Restrict port 8080 to your local network and Tailscale only (see README security hardening section)
- Rotate your `SECRET_KEY` if you suspect it has been exposed — this invalidates all active dashboard sessions
- Facebook Page Access Tokens are permanent but can be revoked at any time from your Meta Developer App dashboard
- LinkedIn Access Tokens expire — re-run the OAuth flow at `/auth/linkedin` if posting starts failing
