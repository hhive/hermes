---
name: hermes-agent-operations
description: "Operate Hermes Agent installations including backup, restore, migration, profile verification, and gateway-safe recovery workflows."
---

# Hermes Agent Operations

Use this skill when the user asks to restore, back up, migrate, repair, or verify a Hermes Agent installation, especially anything involving `~/.hermes`, profiles, gateway state, or a Git-backed backup.

## Core Principles

1. Treat `~/.hermes` as the primary state directory for profiles, memories, skills, sessions, cron jobs, pairing data, logs, and local config.
2. Never overwrite an existing `~/.hermes` without first making a timestamped local backup.
3. Verify live prerequisites before acting: `hermes version`, `hermes profile list`, `git`, and SSH/auth access for remote backups.
4. Keep credentials local and private: `config.yaml`, `.env`, and `auth.json` may be intentionally excluded from Git backups and may need to be restored from a local backup.
5. Distinguish durable restore steps from environment-specific failures. Capture retry patterns and safety checks, not transient network or setup errors.

## Git-Backed Artifact Backup Workflow

When maintaining scheduled scripts that mirror selected Hermes artifacts to Git:

1. Keep paths portable: derive `HERMES_HOME` from `HERMES_HOME` or `Path.home() / ".hermes"`; avoid old host-specific paths.
2. Bound Git subprocesses with explicit timeouts so no-agent cron jobs fail clearly before the scheduler timeout.
3. Prefer SSH remotes for noninteractive cron pushes when SSH auth is configured; HTTPS requires token credentials.
4. If a local proxy is required, inject `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and lowercase variants for Git subprocesses from a script env var such as `HERMES_BACKUP_PROXY`.
5. Treat partial clone directories without `.git` as failed worktrees and recreate or archive them before retrying.
6. Push automated backups to a dedicated branch (for example `hermes-artifacts-backup`) when remote `main` has unrelated history; do not force-push unless explicitly requested.
7. Verify both manual script execution and a scheduler-triggered run; then confirm the remote backup branch with `git ls-remote`.

See `references/git-backed-artifact-backup.md` for failure signatures and a condensed troubleshooting recipe.

## Git-Backed Restore Workflow

1. Inspect current state:
   - `command -v hermes && hermes version`
   - `test -e ~/.hermes && stat ~/.hermes`
   - `git ls-remote <repo>` or `ssh -T git@github.com` for GitHub SSH access.
2. Move the current directory aside:
   - `mv ~/.hermes ~/.hermes.backup.$(date +%F-%H%M%S)`
   - Save the backup path somewhere recoverable if the session may continue.
3. Clone the backup into place:
   - `git clone <repo> ~/.hermes`
   - If the clone is large or the connection is fragile, retry with `git clone --depth 1 <repo> ~/.hermes`.
4. If Hermes or the gateway recreates a skeleton `~/.hermes` between backup and clone, inspect it first, then move it aside as `~/.hermes.runtime-created.<timestamp>` before retrying the clone.
5. Restrict permissions after restore:
   - `chmod -R go-rwx ~/.hermes`
6. Verify the restored installation:
   - `hermes version`
   - `hermes profile list`
   - `git -C ~/.hermes status --short`
7. Verify restored scheduled jobs and portable paths:
   - Run `hermes cron list` and confirm expected jobs, schedules, scripts, delivery targets, and `workdir` values.
   - Inspect `~/.hermes/cron/jobs.json` when `hermes cron list` shows stale absolute paths from another machine; update job `workdir` values to the restored `~/.hermes` path instead of leaving jobs pointed at the old host.
   - For script-backed jobs, run the script once from the restored workdir and confirm it can find Git-backed data files. If a script hardcodes the old Hermes directory, prefer `Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))` so future restores remain portable.
   - `git -C ~/.hermes status --short`

## Credentials and Local Config Pitfall

Git backups of `~/.hermes` often omit secrets and machine-local config via `.gitignore`. After cloning, check whether `config.yaml`, `.env`, and `auth.json` exist. If missing and a pre-restore local backup exists, copy them back with preserved metadata:

```bash
for file in config.yaml .env auth.json; do
  if [ ! -e "$HOME/.hermes/$file" ] && [ -e "$backup/$file" ]; then
    cp -p "$backup/$file" "$HOME/.hermes/$file"
  fi
done
chmod -R go-rwx "$HOME/.hermes"
hermes profile list
```

A successful restore should show the expected profile/model. If the model is blank, local config was likely not restored or the config schema needs migration.

## Post-Restore Git Status

After restoring local-only files from the pre-restore backup, `git -C ~/.hermes status --short` may show expected dirty or untracked entries such as `config.yaml`, `.env`, `auth.json`, `SOUL.md`, `cron/jobs.json`, or `cron/output/...`. Report these clearly as local/runtime state rather than treating them as restore failure, unless the user asked for a pristine Git working tree.

## Gateway Handling

Only restart or start gateway services after the file restore and profile verification are complete. Gateway restart changes live service state, so if the environment requires confirmation or the user denies it, stop and report that the restored files are in place but the gateway was not restarted.

Useful commands:

```bash
hermes gateway restart
hermes profile list
```

## Verification Checklist

- Original `~/.hermes` has a timestamped backup path.
- New `~/.hermes` exists and has restrictive permissions.
- Git clone points to the expected remote/commit.
- Required local config/secrets are present or explicitly reported missing.
- `hermes profile list` recognizes the expected default profile/model.
- Gateway state is reported separately from file restore state.

## Git Backup Cron Troubleshooting

When a script-backed Hermes Git backup cron job times out or hangs:

1. Inspect the cron output file first, then run the script manually with an outer `timeout` to distinguish scheduler timeout from script failure.
2. Check for non-portable restored paths in backup scripts. Prefer `Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()` over machine-specific absolute paths.
3. Prefer the authenticated Git transport already proven on the host. If `git ls-remote https://...` hangs but `ssh -T git@github.com` succeeds, use the SSH remote.
4. Wrap subprocess Git calls with explicit timeouts so cron reports the failing Git operation instead of hanging until the scheduler kills the script.
5. If a clone attempt times out, treat an existing target directory without `.git` as a partial clone and remove/recreate it before retrying.
6. Use shallow clone (`git clone --depth 1`) for backup worktrees unless full history is required.
7. Avoid pushing generated backup snapshots directly to a shared `main` branch when the remote may diverge. Push to a dedicated backup branch or explicitly fetch/rebase before pushing; never silently force-push.

Add a short reference under `references/` when a session reveals a concrete backup-script migration pattern or Git failure transcript worth preserving.

## References

- `references/git-backed-home-restore.md` — session-specific notes from restoring a Git-backed `~/.hermes` backup and recovering omitted local config files.
- `references/git-backup-cron-timeouts.md` — reusable pattern for debugging script-backed Git backup cron timeouts after migration or remote transport issues.
