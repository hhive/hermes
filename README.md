# Hermes Backup

This repository is populated automatically from the local Hermes home directory.

Backed up:
- Curated scripts under `scripts/`
- Cron job definitions and cron output under `cron/`
- Agent-created or customized skills under `skills/`
- A-share paper-trading portfolio/research state

Intentionally excluded:
- `.env`, tokens, credentials, `auth.json`
- Raw logs and raw sessions
- Runtime DB/lock/cache files
- Installed Hermes source checkout and virtualenv
